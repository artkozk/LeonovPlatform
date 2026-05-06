package judge

import (
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"testing"
)

func TestJavaEngineEvaluate(t *testing.T) {
	if !hasWorkingBinary("javac", "-version") {
		t.Skip("javac not found in PATH")
	}
	engine := NewJavaEngine(3, "local")
	source := `import java.util.*;
public class Main {
  public static void main(String[] args) {
    Scanner sc = new Scanner(System.in);
    int a = sc.nextInt();
    int b = sc.nextInt();
    System.out.println(a + b);
  }
}`
	res := engine.EvaluateJava(source, []TestCase{{Input: "2 3", Expected: "5"}, {Input: "10 5", Expected: "15"}})
	if res.Status != "accepted" {
		t.Fatalf("expected accepted, got %s; compile=%s run=%s", res.Status, res.CompileOutput, res.RunLog)
	}
}

func TestJavaEngineEvaluateWrongAnswerStatusWhenAllTestsFail(t *testing.T) {
	if !hasWorkingBinary("javac", "-version") {
		t.Skip("javac not found in PATH")
	}
	engine := NewJavaEngine(3, "local")
	source := `import java.util.*;
public class Main {
  public static void main(String[] args) {
    Scanner sc = new Scanner(System.in);
    int a = sc.nextInt();
    int b = sc.nextInt();
    System.out.println(a + b + 1);
  }
}`
	res := engine.EvaluateJava(source, []TestCase{{Input: "2 3", Expected: "5"}, {Input: "10 5", Expected: "15"}})
	if res.Status != "wrong_answer" {
		t.Fatalf("expected wrong_answer, got %s; compile=%s run=%s", res.Status, res.CompileOutput, res.RunLog)
	}
}

func TestPythonEngineEvaluate(t *testing.T) {
	if _, err := detectPythonBinary(); err != nil {
		t.Skip("python interpreter not found in PATH")
	}

	engine := NewJavaEngine(3, "local")
	source := `a = int(input())
b = int(input())
print(a + b)
`
	res := engine.EvaluatePython(source, []TestCase{{Input: "2\n3", Expected: "5"}, {Input: "10\n5", Expected: "15"}})
	if res.Status != "accepted" {
		t.Fatalf("expected accepted, got %s; compile=%s run=%s", res.Status, res.CompileOutput, res.RunLog)
	}
}

func TestPythonEngineEvaluateWrongAnswerStatusWhenAllTestsFail(t *testing.T) {
	if _, err := detectPythonBinary(); err != nil {
		t.Skip("python interpreter not found in PATH")
	}

	engine := NewJavaEngine(3, "local")
	source := `a = int(input())
b = int(input())
print(a + b + 1)
`
	res := engine.EvaluatePython(source, []TestCase{{Input: "2\n3", Expected: "5"}, {Input: "10\n5", Expected: "15"}})
	if res.Status != "wrong_answer" {
		t.Fatalf("expected wrong_answer, got %s; compile=%s run=%s", res.Status, res.CompileOutput, res.RunLog)
	}
}

func TestIsEquivalentOutputIgnoresLineBreaksAndExtraSpaces(t *testing.T) {
	actual := "Имя: Анна\nВозраст: 25\nГород: Москва"
	expected := "Имя: Анна Возраст: 25   Город: Москва"
	if !isEquivalentOutput(actual, expected) {
		t.Fatalf("expected outputs to be equivalent, actual=%q expected=%q", actual, expected)
	}
}

func TestIsEquivalentOutputKeepsTokenOrderMeaningful(t *testing.T) {
	actual := "Имя: Анна Город: Москва Возраст: 25"
	expected := "Имя: Анна Возраст: 25 Город: Москва"
	if isEquivalentOutput(actual, expected) {
		t.Fatalf("expected outputs to be different, actual=%q expected=%q", actual, expected)
	}
}

func TestSQLEngineEvaluateAccepted(t *testing.T) {
	engine := NewJavaEngine(3, "local")
	initSQL := `
CREATE TABLE users(id INTEGER, name TEXT, active INTEGER);
INSERT INTO users(id, name, active) VALUES
  (1, 'Anna', 1),
  (2, 'Bob', 0),
  (3, 'Cleo', 1);
`
	source := "SELECT id, name FROM users WHERE active = 1 ORDER BY id;"
	reference := "SELECT id, name FROM users WHERE active = 1 ORDER BY id;"
	res := engine.EvaluateSQL(source, []TestCase{{Input: initSQL, Expected: reference}})
	if res.Status != "accepted" {
		t.Fatalf("expected accepted, got %s; run=%s", res.Status, res.RunLog)
	}
}

