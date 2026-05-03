package app

import (
	"bytes"
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"regexp"
	"strings"
	"time"

	"leonovcare/backend/internal/judge"

	"github.com/gin-gonic/gin"
	"github.com/jackc/pgx/v5"
)

type chatCompletionRequest struct {
	Model               string        `json:"model"`
	Messages            []chatMessage `json:"messages"`
	Temperature         float64       `json:"temperature"`
	MaxCompletionTokens int           `json:"max_completion_tokens"`
}

type chatMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type chatCompletionResponse struct {
	Model   string `json:"model"`
	Choices []struct {
		Message chatMessage `json:"message"`
	} `json:"choices"`
	Usage struct {
		PromptTokens     int `json:"prompt_tokens"`
		CompletionTokens int `json:"completion_tokens"`
		TotalTokens      int `json:"total_tokens"`
	} `json:"usage"`
	Error *struct {
		Message string `json:"message"`
	} `json:"error,omitempty"`
}

type openAIRequestError struct {
	StatusCode int
	Message    string
}

type aiHintFailedTest struct {
	Index          int
	Input          string
	Expected       string
	Actual         string
	Error          string
	ExpectedHidden bool
}

type aiHintDiagnostic struct {
	Source        string
	Status        string
	CompileOutput string
	RunLog        string
	FirstFailed   *aiHintFailedTest
}

type aiHintProbeCaseMeta struct {
	input    string
	expected string
	hidden   bool
}

func (e *openAIRequestError) Error() string {
	if e == nil {
		return "openai request error"
	}
	if strings.TrimSpace(e.Message) == "" {
		return fmt.Sprintf("openai status %d", e.StatusCode)
	}
	return fmt.Sprintf("openai status %d: %s", e.StatusCode, e.Message)
}

