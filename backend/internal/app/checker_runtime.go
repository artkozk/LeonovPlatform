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

const (
	checkerDockerImage  = "python:3.12-alpine"
	checkerDockerRunLog = "docker sandbox is required for checker execution"
)

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
		Method             string            `json:"method"`
		Path               string            `json:"path"`
		Headers            map[string]string `json:"headers"`
		JSON               interface{}       `json:"json"`
		ExpectedStatus     int               `json:"expected_status"`
		ExpectedJSON       interface{}       `json:"expected_json"`
		ExpectedJSONSubset interface{}       `json:"expected_json_subset"`
		ExpectedJSONType   string            `json:"expected_json_type"`
		Visibility         string            `json:"visibility"`
	} `json:"tests"`
}

type checkerIDEPlugin struct {
	Type           string   `json:"type"`
	TimeoutSec     int      `json:"timeout_sec"`
	RequiredFiles  []string `json:"required_files"`
	RequiredDirs   []string `json:"required_dirs"`
	ForbiddenFiles []string `json:"forbidden_files"`
	Commands       []struct {
		Cmd            string `json:"cmd"`
		TimeoutSec     int    `json:"timeout_sec"`
		Stdin          string `json:"stdin"`
		ExpectStdout   string `json:"expect_stdout"`
		ExpectExitCode *int   `json:"expect_exit_code"`
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
	if hasWindowsDrivePrefix(candidate) {
		return "", errors.New("absolute volume path is not allowed")
	}
	cleaned := filepath.ToSlash(filepath.Clean(candidate))
	if vol := filepath.VolumeName(cleaned); vol != "" {
		return "", errors.New("absolute volume path is not allowed")
	}
	if hasWindowsDrivePrefix(cleaned) {
		return "", errors.New("absolute volume path is not allowed")
	}
	if strings.HasPrefix(cleaned, "../") || cleaned == ".." {
		return "", errors.New("path escapes workspace")
	}
	if strings.HasPrefix(cleaned, "/") {
		return "", errors.New("absolute path is not allowed")
	}
	return cleaned, nil
}

func hasWindowsDrivePrefix(path string) bool {
	if len(path) < 2 {
		return false
	}
	first := path[0]
	if !((first >= 'a' && first <= 'z') || (first >= 'A' && first <= 'Z')) {
		return false
	}
	return path[1] == ':'
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
	return runShellCommandWithStdin(ctx, workdir, command, "")
}

func runShellCommandWithStdin(ctx context.Context, workdir, command string, stdin string) (string, error, bool) {
	if runtime.GOOS == "windows" {
		return runCommandWithTimeout(ctx, "cmd", []string{"/C", command}, workdir, stdin)
	}
	return runCommandWithTimeout(ctx, "bash", []string{"-lc", command}, workdir, stdin)
}

func checkerDockerUnavailableResult(runLog string) judge.Result {
	if strings.TrimSpace(runLog) == "" {
		runLog = checkerDockerRunLog
	}
	return judge.Result{
		Status:        "failed",
		CompileOutput: "docker is not available",
		RunLog:        runLog,
		Tests:         []judge.TestResult{},
	}
}

func runDockerCommandWithTimeout(ctx context.Context, workspace, image string, command []string, env map[string]string) (string, error, bool) {
	workspaceMount := filepath.ToSlash(workspace) + ":/workspace"
	args := []string{
		"run",
		"--rm",
		"--network", "none",
		"--memory", "256m",
		"--cpus", "1.0",
		"--pids-limit", "128",
		"--read-only",
		"--tmpfs", "/tmp:size=64m",
		"-v", workspaceMount,
		"-w", "/workspace",
	}
	for key, val := range env {
		args = append(args, "-e", key+"="+val)
	}
	args = append(args, image)
	args = append(args, command...)

	cmd := exec.CommandContext(ctx, "docker", args...)
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

func normalizeCommandForAllowlist(raw string) string {
	parts := strings.Fields(strings.ToLower(strings.TrimSpace(raw)))
	return strings.Join(parts, " ")
}

func containsDangerousShellTokens(command string) bool {
	lower := strings.ToLower(strings.TrimSpace(command))
	if lower == "" {
		return true
	}
	for _, token := range []string{"&&", "||", "&", "|", ";", "`", "$(", ">", "<", "\n", "\r"} {
		if strings.Contains(lower, token) {
			return true
		}
	}
	return false
}

func isSimplePythonOrPytestCommand(command string) bool {
	lower := strings.ToLower(strings.TrimSpace(command))
	if lower == "" || containsDangerousShellTokens(lower) {
		return false
	}
	return strings.HasPrefix(lower, "python ") ||
		strings.HasPrefix(lower, "python3 ") ||
		strings.HasPrefix(lower, "python -m pytest") ||
		strings.HasPrefix(lower, "python3 -m pytest") ||
		strings.HasPrefix(lower, "pytest")
}

func isSafePrintfPipeToPython(command string) bool {
	lower := strings.ToLower(strings.TrimSpace(command))
	if lower == "" {
		return false
	}
	if strings.Count(lower, "|") != 1 {
		return false
	}
	parts := strings.SplitN(lower, "|", 2)
	left := strings.TrimSpace(parts[0])
	right := strings.TrimSpace(parts[1])
	if !strings.HasPrefix(left, "printf ") {
		return false
	}
	if strings.Contains(left, "&&") || strings.Contains(left, "||") || strings.Contains(left, ";") || strings.Contains(left, "`") || strings.Contains(left, "$(") {
		return false
	}
	return isSimplePythonOrPytestCommand(right)
}

func isSafeReadOnlyIDECheckerCommand(command string) bool {
	trimmed := strings.TrimSpace(command)
	if trimmed == "" {
		return false
	}
	lower := strings.ToLower(trimmed)
	if strings.Contains(lower, "&&") ||
		strings.Contains(lower, "||") ||
		strings.Contains(lower, ";") ||
		strings.Contains(lower, "`") ||
		strings.Contains(lower, "$(") ||
		strings.Contains(lower, "\n") ||
		strings.Contains(lower, "\r") ||
		strings.Contains(lower, ">") ||
		strings.Contains(lower, "<") {
		return false
	}

	fields := strings.Fields(trimmed)
	if len(fields) == 3 && fields[0] == "test" && fields[1] == "-s" {
		_, err := normalizePathForWorkspace(fields[2])
		return err == nil
	}

	if !strings.HasPrefix(lower, "grep -e ") {
		return false
	}
	_, target, ok := splitSafeGrepECommand(trimmed)
	if !ok {
		return false
	}
	_, err := normalizePathForWorkspace(target)
	return err == nil
}

func splitSafeGrepECommand(command string) (string, string, bool) {
	rest := strings.TrimSpace(command)
	fields := strings.Fields(rest)
	if len(fields) < 4 || fields[0] != "grep" || !strings.EqualFold(fields[1], "-E") {
		return "", "", false
	}
	rest = strings.TrimSpace(strings.TrimPrefix(rest, "grep"))
	rest = strings.TrimSpace(strings.TrimPrefix(rest, "-E"))
	if rest == "" {
		return "", "", false
	}

	var pattern string
	switch rest[0] {
	case '"', '\'':
		quote := rest[0]
		end := strings.IndexByte(rest[1:], quote)
		if end < 0 {
			return "", "", false
		}
		pattern = rest[1 : end+1]
		rest = strings.TrimSpace(rest[end+2:])
	default:
		parts := strings.Fields(rest)
		if len(parts) != 2 {
			return "", "", false
		}
		pattern = parts[0]
		rest = parts[1]
	}

	if strings.TrimSpace(pattern) == "" || len([]rune(pattern)) > 512 {
		return "", "", false
	}
	if strings.ContainsAny(pattern, "&;`<>") || strings.Contains(pattern, "$(") {
		return "", "", false
	}
	targetFields := strings.Fields(rest)
	if len(targetFields) != 1 {
		return "", "", false
	}
	return pattern, targetFields[0], true
}

func (a *App) ideCheckerCommandAllowedInProduction(command string) bool {
	normalized := normalizeCommandForAllowlist(command)
	if normalized == "" {
		return false
	}

	if isSafeReadOnlyIDECheckerCommand(command) {
		return true
	}

	allowlistRaw := strings.TrimSpace(a.Cfg.IDECheckerAllowedCommands)
	allowed := make(map[string]struct{})
	if allowlistRaw != "" {
		for _, chunk := range strings.FieldsFunc(allowlistRaw, func(r rune) bool {
			return r == ',' || r == '\n' || r == ';'
		}) {
			entry := normalizeCommandForAllowlist(chunk)
			if entry != "" {
				allowed[entry] = struct{}{}
			}
		}
		_, ok := allowed[normalized]
		return ok
	}

	for _, entry := range []string{"python -m pytest", "python3 -m pytest", "pytest"} {
		allowed[normalizeCommandForAllowlist(entry)] = struct{}{}
	}
	if _, ok := allowed[normalized]; ok {
		return true
	}

	if isSimplePythonOrPytestCommand(command) {
		return true
	}
	if isSafePrintfPipeToPython(command) {
		return true
	}
	return false
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
	if policy.CheckerType == "python_pytest" {
		var checker checkerPythonPytest
		if err := json.Unmarshal(policy.Checker, &checker); err == nil {
			for _, file := range checker.RequiredFiles {
				if strings.TrimSpace(file) != "" {
					return file
				}
			}
			if pythonPytestImportsModule(checker.PytestCode, "solution") {
				return "solution.py"
			}
		}
	} else {
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
	}
	return defaultPath
}

func pythonPytestImportsModule(testCode, moduleName string) bool {
	module := strings.TrimSpace(moduleName)
	if module == "" {
		return false
	}
	for _, rawLine := range strings.Split(testCode, "\n") {
		line := strings.TrimSpace(rawLine)
		if strings.HasPrefix(line, "from "+module+" import ") {
			return true
		}
		if !strings.HasPrefix(line, "import ") {
			continue
		}
		imports := strings.TrimSpace(strings.TrimPrefix(line, "import "))
		for _, part := range strings.Split(imports, ",") {
			fields := strings.Fields(strings.TrimSpace(part))
			if len(fields) > 0 && fields[0] == module {
				return true
			}
		}
	}
	return false
}

func ensurePythonModuleFile(workspace, moduleName, sourceCode string) error {
	source := strings.TrimSpace(sourceCode)
	if source == "" {
		return nil
	}
	module := strings.TrimSpace(moduleName)
	if module == "" || strings.ContainsAny(module, `/\.`) {
		return nil
	}
	path := module + ".py"
	normalized, err := normalizePathForWorkspace(path)
	if err != nil {
		return err
	}
	fullPath := filepath.Join(workspace, filepath.FromSlash(normalized))
	if _, statErr := os.Stat(fullPath); statErr == nil {
		return nil
	}
	if err := os.MkdirAll(filepath.Dir(fullPath), 0o755); err != nil {
		return err
	}
	return os.WriteFile(fullPath, []byte(sourceCode), 0o644)
}

func inferTemplateFilesFromSourcePolicy(sourcePolicyRaw, language string) []string {
	mainPath := inferMainFilePathFromSourcePolicy(sourcePolicyRaw, language)
	files := []string{mainPath}
	seen := map[string]struct{}{}
	seen[mainPath] = struct{}{}

	policy := parseTaskSourcePolicy(sourcePolicyRaw)
	if policy.CheckerType != "ide_plugin" || len(policy.Checker) == 0 {
		return files
	}
	var checker struct {
		RequiredFiles []string `json:"required_files"`
	}
	if err := json.Unmarshal(policy.Checker, &checker); err != nil {
		return files
	}
	for _, raw := range checker.RequiredFiles {
		normalized, err := normalizePathForWorkspace(raw)
		if err != nil || strings.TrimSpace(normalized) == "" {
			continue
		}
		if _, ok := seen[normalized]; ok {
			continue
		}
		files = append(files, normalized)
		seen[normalized] = struct{}{}
	}
	return files
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
	if _, err := exec.LookPath("docker"); err != nil {
		return checkerDockerUnavailableResult(checkerDockerRunLog)
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
	if pythonPytestImportsModule(checker.PytestCode, "solution") {
		if err := ensurePythonModuleFile(workspace, "solution", sourceCode); err != nil {
			return judge.Result{Status: "failed", CompileOutput: err.Error(), RunLog: "failed to prepare solution module"}
		}
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

	output, runErr, timedOut := runDockerCommandWithTimeout(ctx, workspace, checkerDockerImage, []string{"python3", "__lc_runner.py"}, nil)
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
	if _, err := exec.LookPath("docker"); err != nil {
		return checkerDockerUnavailableResult(checkerDockerRunLog)
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
	entryConfigBytes, err := json.Marshal(map[string]string{"entryFile": entryFile})
	if err != nil {
		return judge.Result{Status: "failed", CompileOutput: err.Error(), RunLog: "unable to serialize entry file"}
	}
	if err := os.WriteFile(filepath.Join(workspace, "__lc_http_entry.json"), entryConfigBytes, 0o644); err != nil {
		return judge.Result{Status: "failed", CompileOutput: err.Error(), RunLog: "unable to write entry metadata"}
	}

	runnerScript := `import asyncio
import importlib.util
import inspect
import json
import pathlib
import sys
import traceback
import types
from typing import Union, get_args, get_origin
from urllib.parse import parse_qs, unquote, urlsplit

class RequestValidationError(Exception):
    pass

class HTTPException(Exception):
    def __init__(self, status_code=500, detail=None):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail

class Response:
    def __init__(self, content=None, status_code=200):
        self.content = content
        self.status_code = status_code

class _Status:
    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_202_ACCEPTED = 202
    HTTP_204_NO_CONTENT = 204
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_409_CONFLICT = 409
    HTTP_422_UNPROCESSABLE_ENTITY = 422
    HTTP_500_INTERNAL_SERVER_ERROR = 500

status = _Status()

def clean_path(value):
    text = str(value or "")
    if text == "":
        return ""
    if not text.startswith("/"):
        text = "/" + text
    if len(text) > 1 and text.endswith("/"):
        text = text[:-1]
    return text

def join_paths(*parts):
    out = ""
    for part in parts:
        piece = str(part or "")
        if piece == "":
            continue
        if out.endswith("/") and piece.startswith("/"):
            out += piece[1:]
        elif not out.endswith("/") and not piece.startswith("/"):
            out += "/" + piece
        else:
            out += piece
    return clean_path(out) or "/"

class FastAPI:
    def __init__(self, **_kwargs):
        self._routes = []
        self.prefix = clean_path(_kwargs.get("prefix", ""))
    def _route(self, method, path, **kwargs):
        def decorator(func):
            self._routes.append({
                "method": method.upper(),
                "path": clean_path(path) or "/",
                "func": func,
                "status_code": int(kwargs.get("status_code", 200) or 200),
            })
            return func
        return decorator
    def get(self, path, **kwargs):
        return self._route("GET", path, **kwargs)
    def post(self, path, **kwargs):
        return self._route("POST", path, **kwargs)
    def put(self, path, **kwargs):
        return self._route("PUT", path, **kwargs)
    def delete(self, path, **kwargs):
        return self._route("DELETE", path, **kwargs)
    def patch(self, path, **kwargs):
        return self._route("PATCH", path, **kwargs)
    def include_router(self, router, prefix="", **_kwargs):
        base = join_paths(prefix, getattr(router, "prefix", ""))
        for route in getattr(router, "_routes", []):
            self._routes.append({
                "method": route.get("method", "GET"),
                "path": join_paths(base, route.get("path", "")),
                "func": route.get("func"),
                "status_code": int(route.get("status_code", 200) or 200),
            })

class APIRouter(FastAPI):
    def __init__(self, prefix="", **kwargs):
        super().__init__(prefix=prefix, **kwargs)

class _Depends:
    def __init__(self, dependency=None):
        self.dependency = dependency

def Depends(value=None):
    return _Depends(value)

def Query(default=None, **_kwargs):
    return default

def Path(default=None, **_kwargs):
    return default

def Body(default=None, **_kwargs):
    return default

class _Missing:
    pass

MISSING = _Missing()

class FieldInfo:
    def __init__(self, default=MISSING, **kwargs):
        self.default = default
        self.kwargs = kwargs

def Field(default=MISSING, **kwargs):
    return FieldInfo(default, **kwargs)

class BaseModel:
    def __init__(self, **data):
        annotations = getattr(self.__class__, "__annotations__", {})
        for name, annotation in annotations.items():
            field_cfg = getattr(self.__class__, name, MISSING)
            if name in data:
                value = data[name]
            elif isinstance(field_cfg, FieldInfo):
                if field_cfg.default is MISSING:
                    raise RequestValidationError(f"missing field {name}")
                value = field_cfg.default
            elif field_cfg is not MISSING:
                value = field_cfg
            else:
                raise RequestValidationError(f"missing field {name}")
            value = convert_value(value, annotation)
            validate_field_constraints(name, value, field_cfg)
            setattr(self, name, value)
        for name, value in data.items():
            if name not in annotations:
                setattr(self, name, value)
    def model_dump(self):
        return dict(self.__dict__)
    def dict(self):
        return self.model_dump()

def is_basemodel_type(annotation):
    try:
        return inspect.isclass(annotation) and issubclass(annotation, BaseModel)
    except TypeError:
        return False

def basemodel_type_from_annotation(annotation):
    if is_basemodel_type(annotation):
        return annotation
    origin = get_origin(annotation)
    if origin in (Union, getattr(types, "UnionType", None)):
        for item in get_args(annotation):
            if is_basemodel_type(item):
                return item
    return None

def convert_value(value, annotation):
    if annotation is inspect._empty or annotation is None:
        return value
    if isinstance(annotation, str):
        return value
    origin = get_origin(annotation)
    if origin in (Union, getattr(types, "UnionType", None)):
        last_error = None
        for item in get_args(annotation):
            if item is type(None) and value is None:
                return None
            if item is type(None):
                continue
            try:
                return convert_value(value, item)
            except RequestValidationError as exc:
                last_error = exc
        if last_error is not None:
            raise last_error
        return value
    if origin in (list, tuple, set):
        if origin is list and not isinstance(value, list):
            raise RequestValidationError(f"invalid list value {value!r}")
        if origin is tuple and not isinstance(value, tuple):
            raise RequestValidationError(f"invalid tuple value {value!r}")
        if origin is set and not isinstance(value, set):
            raise RequestValidationError(f"invalid set value {value!r}")
        args = get_args(annotation)
        if origin is list and args:
            return [convert_value(item, args[0]) for item in value]
        return value
    if annotation is str:
        return str(value)
    if annotation is int:
        try:
            return int(value)
        except (TypeError, ValueError):
            raise RequestValidationError(f"invalid int value {value!r}")
    if annotation is float:
        try:
            return float(value)
        except (TypeError, ValueError):
            raise RequestValidationError(f"invalid float value {value!r}")
    if annotation is bool:
        if isinstance(value, bool):
            return value
        text = str(value).lower()
        if text in ("true", "1", "yes", "on"):
            return True
        if text in ("false", "0", "no", "off"):
            return False
        raise RequestValidationError(f"invalid bool value {value!r}")
    return value

def validate_field_constraints(name, value, field_cfg):
    if not isinstance(field_cfg, FieldInfo):
        return
    opts = field_cfg.kwargs
    if "min_length" in opts and value is not None and len(value) < int(opts["min_length"]):
        raise RequestValidationError(f"{name} is too short")
    if "ge" in opts and value < opts["ge"]:
        raise RequestValidationError(f"{name} is too small")
    if "le" in opts and value > opts["le"]:
        raise RequestValidationError(f"{name} is too large")

fastapi_mod = types.ModuleType("fastapi")
fastapi_mod.FastAPI = FastAPI
fastapi_mod.APIRouter = APIRouter
fastapi_mod.HTTPException = HTTPException
fastapi_mod.Response = Response
fastapi_mod.Depends = Depends
fastapi_mod.Query = Query
fastapi_mod.Path = Path
fastapi_mod.Body = Body
fastapi_mod.status = status
sys.modules["fastapi"] = fastapi_mod

pydantic_mod = types.ModuleType("pydantic")
pydantic_mod.BaseModel = BaseModel
pydantic_mod.Field = Field
sys.modules["pydantic"] = pydantic_mod

result = {"status": "accepted", "compile_output": "", "run_log": "", "tests": []}

with open("__lc_http_entry.json", "r", encoding="utf-8") as f:
    entry_cfg = json.load(f)
entry_file = pathlib.Path(str(entry_cfg.get("entryFile", "main.py")))
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
    if isinstance(value, Response):
        return {} if value.content is None else value.content
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    return value

def split_request_path(raw_path):
    parsed = urlsplit(str(raw_path or ""))
    request_path = clean_path(parsed.path or "/")
    query = {key: values[-1] for key, values in parse_qs(parsed.query, keep_blank_values=True).items()}
    return request_path, query

def match_route_path(route_path, request_path):
    route_parts = [part for part in clean_path(route_path).split("/") if part]
    request_parts = [part for part in clean_path(request_path).split("/") if part]
    if len(route_parts) != len(request_parts):
        return None
    params = {}
    for route_part, request_part in zip(route_parts, request_parts):
        if route_part.startswith("{") and route_part.endswith("}"):
            params[route_part[1:-1]] = unquote(request_part)
            continue
        if route_part != request_part:
            return None
    return params

def resolve_dependency(default):
    dependency = default.dependency
    if dependency is None:
        return None
    if callable(dependency):
        return dependency()
    return dependency

def build_call_kwargs(fn, path_params, query_params, payload):
    kwargs = {}
    sig = inspect.signature(fn)
    for name, param in sig.parameters.items():
        annotation = param.annotation
        default = param.default
        model_type = basemodel_type_from_annotation(annotation)
        if name in path_params:
            kwargs[name] = convert_value(path_params[name], annotation)
            continue
        elif name in query_params:
            kwargs[name] = convert_value(query_params[name], annotation)
            continue
        elif isinstance(default, _Depends):
            kwargs[name] = resolve_dependency(default)
            continue
        elif isinstance(payload, dict) and model_type is not None:
            kwargs[name] = model_type(**payload)
            continue
        elif isinstance(payload, dict) and name in payload:
            kwargs[name] = convert_value(payload[name], annotation)
            continue
        elif default is not inspect._empty:
            kwargs[name] = default
            continue
        elif model_type is not None:
            kwargs[name] = model_type(**(payload if isinstance(payload, dict) else {}))
            continue
        else:
            raise RequestValidationError(f"missing parameter {name}")
    return kwargs

def subset_match(actual, expected):
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return False
        for key, expected_value in expected.items():
            if key not in actual or not subset_match(actual[key], expected_value):
                return False
        return True
    if isinstance(expected, list):
        return actual == expected
    return actual == expected

def json_type_matches(actual, expected_type):
    kind = str(expected_type or "").lower()
    if kind in ("array", "list"):
        return isinstance(actual, list)
    if kind in ("object", "dict"):
        return isinstance(actual, dict)
    if kind in ("string", "str"):
        return isinstance(actual, str)
    if kind in ("number", "int", "float"):
        return isinstance(actual, (int, float)) and not isinstance(actual, bool)
    if kind in ("boolean", "bool"):
        return isinstance(actual, bool)
    if kind in ("null", "none"):
        return actual is None
    return True

for test in checks:
    method = str(test.get("method", "GET")).upper()
    path = str(test.get("path", ""))
    request_path, query_params = split_request_path(path)
    expected_status = int(test.get("expected_status", 200) or 200)
    expected_json = test.get("expected_json")
    expected_json_subset = test.get("expected_json_subset")
    expected_json_type = test.get("expected_json_type")

    route = None
    path_params = {}
    for candidate in app._routes:
        if str(candidate.get("method", "")).upper() != method:
            continue
        matched_params = match_route_path(candidate.get("path", ""), request_path)
        if matched_params is not None:
            route = candidate
            path_params = matched_params
            break
    item = {"name": f"{method} {path}", "passed": True, "error": "", "actual": ""}

    if route is None:
        path_exists = any(match_route_path(candidate.get("path", ""), request_path) is not None for candidate in app._routes)
        actual_status = 405 if path_exists else 404
        item["actual"] = json.dumps({"detail": "method not allowed" if path_exists else "not found"}, ensure_ascii=False)
        if actual_status != expected_status:
            item["passed"] = False
            item["error"] = "method not allowed" if path_exists else "route not found"
            result["status"] = "wrong_answer"
        result["tests"].append(item)
        continue

    fn = route.get("func")
    try:
        payload = test.get("json")
        kwargs = build_call_kwargs(fn, path_params, query_params, payload)
        response = fn(**kwargs)

        if inspect.isawaitable(response):
            response = asyncio.run(response)

        status_code = int(route.get("status_code", 200) or 200)
        body = response
        if isinstance(response, Response):
            status_code = response.status_code
            body = response.content
        if isinstance(response, tuple) and len(response) == 2 and isinstance(response[1], int):
            body = response[0]
            status_code = response[1]

        normalized_body = normalize_payload(body)
        item["actual"] = json.dumps(normalized_body, ensure_ascii=False)

        if status_code != expected_status:
            item["passed"] = False
            item["error"] = f"expected status {expected_status}, got {status_code}"
        elif expected_json_type and not json_type_matches(normalized_body, expected_json_type):
            item["passed"] = False
            item["error"] = f"expected json type {expected_json_type}, got {type(normalized_body).__name__}"
        elif expected_json_subset is not None and not subset_match(normalized_body, expected_json_subset):
            item["passed"] = False
            item["error"] = f"expected json subset {expected_json_subset}, got {normalized_body}"
        elif expected_json is not None and isinstance(expected_json, dict) and not subset_match(normalized_body, expected_json):
            item["passed"] = False
            item["error"] = f"expected json subset {expected_json}, got {normalized_body}"
        elif expected_json is not None and not isinstance(expected_json, dict) and normalized_body != expected_json:
            item["passed"] = False
            item["error"] = f"expected json {expected_json}, got {normalized_body}"

        if not item["passed"] and result["status"] == "accepted":
            result["status"] = "wrong_answer"

    except HTTPException as exc:
        status_code = int(getattr(exc, "status_code", 500) or 500)
        normalized_body = {"detail": getattr(exc, "detail", None)}
        item["actual"] = json.dumps(normalized_body, ensure_ascii=False)
        if status_code != expected_status:
            item["passed"] = False
            item["error"] = f"expected status {expected_status}, got {status_code}"
        elif expected_json_subset is not None and not subset_match(normalized_body, expected_json_subset):
            item["passed"] = False
            item["error"] = f"expected json subset {expected_json_subset}, got {normalized_body}"
        elif expected_json is not None and isinstance(expected_json, dict) and not subset_match(normalized_body, expected_json):
            item["passed"] = False
            item["error"] = f"expected json subset {expected_json}, got {normalized_body}"
        elif expected_json is not None and not isinstance(expected_json, dict) and normalized_body != expected_json:
            item["passed"] = False
            item["error"] = f"expected json {expected_json}, got {normalized_body}"
        if not item["passed"] and result["status"] == "accepted":
            result["status"] = "wrong_answer"
    except RequestValidationError as exc:
        status_code = 422
        normalized_body = {"detail": str(exc) or "validation error"}
        item["actual"] = json.dumps(normalized_body, ensure_ascii=False)
        if status_code != expected_status:
            item["passed"] = False
            item["error"] = f"expected status {expected_status}, got {status_code}"
        if not item["passed"] and result["status"] == "accepted":
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

	output, runErr, timedOut := runDockerCommandWithTimeout(ctx, workspace, checkerDockerImage, []string{"python3", "__lc_http_runner.py"}, nil)
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
		if strings.EqualFold(strings.TrimSpace(a.Cfg.Environment), "production") && !a.ideCheckerCommandAllowedInProduction(cmdText) {
			tr := judge.TestResult{
				Index:    len(tests) + 1,
				Input:    cmdText,
				Expected: "allowlisted command",
				Actual:   "",
				Passed:   false,
				Error:    "command is blocked in production (not in IDE checker allowlist)",
			}
			tests = append(tests, tr)
			continue
		}
		timeoutSec := command.TimeoutSec
		if timeoutSec <= 0 {
			timeoutSec = 8
		}
		ctx, cancel := context.WithTimeout(context.Background(), time.Duration(timeoutSec)*time.Second)
		stdin := command.Stdin
		output, runErr, timedOut := runShellCommandWithStdin(ctx, workspace, cmdText, stdin)
		cancel()
		tr := judge.TestResult{Index: len(tests) + 1, Input: cmdText, Expected: "exit=0", Actual: output}
		if timedOut {
			tr.Passed = false
			tr.Error = "command timeout"
		} else if runErr != nil {
			expectedExitCode := 0
			if command.ExpectExitCode != nil {
				expectedExitCode = *command.ExpectExitCode
			}
			if exitErr, ok := runErr.(*exec.ExitError); ok && exitErr.ExitCode() == expectedExitCode {
				tr.Passed = true
				passed++
			} else {
				tr.Passed = false
				tr.Error = strings.TrimSpace(runErr.Error())
				if tr.Error == "" {
					tr.Error = "command failed"
				}
			}
		} else {
			tr.Passed = true
			passed++
		}
		if tr.Passed && strings.TrimSpace(command.ExpectStdout) != "" {
			expected := normalizeOutput(command.ExpectStdout)
			actual := normalizeOutput(output)
			if expected != actual {
				if tr.Passed {
					passed--
				}
				tr.Passed = false
				tr.Error = "stdout does not match expected output"
				tr.Expected = expected
				tr.Actual = actual
			}
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
	if violation, err := evaluateTaskSourcePolicy(sourcePolicyRaw, taskLanguage, source); err != nil {
		return judge.Result{
			Status:        "failed",
			CompileOutput: err.Error(),
			RunLog:        "source policy evaluation failed",
			Tests:         []judge.TestResult{},
		}
	} else if violation != "" {
		return sourcePolicyViolationResult(violation)
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
