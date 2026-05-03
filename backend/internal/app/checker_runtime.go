package app

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"sort"
	"strings"
	"time"

	"leonovcare/backend/internal/judge"
)

const submissionBundlePrefix = "__LC_BUNDLE_V1__\n"

type submissionFilePayload struct {
	Path    string `json:"path"`
	Content string `json:"content"`
}

type submissionSourceBundle struct {
	SourceCode string                  `json:"sourceCode"`
	Files      []submissionFilePayload `json:"files"`
}

type taskSourcePolicyEnvelope struct {
	Language    string          `json:"language"`
	CheckerType string          `json:"checker_type"`
	Checker     json.RawMessage `json:"checker"`
}

type checkerPythonStdout struct {
	Type       string `json:"type"`
	Language   string `json:"language"`
	TimeoutSec int    `json:"timeout_sec"`
	Tests      []struct {
		Input          string `json:"input"`
		ExpectedStdout string `json:"expected_stdout"`
		Visibility     string `json:"visibility"`
	} `json:"tests"`
}

type checkerSQLQuery struct {
	Type       string `json:"type"`
	Dialect    string `json:"dialect"`
	TimeoutSec int    `json:"timeout_sec"`
	InitSQL    string `json:"init_sql"`
	Checks     []struct {
		Query      string `json:"query"`
		Expected   string `json:"expected"`
		Visibility string `json:"visibility"`
	} `json:"checks"`
}

type checkerPythonPytest struct {
	Type          string   `json:"type"`
	Language      string   `json:"language"`
	TimeoutSec    int      `json:"timeout_sec"`
	RequiredFiles []string `json:"required_files"`
	PytestCode    string   `json:"pytest_code"`
}

type checkerHTTPAPI struct {
	Type       string `json:"type"`
	Language   string `json:"language"`
	Framework  string `json:"framework"`
	TimeoutSec int    `json:"timeout_sec"`
	Tests      []struct {
		Method         string      `json:"method"`
		Path           string      `json:"path"`
		JSON           interface{} `json:"json"`
		ExpectedStatus int         `json:"expected_status"`
		ExpectedJSON   interface{} `json:"expected_json"`
	} `json:"tests"`
}

type checkerIDEPlugin struct {
	Type           string   `json:"type"`
	TimeoutSec     int      `json:"timeout_sec"`
	RequiredFiles  []string `json:"required_files"`
	RequiredDirs   []string `json:"required_dirs"`
	ForbiddenFiles []string `json:"forbidden_files"`
	Commands       []struct {
		Cmd        string `json:"cmd"`
		TimeoutSec int    `json:"timeout_sec"`
	} `json:"commands"`
	SendToServerForHiddenTests bool `json:"send_to_server_for_hidden_tests"`
}

func encodeSubmissionSourceBundle(sourceCode string, files []submissionFilePayload) string {
	if len(files) == 0 {
		return sourceCode
	}
	bundle := submissionSourceBundle{
		SourceCode: sourceCode,
		Files:      files,
	}
	raw, err := json.Marshal(bundle)
	if err != nil {
		return sourceCode
	}
	return submissionBundlePrefix + string(raw)
}

func decodeSubmissionSourceBundle(raw string) (string, []submissionFilePayload) {
	if !strings.HasPrefix(raw, submissionBundlePrefix) {
		return raw, nil
	}
	payload := strings.TrimPrefix(raw, submissionBundlePrefix)
	var bundle submissionSourceBundle
	if err := json.Unmarshal([]byte(payload), &bundle); err != nil {
		return raw, nil
	}
	source := bundle.SourceCode
	if strings.TrimSpace(source) == "" {
		source = firstNonEmptySourceFromFiles(bundle.Files)
	}
	return source, bundle.Files
}

func firstNonEmptySourceFromFiles(files []submissionFilePayload) string {
	for _, file := range files {
		if strings.TrimSpace(file.Content) == "" {
			continue
		}
		lower := strings.ToLower(strings.TrimSpace(file.Path))
		if strings.HasSuffix(lower, ".py") || strings.HasSuffix(lower, ".sql") || strings.HasSuffix(lower, ".java") {
			return file.Content
		}
	}
	for _, file := range files {
		if strings.TrimSpace(file.Content) != "" {
			return file.Content
		}
	}
	return ""
}

