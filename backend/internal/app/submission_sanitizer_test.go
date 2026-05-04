package app

import (
	"encoding/json"
	"strings"
	"testing"

	"leonovcare/backend/internal/judge"
)

func TestValidateSubmissionPayloadSize(t *testing.T) {
	err := validateSubmissionPayloadSize(8, "123456789", nil)
	if err == nil {
		t.Fatalf("expected payload size error")
	}

	err = validateSubmissionPayloadSize(64, "1234", []submissionFilePayload{{Path: "main.py", Content: "print(1)"}})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestSanitizeSubmissionFeedbackForClient(t *testing.T) {
	raw := `[{"index":1,"passed":false,"input":"secret","expected":"42","actual":"17","error":"wrong"},{"index":2,"passed":true}]`
	safe := sanitizeSubmissionFeedbackForClient(raw)

	var items []map[string]interface{}
	if err := json.Unmarshal([]byte(safe), &items); err != nil {
		t.Fatalf("invalid json: %v", err)
	}
	if len(items) != 2 {
		t.Fatalf("expected 2 items, got %d", len(items))
	}
	if _, ok := items[0]["input"]; ok {
		t.Fatalf("sanitized payload must not contain input")
	}
	if _, ok := items[0]["expected"]; ok {
		t.Fatalf("sanitized payload must not contain expected")
	}
}

func TestBuildRunPreviewTestsPayload(t *testing.T) {
	tests := []judge.TestResult{
		{
			Index:    1,
			Passed:   false,
			Input:    "hidden input",
			Expected: "secret expected",
			Actual:   "42",
			Error:    "wrong",
		},
	}
	payload := buildRunPreviewTestsPayload(tests)
	if len(payload) != 1 {
		t.Fatalf("expected 1 payload item, got %d", len(payload))
	}
	if _, ok := payload[0]["expected"]; ok {
		t.Fatalf("preview payload must not include expected")
	}
	if _, ok := payload[0]["input"]; ok {
		t.Fatalf("preview payload must not include input")
	}
}

func TestTrimTextForClient(t *testing.T) {
	long := strings.Repeat("a", 20)
	trimmed := trimTextForClient(long, 5)
	if !strings.Contains(trimmed, "truncated") {
		t.Fatalf("expected truncated marker")
	}
}
