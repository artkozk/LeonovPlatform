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