func normalizePathForWorkspace(pathRaw string) (string, error) {
	candidate := strings.TrimSpace(strings.ReplaceAll(pathRaw, "\\", "/"))
	if candidate == "" {
		return "", errors.New("path is empty")
	}
	cleaned := filepath.ToSlash(filepath.Clean(candidate))
	if strings.HasPrefix(cleaned, "../") || cleaned == ".." {
		return "", errors.New("path escapes workspace")
	}
	if strings.HasPrefix(cleaned, "/") {
		return "", errors.New("absolute path is not allowed")
	}
	return cleaned, nil
}

func writeFilesToWorkspace(workspace string, files []submissionFilePayload) error {
	for _, file := range files {
		path, err := normalizePathForWorkspace(file.Path)
		if err != nil {
			return fmt.Errorf("invalid file path %q: %w", file.Path, err)
		}
		fullPath := filepath.Join(workspace, filepath.FromSlash(path))
		if err := os.MkdirAll(filepath.Dir(fullPath), 0o755); err != nil {
			return err
		}
		if err := os.WriteFile(fullPath, []byte(file.Content), 0o644); err != nil {
			return err
		}
	}
	return nil
}

func ensureDefaultSourceFile(workspace string, sourceCode string, preferredPath string) error {
	source := strings.TrimSpace(sourceCode)
	if source == "" {
		return nil
	}
	path := strings.TrimSpace(preferredPath)
	if path == "" {
		path = "main.py"
	}
	normalized, err := normalizePathForWorkspace(path)
	if err != nil {
		normalized = "main.py"
	}
	fullPath := filepath.Join(workspace, filepath.FromSlash(normalized))
	if err := os.MkdirAll(filepath.Dir(fullPath), 0o755); err != nil {
		return err
	}
	if _, statErr := os.Stat(fullPath); statErr == nil {
		return nil
	}
	return os.WriteFile(fullPath, []byte(sourceCode), 0o644)
}

func detectPythonBinaryForChecker() (string, error) {
	candidates := []string{"python3", "python"}
	for _, candidate := range candidates {
		if _, err := exec.LookPath(candidate); err != nil {
			continue
		}
		cmd := exec.Command(candidate, "--version")
		out, err := cmd.CombinedOutput()
		if err != nil {
			continue
		}
		if strings.Contains(strings.ToLower(string(out)), "python") {
			return candidate, nil
		}
	}
	return "", errors.New("python runtime is not available")
}

func runCommandWithTimeout(ctx context.Context, command string, args []string, workdir string, stdin string) (string, error, bool) {
	cmd := exec.CommandContext(ctx, command, args...)
	cmd.Dir = workdir
	if stdin != "" {
		cmd.Stdin = strings.NewReader(stdin)
	}
	var stdout bytes.Buffer
	var stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	err := cmd.Run()
	if errors.Is(ctx.Err(), context.DeadlineExceeded) {
		return strings.TrimSpace(stdout.String() + "\n" + stderr.String()), err, true
	}
	output := strings.TrimSpace(stdout.String())
	errOutput := strings.TrimSpace(stderr.String())
	if errOutput != "" {
		if output == "" {
			output = errOutput
		} else {
			output = output + "\n" + errOutput
		}
	}
	return output, err, false
}

func runShellCommand(ctx context.Context, workdir, command string) (string, error, bool) {
	if runtime.GOOS == "windows" {
		return runCommandWithTimeout(ctx, "cmd", []string{"/C", command}, workdir, "")
	}
	return runCommandWithTimeout(ctx, "bash", []string{"-lc", command}, workdir, "")
}

func parseTaskSourcePolicy(sourcePolicyRaw string) taskSourcePolicyEnvelope {
	trimmed := strings.TrimSpace(sourcePolicyRaw)
	if trimmed == "" {
		return taskSourcePolicyEnvelope{}
	}
	var envelope taskSourcePolicyEnvelope
	if err := json.Unmarshal([]byte(trimmed), &envelope); err != nil {
		return taskSourcePolicyEnvelope{}
	}
	envelope.CheckerType = strings.ToLower(strings.TrimSpace(envelope.CheckerType))
	return envelope
}

func inferTaskTypeFromSourcePolicy(sourcePolicyRaw string) string {
	switch parseTaskSourcePolicy(sourcePolicyRaw).CheckerType {
	case "ide_plugin":
		return "PROJECT"
	case "python_pytest", "http_api":
		return "UNIT_TEST"
	case "python_stdout", "sql_query":
		return "CONSOLE"
	default:
		return "CONSOLE"
	}
}