func (a *App) TaskHint(c *gin.Context) {
	uctx, ok := userFromContext(c)
	if !ok {
		unauthorized(c, "unauthorized")
		return
	}

	var req struct {
		TaskID     string `json:"taskId" binding:"required,uuid"`
		SourceCode string `json:"sourceCode"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		badRequest(c, err)
		return
	}

	var title, statement, topic, taskLanguage, sourcePolicyRaw string
	var difficulty int
	err := a.DB.QueryRow(c.Request.Context(), `
		SELECT title, statement_md, topic, difficulty, COALESCE(language, 'java'), COALESCE(source_policy::text, '{}'::text)
		FROM tasks
		WHERE id = $1 AND is_published = TRUE
	`, req.TaskID).Scan(&title, &statement, &topic, &difficulty, &taskLanguage, &sourcePolicyRaw)
	if err != nil {
		notFound(c, "task not found")
		return
	}

	allowed, err := a.canUsePersonalHints(c, uctx.ID, uctx.Role)
	if err != nil {
		internalServerError(c, err)
		return
	}
	if !allowed {
		c.JSON(http.StatusPaymentRequired, gin.H{
			"error":        "ai hints are available only for Premium plan",
			"status":       "upgrade_required",
			"requiredPlan": "premium",
		})
		return
	}

	sourceRaw := strings.TrimSpace(req.SourceCode)
	sourceForPrompt := sourceRaw
	if sourceForPrompt == "" {
		sourceForPrompt = "Код не приложен. Пользователь запросил подсказку до отправки."
	}

	if a.Cfg.OpenAIAPIKey == "" {
		_ = a.logAIHint(c, uctx.ID, req.TaskID, uctx.PlanCode, "pending_openai_config", a.Cfg.OpenAIModel, len(sourceForPrompt), 0, 0, 0, "", "OPENAI_API_KEY is empty")
		c.JSON(http.StatusOK, gin.H{
			"status": "pending_openai_config",
			"hint":   "AI-подсказки включатся после заполнения OPENAI_API_KEY на сервере.",
		})
		return
	}

	policyHints := parseHintsFromSourcePolicy(sourcePolicyRaw)
	previousHint, _ := a.loadLatestSuccessfulHint(c, uctx.ID, req.TaskID)
	diagnostic, _ := a.loadHintDiagnostic(c, uctx.ID, req.TaskID, taskLanguage, sourceRaw)
	prompt := a.buildAIPrompt(taskLanguage, title, statement, topic, difficulty, sourceForPrompt, policyHints, previousHint, diagnostic)
	hint, model, promptTokens, completionTokens, totalTokens, err := a.requestAIHint(c, prompt)
	if err != nil {
		if isOpenAIRegionRestricted(err) {
			fallback := buildLocalHintFallback(title, topic, difficulty, sourceForPrompt)
			_ = a.logAIHint(c, uctx.ID, req.TaskID, uctx.PlanCode, "fallback_region_restricted", "local-fallback", len(sourceForPrompt), 0, 0, 0, fallback, err.Error())
			c.JSON(http.StatusOK, gin.H{
				"status": "ok",
				"model":  "local-fallback",
				"hint":   fallback,
				"usage": gin.H{
					"promptTokens":     0,
					"completionTokens": 0,
					"totalTokens":      0,
				},
			})
			return
		}
		_ = a.logAIHint(c, uctx.ID, req.TaskID, uctx.PlanCode, "failed", a.Cfg.OpenAIModel, len(sourceForPrompt), 0, 0, 0, "", err.Error())
		c.JSON(http.StatusBadGateway, APIError{Error: "ai hint failed", Details: err.Error()})
		return
	}

	_ = a.logAIHint(c, uctx.ID, req.TaskID, uctx.PlanCode, "ok", model, len(sourceForPrompt), promptTokens, completionTokens, totalTokens, hint, "")

	c.JSON(http.StatusOK, gin.H{
		"status": "ok",
		"model":  model,
		"hint":   hint,
		"usage": gin.H{
			"promptTokens":     promptTokens,
			"completionTokens": completionTokens,
			"totalTokens":      totalTokens,
		},
	})
}

func (a *App) canUsePersonalHints(c *gin.Context, userID, role string) (bool, error) {
	if role == "admin" {
		return true, nil
	}
	var allowed bool
	err := a.DB.QueryRow(c.Request.Context(), `
		SELECT COALESCE(p.has_personal_hints, FALSE)
		FROM users u
		LEFT JOIN subscriptions s ON s.user_id = u.id AND s.status='active' AND (s.ends_at IS NULL OR s.ends_at > NOW())
		LEFT JOIN plans p ON p.id = s.plan_id
		WHERE u.id = $1
	`, userID).Scan(&allowed)
	if err != nil {
		return false, err
	}
	return allowed, nil
}

func (a *App) buildAIPrompt(taskLanguage, title, statement, topic string, difficulty int, source string, policyHints []string, previousHint string, diagnostic *aiHintDiagnostic) string {
	language := normalizeTaskLanguage(taskLanguage)
	langLabel := "Java"
	codeFence := "java"
	if language == "python" {
		langLabel = "Python"
		codeFence = "python"
	} else if language == "sql" {
		langLabel = "SQL"
		codeFence = "sql"
	}

	var sb strings.Builder
	sb.WriteString("Ты — наставник по программированию для учеников с нулевым опытом.\n")
	sb.WriteString("Язык задачи: ")
	sb.WriteString(langLabel)
	sb.WriteString(".\n")
	sb.WriteString("Критично: не придумывай ошибки и требования. Опирайся только на условие и диагностические факты ниже.\n")
	sb.WriteString("Дай только СЛЕДУЮЩИЙ микро-шаг, который ученик может выполнить прямо сейчас.\n")
	sb.WriteString("Нельзя давать полное готовое решение, полный код программы или финальный ответ целиком.\n")
	sb.WriteString("Если шаг уже выполнен, дай следующий по порядку. Если нет — мягко повтори ближайший шаг.\n")
	sb.WriteString("Нельзя раскрывать ожидаемый вывод скрытых тестов дословно.\n")
	sb.WriteString("Ответ только на русском, коротко и понятно для новичка.\n")
	sb.WriteString("Формат строго такой:\n")
	sb.WriteString("Следующий шаг:\n")
	sb.WriteString("- ...\n")
	sb.WriteString("Зачем этот шаг:\n")
	sb.WriteString("- ...\n")
	sb.WriteString("Проверь себя:\n")
	sb.WriteString("- ...\n")
	sb.WriteString("Как получить следующий шаг:\n")
	sb.WriteString("- После выполнения нажми «AI-подсказка» снова и покажи обновленный код.\n\n")
	sb.WriteString("Задача:\n")
	sb.WriteString(fmt.Sprintf("Название: %s\n", title))
	sb.WriteString(fmt.Sprintf("Тема: %s\n", topic))
	sb.WriteString(fmt.Sprintf("Сложность: %d/5\n", difficulty))
	sb.WriteString("Условие:\n")
	sb.WriteString(truncateForAI(statement, 4500))
	if len(policyHints) > 0 {
		sb.WriteString("\n\nПодсказки автора задачи (используй как приоритетный учебный вектор, но не копируй дословно):\n")
		for _, hint := range policyHints {
			if strings.TrimSpace(hint) == "" {
				continue
			}
			sb.WriteString("- ")
			sb.WriteString(truncateForAI(strings.TrimSpace(hint), 300))
			sb.WriteString("\n")
		}
	}
	sb.WriteString("\n\nКод студента:\n```")
	sb.WriteString(codeFence)
	sb.WriteString("\n")
	sb.WriteString(truncateForAI(source, 4000))
	sb.WriteString("\n```")
	if explicitFormat := extractExplicitOutputFormat(statement); explicitFormat != "" {
		sb.WriteString("\n\nЯвный формат вывода из условия:\n")
		sb.WriteString(truncateForAI(explicitFormat, 500))
	}
	if diagnostic != nil {
		sb.WriteString("\n\nКонтекст диагностики (используй как факты):\n")
		sb.WriteString("- Источник: ")
		sb.WriteString(diagnostic.Source)
		sb.WriteString("\n- Статус: ")
		sb.WriteString(strings.TrimSpace(diagnostic.Status))
		sb.WriteString("\n")
		if diagnostic.FirstFailed != nil {
			sb.WriteString("- Первая проблемная проверка:\n")
			sb.WriteString(fmt.Sprintf("  - Номер: %d\n", diagnostic.FirstFailed.Index))
			if strings.TrimSpace(diagnostic.FirstFailed.Input) != "" {
				sb.WriteString("  - Ввод: ")
				sb.WriteString(truncateForAI(diagnostic.FirstFailed.Input, 500))
				sb.WriteString("\n")
			}
			if diagnostic.FirstFailed.ExpectedHidden {
				sb.WriteString("  - Ожидалось: [скрытый тест, не раскрывать дословно]\n")
			} else if strings.TrimSpace(diagnostic.FirstFailed.Expected) != "" {
				sb.WriteString("  - Ожидалось: ")
				sb.WriteString(truncateForAI(diagnostic.FirstFailed.Expected, 500))
				sb.WriteString("\n")
			}
			if strings.TrimSpace(diagnostic.FirstFailed.Actual) != "" {
				sb.WriteString("  - Фактически: ")
				sb.WriteString(truncateForAI(diagnostic.FirstFailed.Actual, 500))
				sb.WriteString("\n")
			}
			if strings.TrimSpace(diagnostic.FirstFailed.Error) != "" {
				sb.WriteString("  - Ошибка: ")
				sb.WriteString(truncateForAI(diagnostic.FirstFailed.Error, 800))
				sb.WriteString("\n")
			}
		}
		if strings.TrimSpace(diagnostic.CompileOutput) != "" {
			sb.WriteString("- Сообщение компиляции:\n")
			sb.WriteString(truncateForAI(strings.TrimSpace(diagnostic.CompileOutput), 1200))
			sb.WriteString("\n")
		}
		if strings.TrimSpace(diagnostic.RunLog) != "" {
			sb.WriteString("- Лог выполнения:\n")
			sb.WriteString(truncateForAI(strings.TrimSpace(diagnostic.RunLog), 1200))
			sb.WriteString("\n")
		}
	}
	if strings.TrimSpace(previousHint) != "" {
		sb.WriteString("\n\nПредыдущая подсказка, которую уже получил ученик:\n")
		sb.WriteString(truncateForAI(previousHint, 1200))
	}
	return sb.String()
}

func (a *App) requestAIHint(c *gin.Context, prompt string) (hint, model string, promptTokens, completionTokens, totalTokens int, err error) {
	reqBody := chatCompletionRequest{
		Model: a.Cfg.OpenAIModel,
		Messages: []chatMessage{
			{Role: "system", Content: "Ты педагогический AI-ментор. Помогаешь учиться с нуля, не даешь готовых решений, ведешь маленькими шагами."},
			{Role: "user", Content: prompt},
		},
		Temperature:         0.15,
		MaxCompletionTokens: 420,
	}
	body, err := json.Marshal(reqBody)
	if err != nil {
		return "", "", 0, 0, 0, err
	}

	url := strings.TrimRight(a.Cfg.OpenAIBaseURL, "/") + "/v1/chat/completions"
	httpReq, err := http.NewRequestWithContext(c.Request.Context(), http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return "", "", 0, 0, 0, err
	}
	httpReq.Header.Set("Authorization", "Bearer "+a.Cfg.OpenAIAPIKey)
	httpReq.Header.Set("Content-Type", "application/json")

	client := a.newOpenAIHTTPClient()
	resp, err := client.Do(httpReq)
	if err != nil {
		return "", "", 0, 0, 0, err
	}
	defer resp.Body.Close()

	raw, err := io.ReadAll(io.LimitReader(resp.Body, 2*1024*1024))
	if err != nil {
		return "", "", 0, 0, 0, err
	}

	var parsed chatCompletionResponse
	if err := json.Unmarshal(raw, &parsed); err != nil {
		return "", "", 0, 0, 0, fmt.Errorf("decode openai response: %w", err)
	}
	if resp.StatusCode >= 300 {
		if parsed.Error != nil && parsed.Error.Message != "" {
			return "", "", 0, 0, 0, &openAIRequestError{
				StatusCode: resp.StatusCode,
				Message:    parsed.Error.Message,
			}
		}
		return "", "", 0, 0, 0, &openAIRequestError{
			StatusCode: resp.StatusCode,
			Message:    strings.TrimSpace(string(raw)),
		}
	}
	if len(parsed.Choices) == 0 || strings.TrimSpace(parsed.Choices[0].Message.Content) == "" {
		return "", "", 0, 0, 0, fmt.Errorf("openai returned empty hint")
	}

	return strings.TrimSpace(parsed.Choices[0].Message.Content), parsed.Model, parsed.Usage.PromptTokens, parsed.Usage.CompletionTokens, parsed.Usage.TotalTokens, nil
}

func (a *App) logAIHint(c *gin.Context, userID, taskID, planCode, status, model string, sourceLen, promptTokens, completionTokens, totalTokens int, response, errorText string) error {
	_, err := a.DB.Exec(c.Request.Context(), `
		INSERT INTO ai_hint_requests(
			user_id, task_id, plan_code, status, model, source_code_length,
			prompt_tokens, completion_tokens, total_tokens, response_text, error_text
		)
		VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
	`, userID, taskID, planCode, status, model, sourceLen, promptTokens, completionTokens, totalTokens, response, errorText)
	return err
}

func (a *App) loadLatestSuccessfulHint(c *gin.Context, userID, taskID string) (string, error) {
	var hint string
	err := a.DB.QueryRow(c.Request.Context(), `
		SELECT COALESCE(response_text, '')
		FROM ai_hint_requests
		WHERE user_id = $1
		  AND task_id = $2
		  AND status IN ('ok', 'fallback_region_restricted')
		ORDER BY created_at DESC
		LIMIT 1
	`, userID, taskID).Scan(&hint)
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(hint), nil
}

func (a *App) loadHintDiagnostic(c *gin.Context, userID, taskID, taskLanguage, source string) (*aiHintDiagnostic, error) {
	if strings.TrimSpace(source) == "" {
		return nil, nil
	}
	latest, err := a.loadLatestSubmissionDiagnostic(c, userID, taskID, source)
	if err == nil && latest != nil {
		return latest, nil
	}
	return a.buildRuntimeProbeDiagnostic(c, taskID, taskLanguage, source)
}

func (a *App) loadLatestSubmissionDiagnostic(c *gin.Context, userID, taskID, source string) (*aiHintDiagnostic, error) {
	var (
		status, latestSource                     string
		compileOutputRaw, runLogRaw, feedbackRaw sql.NullString
	)
	err := a.DB.QueryRow(c.Request.Context(), `
		SELECT status, source_code, compile_output, run_log, feedback::text
		FROM submissions
		WHERE user_id = $1
		  AND task_id = $2
		  AND status NOT IN ('queued', 'processing')
		ORDER BY created_at DESC
		LIMIT 1
	`, userID, taskID).Scan(&status, &latestSource, &compileOutputRaw, &runLogRaw, &feedbackRaw)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return nil, nil
		}
		return nil, err
	}

	if strings.TrimSpace(latestSource) != strings.TrimSpace(source) {
		return nil, nil
	}

	tests, err := parseSubmissionFeedbackTests(feedbackRaw.String)
	if err != nil {
		return nil, nil
	}
	firstFailed, _ := firstFailedTest(tests)
	if firstFailed != nil {
		if hidden, hiddenErr := a.isHiddenTestPosition(c, taskID, firstFailed.Index); hiddenErr == nil && hidden {
			firstFailed.Expected = ""
			firstFailed.ExpectedHidden = true
		}
	}

	return &aiHintDiagnostic{
		Source:        "latest_submission_same_source",
		Status:        strings.TrimSpace(status),
		CompileOutput: strings.TrimSpace(compileOutputRaw.String),
		RunLog:        sanitizeRunLogForHint(strings.TrimSpace(runLogRaw.String), firstFailed),
		FirstFailed:   firstFailed,
	}, nil
}

