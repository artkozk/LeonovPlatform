package app

import (
	"testing"

	"leonovcare/backend/internal/judge"
)

func TestNormalizeRunPreviewResult_RuntimeError(t *testing.T) {
	result := judge.Result{
		Status: "failed",
		Score:  0,
		Tests: []judge.TestResult{
			{
				Index: 1,
				Input: "1\n2\n",
				Error: "Traceback (most recent call last): ...",
			},
		},
	}

	preview := normalizeRunPreviewResult(result)
	if preview.Status != "runtime_error" {
		t.Fatalf("expected runtime_error, got %s", preview.Status)
	}
}

func TestNormalizeRunPreviewResult_SuccessRun(t *testing.T) {
	result := judge.Result{
		Status: "wrong_answer",
		Score:  0,
		RunLog: "test 1: expected '', got '42'",
		Tests: []judge.TestResult{
			{
				Index:  1,
				Input:  "",
				Actual: "42",
				Error:  "",
			},
		},
	}

	preview := normalizeRunPreviewResult(result)
	if preview.Status != "ran" {
		t.Fatalf("expected ran, got %s", preview.Status)
	}
	if preview.RunLog != "" {
		t.Fatalf("expected run log to be cleared, got %q", preview.RunLog)
	}
}

func TestNormalizeRunPreviewResult_CompileError(t *testing.T) {
	result := judge.Result{
		Status:        "failed",
		Score:         0,
		CompileOutput: "SyntaxError",
		RunLog:        "Compilation failed",
		Tests:         []judge.TestResult{},
	}

	preview := normalizeRunPreviewResult(result)
	if preview.Status != "compile_error" {
		t.Fatalf("expected compile_error, got %s", preview.Status)
	}
}