func inferMainFilePathFromSourcePolicy(sourcePolicyRaw, language string) string {
	policy := parseTaskSourcePolicy(sourcePolicyRaw)
	defaultPath := "main.py"
	if strings.EqualFold(strings.TrimSpace(language), "sql") {
		defaultPath = "query.sql"
	}
	if len(policy.Checker) == 0 {
		return defaultPath
	}
	var checker struct {
		RequiredFiles []string `json:"required_files"`
	}
	if err := json.Unmarshal(policy.Checker, &checker); err == nil {
		for _, file := range checker.RequiredFiles {
			if strings.TrimSpace(file) != "" {
				return file
			}
		}
	}
	return defaultPath
}

func buildJudgeTestsFromPythonStdout(checker checkerPythonStdout) []judge.TestCase {
	out := make([]judge.TestCase, 0, len(checker.Tests))
	for _, tc := range checker.Tests {
		expected := strings.TrimSpace(tc.ExpectedStdout)
		if expected == "" {
			continue
		}
		out = append(out, judge.TestCase{Input: tc.Input, Expected: tc.ExpectedStdout})
	}
	return out
}

func buildJudgeTestsFromSQLChecker(checker checkerSQLQuery, solutionCode string) []judge.TestCase {
	out := make([]judge.TestCase, 0, len(checker.Checks))
	solution := strings.TrimSpace(solutionCode)
	for _, ck := range checker.Checks {
		expected := strings.TrimSpace(ck.Expected)
		if strings.EqualFold(expected, "match_solution_behavior") || expected == "" {
			expected = solution
		}
		if expected == "" {
			continue
		}
		out = append(out, judge.TestCase{Input: checker.InitSQL, Expected: expected})
	}
	if len(out) == 0 && solution != "" {
		out = append(out, judge.TestCase{Input: checker.InitSQL, Expected: solution})
	}
	return out
}

func selectPreferredTaskFile(files []submissionFilePayload, preferred []string) string {
	for _, candidate := range preferred {
		normalized, err := normalizePathForWorkspace(candidate)
		if err != nil {
			continue
		}
		for _, file := range files {
			current, err := normalizePathForWorkspace(file.Path)
			if err != nil {
				continue
			}
			if current == normalized {
				return normalized
			}
		}
	}
	for _, file := range files {
		normalized, err := normalizePathForWorkspace(file.Path)
		if err != nil {
			continue
		}
		lower := strings.ToLower(normalized)
		if strings.HasSuffix(lower, ".py") {
			return normalized
		}
	}
	if len(preferred) > 0 {
		normalized, err := normalizePathForWorkspace(preferred[0])
		if err == nil {
			return normalized
		}
	}
	return "main.py"
}

func parseRunnerJSON(output string) (map[string]interface{}, error) {
	trimmed := strings.TrimSpace(output)
	if trimmed == "" {
		return nil, errors.New("empty runner output")
	}
	start := strings.Index(trimmed, "{")
	end := strings.LastIndex(trimmed, "}")
	if start < 0 || end < start {
		return nil, errors.New("runner output is not json")
	}
	candidate := trimmed[start : end+1]
	var payload map[string]interface{}
	if err := json.Unmarshal([]byte(candidate), &payload); err != nil {
		return nil, err
	}
	return payload, nil
}

func buildResultFromRunnerPayload(payload map[string]interface{}, fallbackStatus string) judge.Result {
	status := strings.TrimSpace(fmt.Sprint(payload["status"]))
	if status == "" || status == "<nil>" {
		status = fallbackStatus
	}
	runLog := strings.TrimSpace(fmt.Sprint(payload["run_log"]))
	compileOutput := strings.TrimSpace(fmt.Sprint(payload["compile_output"]))

	rawTests, _ := payload["tests"].([]interface{})
	tests := make([]judge.TestResult, 0, len(rawTests))
	passedCount := 0
	for idx, raw := range rawTests {
		obj, _ := raw.(map[string]interface{})
		name := strings.TrimSpace(fmt.Sprint(obj["name"]))
		passed := false
		if rawPassed, ok := obj["passed"].(bool); ok {
			passed = rawPassed
		}
		errText := strings.TrimSpace(fmt.Sprint(obj["error"]))
		if errText == "<nil>" {
			errText = ""
		}
		tests = append(tests, judge.TestResult{
			Index:    idx + 1,
			Input:    name,
			Expected: "",
			Actual:   strings.TrimSpace(fmt.Sprint(obj["actual"])),
			Passed:   passed,
			Error:    errText,
		})
		if passed {
			passedCount++
		}
	}
	score := 0
	if len(tests) > 0 {
		score = int(float64(passedCount) / float64(len(tests)) * 100)
	}
	return judge.Result{
		Status:        status,
		Score:         score,
		CompileOutput: compileOutput,
		RunLog:        runLog,
		Tests:         tests,
	}
}

