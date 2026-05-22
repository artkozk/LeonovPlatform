package app

import (
	"strings"
	"testing"

	"leonovcare/backend/internal/config"
)

func TestTruncateForAI(t *testing.T) {
	in := "1234567890"
	out := truncateForAI(in, 5)
	if out == in {
		t.Fatalf("expected truncation")
	}
	if out[:5] != "12345" {
		t.Fatalf("unexpected prefix: %q", out)
	}
}

func TestBuildAIPromptContainsTaskContext(t *testing.T) {
	a := &App{}
	prompt := a.buildAIPrompt("java", "Sum", "Найдите сумму двух чисел", "math", 1, "class Main {}", nil, "", nil)
	if prompt == "" {
		t.Fatalf("prompt must not be empty")
	}
	if !strings.Contains(prompt, "Название: Sum") {
		t.Fatalf("prompt must include task title")
	}
	if !strings.Contains(prompt, "class Main {}") {
		t.Fatalf("prompt must include source")
	}
}

func TestBuildAIPromptUsesPythonFence(t *testing.T) {
	a := &App{}
	prompt := a.buildAIPrompt("python", "Print", "Выведите текст", "basics", 1, "print('ok')", nil, "Предыдущий шаг", nil)
	if !strings.Contains(prompt, "```python") {
		t.Fatalf("prompt must include python code fence")
	}
	if !strings.Contains(prompt, "Предыдущая подсказка") {
		t.Fatalf("prompt must include previous hint context")
	}
}

func TestBuildAIPromptIncludesDiagnosticContext(t *testing.T) {
	a := &App{}
	diag := &aiHintDiagnostic{
		Source: "runtime_probe_3_tests",
		Status: "wrong_answer",
		FirstFailed: &aiHintFailedTest{
			Index:          1,
			Input:          "stdin sample",
			ExpectedHidden: true,
			Actual:         "Анна: Анна Возраст: 25",
		},
	}
	prompt := a.buildAIPrompt(
		"python",
		"Анкета",
		"Выведи анкету в формате: Имя: Анна Возраст: 25 Город: Москва",
		"strings",
		1,
		"print('Анна')",
		[]string{"Сначала проверь формат."},
		"",
		diag,
	)
	if !strings.Contains(prompt, "Контекст диагностики") {
		t.Fatalf("prompt must include diagnostic section")
	}
	if !strings.Contains(prompt, "[скрытый тест, не раскрывать дословно]") {
		t.Fatalf("prompt must mask hidden expected output")
	}
	if !strings.Contains(prompt, "Явный формат вывода из условия") {
		t.Fatalf("prompt must include explicit output format extracted from statement")
	}
	if !strings.Contains(prompt, "Подсказки автора задачи") {
		t.Fatalf("prompt must include source policy hints section")
	}
}

func TestIsOpenAIRegionRestricted(t *testing.T) {
	err := &openAIRequestError{
		StatusCode: 403,
		Message:    "Country, region, or territory not supported",
	}
	if !isOpenAIRegionRestricted(err) {
		t.Fatalf("expected region restriction to be detected")
	}
}

func TestBuildLocalHintFallbackNotEmpty(t *testing.T) {
	out := buildLocalHintFallback("Сумма", "арифметика", 1, "a = int(input())\nb = int(input())\nprint(a+b)")
	if strings.TrimSpace(out) == "" {
		t.Fatalf("fallback hint should not be empty")
	}
	if !strings.Contains(out, "Следующий шаг:") {
		t.Fatalf("fallback hint should keep step-by-step format")
	}
}

func TestOpenAIProxyURLPrefersDirect(t *testing.T) {
	a := &App{
		Cfg: config.Config{
			OpenAIHTTPProxy: "http://user:pass@proxy.local:8080",
			OpenAIProxyHost: "ignored.local",
			OpenAIProxyPort: "9999",
		},
	}
	if got := a.openAIProxyURL(); got != "http://user:pass@proxy.local:8080" {
		t.Fatalf("unexpected proxy url: %q", got)
	}
}

func TestOpenAIProxyURLBuildsFromParts(t *testing.T) {
	a := &App{
		Cfg: config.Config{
			OpenAIProxyHost:     "141.11.162.95",
			OpenAIProxyPort:     "47198",
			OpenAIProxyUsername: "PSJ3ETN5",
			OpenAIProxyPassword: "2S3W79O2",
		},
	}
	got := a.openAIProxyURL()
	want := "http://PSJ3ETN5:2S3W79O2@141.11.162.95:47198"
	if got != want {
		t.Fatalf("unexpected proxy url: got %q want %q", got, want)
	}
}

func TestNormalizeTaskLanguage(t *testing.T) {
	if got := normalizeTaskLanguage("python"); got != "python" {
		t.Fatalf("unexpected language normalize result: %q", got)
	}
	if got := normalizeTaskLanguage("unknown"); got != "java" {
		t.Fatalf("unexpected default language: %q", got)
	}
}

func TestExtractExplicitOutputFormat(t *testing.T) {
	statement := "Текст\nВыведи анкету в формате: Имя: Анна Возраст: 25 Город: Москва\nДалее..."
	got := extractExplicitOutputFormat(statement)
	if got != "Имя: Анна Возраст: 25 Город: Москва" {
		t.Fatalf("unexpected extracted format: %q", got)
	}
}

func TestSanitizeRunLogForHintHiddenExpected(t *testing.T) {
	failed := &aiHintFailedTest{ExpectedHidden: true}
	log := "test 1: expected 'abc', got 'def'"
	got := sanitizeRunLogForHint(log, failed)
	if strings.Contains(got, "expected 'abc'") || strings.Contains(got, "got 'def'") {
		t.Fatalf("run log should be sanitized for hidden expected output: %q", got)
	}
}

func TestParseHintsFromSourcePolicy(t *testing.T) {
	raw := `{"hints":["Проверь условие if.","  ","Не забудь else."]}`
	got := parseHintsFromSourcePolicy(raw)
	if len(got) != 2 {
		t.Fatalf("expected 2 hints, got %d", len(got))
	}
	if got[0] != "Проверь условие if." || got[1] != "Не забудь else." {
		t.Fatalf("unexpected hints: %#v", got)
	}
}
