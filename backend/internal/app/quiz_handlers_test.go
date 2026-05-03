package app

import "testing"

func TestSanitizeQuizPayloadForStudent(t *testing.T) {
	payload := map[string]any{
		"type": "single_choice",
		"questions": []any{
			map[string]any{
				"id":              "q1",
				"question":        "Demo?",
				"correctOptionId": "B",
				"options": []any{
					map[string]any{"id": "A", "text": "No"},
					map[string]any{"id": "B", "text": "Yes"},
				},
			},
		},
	}

	sanitizedAny := sanitizeQuizPayloadForStudent(payload)
	sanitized, ok := sanitizedAny.(map[string]any)
	if !ok {
		t.Fatalf("sanitized payload must be map")
	}
	questions, ok := sanitized["questions"].([]any)
	if !ok || len(questions) != 1 {
		t.Fatalf("expected one question")
	}
	question, ok := questions[0].(map[string]any)
	if !ok {
		t.Fatalf("question must be map")
	}
	if _, exists := question["correctOptionId"]; exists {
		t.Fatalf("correctOptionId must be removed from student payload")
	}
}

func TestExtractQuizQuestionsForCheck(t *testing.T) {
	raw := `{"type":"single_choice","questions":[{"id":"q1","question":"Q?","options":[{"id":"A","text":"1"},{"id":"B","text":"2"}],"correctOptionId":"b"}]}`
	questions, err := extractQuizQuestionsForCheck(raw)
	if err != nil {
		t.Fatalf("unexpected parse error: %v", err)
	}
	if len(questions) != 1 {
		t.Fatalf("expected 1 question, got %d", len(questions))
	}
	if questions[0].CorrectOptionID != "B" {
		t.Fatalf("expected normalized correct option B, got %q", questions[0].CorrectOptionID)
	}
}
