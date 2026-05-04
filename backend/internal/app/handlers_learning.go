package app

import (
	"database/sql"
	"encoding/csv"
	"encoding/json"
	"errors"
	"net/http"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"leonovcare/backend/internal/judge"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
)

func (a *App) Me(c *gin.Context) {
	uctx, ok := userFromContext(c)
	if !ok {
		unauthorized(c, "unauthorized")
		return
	}

	var resp struct {
		ID             string `json:"id"`
		PublicID       string `json:"publicId"`
		Email          string `json:"email"`
		FirstName      string `json:"firstName"`
		LastName       string `json:"lastName"`
		Nickname       string `json:"nickname"`
		Role           string `json:"role"`
		Level          int    `json:"level"`
		XP             int    `json:"xp"`
		Streak         int    `json:"streak"`
		EmailVerified  bool   `json:"emailVerified"`
		Theme          string `json:"theme"`
		Language       string `json:"language"`
		Notifications  bool   `json:"notificationsEmail"`
		CodeFontSize   int    `json:"codeFontSize"`
		EditorTabSize  int    `json:"editorTabSize"`
		EditorWordWrap bool   `json:"editorWordWrap"`
		PlanCode       string `json:"planCode"`
	}

	err := a.DB.QueryRow(c.Request.Context(), `
		SELECT u.id, u.public_id, u.email, u.first_name, u.last_name, u.nickname, u.role, u.level, u.xp, u.streak, u.is_email_verified,
		       'light' AS theme, s.language, s.notifications_email, s.code_font_size, s.editor_tab_size, s.editor_word_wrap
		FROM users u
		LEFT JOIN user_settings s ON s.user_id = u.id
		WHERE u.id = $1
	`, uctx.ID).Scan(
		&resp.ID, &resp.PublicID, &resp.Email, &resp.FirstName, &resp.LastName, &resp.Nickname, &resp.Role, &resp.Level, &resp.XP, &resp.Streak, &resp.EmailVerified,
		&resp.Theme, &resp.Language, &resp.Notifications, &resp.CodeFontSize, &resp.EditorTabSize, &resp.EditorWordWrap,
	)
	if err != nil {
		internalServerError(c, err)
		return
	}
	resp.PlanCode = uctx.PlanCode
	c.JSON(http.StatusOK, resp)
}

