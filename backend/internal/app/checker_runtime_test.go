package app

import (
	"encoding/json"
	"os/exec"
	"strings"
	"testing"
)

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

func TestInferMainFilePathFromSourcePolicy_PytestSolutionModule(t *testing.T) {
	policy := `{"checker_type":"python_pytest","checker":{"pytest_code":"from solution import greet\n\ndef test_greet():\n    assert greet('Ann') == 'Hi Ann'\n"}}`
	if got := inferMainFilePathFromSourcePolicy(policy, "python"); got != "solution.py" {
		t.Fatalf("expected solution.py for pytest checker importing solution, got %q", got)
	}
}

func TestPublicRunPreviewSourcePolicyKeepsOnlyPublicPythonStdoutTests(t *testing.T) {
	policy := `{
		"language":"python",
		"checker_type":"python_stdout",
		"checker":{
			"type":"python_stdout",
			"tests":[
				{"input":"17\n","expected_stdout":"Нельзя\n","visibility":"public"},
				{"input":"99\n","expected_stdout":"Можно\n","visibility":"hidden"}
			]
		}
	}`

	previewPolicy := parseTaskSourcePolicy(publicRunPreviewSourcePolicy(policy))
	var checker checkerPythonStdout
	if err := json.Unmarshal(previewPolicy.Checker, &checker); err != nil {
		t.Fatal(err)
	}
	if len(checker.Tests) != 1 {
		t.Fatalf("expected one public preview test, got %d", len(checker.Tests))
	}
	if checker.Tests[0].Input != "17\n" {
		t.Fatalf("expected public stdin to be preserved, got %q", checker.Tests[0].Input)
	}
	if strings.EqualFold(checker.Tests[0].Visibility, "hidden") {
		t.Fatalf("hidden checker test leaked into run preview")
	}
}

func TestPythonPytestImportsModule(t *testing.T) {
	if !pythonPytestImportsModule("import inspect, solution\n", "solution") {
		t.Fatalf("expected comma import to be detected")
	}
	if !pythonPytestImportsModule("from solution import greet\n", "solution") {
		t.Fatalf("expected from import to be detected")
	}
	if pythonPytestImportsModule("from app import solution\n", "solution") {
		t.Fatalf("expected unrelated import to be ignored")
	}
}

func TestHTTPAPICheckerPreservesExpectedJSONFields(t *testing.T) {
	raw := []byte(`{
		"type":"http_api",
		"tests":[{
			"method":"GET",
			"path":"/items?limit=10",
			"expected_status":200,
			"expected_json_subset":{"status":"ok"},
			"expected_json_type":"object",
			"headers":{"Authorization":"Bearer token"},
			"visibility":"hidden"
		}]
	}`)
	var checker checkerHTTPAPI
	if err := json.Unmarshal(raw, &checker); err != nil {
		t.Fatal(err)
	}
	out, err := json.Marshal(checker.Tests)
	if err != nil {
		t.Fatal(err)
	}
	text := string(out)
	for _, want := range []string{`"expected_json_subset"`, `"expected_json_type"`, `"headers"`, `"visibility"`} {
		if !strings.Contains(text, want) {
			t.Fatalf("expected serialized tests to preserve %s, got %s", want, text)
		}
	}
}

func TestEvaluateHTTPAPICheckerSupportsFastAPIContracts(t *testing.T) {
	if _, err := exec.LookPath("docker"); err != nil {
		t.Skip("docker is not available")
	}
	if err := exec.Command("docker", "info").Run(); err != nil {
		t.Skip("docker daemon is not available")
	}

	source := `from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

class TaskIn(BaseModel):
    title: str

@app.get("/items/{item_id}")
def get_item(item_id: int, limit: int = 10):
    if item_id != 1:
        raise HTTPException(status_code=404, detail="not found")
    return {"id": item_id, "limit": limit, "extra": "ok"}

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskIn):
    return {"id": 1, "title": payload.title, "done": False}
`
	checker := json.RawMessage(`{
		"type":"http_api",
		"timeout_sec":12,
		"tests":[
			{"method":"GET","path":"/items/1?limit=20","expected_status":200,"expected_json_subset":{"id":1,"limit":20}},
			{"method":"GET","path":"/items/2","expected_status":404},
			{"method":"POST","path":"/tasks","json":{"title":"Buy milk"},"expected_status":201,"expected_json":{"title":"Buy milk"}},
			{"method":"POST","path":"/tasks","json":{},"expected_status":422}
		]
	}`)

	result := (&App{}).evaluateHTTPAPIChecker(source, nil, checker)
	if result.Status != "accepted" {
		t.Fatalf("expected accepted, got %s: %s", result.Status, result.RunLog)
	}
	if result.Score != 100 {
		t.Fatalf("expected score 100, got %d", result.Score)
	}
}

