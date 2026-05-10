package app

import "testing"

func TestNormalizeNicknameKeepsCyrillicLetters(t *testing.T) {
	got := normalizeNickname("Иван Петров")
	want := "иван_петров"
	if got != want {
		t.Fatalf("unexpected normalized nickname: got %q want %q", got, want)
	}
}

func TestNormalizeNicknameKeepsLatinCompatibility(t *testing.T) {
	got := normalizeNickname("Ivan.Petrov-42")
	want := "ivan_petrov-42"
	if got != want {
		t.Fatalf("unexpected normalized nickname: got %q want %q", got, want)
	}
}

func TestNormalizeNicknameTruncatesByRunes(t *testing.T) {
	got := normalizeNickname("абвгдеёжзийклмнопрстуфхцчшщъыьэюяabc")
	if len([]rune(got)) != 32 {
		t.Fatalf("nickname must be truncated to 32 runes, got %d in %q", len([]rune(got)), got)
	}
}

func TestNormalizeEmailTrimsAndLowercases(t *testing.T) {
	got := normalizeEmail("  USER@Example.COM  ")
	if got != "user@example.com" {
		t.Fatalf("unexpected normalized email: %q", got)
	}
}

func TestNormalizeAndValidateEmailAcceptsTrimmedInput(t *testing.T) {
	got, err := normalizeAndValidateEmail("  USER@Example.COM  ")
	if err != nil {
		t.Fatalf("expected valid email, got error: %v", err)
	}
	if got != "user@example.com" {
		t.Fatalf("unexpected normalized email: %q", got)
	}
}

func TestNormalizeAndValidateEmailRejectsInvalidInput(t *testing.T) {
	if _, err := normalizeAndValidateEmail("not-an-email"); err == nil {
		t.Fatal("expected invalid email error")
	}
}

func TestNormalizeAndValidateEmailRejectsDisplayNameFormat(t *testing.T) {
	if _, err := normalizeAndValidateEmail("John Doe <john@example.com>"); err == nil {
		t.Fatal("expected invalid email error for display name format")
	}
}