func (a *App) evaluatePythonPytestChecker(sourceCode string, files []submissionFilePayload, checkerRaw json.RawMessage) judge.Result {
	var checker checkerPythonPytest
	if err := json.Unmarshal(checkerRaw, &checker); err != nil {
		return judge.Result{Status: "failed", CompileOutput: err.Error(), RunLog: "invalid python_pytest checker config"}
	}
	if strings.TrimSpace(checker.PytestCode) == "" {
		return judge.Result{Status: "failed", CompileOutput: "pytest_code is empty", RunLog: "checker is not configured"}
	}

	pythonBin, err := detectPythonBinaryForChecker()
	if err != nil {
		return judge.Result{Status: "failed", CompileOutput: err.Error(), RunLog: "python runtime is not available"}
	}

	workspace, err := os.MkdirTemp("", "lc-pytest-check-*")
	if err != nil {
		return judge.Result{Status: "failed", CompileOutput: err.Error(), RunLog: "unable to create workspace"}
	}
	defer os.RemoveAll(workspace)

	if len(files) > 0 {
		if err := writeFilesToWorkspace(workspace, files); err != nil {
			return judge.Result{Status: "failed", CompileOutput: err.Error(), RunLog: "failed to write submission files"}
		}
	}
	preferredFile := selectPreferredTaskFile(files, checker.RequiredFiles)
	if err := ensureDefaultSourceFile(workspace, sourceCode, preferredFile); err != nil {
		return judge.Result{Status: "failed", CompileOutput: err.Error(), RunLog: "failed to prepare source file"}
	}

	pytestStub := `class raises:
    def __init__(self, exc_type):
        self.exc_type = exc_type
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return exc_type is not None and issubclass(exc_type, self.exc_type)

class _Mark:
    def __getattr__(self, _name):
        def decorator(*_args, **_kwargs):
            def wrapper(func):
                return func
            return wrapper
        return decorator

mark = _Mark()

def fixture(*_args, **_kwargs):
    def wrapper(func):
        return func
    return wrapper
`

	runnerScript := `import importlib
import json
import traceback

result = {"status": "accepted", "compile_output": "", "run_log": "", "tests": []}

try:
    module = importlib.import_module("__lc_tests")
except Exception:
    result["status"] = "compile_error"
    result["compile_output"] = traceback.format_exc()
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0)

test_names = sorted([name for name in dir(module) if name.startswith("test_")])
if not test_names:
    result["status"] = "failed"
    result["run_log"] = "no test_* functions found"
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0)

for name in test_names:
    item = {"name": name, "passed": True, "error": "", "actual": ""}
    try:
        fn = getattr(module, name)
        if not callable(fn):
            continue
        fn()
    except AssertionError as exc:
        item["passed"] = False
        item["error"] = str(exc) or "assertion failed"
        if result["status"] == "accepted":
            result["status"] = "wrong_answer"
    except Exception:
        item["passed"] = False
        item["error"] = traceback.format_exc()
        result["status"] = "runtime_error"
    result["tests"].append(item)

if result["status"] != "accepted":
    failed = [t for t in result["tests"] if not t.get("passed")]
    if failed:
        result["run_log"] = failed[0].get("error", "")

print(json.dumps(result, ensure_ascii=False))
`

	if err := os.WriteFile(filepath.Join(workspace, "pytest.py"), []byte(pytestStub), 0o644); err != nil {
		return judge.Result{Status: "failed", CompileOutput: err.Error(), RunLog: "unable to write pytest stub"}
	}
	if err := os.WriteFile(filepath.Join(workspace, "__lc_tests.py"), []byte(checker.PytestCode), 0o644); err != nil {
		return judge.Result{Status: "failed", CompileOutput: err.Error(), RunLog: "unable to write tests"}
	}
	if err := os.WriteFile(filepath.Join(workspace, "__lc_runner.py"), []byte(runnerScript), 0o644); err != nil {
		return judge.Result{Status: "failed", CompileOutput: err.Error(), RunLog: "unable to write runner"}
	}

	timeoutSec := checker.TimeoutSec
	if timeoutSec <= 0 {
		timeoutSec = 12
	}
	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(timeoutSec)*time.Second)
	defer cancel()

	output, runErr, timedOut := runCommandWithTimeout(ctx, pythonBin, []string{"__lc_runner.py"}, workspace, "")
	if timedOut {
		return judge.Result{Status: "time_limit", CompileOutput: "Execution timeout", RunLog: "pytest checker timeout"}
	}
	if runErr != nil && strings.TrimSpace(output) == "" {
		return judge.Result{Status: "runtime_error", CompileOutput: runErr.Error(), RunLog: "pytest runner failed"}
	}

	payload, parseErr := parseRunnerJSON(output)
	if parseErr != nil {
		return judge.Result{Status: "runtime_error", CompileOutput: parseErr.Error(), RunLog: output}
	}
	return buildResultFromRunnerPayload(payload, "failed")
}

