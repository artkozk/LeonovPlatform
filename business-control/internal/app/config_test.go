package app

import (
	"errors"
	"testing"
)

func TestGeminiExpressModeDefaults(t *testing.T) {
	t.Setenv("GEMINI_MODEL", "")
	t.Setenv("GEMINI_BASE_URL", "")

	config := LoadConfig()
	if config.GeminiModel != "gemini-2.5-flash" {
		t.Fatalf("GeminiModel = %q", config.GeminiModel)
	}
	if config.GeminiBaseURL != "https://aiplatform.googleapis.com/v1/publishers/google" {
		t.Fatalf("GeminiBaseURL = %q", config.GeminiBaseURL)
	}
}

func TestAIUnavailableMessageExplainsActionableProviderFailures(t *testing.T) {
	tests := []struct {
		name     string
		provider string
		err      error
		want     string
	}{
		{name: "billing", provider: "gemini", err: errors.New("gemini status 403: BILLING_DISABLED"), want: "В Google Cloud не включён биллинг; локальный анализ активен"},
		{name: "quota", provider: "gemini", err: errors.New("gemini status 429: RESOURCE_EXHAUSTED"), want: "Квота внешнего AI исчерпана; локальный анализ активен"},
		{name: "generic Gemini", provider: "gemini", err: errors.New("gemini status 503: UNAVAILABLE"), want: "Google Vertex AI временно недоступен; локальный анализ активен"},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			if got := aiUnavailableMessage(test.provider, test.err); got != test.want {
				t.Fatalf("message = %q, want %q", got, test.want)
			}
		})
	}
}
