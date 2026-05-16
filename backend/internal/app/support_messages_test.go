package app

import (
	"path/filepath"
	"strings"
	"testing"
)

// ============================================================================
// Support chat — unit tests for filename / storage path safety (2026-05-16).
//
// Эти тесты — анти-регрессия для безопасности вложений (blueprint §9,
// §13 п.6, §14 п.1-2): path traversal, нулевые байты, control-символы,
// слишком длинные имена, попытки писать за пределы storage_dir.
//
// Тесты намеренно проверяют PRIVATE helpers пакета (sanitizeFilename,
// safeStoragePath, supportPreviewFromBody), потому что эти helpers
// единственные точки входа для опасных строк во весь storage layer.
// ============================================================================

func TestSanitizeFilenameRemovesPathTraversal(t *testing.T) {
	cases := []struct {
		in   string
		want string
	}{
		{"../../etc/passwd", "passwd"},
		{"..\\..\\windows\\System32\\cmd.exe", "cmd.exe"},
		{"normal.txt", "normal.txt"},
		{"спецификация.pdf", "спецификация.pdf"},
		{"a<b>c|d?.txt", "a_b_c_d_.txt"},
		{"", "file"},
		{".", "file"},
		{"..", "file"},
		{"contains\x00null.txt", "containsnull.txt"},
	}
	for _, tc := range cases {
		got := sanitizeFilename(tc.in)
		if got != tc.want {
			t.Errorf("sanitizeFilename(%q) = %q, want %q", tc.in, got, tc.want)
		}
	}
}

func TestSanitizeFilenameTruncatesOverlongInput(t *testing.T) {
	in := strings.Repeat("a", 500) + ".txt"
	got := sanitizeFilename(in)
	if len([]rune(got)) > 180 {
		t.Errorf("sanitizeFilename did not truncate: %d runes", len([]rune(got)))
	}
}

func TestSafeStoragePathRejectsTraversal(t *testing.T) {
	root := filepath.Join("C:\\", "tmp", "support-test-root")
	cases := []string{
		"../../escape.txt",
		"..\\\\escape.txt",
		"conv/abc/../../escape.txt",
	}
	for _, key := range cases {
		if _, err := safeStoragePath(root, key); err == nil {
			t.Errorf("safeStoragePath accepted traversal: %q", key)
		}
	}
}

func TestSafeStoragePathAcceptsNormalKey(t *testing.T) {
	root, err := filepath.Abs(filepath.Join(t.TempDir(), "root"))
	if err != nil {
		t.Fatal(err)
	}
	full, err := safeStoragePath(root, "conv/abc/msg/def/123-foo.txt")
	if err != nil {
		t.Fatalf("safeStoragePath failed on valid key: %v", err)
	}
	if !strings.HasPrefix(full, root) {
		t.Errorf("resolved path %q does not stay under root %q", full, root)
	}
}

func TestSupportPreviewFromBody(t *testing.T) {
	cases := []struct {
		body           string
		hasAttachments bool
		want           string
	}{
		{"Hello", false, "Hello"},
		{"  hi  ", false, "hi"},
		{"", true, "📎 вложение"},
		{"", false, ""},
		{strings.Repeat("a", 300), false, strings.Repeat("a", 240)},
	}
	for _, tc := range cases {
		got := supportPreviewFromBody(tc.body, tc.hasAttachments)
		if got != tc.want {
			t.Errorf("supportPreviewFromBody(%q,%v) = %q, want %q", tc.body, tc.hasAttachments, got, tc.want)
		}
	}
}

func TestSupportDisplayName(t *testing.T) {
	got := supportDisplayName("Иван", "Петров", "ivan", "ivan@example.com")
	if got != "Иван Петров" {
		t.Errorf("expected full name, got %q", got)
	}
	got = supportDisplayName("", "", "ivan", "ivan@example.com")
	if got != "ivan" {
		t.Errorf("expected username fallback, got %q", got)
	}
	got = supportDisplayName("", "", "", "ivan@example.com")
	if got != "ivan@example.com" {
		t.Errorf("expected email fallback, got %q", got)
	}
}

func TestIsValidSupportStatus(t *testing.T) {
	for _, s := range []string{"open", "resolved", "closed"} {
		if !isValidSupportStatus(s) {
			t.Errorf("expected %q to be valid", s)
		}
	}
	if isValidSupportStatus("archived") {
		t.Error("expected 'archived' to be invalid")
	}
}