func (a *App) buildRuntimeProbeDiagnostic(c *gin.Context, taskID, taskLanguage, source string) (*aiHintDiagnostic, error) {
	rows, err := a.DB.Query(c.Request.Context(), `
		SELECT input_data, expected_output, is_hidden
		FROM task_test_cases
		WHERE task_id = $1
		ORDER BY position ASC
		LIMIT 3
	`, taskID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	testCases := make([]judge.TestCase, 0, 3)
	caseMetaByIndex := make(map[int]aiHintProbeCaseMeta)

	for rows.Next() {
		var input, expected string
		var hidden bool
		if scanErr := rows.Scan(&input, &expected, &hidden); scanErr != nil {
			return nil, scanErr
		}
		testCases = append(testCases, judge.TestCase{Input: input, Expected: expected})
		index := len(testCases)
		caseMetaByIndex[index] = aiHintProbeCaseMeta{
			input:    input,
			expected: expected,
			hidden:   hidden,
		}
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}
	if len(testCases) == 0 {
		return nil, nil
	}

	result := a.evalTask(taskLanguage, source, testCases)
	firstFailed := probeFirstFailed(result.Tests, caseMetaByIndex)

	return &aiHintDiagnostic{
		Source:        "runtime_probe_3_tests",
		Status:        strings.TrimSpace(result.Status),
		CompileOutput: strings.TrimSpace(result.CompileOutput),
		RunLog:        sanitizeRunLogForHint(strings.TrimSpace(result.RunLog), firstFailed),
		FirstFailed:   firstFailed,
	}, nil
}

func parseSubmissionFeedbackTests(raw string) ([]judge.TestResult, error) {
	text := strings.TrimSpace(raw)
	if text == "" {
		return nil, nil
	}
	var tests []judge.TestResult
	if err := json.Unmarshal([]byte(text), &tests); err != nil {
		return nil, err
	}
	return tests, nil
}

func parseHintsFromSourcePolicy(sourcePolicyRaw string) []string {
	text := strings.TrimSpace(sourcePolicyRaw)
	if text == "" {
		return nil
	}
	var payload struct {
		Hints []string `json:"hints"`
	}
	if err := json.Unmarshal([]byte(text), &payload); err != nil {
		return nil
	}
	out := make([]string, 0, len(payload.Hints))
	for _, item := range payload.Hints {
		normalized := strings.TrimSpace(item)
		if normalized == "" {
			continue
		}
		out = append(out, normalized)
	}
	return out
}

func firstFailedTest(tests []judge.TestResult) (*aiHintFailedTest, bool) {
	for idx, t := range tests {
		passed := t.Passed
		if strings.TrimSpace(t.Error) != "" {
			passed = false
		}
		if passed {
			continue
		}
		index := t.Index
		if index <= 0 {
			index = idx + 1
		}
		return &aiHintFailedTest{
			Index:    index,
			Input:    strings.TrimSpace(t.Input),
			Expected: strings.TrimSpace(t.Expected),
			Actual:   strings.TrimSpace(t.Actual),
			Error:    strings.TrimSpace(t.Error),
		}, true
	}
	return nil, false
}

func probeFirstFailed(tests []judge.TestResult, caseMetaByIndex map[int]aiHintProbeCaseMeta) *aiHintFailedTest {
	failed, ok := firstFailedTest(tests)
	if !ok || failed == nil {
		return nil
	}
	meta, exists := caseMetaByIndex[failed.Index]
	if exists {
		if strings.TrimSpace(failed.Input) == "" {
			failed.Input = strings.TrimSpace(meta.input)
		}
		if meta.hidden {
			failed.Expected = ""
			failed.ExpectedHidden = true
		} else if strings.TrimSpace(failed.Expected) == "" {
			failed.Expected = strings.TrimSpace(meta.expected)
		}
	}
	return failed
}

func (a *App) isHiddenTestPosition(c *gin.Context, taskID string, position int) (bool, error) {
	if strings.TrimSpace(taskID) == "" || position <= 0 {
		return false, nil
	}
	var hidden bool
	err := a.DB.QueryRow(c.Request.Context(), `
		SELECT is_hidden
		FROM task_test_cases
		WHERE task_id = $1 AND position = $2
		LIMIT 1
	`, taskID, position).Scan(&hidden)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return false, nil
		}
		return false, err
	}
	return hidden, nil
}