func (a *App) UpdateSettings(c *gin.Context) {
	uctx, ok := userFromContext(c)
	if !ok {
		unauthorized(c, "unauthorized")
		return
	}
	var req struct {
		Theme              string `json:"theme"`
		Language           string `json:"language"`
		NotificationsEmail *bool  `json:"notificationsEmail"`
		CodeFontSize       *int   `json:"codeFontSize"`
		EditorTabSize      *int   `json:"editorTabSize"`
		EditorWordWrap     *bool  `json:"editorWordWrap"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		badRequest(c, err)
		return
	}

	// Theme is kept in the request for backwards API compatibility, but the product is light-only.
	req.Theme = "light"
	if req.Language == "" {
		req.Language = "ru"
	}
	notif := true
	if req.NotificationsEmail != nil {
		notif = *req.NotificationsEmail
	}
	font := 14
	if req.CodeFontSize != nil {
		font = *req.CodeFontSize
	}
	tab := 4
	if req.EditorTabSize != nil {
		tab = *req.EditorTabSize
	}
	wrap := true
	if req.EditorWordWrap != nil {
		wrap = *req.EditorWordWrap
	}

	_, err := a.DB.Exec(c.Request.Context(), `
		INSERT INTO user_settings(user_id, theme, language, notifications_email, code_font_size, editor_tab_size, editor_word_wrap, updated_at)
		VALUES($1, $2, $3, $4, $5, $6, $7, NOW())
		ON CONFLICT(user_id)
		DO UPDATE SET theme=EXCLUDED.theme, language=EXCLUDED.language, notifications_email=EXCLUDED.notifications_email,
		              code_font_size=EXCLUDED.code_font_size, editor_tab_size=EXCLUDED.editor_tab_size,
		              editor_word_wrap=EXCLUDED.editor_word_wrap, updated_at=NOW()
	`, uctx.ID, req.Theme, req.Language, notif, font, tab, wrap)
	if err != nil {
		internalServerError(c, err)
		return
	}
	c.JSON(http.StatusOK, gin.H{"status": "updated"})
}

func (a *App) ListCourses(c *gin.Context) {
	rows, err := a.DB.Query(c.Request.Context(), `
		SELECT id, slug, title, description
		FROM courses
		WHERE is_published = TRUE
		ORDER BY created_at ASC
	`)
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer rows.Close()

	type course struct {
		ID          string `json:"id"`
		Slug        string `json:"slug"`
		Title       string `json:"title"`
		Description string `json:"description"`
	}

	out := []course{}
	for rows.Next() {
		var item course
		if err := rows.Scan(&item.ID, &item.Slug, &item.Title, &item.Description); err != nil {
			internalServerError(c, err)
			return
		}
		out = append(out, item)
	}
	c.JSON(http.StatusOK, gin.H{"items": out})
}

func (a *App) GetCourse(c *gin.Context) {
	courseID := c.Param("courseID")

	var course struct {
		ID          string `json:"id"`
		Slug        string `json:"slug"`
		Title       string `json:"title"`
		Description string `json:"description"`
	}
	if err := a.DB.QueryRow(c.Request.Context(), `
		SELECT id, slug, title, description FROM courses WHERE id = $1 AND is_published=TRUE
	`, courseID).Scan(&course.ID, &course.Slug, &course.Title, &course.Description); err != nil {
		notFound(c, "course not found")
		return
	}

	rows, err := a.DB.Query(c.Request.Context(), `
		SELECT
			l.id,
			l.title,
			l.position,
			m.title AS module_title,
			COALESCE(lb.block_count, 0) AS block_count
		FROM lessons l
		JOIN modules m ON m.id = l.module_id
		LEFT JOIN (
			SELECT lesson_id, COUNT(*)::int AS block_count
			FROM lesson_blocks
			WHERE is_published = TRUE
			GROUP BY lesson_id
		) lb ON lb.lesson_id = l.id
		WHERE m.course_id = $1 AND l.is_published = TRUE
		ORDER BY m.position, l.position
	`, courseID)
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer rows.Close()

	type lessonBrief struct {
		ID          string `json:"id"`
		Title       string `json:"title"`
		Position    int    `json:"position"`
		ModuleTitle string `json:"moduleTitle"`
		BlockCount  int    `json:"blockCount"`
	}
	lessons := []lessonBrief{}
	for rows.Next() {
		var l lessonBrief
		if err := rows.Scan(&l.ID, &l.Title, &l.Position, &l.ModuleTitle, &l.BlockCount); err != nil {
			internalServerError(c, err)
			return
		}
		lessons = append(lessons, l)
	}
	if err := rows.Err(); err != nil {
		internalServerError(c, err)
		return
	}

	c.JSON(http.StatusOK, gin.H{"course": course, "lessons": lessons})
}

func (a *App) GetCourseTasksCatalog(c *gin.Context) {
	courseID := c.Param("courseID")

	var exists bool
	if err := a.DB.QueryRow(c.Request.Context(), `
		SELECT EXISTS(SELECT 1 FROM courses WHERE id = $1 AND is_published = TRUE)
	`, courseID).Scan(&exists); err != nil {
		internalServerError(c, err)
		return
	}
	if !exists {
		notFound(c, "course not found")
		return
	}

	rows, err := a.DB.Query(c.Request.Context(), `
		SELECT
			t.id,
			t.title,
			t.difficulty,
			t.xp_reward,
			t.topic,
			COALESCE(t.language, 'java') AS language,
			l.id AS lesson_id,
			l.title AS lesson_title,
			m.title AS module_title
		FROM tasks t
		JOIN lessons l ON l.id = t.lesson_id
		JOIN modules m ON m.id = l.module_id
		WHERE m.course_id = $1
		  AND l.is_published = TRUE
		  AND t.is_published = TRUE
		ORDER BY m.position, l.position, t.difficulty ASC, t.title ASC
	`, courseID)
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer rows.Close()

	type taskCatalogItem struct {
		TaskID      string `json:"taskId"`
		Title       string `json:"title"`
		Difficulty  int    `json:"difficulty"`
		XP          int    `json:"xp"`
		Topic       string `json:"topic"`
		Language    string `json:"language"`
		LessonID    string `json:"lessonId"`
		LessonTitle string `json:"lessonTitle"`
		ModuleTitle string `json:"moduleTitle"`
	}

	items := make([]taskCatalogItem, 0)
	for rows.Next() {
		var item taskCatalogItem
		if err := rows.Scan(
			&item.TaskID,
			&item.Title,
			&item.Difficulty,
			&item.XP,
			&item.Topic,
			&item.Language,
			&item.LessonID,
			&item.LessonTitle,
			&item.ModuleTitle,
		); err != nil {
			internalServerError(c, err)
			return
		}
		items = append(items, item)
	}
	if err := rows.Err(); err != nil {
		internalServerError(c, err)
		return
	}

	c.JSON(http.StatusOK, gin.H{"items": items})
}

func (a *App) GetLesson(c *gin.Context) {
	lessonID := c.Param("lessonID")

	var lesson struct {
		ID          string `json:"id"`
		Title       string `json:"title"`
		Content     string `json:"contentMd"`
		Position    int    `json:"position"`
		ModuleTitle string `json:"moduleTitle"`
	}
	if err := a.DB.QueryRow(c.Request.Context(), `
		SELECT l.id, l.title, l.content_md, l.position, m.title
		FROM lessons l
		JOIN modules m ON m.id = l.module_id
		WHERE l.id = $1 AND l.is_published = TRUE
	`, lessonID).Scan(&lesson.ID, &lesson.Title, &lesson.Content, &lesson.Position, &lesson.ModuleTitle); err != nil {
		notFound(c, "lesson not found")
		return
	}

	taskRows, err := a.DB.Query(c.Request.Context(), `
		SELECT id, title, difficulty, topic, xp_reward, COALESCE(language, 'java'), COALESCE(source_policy::text, '{}'::text)
		FROM tasks
		WHERE lesson_id = $1 AND is_published = TRUE
		ORDER BY difficulty ASC, title ASC
	`, lessonID)
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer taskRows.Close()

	tasks := make([]gin.H, 0)
	for taskRows.Next() {
		var id, title, topic, language, sourcePolicyRaw string
		var diff, xp int
		if err := taskRows.Scan(&id, &title, &diff, &topic, &xp, &language, &sourcePolicyRaw); err != nil {
			internalServerError(c, err)
			return
		}
		tasks = append(tasks, gin.H{
			"id":         id,
			"title":      title,
			"difficulty": diff,
			"topic":      topic,
			"xpReward":   xp,
			"language":   language,
			"type":       inferTaskTypeFromSourcePolicy(sourcePolicyRaw),
		})
	}

	blockRows, err := a.DB.Query(c.Request.Context(), `
		SELECT
			lb.id,
			lb.block_type,
			lb.title,
			lb.content_md,
			lb.position,
			COALESCE(lb.quiz_payload, 'null'::jsonb)::text AS quiz_payload_text,
			lb.task_id::text,
			COALESCE(t.title, '')
		FROM lesson_blocks lb
		LEFT JOIN tasks t ON t.id = lb.task_id
		WHERE lb.lesson_id = $1 AND lb.is_published = TRUE
		ORDER BY lb.position ASC
	`, lessonID)
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer blockRows.Close()

	blocks := make([]gin.H, 0)
	for blockRows.Next() {
		var (
			id, blockType, title, content, quizPayloadText, taskTitle string
			position                                                  int
			taskID                                                    sql.NullString
		)
		if err := blockRows.Scan(&id, &blockType, &title, &content, &position, &quizPayloadText, &taskID, &taskTitle); err != nil {
			internalServerError(c, err)
			return
		}

		item := gin.H{
			"id":        id,
			"type":      blockType,
			"title":     title,
			"contentMd": content,
			"position":  position,
		}
		if taskID.Valid && taskID.String != "" {
			item["taskId"] = taskID.String
			item["taskTitle"] = taskTitle
		}
		if quizPayloadText != "" && quizPayloadText != "null" {
			var quiz any
			if err := json.Unmarshal([]byte(quizPayloadText), &quiz); err == nil {
				item["quiz"] = sanitizeQuizPayloadForStudent(quiz)
			}
		}
		blocks = append(blocks, item)
	}

	c.JSON(http.StatusOK, gin.H{"lesson": lesson, "tasks": tasks, "blocks": blocks})
}

func (a *App) GetTask(c *gin.Context) {
	taskID := c.Param("taskID")
	var task struct {
		ID         string `json:"id"`
		Title      string `json:"title"`
		Statement  string `json:"statementMd"`
		Starter    string `json:"starterCode"`
		Difficulty int    `json:"difficulty"`
		XP         int    `json:"xpReward"`
		Topic      string `json:"topic"`
		Language   string `json:"language"`
		Type       string `json:"type"`
		MainFile   string `json:"mainFilePath"`
		EntryPoint string `json:"entryPoint"`
	}
	var sourcePolicyRaw string
	var solutionCode string
	if err := a.DB.QueryRow(c.Request.Context(), `
		SELECT id, title, statement_md, starter_code, difficulty, xp_reward, topic, COALESCE(language, 'java'), COALESCE(source_policy::text, '{}'::text), COALESCE(solution_code, '')
		FROM tasks WHERE id = $1 AND is_published = TRUE
	`, taskID).Scan(&task.ID, &task.Title, &task.Statement, &task.Starter, &task.Difficulty, &task.XP, &task.Topic, &task.Language, &sourcePolicyRaw, &solutionCode); err != nil {
		notFound(c, "task not found")
		return
	}
	task.Type = inferTaskTypeFromSourcePolicy(sourcePolicyRaw)
	task.MainFile = inferMainFilePathFromSourcePolicy(sourcePolicyRaw, task.Language)
	task.EntryPoint = filepath.Base(task.MainFile)
	task.Starter = withStarterFallback(task.Starter, task.Statement, task.Language, solutionCode)
	rows, err := a.DB.Query(c.Request.Context(), `
		SELECT input_data, expected_output, is_hidden, position
		FROM task_test_cases
		WHERE task_id = $1
		ORDER BY position ASC
	`, taskID)
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer rows.Close()

	tests := []gin.H{}
	for rows.Next() {
		var input, expected string
		var hidden bool
		var pos int
		if err := rows.Scan(&input, &expected, &hidden, &pos); err != nil {
			internalServerError(c, err)
			return
		}
		if hidden {
			tests = append(tests, gin.H{"position": pos, "input": input, "expected": "***"})
		} else {
			tests = append(tests, gin.H{"position": pos, "input": input, "expected": expected})
		}
	}

	c.JSON(http.StatusOK, gin.H{"task": task, "examples": tests})
}

func withStarterFallback(starterCode, statementMd, language, solutionCode string) string {
	starter := strings.ReplaceAll(starterCode, "\r\n", "\n")
	starter = strings.ReplaceAll(starter, "\r", "\n")
	if strings.TrimSpace(starter) != "" {
		return starter
	}

	if isFixFromEditorStatement(statementMd) {
		buggy := buildBuggyStarterFromSolution(solutionCode, language)
		if strings.TrimSpace(buggy) != "" {
			return buggy
		}
	}

	normalizedLang := strings.ToLower(strings.TrimSpace(language))
	switch normalizedLang {
	case "python", "python3", "py":
		return "# Напишите решение здесь\n"
	case "sql":
		return "-- Напишите SQL-запрос здесь\n"
	default:
		return "// Write your solution here\n"
	}
}

func isFixFromEditorStatement(statementMd string) bool {
	normalized := strings.ToLower(strings.TrimSpace(statementMd))
	if normalized == "" {
		return false
	}
	return strings.Contains(normalized, "исправь код из редактора")
}

func buildBuggyStarterFromSolution(solutionCode, language string) string {
	solution := strings.ReplaceAll(solutionCode, "\r\n", "\n")
	solution = strings.ReplaceAll(solution, "\r", "\n")
	if strings.TrimSpace(solution) == "" {
		return ""
	}

	normalizedLang := strings.ToLower(strings.TrimSpace(language))
	if normalizedLang == "python" || normalizedLang == "python3" || normalizedLang == "py" {
		lines := strings.Split(solution, "\n")
		for i, line := range lines {
			if strings.Contains(line, "print(") {
				lines[i] = strings.Replace(line, "print(", "pritn(", 1)
				return strings.TrimSpace(strings.Join(lines, "\n")) + "\n"
			}
		}
		if len(lines) > 0 {
			lines[0] = "# Исправьте код так, чтобы прошла проверка\n" + lines[0]
		}
		return strings.TrimSpace(strings.Join(lines, "\n")) + "\n"
	}

	return ""
}

func (a *App) RunTask(c *gin.Context) {
	if _, ok := userFromContext(c); !ok {
		unauthorized(c, "unauthorized")
		return
	}

	var req struct {
		SourceCode string `json:"sourceCode" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		badRequest(c, err)
		return
	}
	source := req.SourceCode
	if strings.TrimSpace(source) == "" {
		badRequest(c, errors.New("sourceCode is required"))
		return
	}

	taskID := c.Param("taskID")
	var language string
	var sourcePolicyRaw string
	var solutionCode string
	if err := a.DB.QueryRow(c.Request.Context(), `
		SELECT COALESCE(language, 'java'), COALESCE(source_policy::text, '{}'::text), COALESCE(solution_code, '')
		FROM tasks
		WHERE id = $1 AND is_published = TRUE
	`, taskID).Scan(&language, &sourcePolicyRaw, &solutionCode); err != nil {
		notFound(c, "task not found")
		return
	}
	if violation, err := evaluateTaskSourcePolicy(sourcePolicyRaw, language, source); err != nil {
		internalServerError(c, err)
		return
	} else if violation != "" {
		result := normalizeRunPreviewResult(sourcePolicyViolationResult(violation))
		c.JSON(http.StatusOK, gin.H{
			"status":        result.Status,
			"score":         result.Score,
			"compileOutput": result.CompileOutput,
			"runLog":        result.RunLog,
			"tests":         result.Tests,
		})
		return
	}

	rows, err := a.DB.Query(c.Request.Context(), `
		SELECT input_data, expected_output
		FROM task_test_cases
		WHERE task_id = $1
		ORDER BY position ASC
	`, taskID)
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer rows.Close()

	tests := make([]judge.TestCase, 0)
	for rows.Next() {
		var inputData, expectedOutput string
		if err := rows.Scan(&inputData, &expectedOutput); err != nil {
			internalServerError(c, err)
			return
		}
		tests = append(tests, judge.TestCase{Input: inputData, Expected: expectedOutput})
	}
	if err := rows.Err(); err != nil {
		internalServerError(c, err)
		return
	}

	result := a.evaluateTaskByPolicy(language, source, nil, tests, sourcePolicyRaw, solutionCode)
	result = normalizeRunPreviewResult(result)
	c.JSON(http.StatusOK, gin.H{
		"status":        result.Status,
		"score":         result.Score,
		"compileOutput": result.CompileOutput,
		"runLog":        result.RunLog,
		"tests":         result.Tests,
	})
}