func TestNormalizeCommandForAllowlist(t *testing.T) {
	got := normalizeCommandForAllowlist("  PyTest   -q  ")
	if got != "pytest -q" {
		t.Fatalf("unexpected normalized command: %q", got)
	}
}

func TestIDECheckerCommandAllowedInProduction(t *testing.T) {
	a := &App{}
	a.Cfg.IDECheckerAllowedCommands = "python -m pytest,pytest"

	if !a.ideCheckerCommandAllowedInProduction("pytest") {
		t.Fatalf("expected pytest to be allowlisted")
	}
	if !a.ideCheckerCommandAllowedInProduction("test -s main.py") {
		t.Fatalf("expected read-only file existence check to be allowed")
	}
	if !a.ideCheckerCommandAllowedInProduction(`grep -E "python|main.py|вывод|команда" README.md`) {
		t.Fatalf("expected read-only grep check to be allowed")
	}
	if a.ideCheckerCommandAllowedInProduction("python main.py") {
		t.Fatalf("expected command to be blocked by explicit allowlist")
	}
	if a.ideCheckerCommandAllowedInProduction("bash -lc whoami") {
		t.Fatalf("unexpected non-allowlisted command")
	}
	if a.ideCheckerCommandAllowedInProduction("test -s ../secret.txt") {
		t.Fatalf("path traversal in test command must be blocked")
	}
	if a.ideCheckerCommandAllowedInProduction(`grep -E "ok" README.md; cat /etc/passwd`) {
		t.Fatalf("shell injection in grep command must be blocked")
	}
}

func TestIDECheckerCommandAllowedInProductionDefaultSafeSet(t *testing.T) {
	a := &App{}
	a.Cfg.IDECheckerAllowedCommands = ""

	if !a.ideCheckerCommandAllowedInProduction("python main.py") {
		t.Fatalf("expected python main.py to be allowed in default safe set")
	}
	if !a.ideCheckerCommandAllowedInProduction("printf '2026\\n' | python main.py") {
		t.Fatalf("expected safe printf->python command to be allowed")
	}
	if !a.ideCheckerCommandAllowedInProduction("test -s src/app.py") {
		t.Fatalf("expected safe test -s command to be allowed")
	}
	if !a.ideCheckerCommandAllowedInProduction(`grep -E "def|return|print|class" src/app.py`) {
		t.Fatalf("expected safe grep -E command to be allowed")
	}
	if a.ideCheckerCommandAllowedInProduction("python main.py; rm -rf /") {
		t.Fatalf("dangerous command must be blocked")
	}
	if a.ideCheckerCommandAllowedInProduction("python main.py & whoami") {
		t.Fatalf("windows command separator must be blocked")
	}
	if a.ideCheckerCommandAllowedInProduction("python main.py | cat") {
		t.Fatalf("arbitrary pipe must be blocked")
	}
}

func TestInferTemplateFilesFromSourcePolicy(t *testing.T) {
	policy := `{"checker_type":"ide_plugin","checker":{"required_files":["main.py","README.md","./README.md"]}}`
	got := inferTemplateFilesFromSourcePolicy(policy, "python")
	if len(got) != 2 {
		t.Fatalf("expected 2 unique template files, got %d: %#v", len(got), got)
	}
	if got[0] != "main.py" {
		t.Fatalf("expected first template file to be main.py, got %q", got[0])
	}
	if got[1] != "README.md" {
		t.Fatalf("expected README.md to be included, got %#v", got)
	}
}

func TestEvaluateTaskByPolicyRejectsSourcePolicyViolation(t *testing.T) {
	a := &App{}
	policy := `{
		"language": "python",
		"forbidAny": [{"pattern": "(?m)^\\s*print\\s*\\(\\s*20\\s*\\)\\s*$", "message": "Нельзя печатать 20 напрямую."}]
	}`

	result := a.evaluateTaskByPolicy("python", "print(20)\n", nil, nil, policy, "")
	if result.Status != "wrong_answer" {
		t.Fatalf("expected wrong_answer, got %s", result.Status)
	}
	if result.CompileOutput != "Нельзя печатать 20 напрямую." {
		t.Fatalf("unexpected violation message: %q", result.CompileOutput)
	}
}

func TestNormalizePathForWorkspaceRejectsAbsoluteVolumePath(t *testing.T) {
	_, err := normalizePathForWorkspace("C:/Windows/System32/drivers/etc/hosts")
	if err == nil {
		t.Fatalf("expected Windows volume path to be rejected")
	}
}