func extractExplicitOutputFormat(statement string) string {
	text := strings.ReplaceAll(statement, "\r\n", "\n")
	text = strings.ReplaceAll(text, "\r", "\n")
	lines := strings.Split(text, "\n")
	re := regexp.MustCompile(`(?i)в\s+формате\s*[:\-]\s*(.+)$`)
	for _, rawLine := range lines {
		line := strings.TrimSpace(rawLine)
		if line == "" {
			continue
		}
		match := re.FindStringSubmatch(line)
		if len(match) < 2 {
			continue
		}
		format := strings.TrimSpace(match[1])
		format = strings.Trim(format, "`")
		if format != "" {
			return format
		}
	}
	return ""
}

func sanitizeRunLogForHint(runLog string, failed *aiHintFailedTest) string {
	logText := strings.TrimSpace(runLog)
	if logText == "" {
		return ""
	}
	lowerStatusTokens := []string{"expected", "got"}
	if failed != nil && failed.ExpectedHidden {
		for _, token := range lowerStatusTokens {
			if strings.Contains(strings.ToLower(logText), token) {
				return "Есть расхождение между ожидаемым и фактическим выводом на скрытом тесте."
			}
		}
	}
	return logText
}

func truncateForAI(s string, max int) string {
	if len(s) <= max {
		return s
	}
	return s[:max] + "\n\n[...truncated...]"
}