func (a *App) evaluateHTTPAPIChecker(sourceCode string, files []submissionFilePayload, checkerRaw json.RawMessage) judge.Result {
	var checker checkerHTTPAPI
	if err := json.Unmarshal(checkerRaw, &checker); err != nil {
		return judge.Result{Status: "failed", CompileOutput: err.Error(), RunLog: "invalid http_api checker config"}
	}
	if len(checker.Tests) == 0 {
		return judge.Result{Status: "failed", CompileOutput: "http_api tests are empty", RunLog: "checker is not configured"}
	}

	pythonBin, err := detectPythonBinaryForChecker()
	if err != nil {
		return judge.Result{Status: "failed", CompileOutput: err.Error(), RunLog: "python runtime is not available"}
	}

	workspace, err := os.MkdirTemp("", "lc-http-check-*")
	if err != nil {
		return judge.Result{Status: "failed", CompileOutput: err.Error(), RunLog: "unable to create workspace"}
	}
	defer os.RemoveAll(workspace)

	if len(files) > 0 {
		if err := writeFilesToWorkspace(workspace, files); err != nil {
			return judge.Result{Status: "failed", CompileOutput: err.Error(), RunLog: "failed to write submission files"}
		}
	}
	entryFile := selectPreferredTaskFile(files, []string{"main.py", "app/main.py"})
	if err := ensureDefaultSourceFile(workspace, sourceCode, entryFile); err != nil {
		return judge.Result{Status: "failed", CompileOutput: err.Error(), RunLog: "failed to prepare source file"}
	}

	testsBytes, err := json.Marshal(checker.Tests)
	if err != nil {
		return judge.Result{Status: "failed", CompileOutput: err.Error(), RunLog: "unable to serialize tests"}
	}
	if err := os.WriteFile(filepath.Join(workspace, "__lc_http_tests.json"), testsBytes, 0o644); err != nil {
		return judge.Result{Status: "failed", CompileOutput: err.Error(), RunLog: "unable to write tests"}
	}

	runnerScript := `import asyncio
import importlib.util
import inspect
import json
import pathlib
import sys
import traceback
import types

class HTTPException(Exception):
    def __init__(self, status_code=500, detail=None):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail

class FastAPI:
    def __init__(self):
        self._routes = []
    def _route(self, method, path):
        def decorator(func):
            self._routes.append({"method": method.upper(), "path": path, "func": func})
            return func
        return decorator
    def get(self, path, **_kwargs):
        return self._route("GET", path)
    def post(self, path, **_kwargs):
        return self._route("POST", path)
    def put(self, path, **_kwargs):
        return self._route("PUT", path)
    def delete(self, path, **_kwargs):
        return self._route("DELETE", path)
    def patch(self, path, **_kwargs):
        return self._route("PATCH", path)

class APIRouter(FastAPI):
    pass

def Depends(value=None):
    return value

def Query(default=None, **_kwargs):
    return default

def Path(default=None, **_kwargs):
    return default

def Body(default=None, **_kwargs):
    return default

fastapi_mod = types.ModuleType("fastapi")
fastapi_mod.FastAPI = FastAPI
fastapi_mod.APIRouter = APIRouter
fastapi_mod.HTTPException = HTTPException
fastapi_mod.Depends = Depends
fastapi_mod.Query = Query
fastapi_mod.Path = Path
fastapi_mod.Body = Body
sys.modules["fastapi"] = fastapi_mod

result = {"status": "accepted", "compile_output": "", "run_log": "", "tests": []}

entry_file = pathlib.Path("` + entryFile + `")
if not entry_file.exists():
    result["status"] = "failed"
    result["run_log"] = f"entry file not found: {entry_file}"
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0)

spec = importlib.util.spec_from_file_location("student_app", entry_file)
module = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(module)
except Exception:
    result["status"] = "compile_error"
    result["compile_output"] = traceback.format_exc()
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0)

app = getattr(module, "app", None)
if app is None:
    for value in module.__dict__.values():
        if isinstance(value, FastAPI):
            app = value
            break

if app is None or not hasattr(app, "_routes"):
    result["status"] = "failed"
    result["run_log"] = "FastAPI app instance not found"
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0)

with open("__lc_http_tests.json", "r", encoding="utf-8") as f:
    checks = json.load(f)

def normalize_payload(value):
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    return value

for test in checks:
    method = str(test.get("method", "GET")).upper()
    path = str(test.get("path", ""))
    expected_status = int(test.get("expected_status", 200) or 200)
    expected_json = test.get("expected_json")

    route = next((r for r in app._routes if str(r.get("method", "")).upper() == method and str(r.get("path", "")) == path), None)
    item = {"name": f"{method} {path}", "passed": True, "error": "", "actual": ""}

    if route is None:
        item["passed"] = False
        item["error"] = "route not found"
        result["status"] = "wrong_answer"
        result["tests"].append(item)
        continue

    fn = route.get("func")
    try:
        payload = test.get("json")
        if isinstance(payload, dict):
            kwargs = {}
            sig = inspect.signature(fn)
            for name, param in sig.parameters.items():
                if name in payload:
                    kwargs[name] = payload[name]
                elif param.default is inspect._empty:
                    kwargs[name] = None
            response = fn(**kwargs)
        else:
            response = fn()

        if inspect.isawaitable(response):
            response = asyncio.run(response)

        status_code = 200
        body = response
        if isinstance(response, tuple) and len(response) == 2 and isinstance(response[1], int):
            body = response[0]
            status_code = response[1]

        normalized_body = normalize_payload(body)
        item["actual"] = json.dumps(normalized_body, ensure_ascii=False)

        if status_code != expected_status:
            item["passed"] = False
            item["error"] = f"expected status {expected_status}, got {status_code}"
        elif expected_json is not None and normalized_body != expected_json:
            item["passed"] = False
            item["error"] = f"expected json {expected_json}, got {normalized_body}"

        if not item["passed"] and result["status"] == "accepted":
            result["status"] = "wrong_answer"

    except HTTPException as exc:
        item["passed"] = False
        item["error"] = f"HTTPException status={getattr(exc, 'status_code', '?')} detail={getattr(exc, 'detail', '')}"
        result["status"] = "wrong_answer"
    except Exception:
        item["passed"] = False
        item["error"] = traceback.format_exc()
        result["status"] = "runtime_error"

    result["tests"].append(item)

if result["status"] != "accepted":
    failed = [t for t in result["tests"] if not t.get("passed")]
    if failed:
        result["run_log"] = failed[0].get("error", "")

print(json.dumps(result, ensure_ascii=False))
`

	if err := os.WriteFile(filepath.Join(workspace, "__lc_http_runner.py"), []byte(runnerScript), 0o644); err != nil {
		return judge.Result{Status: "failed", CompileOutput: err.Error(), RunLog: "unable to write runner"}
	}

	timeoutSec := checker.TimeoutSec
	if timeoutSec <= 0 {
		timeoutSec = 12
	}
	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(timeoutSec)*time.Second)
	defer cancel()

	output, runErr, timedOut := runCommandWithTimeout(ctx, pythonBin, []string{"__lc_http_runner.py"}, workspace, "")
	if timedOut {
		return judge.Result{Status: "time_limit", CompileOutput: "Execution timeout", RunLog: "http_api checker timeout"}
	}
	if runErr != nil && strings.TrimSpace(output) == "" {
		return judge.Result{Status: "runtime_error", CompileOutput: runErr.Error(), RunLog: "http_api runner failed"}
	}

	payload, parseErr := parseRunnerJSON(output)
	if parseErr != nil {
		return judge.Result{Status: "runtime_error", CompileOutput: parseErr.Error(), RunLog: output}
	}
	return buildResultFromRunnerPayload(payload, "failed")
}

