package judge

import (
	"bytes"
	"context"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

type TestCase struct {
	Input    string `json:"input"`
	Expected string `json:"expected"`
}

type TestResult struct {
	Index    int    `json:"index"`
	Passed   bool   `json:"passed"`
	Input    string `json:"input"`
	Expected string `json:"expected"`
	Actual   string `json:"actual"`
	Error    string `json:"error,omitempty"`
}

type Result struct {
	Status        string       `json:"status"`
	Score         int          `json:"score"`
	CompileOutput string       `json:"compileOutput"`
	RunLog        string       `json:"runLog"`
	Tests         []TestResult `json:"tests"`
}

type Engine interface {
	EvaluateJava(source string, testCases []TestCase) Result
	EvaluatePython(source string, testCases []TestCase) Result
	EvaluateSQL(source string, testCases []TestCase) Result
}

type javaEngine struct {
	timeout time.Duration
	mode    string
}

const sourceEquivalencePrefix = "__SOURCE_EQ__\n"

func NewJavaEngine(timeoutSeconds int, mode string) Engine {
	if timeoutSeconds <= 0 {
		timeoutSeconds = 4
	}
	mode = strings.ToLower(strings.TrimSpace(mode))
	if mode == "" {
		mode = "local"
	}
	return &javaEngine{timeout: time.Duration(timeoutSeconds) * time.Second, mode: mode}
}

func (j *javaEngine) EvaluateJava(source string, testCases []TestCase) Result {
	if j.mode == "docker" {
		if _, err := exec.LookPath("docker"); err != nil {
			return j.evaluateLocal(source, testCases)
		}
		return j.evaluateDocker(source, testCases)
	}
	if j.mode == "auto" {
		if _, err := exec.LookPath("docker"); err == nil {
			return j.evaluateDocker(source, testCases)
		}
	}
	return j.evaluateLocal(source, testCases)
}

func (j *javaEngine) EvaluatePython(source string, testCases []TestCase) Result {
	if j.mode == "docker" {
		if _, err := exec.LookPath("docker"); err != nil {
			return j.evaluatePythonLocal(source, testCases)
		}
		return j.evaluatePythonDocker(source, testCases)
	}
	if j.mode == "auto" {
		if _, err := exec.LookPath("docker"); err == nil {
			return j.evaluatePythonDocker(source, testCases)
		}
	}
	return j.evaluatePythonLocal(source, testCases)
}

func normalizeComparableSQL(s string) string {
	text := strings.ReplaceAll(s, "\r", "\n")
	lines := strings.Split(text, "\n")
	clean := make([]string, 0, len(lines))
	for _, line := range lines {
		cut := line
		if idx := strings.Index(cut, "--"); idx >= 0 {
			cut = cut[:idx]
		}
		clean = append(clean, cut)
	}

	joined := strings.Join(clean, "\n")
	joined = strings.ReplaceAll(joined, "/*", " ")
	joined = strings.ReplaceAll(joined, "*/", " ")
	joined = strings.ReplaceAll(joined, ";", " ")
	parts := strings.Fields(strings.ToLower(strings.TrimSpace(joined)))
	return strings.Join(parts, " ")
}

func normalizeComparableSourceCode(s string) string {
	text := strings.ReplaceAll(s, "\r", "\n")
	lines := strings.Split(text, "\n")
	clean := make([]string, 0, len(lines))
	for _, line := range lines {
		trimmed := strings.TrimSpace(line)
		if strings.HasPrefix(trimmed, "#") || strings.HasPrefix(trimmed, "//") {
			continue
		}
		clean = append(clean, line)
	}
	parts := strings.Fields(strings.TrimSpace(strings.Join(clean, "\n")))
	return strings.Join(parts, " ")
}

func (j *javaEngine) EvaluateSQL(source string, testCases []TestCase) Result {
	if len(testCases) == 0 {
		return Result{
			Status:        "failed",
			CompileOutput: "no sql tests configured",
			RunLog:        "task has no sql reference query",
			Tests:         []TestResult{},
		}
	}

	actualNorm := normalizeComparableSQL(source)
	results := make([]TestResult, 0, len(testCases))
	passed := 0
	runLogs := make([]string, 0, len(testCases))

	for i, tc := range testCases {
		expectedNorm := normalizeComparableSQL(tc.Expected)
		tr := TestResult{
			Index:    i + 1,
			Input:    tc.Input,
			Expected: strings.TrimSpace(tc.Expected),
			Actual:   strings.TrimSpace(source),
		}
		tr.Passed = actualNorm == expectedNorm && expectedNorm != ""
		if tr.Passed {
			passed++
		} else {
			runLogs = append(runLogs, fmt.Sprintf("test %d: SQL query does not match reference", i+1))
		}
		results = append(results, tr)
	}

	score := int(float64(passed) / float64(len(testCases)) * 100)
	status := classifyTestStatus(testCases, results, passed)

	return Result{
		Status:        status,
		Score:         score,
		CompileOutput: "",
		RunLog:        strings.Join(runLogs, "\n"),
		Tests:         results,
	}
}

func (j *javaEngine) evaluateLocal(source string, testCases []TestCase) Result {
	workspace, err := os.MkdirTemp("", "lc-java-judge-*")
	if err != nil {
		return Result{Status: "failed", CompileOutput: err.Error(), RunLog: "unable to create workspace"}
	}
	defer os.RemoveAll(workspace)

	mainPath := filepath.Join(workspace, "Main.java")
	if err := os.WriteFile(mainPath, []byte(source), 0o644); err != nil {
		return Result{Status: "failed", CompileOutput: err.Error(), RunLog: "unable to write source"}
	}

	compileCtx, cancelCompile := context.WithTimeout(context.Background(), j.timeout)
	defer cancelCompile()

	compileCmd := exec.CommandContext(compileCtx, "javac", "Main.java")
	compileCmd.Dir = workspace
	compileOut, compileErr := compileCmd.CombinedOutput()
	if compileCtx.Err() == context.DeadlineExceeded {
		return Result{Status: "compile_error", CompileOutput: "Compilation timeout", RunLog: "javac timeout"}
	}
	if compileErr != nil {
		return Result{Status: "compile_error", CompileOutput: string(compileOut), RunLog: "Compilation failed"}
	}

	results := make([]TestResult, 0, len(testCases))
	passed := 0
	var runLogs []string

	for i, tc := range testCases {
		runCtx, cancelRun := context.WithTimeout(context.Background(), j.timeout)
		runCmd := exec.CommandContext(runCtx, "java", "Main")
		runCmd.Dir = workspace
		runCmd.Stdin = strings.NewReader(tc.Input)

		var stdout bytes.Buffer
		var stderr bytes.Buffer
		runCmd.Stdout = &stdout
		runCmd.Stderr = &stderr

		err := runCmd.Run()
		cancelRun()

		actual := strings.TrimSpace(stdout.String())
		expected := strings.TrimSpace(tc.Expected)
		tr := TestResult{Index: i + 1, Input: tc.Input, Expected: expected, Actual: actual}

		if runCtx.Err() == context.DeadlineExceeded {
			tr.Passed = false
			tr.Error = "Time limit exceeded"
			runLogs = append(runLogs, fmt.Sprintf("test %d: time limit exceeded", i+1))
			results = append(results, tr)
			continue
		}
		if err != nil {
			tr.Passed = false
			tr.Error = strings.TrimSpace(stderr.String())
			runLogs = append(runLogs, fmt.Sprintf("test %d: runtime error %s", i+1, tr.Error))
			results = append(results, tr)
			continue
		}

		tr.Passed = isEquivalentOutput(actual, expected)
		if tr.Passed {
			passed++
		} else {
			runLogs = append(runLogs, fmt.Sprintf("test %d: expected '%s', got '%s'", i+1, expected, actual))
		}
		results = append(results, tr)
	}

	score := 0
	if len(testCases) > 0 {
		score = int(float64(passed) / float64(len(testCases)) * 100)
	}
	status := classifyTestStatus(testCases, results, passed)

	return Result{
		Status:        status,
		Score:         score,
		CompileOutput: string(compileOut),
		RunLog:        strings.Join(runLogs, "\n"),
		Tests:         results,
	}
}

func detectPythonBinary() (string, error) {
	return detectPythonBinaryFromCandidates([]string{"python3", "python"})
}

func detectPythonBinaryFromCandidates(candidates []string) (string, error) {
	for _, candidate := range candidates {
		if _, err := exec.LookPath(candidate); err != nil {
			continue
		}
		verifyCmd := exec.Command(candidate, "--version")
		verifyOut, verifyErr := verifyCmd.CombinedOutput()
		if verifyErr != nil {
			continue
		}
		if strings.Contains(strings.ToLower(string(verifyOut)), "python") {
			return candidate, nil
		}
	}
	return "", fmt.Errorf("python interpreter not found in PATH")
}

func (j *javaEngine) evaluatePythonLocal(source string, testCases []TestCase) Result {
	pythonBin, err := detectPythonBinary()
	if err != nil {
		return Result{
			Status:        "failed",
			CompileOutput: err.Error(),
			RunLog:        "python runtime is not available",
		}
	}

	workspace, err := os.MkdirTemp("", "lc-python-judge-*")
	if err != nil {
		return Result{Status: "failed", CompileOutput: err.Error(), RunLog: "unable to create workspace"}
	}
	defer os.RemoveAll(workspace)

	mainPath := filepath.Join(workspace, "main.py")
	if err := os.WriteFile(mainPath, []byte(source), 0o644); err != nil {
		return Result{Status: "failed", CompileOutput: err.Error(), RunLog: "unable to write source"}
	}

	compileCtx, cancelCompile := context.WithTimeout(context.Background(), j.timeout)
	defer cancelCompile()

	compileCmd := exec.CommandContext(compileCtx, pythonBin, "-m", "py_compile", "main.py")
	compileCmd.Dir = workspace
	compileOut, compileErr := compileCmd.CombinedOutput()
	if compileCtx.Err() == context.DeadlineExceeded {
		return Result{Status: "compile_error", CompileOutput: "Compilation timeout", RunLog: "python compile timeout"}
	}
	if compileErr != nil {
		return Result{Status: "compile_error", CompileOutput: string(compileOut), RunLog: "Compilation failed"}
	}

	results := make([]TestResult, 0, len(testCases))
	passed := 0
	var runLogs []string

	for i, tc := range testCases {
		if strings.HasPrefix(tc.Expected, sourceEquivalencePrefix) {
			expectedSource := strings.TrimPrefix(tc.Expected, sourceEquivalencePrefix)
			expectedNorm := normalizeComparableSourceCode(expectedSource)
			actualNorm := normalizeComparableSourceCode(source)
			tr := TestResult{
				Index:    i + 1,
				Input:    tc.Input,
				Expected: "[source equivalence]",
				Actual:   strings.TrimSpace(source),
				Passed:   expectedNorm != "" && actualNorm == expectedNorm,
			}
			if tr.Passed {
				passed++
			} else {
				runLogs = append(runLogs, fmt.Sprintf("test %d: source code does not match required structure", i+1))
			}
			results = append(results, tr)
			continue
		}

		runCtx, cancelRun := context.WithTimeout(context.Background(), j.timeout)
		runCmd := exec.CommandContext(runCtx, pythonBin, "main.py")
		runCmd.Dir = workspace
		runCmd.Stdin = strings.NewReader(tc.Input)

		var stdout bytes.Buffer
		var stderr bytes.Buffer
		runCmd.Stdout = &stdout
		runCmd.Stderr = &stderr

		err := runCmd.Run()
		cancelRun()

		actual := strings.TrimSpace(stdout.String())
		expected := strings.TrimSpace(tc.Expected)
		tr := TestResult{Index: i + 1, Input: tc.Input, Expected: expected, Actual: actual}

		if runCtx.Err() == context.DeadlineExceeded {
			tr.Passed = false
			tr.Error = "Time limit exceeded"
			runLogs = append(runLogs, fmt.Sprintf("test %d: time limit exceeded", i+1))
			results = append(results, tr)
			continue
		}
		if err != nil {
			tr.Passed = false
			tr.Error = strings.TrimSpace(stderr.String())
			if tr.Error == "" {
				tr.Error = err.Error()
			}
			runLogs = append(runLogs, fmt.Sprintf("test %d: runtime error %s", i+1, tr.Error))
			results = append(results, tr)
			continue
		}

		tr.Passed = isEquivalentOutput(actual, expected)
		if tr.Passed {
			passed++
		} else {
			runLogs = append(runLogs, fmt.Sprintf("test %d: expected '%s', got '%s'", i+1, expected, actual))
		}
		results = append(results, tr)
	}

	score := 0
	if len(testCases) > 0 {
		score = int(float64(passed) / float64(len(testCases)) * 100)
	}
	status := classifyTestStatus(testCases, results, passed)

	return Result{
		Status:        status,
		Score:         score,
		CompileOutput: strings.TrimSpace(string(compileOut)),
		RunLog:        strings.Join(runLogs, "\n"),
		Tests:         results,
	}
}

func (j *javaEngine) evaluateDocker(source string, testCases []TestCase) Result {
	if _, err := exec.LookPath("docker"); err != nil {
		return Result{
			Status:        "failed",
			CompileOutput: "docker is not available",
			RunLog:        "docker sandbox is required for judge mode=docker",
		}
	}

	workspace, err := os.MkdirTemp("", "lc-java-judge-*")
	if err != nil {
		return Result{Status: "failed", CompileOutput: err.Error(), RunLog: "unable to create workspace"}
	}
	defer os.RemoveAll(workspace)

	mainPath := filepath.Join(workspace, "Main.java")
	if err := os.WriteFile(mainPath, []byte(source), 0o644); err != nil {
		return Result{Status: "failed", CompileOutput: err.Error(), RunLog: "unable to write source"}
	}

	compileCtx, cancelCompile := context.WithTimeout(context.Background(), j.timeout)
	defer cancelCompile()

	compileOut, compileErr, timedOut := j.runDockerCommand(compileCtx, workspace, "eclipse-temurin:21-jdk", []string{"javac", "Main.java"}, "")
	if timedOut {
		return Result{Status: "compile_error", CompileOutput: "Compilation timeout", RunLog: "docker javac timeout"}
	}
	if compileErr != nil {
		return Result{Status: "compile_error", CompileOutput: strings.TrimSpace(compileOut), RunLog: "Compilation failed in docker sandbox"}
	}

	results := make([]TestResult, 0, len(testCases))
	passed := 0
	var runLogs []string

	for i, tc := range testCases {
		runCtx, cancelRun := context.WithTimeout(context.Background(), j.timeout)
		runOut, runErr, runTimedOut := j.runDockerCommand(runCtx, workspace, "eclipse-temurin:21-jdk", []string{"java", "Main"}, tc.Input)
		cancelRun()

		actual := strings.TrimSpace(runOut)
		expected := strings.TrimSpace(tc.Expected)
		tr := TestResult{Index: i + 1, Input: tc.Input, Expected: expected, Actual: actual}

		if runTimedOut {
			tr.Passed = false
			tr.Error = "Time limit exceeded"
			runLogs = append(runLogs, fmt.Sprintf("test %d: time limit exceeded", i+1))
			results = append(results, tr)
			continue
		}
		if runErr != nil {
			tr.Passed = false
			tr.Error = strings.TrimSpace(runOut)
			if tr.Error == "" {
				tr.Error = runErr.Error()
			}
			runLogs = append(runLogs, fmt.Sprintf("test %d: runtime error %s", i+1, tr.Error))
			results = append(results, tr)
			continue
		}

		tr.Passed = isEquivalentOutput(actual, expected)
		if tr.Passed {
			passed++
		} else {
			runLogs = append(runLogs, fmt.Sprintf("test %d: expected '%s', got '%s'", i+1, expected, actual))
		}
		results = append(results, tr)
	}

	score := 0
	if len(testCases) > 0 {
		score = int(float64(passed) / float64(len(testCases)) * 100)
	}
	status := classifyTestStatus(testCases, results, passed)

	return Result{
		Status:        status,
		Score:         score,
		CompileOutput: strings.TrimSpace(compileOut),
		RunLog:        strings.Join(runLogs, "\n"),
		Tests:         results,
	}
}

func (j *javaEngine) evaluatePythonDocker(source string, testCases []TestCase) Result {
	if _, err := exec.LookPath("docker"); err != nil {
		return Result{
			Status:        "failed",
			CompileOutput: "docker is not available",
			RunLog:        "docker sandbox is required for judge mode=docker",
		}
	}

	workspace, err := os.MkdirTemp("", "lc-python-judge-*")
	if err != nil {
		return Result{Status: "failed", CompileOutput: err.Error(), RunLog: "unable to create workspace"}
	}
	defer os.RemoveAll(workspace)

	mainPath := filepath.Join(workspace, "main.py")
	if err := os.WriteFile(mainPath, []byte(source), 0o644); err != nil {
		return Result{Status: "failed", CompileOutput: err.Error(), RunLog: "unable to write source"}
	}

	compileCtx, cancelCompile := context.WithTimeout(context.Background(), j.timeout)
	defer cancelCompile()

	compileOut, compileErr, timedOut := j.runDockerCommand(compileCtx, workspace, "python:3.12-alpine", []string{"python3", "-m", "py_compile", "main.py"}, "")
	if timedOut {
		return Result{Status: "compile_error", CompileOutput: "Compilation timeout", RunLog: "docker python compile timeout"}
	}
	if compileErr != nil {
		return Result{Status: "compile_error", CompileOutput: strings.TrimSpace(compileOut), RunLog: "Compilation failed in docker sandbox"}
	}

	results := make([]TestResult, 0, len(testCases))
	passed := 0
	var runLogs []string

	for i, tc := range testCases {
		if strings.HasPrefix(tc.Expected, sourceEquivalencePrefix) {
			expectedSource := strings.TrimPrefix(tc.Expected, sourceEquivalencePrefix)
			expectedNorm := normalizeComparableSourceCode(expectedSource)
			actualNorm := normalizeComparableSourceCode(source)
			tr := TestResult{
				Index:    i + 1,
				Input:    tc.Input,
				Expected: "[source equivalence]",
				Actual:   strings.TrimSpace(source),
				Passed:   expectedNorm != "" && actualNorm == expectedNorm,
			}
			if tr.Passed {
				passed++
			} else {
				runLogs = append(runLogs, fmt.Sprintf("test %d: source code does not match required structure", i+1))
			}
			results = append(results, tr)
			continue
		}

		runCtx, cancelRun := context.WithTimeout(context.Background(), j.timeout)
		runOut, runErr, runTimedOut := j.runDockerCommand(runCtx, workspace, "python:3.12-alpine", []string{"python3", "main.py"}, tc.Input)
		cancelRun()

		actual := strings.TrimSpace(runOut)
		expected := strings.TrimSpace(tc.Expected)
		tr := TestResult{Index: i + 1, Input: tc.Input, Expected: expected, Actual: actual}

		if runTimedOut {
			tr.Passed = false
			tr.Error = "Time limit exceeded"
			runLogs = append(runLogs, fmt.Sprintf("test %d: time limit exceeded", i+1))
			results = append(results, tr)
			continue
		}
		if runErr != nil {
			tr.Passed = false
			tr.Error = strings.TrimSpace(runOut)
			if tr.Error == "" {
				tr.Error = runErr.Error()
			}
			runLogs = append(runLogs, fmt.Sprintf("test %d: runtime error %s", i+1, tr.Error))
			results = append(results, tr)
			continue
		}

		tr.Passed = isEquivalentOutput(actual, expected)
		if tr.Passed {
			passed++
		} else {
			runLogs = append(runLogs, fmt.Sprintf("test %d: expected '%s', got '%s'", i+1, expected, actual))
		}
		results = append(results, tr)
	}

	score := 0
	if len(testCases) > 0 {
		score = int(float64(passed) / float64(len(testCases)) * 100)
	}
	status := classifyTestStatus(testCases, results, passed)

	return Result{
		Status:        status,
		Score:         score,
		CompileOutput: strings.TrimSpace(compileOut),
		RunLog:        strings.Join(runLogs, "\n"),
		Tests:         results,
	}
}

func classifyTestStatus(testCases []TestCase, results []TestResult, passed int) string {
	if len(testCases) == 0 {
		return "failed"
	}
	if passed == len(testCases) {
		return "accepted"
	}

	hasRuntimeError := false
	hasWrongAnswer := false
	hasTimeLimit := false
	for _, tr := range results {
		if strings.TrimSpace(tr.Error) != "" {
			hasRuntimeError = true
			if strings.Contains(strings.ToLower(tr.Error), "time limit") {
				hasTimeLimit = true
			}
			continue
		}
		if !tr.Passed {
			hasWrongAnswer = true
		}
	}

	if hasTimeLimit {
		return "time_limit"
	}
	if hasRuntimeError {
		return "runtime_error"
	}
	if hasWrongAnswer {
		return "wrong_answer"
	}
	return "failed"
}

func normalizeComparableOutput(s string) string {
	parts := strings.Fields(strings.TrimSpace(s))
	return strings.Join(parts, " ")
}

func isEquivalentOutput(actual, expected string) bool {
	return normalizeComparableOutput(actual) == normalizeComparableOutput(expected)
}

func (j *javaEngine) runDockerCommand(ctx context.Context, workspace, image string, command []string, stdin string) (string, error, bool) {
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
		image,
	}
	args = append(args, command...)

	cmd := exec.CommandContext(ctx, "docker", args...)
	if stdin != "" {
		cmd.Stdin = strings.NewReader(stdin)
	}

	var stdout bytes.Buffer
	var stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	err := cmd.Run()
	if ctx.Err() == context.DeadlineExceeded {
		return "", nil, true
	}

	combined := strings.TrimSpace(strings.TrimSpace(stdout.String()) + "\n" + strings.TrimSpace(stderr.String()))
	if err != nil {
		if errors.Is(err, context.DeadlineExceeded) {
			return combined, nil, true
		}
		return combined, err, false
	}
	return strings.TrimSpace(stdout.String()), nil, false
}