func normalizeTaskLanguage(v string) string {
	lower := strings.ToLower(strings.TrimSpace(v))
	switch lower {
	case "python", "py":
		return "python"
	case "java":
		return "java"
	case "sql", "postgresql", "postgres":
		return "sql"
	default:
		return "java"
	}
}

func isOpenAIRegionRestricted(err error) bool {
	if err == nil {
		return false
	}

	var reqErr *openAIRequestError
	if errors.As(err, &reqErr) && reqErr != nil && reqErr.StatusCode == http.StatusForbidden {
		return containsRegionRestrictionMarker(reqErr.Message)
	}

	return containsRegionRestrictionMarker(err.Error())
}

func containsRegionRestrictionMarker(s string) bool {
	lower := strings.ToLower(strings.TrimSpace(s))
	if lower == "" {
		return false
	}
	if strings.Contains(lower, "unsupported_country_region_territory") {
		return true
	}
	return strings.Contains(lower, "country, region, or territory not supported")
}

func buildLocalHintFallback(title, topic string, difficulty int, source string) string {
	sourceLower := strings.ToLower(source)
	tips := []string{
		fmt.Sprintf("Задача: **%s**. Сначала сформулируй в 1 фразу, что именно должен вывести код.", strings.TrimSpace(title)),
		"Проверь пары `ввод -> обработка -> вывод`: обычно ошибка в одном из этих трёх шагов.",
		"Сравни ожидаемый формат ответа посимвольно: лишние пробелы/переводы строки часто ломают проверку.",
	}

	if strings.Contains(sourceLower, "print(") || strings.Contains(sourceLower, "input(") {
		tips = append(tips, "Для Python проверь отступы и типы: где нужно число, делай `int(...)` перед вычислениями.")
	}
	if strings.Contains(sourceLower, "system.out.print") || strings.Contains(sourceLower, "scanner") || strings.Contains(sourceLower, "public static void main") {
		tips = append(tips, "Для Java проверь порядок чтения через `Scanner` и то, что печатаешь только требуемый результат без лишнего текста.")
	}

	if strings.TrimSpace(topic) != "" {
		tips = append(tips, fmt.Sprintf("Тема задачи: `%s`, сложность `%d/5` — начни с самого простого рабочего варианта, потом сокращай и улучшай.", strings.TrimSpace(topic), difficulty))
	}

	var b strings.Builder
	b.WriteString("Временный fallback-режим подсказки (основной AI-провайдер сейчас недоступен):\n\n")
	for i, tip := range tips {
		b.WriteString(fmt.Sprintf("%d. %s\n", i+1, tip))
	}
	b.WriteString("\nЕсли хочешь, пришли текущую версию решения — разберу по шагам, где именно логическая ошибка.")
	return strings.TrimSpace(b.String())
}