func (a *App) CreateSubmission(c *gin.Context) {
	uctx, ok := userFromContext(c)
	if !ok {
		unauthorized(c, "unauthorized")
		return
	}

	var req struct {
		SourceCode string                  `json:"sourceCode"`
		Files      []submissionFilePayload `json:"files"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		badRequest(c, err)
		return
	}
	sourceCode := req.SourceCode
	if strings.TrimSpace(sourceCode) == "" {
		sourceCode = firstNonEmptySourceFromFiles(req.Files)
	}
	if strings.TrimSpace(sourceCode) == "" && len(req.Files) == 0 {
		badRequest(c, errors.New("sourceCode is required"))
		return
	}

	taskID := c.Param("taskID")
	var maxAttempts int
	var taskLanguage string
	var sourcePolicyRaw string
	if err := a.DB.QueryRow(c.Request.Context(), `
		SELECT max_attempts, COALESCE(language, 'java'), COALESCE(source_policy::text, '{}'::text)
		FROM tasks
		WHERE id = $1 AND is_published = TRUE
	`, taskID).Scan(&maxAttempts, &taskLanguage, &sourcePolicyRaw); err != nil {
		notFound(c, "task not found")
		return
	}

	var dailyLimit int
	err := a.DB.QueryRow(c.Request.Context(), `
		SELECT COALESCE(p.daily_submission_limit, $2)
		FROM users u
		LEFT JOIN subscriptions s ON s.user_id = u.id AND s.status='active' AND (s.ends_at IS NULL OR s.ends_at > NOW())
		LEFT JOIN plans p ON p.id = s.plan_id
		WHERE u.id = $1
	`, uctx.ID, a.Cfg.DailyFreeSubmissions).Scan(&dailyLimit)
	if err != nil {
		internalServerError(c, err)
		return
	}

	var todayCount int
	if err := a.DB.QueryRow(c.Request.Context(), `
		SELECT COUNT(*) FROM submissions
		WHERE user_id = $1 AND created_at::date = CURRENT_DATE
	`, uctx.ID).Scan(&todayCount); err != nil {
		internalServerError(c, err)
		return
	}
	if dailyLimit > 0 && todayCount >= dailyLimit {
		c.JSON(http.StatusPaymentRequired, APIError{Error: "daily submission limit reached for your plan"})
		return
	}

	var taskAttempts int
	if err := a.DB.QueryRow(c.Request.Context(), `
		SELECT COUNT(*) FROM submissions WHERE user_id = $1 AND task_id = $2
	`, uctx.ID, taskID).Scan(&taskAttempts); err != nil {
		internalServerError(c, err)
		return
	}
	if maxAttempts > 0 && taskAttempts >= maxAttempts {
		c.JSON(http.StatusTooManyRequests, APIError{Error: "max attempts exceeded for this task"})
		return
	}

	if violation, err := evaluateTaskSourcePolicy(sourcePolicyRaw, taskLanguage, sourceCode); err != nil {
		internalServerError(c, err)
		return
	} else if violation != "" {
		submissionID := uuid.NewString()
		encodedSource := encodeSubmissionSourceBundle(sourceCode, req.Files)
		_, err = a.DB.Exec(c.Request.Context(), `
			INSERT INTO submissions(id, user_id, task_id, source_code, status, score, attempts_used, compile_output, run_log, feedback)
			VALUES($1, $2, $3, $4, 'wrong_answer', 0, $5, $6, $7, '[]'::jsonb)
		`, submissionID, uctx.ID, taskID, encodedSource, taskAttempts+1, violation, "source policy check failed")
		if err != nil {
			internalServerError(c, err)
			return
		}
		c.JSON(http.StatusAccepted, gin.H{
			"submissionId":          submissionID,
			"status":                "wrong_answer",
			"sourcePolicyViolation": true,
		})
		return
	}

	submissionID := uuid.NewString()
	encodedSource := encodeSubmissionSourceBundle(sourceCode, req.Files)
	_, err = a.DB.Exec(c.Request.Context(), `
		INSERT INTO submissions(id, user_id, task_id, source_code, status, attempts_used)
		VALUES($1, $2, $3, $4, 'queued', $5)
	`, submissionID, uctx.ID, taskID, encodedSource, taskAttempts+1)
	if err != nil {
		internalServerError(c, err)
		return
	}

	job := QueueJob{SubmissionID: submissionID}
	payload := jsonMarshal(job)
	if err := a.Redis.RPush(c.Request.Context(), a.Cfg.SubmissionQueueName, payload).Err(); err != nil {
		internalServerError(c, err)
		return
	}

	c.JSON(http.StatusAccepted, gin.H{"submissionId": submissionID, "status": "queued"})
}

func (a *App) GetSubmission(c *gin.Context) {
	uctx, ok := userFromContext(c)
	if !ok {
		unauthorized(c, "unauthorized")
		return
	}
	subID := c.Param("submissionID")

	var ownerID, status, createdAt string
	var compileOutput, runLog, feedback, sourceCode, solutionCode sql.NullString
	var score int
	err := a.DB.QueryRow(c.Request.Context(), `
		SELECT s.user_id::text, s.status, s.score, s.compile_output, s.run_log, s.feedback::text, s.created_at::text, s.source_code, t.solution_code
		FROM submissions s
		JOIN tasks t ON t.id = s.task_id
		WHERE s.id = $1
	`, subID).Scan(&ownerID, &status, &score, &compileOutput, &runLog, &feedback, &createdAt, &sourceCode, &solutionCode)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			notFound(c, "submission not found")
			return
		}
		internalServerError(c, err)
		return
	}
	if ownerID != uctx.ID && uctx.Role != "admin" {
		c.JSON(http.StatusForbidden, APIError{Error: "forbidden"})
		return
	}

	submittedSource, _ := decodeSubmissionSourceBundle(sourceCode.String)
	referenceCode := ""
	if strings.EqualFold(strings.TrimSpace(status), "accepted") &&
		normalizeCodeForReferenceCompare(submittedSource) != normalizeCodeForReferenceCompare(solutionCode.String) {
		referenceCode = strings.TrimSpace(solutionCode.String)
	}

	c.JSON(http.StatusOK, gin.H{
		"id":            subID,
		"status":        status,
		"score":         score,
		"compileOutput": compileOutput.String,
		"runLog":        runLog.String,
		"feedback":      feedback.String,
		"referenceCode": referenceCode,
		"createdAt":     createdAt,
	})
}

func (a *App) SubmissionHistory(c *gin.Context) {
	uctx, ok := userFromContext(c)
	if !ok {
		unauthorized(c, "unauthorized")
		return
	}

	rows, err := a.DB.Query(c.Request.Context(), `
		SELECT latest.id, latest.task_id, latest.title, latest.status, latest.score, latest.created_at
		FROM (
			SELECT DISTINCT ON (s.task_id)
				s.id,
				s.task_id::text AS task_id,
				t.title,
				s.status,
				s.score,
				s.created_at
			FROM submissions s
			JOIN tasks t ON t.id = s.task_id
			WHERE s.user_id = $1
			ORDER BY s.task_id, s.created_at DESC, s.id DESC
		) AS latest
		ORDER BY latest.created_at DESC, latest.id DESC
		LIMIT 100
	`, uctx.ID)
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer rows.Close()

	items := make([]gin.H, 0)
	for rows.Next() {
		var id, taskID, title, status string
		var score int
		var created time.Time
		if err := rows.Scan(&id, &taskID, &title, &status, &score, &created); err != nil {
			internalServerError(c, err)
			return
		}
		items = append(items, gin.H{
			"id": id, "taskId": taskID, "taskTitle": title, "status": status, "score": score, "createdAt": created,
		})
	}
	c.JSON(http.StatusOK, gin.H{"items": items})
}

func (a *App) MyAchievements(c *gin.Context) {
	uctx, ok := userFromContext(c)
	if !ok {
		unauthorized(c, "unauthorized")
		return
	}

	rows, err := a.DB.Query(c.Request.Context(), `
		SELECT a.code, a.title, a.description, ua.unlocked_at
		FROM user_achievements ua
		JOIN achievements a ON a.id = ua.achievement_id
		WHERE ua.user_id = $1
		ORDER BY ua.unlocked_at DESC
	`, uctx.ID)
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer rows.Close()

	items := []gin.H{}
	for rows.Next() {
		var code, title, desc string
		var unlockedAt time.Time
		if err := rows.Scan(&code, &title, &desc, &unlockedAt); err != nil {
			internalServerError(c, err)
			return
		}
		items = append(items, gin.H{"code": code, "title": title, "description": desc, "unlockedAt": unlockedAt})
	}
	c.JSON(http.StatusOK, gin.H{"items": items})
}

func (a *App) Leaderboard(c *gin.Context) {
	rows, err := a.DB.Query(c.Request.Context(), `
		SELECT nickname, first_name, last_name, xp, level
		FROM users
		WHERE is_blocked = FALSE
		ORDER BY xp DESC, level DESC
		LIMIT 100
	`)
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer rows.Close()
	items := []gin.H{}
	rank := 1
	for rows.Next() {
		var nickname, firstName, lastName string
		var xp, level int
		if err := rows.Scan(&nickname, &firstName, &lastName, &xp, &level); err != nil {
			internalServerError(c, err)
			return
		}
		items = append(items, gin.H{
			"rank":      rank,
			"nickname":  nickname,
			"firstName": firstName,
			"lastName":  lastName,
			"xp":        xp,
			"level":     level,
		})
		rank++
	}
	c.JSON(http.StatusOK, gin.H{"items": items})
}

func (a *App) processSubmission(ctx *gin.Context, submissionID string) error {
	_ = ctx
	_ = submissionID
	return nil
}

func (a *App) evalTask(language, source string, testCases []judge.TestCase) judge.Result {
	switch strings.ToLower(strings.TrimSpace(language)) {
	case "", "java":
		return a.Judge.EvaluateJava(source, testCases)
	case "python", "python3", "py":
		return a.Judge.EvaluatePython(source, testCases)
	case "sql":
		return a.Judge.EvaluateSQL(source, testCases)
	default:
		return judge.Result{
			Status:        "failed",
			CompileOutput: "unsupported language: " + language,
			RunLog:        "task language is not configured in judge",
		}
	}
}

func (a *App) AdminMetricsExportCSV(c *gin.Context) {
	from := c.Query("from")
	to := c.Query("to")
	if from == "" {
		from = time.Now().AddDate(0, 0, -30).Format("2006-01-02")
	}
	if to == "" {
		to = time.Now().Format("2006-01-02")
	}
	if _, err := time.Parse("2006-01-02", from); err != nil {
		badRequest(c, err)
		return
	}
	if _, err := time.Parse("2006-01-02", to); err != nil {
		badRequest(c, err)
		return
	}

	rows, err := a.DB.Query(c.Request.Context(), `
		SELECT DATE(s.created_at) as dt,
		       COUNT(*) as submissions,
		       COUNT(*) FILTER (WHERE s.status='accepted') as accepted,
		       COALESCE(SUM(x.points), 0) as xp_gained
		FROM submissions s
		LEFT JOIN xp_events x ON x.submission_id = s.id
		WHERE s.created_at::date BETWEEN $1::date AND $2::date
		GROUP BY dt
		ORDER BY dt
	`, from, to)
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer rows.Close()

	c.Header("Content-Disposition", "attachment; filename=metrics.csv")
	c.Header("Content-Type", "text/csv")
	w := csv.NewWriter(c.Writer)
	_ = w.Write([]string{"date", "submissions", "accepted", "xp_gained"})
	for rows.Next() {
		var dt string
		var submissions, accepted, xp int
		if err := rows.Scan(&dt, &submissions, &accepted, &xp); err != nil {
			internalServerError(c, err)
			return
		}
		_ = w.Write([]string{dt, strconv.Itoa(submissions), strconv.Itoa(accepted), strconv.Itoa(xp)})
	}
	w.Flush()
}

func normalizeOutput(s string) string {
	return strings.TrimSpace(strings.ReplaceAll(s, "\r\n", "\n"))
}

func normalizeCodeForReferenceCompare(s string) string {
	lines := strings.Split(strings.ReplaceAll(strings.ReplaceAll(s, "\r\n", "\n"), "\r", "\n"), "\n")
	filtered := make([]string, 0, len(lines))
	for _, raw := range lines {
		trimmed := strings.TrimSpace(raw)
		if trimmed == "" {
			continue
		}
		filtered = append(filtered, trimmed)
	}
	return strings.Join(filtered, "\n")
}

func normalizeRunPreviewResult(result judge.Result) judge.Result {
	preview := result
	preview.Score = 0
	if len(preview.Tests) > 1 {
		preview.Tests = preview.Tests[:1]
	}

	compileOutput := strings.TrimSpace(preview.CompileOutput)
	runLog := strings.ToLower(strings.TrimSpace(preview.RunLog))

	if compileOutput != "" && len(preview.Tests) == 0 {
		preview.Status = "compile_error"
		return preview
	}

	if len(preview.Tests) > 0 {
		first := preview.Tests[0]
		if strings.TrimSpace(first.Error) != "" {
			lowerErr := strings.ToLower(first.Error)
			if strings.Contains(lowerErr, "time limit") || strings.Contains(runLog, "time limit") {
				preview.Status = "time_limit"
				return preview
			}
			preview.Status = "runtime_error"
			return preview
		}
	}

	if strings.Contains(runLog, "time limit") {
		preview.Status = "time_limit"
		return preview
	}

	preview.Status = "ran"
	preview.RunLog = ""
	return preview
}