func pathExists(path string) bool {
	_, err := os.Stat(path)
	return err == nil
}

func collectWorkspaceRelativePaths(root string) (map[string]os.FileInfo, error) {
	items := map[string]os.FileInfo{}
	err := filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		rel, err := filepath.Rel(root, path)
		if err != nil {
			return err
		}
		rel = filepath.ToSlash(rel)
		if rel == "." {
			return nil
		}
		items[rel] = info
		return nil
	})
	return items, err
}

func checkForbiddenPathExists(root string, forbidden string, items map[string]os.FileInfo) bool {
	normalized := strings.TrimSpace(strings.ReplaceAll(forbidden, "\\", "/"))
	if normalized == "" {
		return false
	}
	normalized = strings.TrimPrefix(normalized, "./")
	if strings.HasSuffix(normalized, "/") {
		normalized = strings.TrimSuffix(normalized, "/")
		if normalized == "" {
			return false
		}
		for rel, info := range items {
			if info.IsDir() {
				if rel == normalized || strings.HasPrefix(rel, normalized+"/") {
					return true
				}
			}
		}
		return false
	}

	for rel := range items {
		if rel == normalized || strings.HasPrefix(rel, normalized+"/") {
			return true
		}
	}
	if strings.Contains(normalized, "/") {
		return pathExists(filepath.Join(root, filepath.FromSlash(normalized)))
	}
	for rel := range items {
		if filepath.Base(rel) == normalized {
			return true
		}
	}
	return false
}