func (a *App) newOpenAIHTTPClient() *http.Client {
	transport := &http.Transport{Proxy: http.ProxyFromEnvironment}
	if proxyRaw := a.openAIProxyURL(); proxyRaw != "" {
		if parsed, err := url.Parse(proxyRaw); err == nil {
			transport.Proxy = http.ProxyURL(parsed)
		}
	}
	return &http.Client{
		Timeout:   30 * time.Second,
		Transport: transport,
	}
}

func (a *App) openAIProxyURL() string {
	if direct := strings.TrimSpace(a.Cfg.OpenAIHTTPProxy); direct != "" {
		return direct
	}

	host := strings.TrimSpace(a.Cfg.OpenAIProxyHost)
	port := strings.TrimSpace(a.Cfg.OpenAIProxyPort)
	if host == "" || port == "" {
		return ""
	}

	user := strings.TrimSpace(a.Cfg.OpenAIProxyUsername)
	pass := strings.TrimSpace(a.Cfg.OpenAIProxyPassword)
	if user == "" && pass == "" {
		return fmt.Sprintf("http://%s:%s", host, port)
	}

	u := &url.URL{
		Scheme: "http",
		Host:   fmt.Sprintf("%s:%s", host, port),
		User:   url.UserPassword(user, pass),
	}
	return u.String()
}