func TestSQLEngineEvaluateWrongAnswer(t *testing.T) {
	engine := NewJavaEngine(3, "local")
	initSQL := `
CREATE TABLE users(id INTEGER, name TEXT, active INTEGER);
INSERT INTO users(id, name, active) VALUES
  (1, 'Anna', 1),
  (2, 'Bob', 0),
  (3, 'Cleo', 1);
`
	source := "SELECT id, name FROM users ORDER BY id;"
	reference := "SELECT id, name FROM users WHERE active = 1 ORDER BY id;"
	res := engine.EvaluateSQL(source, []TestCase{{Input: initSQL, Expected: reference}})
	if res.Status != "wrong_answer" {
		t.Fatalf("expected wrong_answer, got %s; run=%s", res.Status, res.RunLog)
	}
}

func TestDockerModeFallsBackToLocalWhenDockerUnavailable(t *testing.T) {
	if _, err := detectPythonBinary(); err != nil {
		t.Skip("python interpreter not found in PATH")
	}
	if dockerBinaryAvailable() {
		t.Skip("docker binary is available; fallback path is not active")
	}

	engine := NewJavaEngine(3, "docker")
	res := engine.EvaluatePython("print('ok')\n", []TestCase{{Input: "", Expected: "ok"}})
	if res.Status != "accepted" {
		t.Fatalf("expected accepted status with local fallback, got %s; compile=%q run=%q", res.Status, res.CompileOutput, res.RunLog)
	}
	if strings.Contains(strings.ToLower(res.CompileOutput), "docker") {
		t.Fatalf("unexpected docker error in compile output: %q", res.CompileOutput)
	}
}

func TestPythonEngineDockerModePassesStdinToContainer(t *testing.T) {
	if !dockerBinaryAvailable() {
		t.Skip("docker binary is not available")
	}
	if !dockerDaemonAvailableForTests() {
		t.Skip("docker daemon is not available")
	}

	engine := NewJavaEngine(3, "docker")
	source := `price = int(input())
print(price - price // 10)
`

	res := engine.EvaluatePython(source, []TestCase{{Input: "1000\n", Expected: "900"}})
	if res.Status != "accepted" {
		t.Fatalf("expected accepted, got %s; compile=%q run=%q", res.Status, res.CompileOutput, res.RunLog)
	}
}

func TestDetectPythonBinaryFromCandidatesSkipsBrokenAlias(t *testing.T) {
	dir := t.TempDir()
	var brokenName string
	var workingName string
	var brokenContent []byte
	var workingContent []byte

	if runtime.GOOS == "windows" {
		brokenName = "python3.cmd"
		workingName = "python.cmd"
		brokenContent = []byte("@echo off\r\necho Python\r\nexit /b 1\r\n")
		workingContent = []byte("@echo off\r\necho Python 3.12.0\r\nexit /b 0\r\n")
	} else {
		brokenName = "python3"
		workingName = "python"
		brokenContent = []byte("#!/usr/bin/env sh\necho Python\nexit 1\n")
		workingContent = []byte("#!/usr/bin/env sh\necho Python 3.12.0\nexit 0\n")
	}

	brokenPath := filepath.Join(dir, brokenName)
	workingPath := filepath.Join(dir, workingName)

	if err := os.WriteFile(brokenPath, brokenContent, 0o755); err != nil {
		t.Fatalf("write broken alias: %v", err)
	}
	if err := os.WriteFile(workingPath, workingContent, 0o755); err != nil {
		t.Fatalf("write working binary: %v", err)
	}

	originalPath := os.Getenv("PATH")
	t.Setenv("PATH", dir+string(os.PathListSeparator)+originalPath)
	if runtime.GOOS == "windows" {
		t.Setenv("PATHEXT", ".COM;.EXE;.BAT;.CMD")
	}

	bin, err := detectPythonBinaryFromCandidates([]string{"python3", "python"})
	if err != nil {
		t.Fatalf("expected python binary, got error: %v", err)
	}
	if bin != "python" {
		t.Fatalf("expected fallback python, got %q", bin)
	}
}

func hasWorkingBinary(binary string, versionArg string) bool {
	cmd := exec.Command(binary, versionArg)
	return cmd.Run() == nil
}

func dockerDaemonAvailableForTests() bool {
	cmd := exec.Command("docker", "info")
	return cmd.Run() == nil
}

func TestBuildDockerRunArgsAddsInteractiveFlagForStdin(t *testing.T) {
	argsWithStdin := buildDockerRunArgs("/tmp/workspace", "python:3.12-alpine", []string{"python3", "main.py"}, true)
	argsWithoutStdin := buildDockerRunArgs("/tmp/workspace", "python:3.12-alpine", []string{"python3", "main.py"}, false)

	joinedWithStdin := strings.Join(argsWithStdin, " ")
	joinedWithoutStdin := strings.Join(argsWithoutStdin, " ")

	if !strings.Contains(joinedWithStdin, " -i ") {
		t.Fatalf("expected docker args to include -i for stdin: %s", joinedWithStdin)
	}
	if strings.Contains(joinedWithoutStdin, " -i ") {
		t.Fatalf("did not expect docker args to include -i without stdin: %s", joinedWithoutStdin)
	}
}