func (a *App) evaluateIDEPluginChecker(sourceCode string, files []submissionFilePayload, checkerRaw json.RawMessage) judge.Result {
	var checker checkerIDEPlugin
	if err := json.Unmarshal(checkerRaw, &checker); err != nil {
		return judge.Result{Status: "failed", CompileOutput: err.Error(), RunLog: "invalid ide_plugin checker config"}
	}

	workspace, err := os.MkdirTemp("", "lc-ide-check-*")
	if err != nil {
		return judge.Result{Status: "failed", CompileOutput: err.Error(), RunLog: "unable to create workspace"}
	}
	defer os.RemoveAll(workspace)

	if len(files) > 0 {
		if err := writeFilesToWorkspace(workspace, files); err != nil {
			return judge.Result{Status: "failed", CompileOutput: err.Error(), RunLog: "failed to write submission files"}
		}
	}

	preferred := "main.py"
	if len(checker.RequiredFiles) > 0 {
		preferred = checker.RequiredFiles[0]
	}
	if err := ensureDefaultSourceFile(workspace, sourceCode, preferred); err != nil {
		return judge.Result{Status: "failed", CompileOutput: err.Error(), RunLog: "failed to prepare source file"}
	}

	items, walkErr := collectWorkspaceRelativePaths(workspace)
	if walkErr != nil {
		return judge.Result{Status: "failed", CompileOutput: walkErr.Error(), RunLog: "failed to inspect workspace"}
	}

	tests := make([]judge.TestResult, 0)
	passed := 0

	sortedRequiredFiles := append([]string(nil), checker.RequiredFiles...)
	sort.Strings(sortedRequiredFiles)
	for idx, required := range sortedRequiredFiles {
		normalized, err := normalizePathForWorkspace(required)
		tr := judge.TestResult{Index: len(tests) + 1, Input: required, Expected: "exists", Actual: ""}
		if err != nil {
			tr.Passed = false
			tr.Error = "invalid required file path"
			tests = append(tests, tr)
			continue
		}
		fullPath := filepath.Join(workspace, filepath.FromSlash(normalized))
		if stat, statErr := os.Stat(fullPath); statErr == nil && !stat.IsDir() {
			tr.Passed = true
			tr.Actual = "exists"
			passed++
		} else {
			tr.Passed = false
			tr.Error = "required file is missing"
		}
		tr.Index = idx + 1
		tests = append(tests, tr)
	}

	sortedRequiredDirs := append([]string(nil), checker.RequiredDirs...)
	sort.Strings(sortedRequiredDirs)
	for _, required := range sortedRequiredDirs {
		normalized, err := normalizePathForWorkspace(required)
		tr := judge.TestResult{Index: len(tests) + 1, Input: required, Expected: "dir exists", Actual: ""}
		if err != nil {
			tr.Passed = false
			tr.Error = "invalid required dir path"
			tests = append(tests, tr)
			continue
		}
		fullPath := filepath.Join(workspace, filepath.FromSlash(normalized))
		if stat, statErr := os.Stat(fullPath); statErr == nil && stat.IsDir() {
			tr.Passed = true
			tr.Actual = "exists"
			passed++
		} else {
			tr.Passed = false
			tr.Error = "required directory is missing"
		}
		tests = append(tests, tr)
	}

	sortedForbidden := append([]string(nil), checker.ForbiddenFiles...)
	sort.Strings(sortedForbidden)
	for _, forbidden := range sortedForbidden {
		tr := judge.TestResult{Index: len(tests) + 1, Input: forbidden, Expected: "not exists", Actual: ""}
		if checkForbiddenPathExists(workspace, forbidden, items) {
			tr.Passed = false
			tr.Error = "forbidden path detected"
		} else {
			tr.Passed = true
			tr.Actual = "not found"
			passed++
		}
		tests = append(tests, tr)
	}

	for _, command := range checker.Commands {
		cmdText := strings.TrimSpace(command.Cmd)
		if cmdText == "" {
			continue
		}
		timeoutSec := command.TimeoutSec
		if timeoutSec <= 0 {
			timeoutSec = 8
		}
		ctx, cancel := context.WithTimeout(context.Background(), time.Duration(timeoutSec)*time.Second)
		output, runErr, timedOut := runShellCommand(ctx, workspace, cmdText)
		cancel()
		tr := judge.TestResult{Index: len(tests) + 1, Input: cmdText, Expected: "exit=0", Actual: output}
		if timedOut {
			tr.Passed = false
			tr.Error = "command timeout"
		} else if runErr != nil {
			tr.Passed = false
			tr.Error = strings.TrimSpace(runErr.Error())
			if tr.Error == "" {
				tr.Error = "command failed"
			}
		} else {
			tr.Passed = true
			passed++
		}
		tests = append(tests, tr)
	}

	status := "accepted"
	runLogs := make([]string, 0)
	for _, tr := range tests {
		if tr.Passed {
			continue
		}
		if strings.TrimSpace(tr.Error) != "" {
			runLogs = append(runLogs, fmt.Sprintf("check %d (%s): %s", tr.Index, tr.Input, tr.Error))
		}
	}
	if len(runLogs) > 0 {
		status = "wrong_answer"
	}
	score := 0
	if len(tests) > 0 {
		score = int(float64(passed) / float64(len(tests)) * 100)
	}

	return judge.Result{
		Status:        status,
		Score:         score,
		CompileOutput: "",
		RunLog:        strings.Join(runLogs, "\n"),
		Tests:         tests,
	}
}

