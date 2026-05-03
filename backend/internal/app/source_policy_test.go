package app

import "testing"

func TestEvaluateTaskSourcePolicy_EmptyPolicy(t *testing.T) {
	violation, err := evaluateTaskSourcePolicy("", "python", `print("ok")`)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if violation != "" {
		t.Fatalf("expected no violation, got: %q", violation)
	}
}

func TestEvaluateTaskSourcePolicy_RequireAndForbid(t *testing.T) {
	policy := `{
		"language": "python",
		"message": "custom violation",
		"requireAllRegex": ["(?m)^\\s*print\\s*\\(\\s*12\\s*\\+\\s*8\\s*\\)\\s*$"],
		"forbidAnyRegex": ["(?m)^\\s*print\\s*\\(\\s*20\\s*\\)\\s*$"]
	}`

	violation, err := evaluateTaskSourcePolicy(policy, "python", "print(20)")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if violation == "" {
		t.Fatalf("expected violation for forbidden pattern")
	}
	if violation == "custom violation" {
		t.Fatalf("expected context-aware message for forbidden pattern, got static: %q", violation)
	}
	if violation == "" || violation == "Решение не прошло проверку шаблона. Проверьте требования к оформлению и логике задачи." {
		t.Fatalf("expected specific violation message, got: %q", violation)
	}

	okViolation, err := evaluateTaskSourcePolicy(policy, "python", "print(12 + 8)")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if okViolation != "" {
		t.Fatalf("expected no violation for valid source, got: %q", okViolation)
	}
}

func TestEvaluateTaskSourcePolicy_EmptySourceMessage(t *testing.T) {
	policy := `{
		"language": "python",
		"emptySourceMessage": "Код пуст. Добавьте решение."
	}`

	violation, err := evaluateTaskSourcePolicy(policy, "python", "   \n\t ")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if violation != "Код пуст. Добавьте решение." {
		t.Fatalf("expected empty-source message, got: %q", violation)
	}
}

func TestEvaluateTaskSourcePolicy_ObjectRules(t *testing.T) {
	policy := `{
		"language": "python",
		"forbidAny": [
			{"pattern": "(?m)^\\s*print\\s*\\(\\s*20\\s*\\)\\s*$", "message": "Не печатайте готовую константу 20."}
		],
		"requireAll": [
			{"pattern": "(?m)^\\s*print\\s*\\(\\s*12\\s*\\+\\s*8\\s*\\)\\s*$", "message": "Добавьте выражение 12 + 8."}
		]
	}`

	violationForbid, err := evaluateTaskSourcePolicy(policy, "python", "print(20)")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if violationForbid != "Не печатайте готовую константу 20." {
		t.Fatalf("expected custom forbid message, got: %q", violationForbid)
	}

	violationRequire, err := evaluateTaskSourcePolicy(policy, "python", "print(10)")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if violationRequire != "Добавьте выражение 12 + 8." {
		t.Fatalf("expected custom require message, got: %q", violationRequire)
	}
}

func TestEvaluateTaskSourcePolicy_IgnoreCommentOnlyLines(t *testing.T) {
	policy := `{
		"language": "python",
		"ignoreCommentOnlyLines": true,
		"forbidAnyRegex": ["(?m)^\\s*print\\s*\\(\\s*20\\s*\\)\\s*$"]
	}`

	source := "# print(20)\nprint(12 + 8)"
	violation, err := evaluateTaskSourcePolicy(policy, "python", source)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if violation != "" {
		t.Fatalf("expected no violation when forbidden pattern is only in comment, got: %q", violation)
	}
}

func TestEvaluateTaskSourcePolicy_SkipOtherLanguage(t *testing.T) {
	policy := `{
		"language": "python",
		"forbidAnyRegex": ["(?m)^\\s*System\\.out\\.println\\("]
	}`

	violation, err := evaluateTaskSourcePolicy(policy, "java", `System.out.println("ok");`)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if violation != "" {
		t.Fatalf("expected no violation for non-target language, got: %q", violation)
	}
}

func TestEvaluateTaskSourcePolicy_InvalidRegex(t *testing.T) {
	policy := `{
		"language": "python",
		"requireAllRegex": ["("]
	}`

	_, err := evaluateTaskSourcePolicy(policy, "python", `print("x")`)
	if err == nil {
		t.Fatalf("expected regex compilation error")
	}
}
