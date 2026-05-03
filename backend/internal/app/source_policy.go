package app

import (
	"encoding/json"
	"fmt"
	"regexp"
	"strings"

	"leonovcare/backend/internal/judge"
)

type taskSourcePolicyRule struct {
	Pattern string `json:"pattern"`
	Message string `json:"message"`
}

type taskSourcePolicy struct {
	Language               string   `json:"language"`
	Message                string   `json:"message"`
	EmptySourceMessage     string   `json:"emptySourceMessage"`
	RequireAllRegex        []string `json:"requireAllRegex"`
	ForbidAnyRegex         []string `json:"forbidAnyRegex"`
	RequireAll             []taskSourcePolicyRule `json:"requireAll"`
	ForbidAny              []taskSourcePolicyRule `json:"forbidAny"`
	IgnoreCommentOnlyLines bool     `json:"ignoreCommentOnlyLines"`
}

func evaluateTaskSourcePolicy(policyRaw, language, source string) (string, error) {
	raw := strings.TrimSpace(policyRaw)
	if raw == "" || raw == "{}" || raw == "null" {
		return "", nil
	}

	var policy taskSourcePolicy
	if err := json.Unmarshal([]byte(raw), &policy); err != nil {
		return "", fmt.Errorf("decode source policy: %w", err)
	}

	policyLanguage := strings.ToLower(strings.TrimSpace(policy.Language))
	normalizedLanguage := strings.ToLower(strings.TrimSpace(language))
	if policyLanguage != "" && policyLanguage != normalizedLanguage {
		return "", nil
	}

	normalizedSource := normalizePolicySource(source, policy.IgnoreCommentOnlyLines)
	if strings.TrimSpace(normalizedSource) == "" {
		message := strings.TrimSpace(policy.EmptySourceMessage)
		if message != "" {
			return message, nil
		}
		return "Код пока пуст. Добавьте решение и запустите проверку снова.", nil
	}

	forbidRules := mergeLegacyAndObjectRules(policy.ForbidAnyRegex, policy.ForbidAny)
	for _, rule := range forbidRules {
		rx, err := regexp.Compile(rule.Pattern)
		if err != nil {
			return "", fmt.Errorf("compile forbid regex '%s': %w", rule.Pattern, err)
		}
		match := rx.FindString(normalizedSource)
		if match != "" {
			return forbidViolationMessage(policy, rule, match), nil
		}
	}

	requireRules := mergeLegacyAndObjectRules(policy.RequireAllRegex, policy.RequireAll)
	for _, rule := range requireRules {
		rx, err := regexp.Compile(rule.Pattern)
		if err != nil {
			return "", fmt.Errorf("compile require regex '%s': %w", rule.Pattern, err)
		}
		if !rx.MatchString(normalizedSource) {
			return requireViolationMessage(policy, rule), nil
		}
	}

	return "", nil
}

func sourcePolicyViolationResult(message string) judge.Result {
	return judge.Result{
		Status:        "wrong_answer",
		Score:         0,
		CompileOutput: message,
		RunLog:        "source policy check failed",
		Tests:         []judge.TestResult{},
	}
}

func normalizePolicySource(source string, ignoreCommentOnlyLines bool) string {
	normalized := strings.ReplaceAll(source, "\r\n", "\n")
	normalized = strings.ReplaceAll(normalized, "\r", "\n")

	if !ignoreCommentOnlyLines {
		return normalized
	}

	lines := strings.Split(normalized, "\n")
	filtered := make([]string, 0, len(lines))
	for _, line := range lines {
		trimmed := strings.TrimSpace(line)
		if strings.HasPrefix(trimmed, "#") || strings.HasPrefix(trimmed, "//") {
			continue
		}
		filtered = append(filtered, line)
	}
	return strings.Join(filtered, "\n")
}

func mergeLegacyAndObjectRules(legacy []string, objectRules []taskSourcePolicyRule) []taskSourcePolicyRule {
	merged := make([]taskSourcePolicyRule, 0, len(legacy)+len(objectRules))
	for _, pattern := range legacy {
		if strings.TrimSpace(pattern) == "" {
			continue
		}
		merged = append(merged, taskSourcePolicyRule{Pattern: pattern})
	}
	for _, rule := range objectRules {
		if strings.TrimSpace(rule.Pattern) == "" {
			continue
		}
		merged = append(merged, rule)
	}
	return merged
}

func basePolicyMessage(policy taskSourcePolicy) string {
	message := strings.TrimSpace(policy.Message)
	if message != "" {
		return message
	}
	return "Решение не прошло проверку шаблона. Проверьте требования к оформлению и логике задачи."
}

func forbidViolationMessage(policy taskSourcePolicy, rule taskSourcePolicyRule, matchedFragment string) string {
	if text := strings.TrimSpace(rule.Message); text != "" {
		return text
	}

	match := strings.TrimSpace(matchedFragment)
	if match == "" {
		return basePolicyMessage(policy)
	}

	runes := []rune(match)
	if len(runes) > 80 {
		match = string(runes[:80]) + "..."
	}

	return fmt.Sprintf("Это решение содержит готовый вывод `%s`. Покажите вычисление по условию задачи, а не только итоговые константы.", match)
}

func requireViolationMessage(policy taskSourcePolicy, rule taskSourcePolicyRule) string {
	if text := strings.TrimSpace(rule.Message); text != "" {
		return text
	}
	return basePolicyMessage(policy)
}