func (a *App) evaluateTaskByPolicy(taskLanguage, sourceCode string, files []submissionFilePayload, testCases []judge.TestCase, sourcePolicyRaw, solutionCode string) judge.Result {
	policy := parseTaskSourcePolicy(sourcePolicyRaw)
	checkerType := strings.ToLower(strings.TrimSpace(policy.CheckerType))

	source := sourceCode
	if strings.TrimSpace(source) == "" {
		source = firstNonEmptySourceFromFiles(files)
	}

	switch checkerType {
	case "python_stdout":
		var checker checkerPythonStdout
		if err := json.Unmarshal(policy.Checker, &checker); err == nil {
			checkerTests := buildJudgeTestsFromPythonStdout(checker)
			if len(checkerTests) > 0 {
				return a.evalTask("python", source, checkerTests)
			}
		}
		if len(testCases) > 0 {
			return a.evalTask("python", source, testCases)
		}
	case "sql_query":
		var checker checkerSQLQuery
		if err := json.Unmarshal(policy.Checker, &checker); err == nil {
			checkerTests := buildJudgeTestsFromSQLChecker(checker, solutionCode)
			if len(checkerTests) > 0 {
				return a.evalTask("sql", source, checkerTests)
			}
		}
		if len(testCases) > 0 {
			return a.evalTask("sql", source, testCases)
		}
	case "python_pytest":
		return a.evaluatePythonPytestChecker(source, files, policy.Checker)
	case "http_api":
		return a.evaluateHTTPAPIChecker(source, files, policy.Checker)
	case "ide_plugin":
		return a.evaluateIDEPluginChecker(source, files, policy.Checker)
	}

	if len(testCases) == 0 {
		return judge.Result{Status: "failed", CompileOutput: "no test cases configured", RunLog: "task has no executable tests"}
	}
	return a.evalTask(taskLanguage, source, testCases)
}
