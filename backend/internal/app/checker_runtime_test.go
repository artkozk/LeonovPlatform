package app

import "testing"

func TestEncodeDecodeSubmissionSourceBundleRoundTrip(t *testing.T) {
	files := []submissionFilePayload{
		{Path: "main.py", Content: "print('ok')\n"},
		{Path: "README.md", Content: "# Demo\n"},
	}

	encoded := encodeSubmissionSourceBundle("print('ok')\n", files)
	source, decodedFiles := decodeSubmissionSourceBundle(encoded)

	if source != "print('ok')\n" {
		t.Fatalf("unexpected source: %q", source)
	}
	if len(decodedFiles) != 2 {
		t.Fatalf("expected 2 files, got %d", len(decodedFiles))
	}
	if decodedFiles[0].Path != "main.py" {
		t.Fatalf("unexpected first file path: %q", decodedFiles[0].Path)
	}
}

func TestInferTaskTypeFromSourcePolicy(t *testing.T) {
	projectPolicy := `{"checker_type":"ide_plugin","checker":{}}`
	if got := inferTaskTypeFromSourcePolicy(projectPolicy); got != "PROJECT" {
		t.Fatalf("expected PROJECT, got %q", got)
	}

	unitPolicy := `{"checker_type":"python_pytest","checker":{}}`
	if got := inferTaskTypeFromSourcePolicy(unitPolicy); got != "UNIT_TEST" {
		t.Fatalf("expected UNIT_TEST, got %q", got)
	}
}

func TestInferMainFilePathFromSourcePolicy(t *testing.T) {
	policy := `{"checker_type":"ide_plugin","checker":{"required_files":["app/main.py","README.md"]}}`
	if got := inferMainFilePathFromSourcePolicy(policy, "python"); got != "app/main.py" {
		t.Fatalf("expected app/main.py, got %q", got)
	}

	if got := inferMainFilePathFromSourcePolicy(`{"checker_type":"sql_query","checker":{}}`, "sql"); got != "query.sql" {
		t.Fatalf("expected query.sql fallback, got %q", got)
	}
}
