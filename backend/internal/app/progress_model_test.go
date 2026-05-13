package app

import (
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgtype"
)

func TestNormalizeProgressSource(t *testing.T) {
	cases := map[string]string{
		"":           "manual",
		"manual":     "manual",
		"quiz":       "quiz",
		"submission": "submission",
		"SYSTEM":     "system",
		"unknown":    "manual",
	}

	for input, expected := range cases {
		if actual := normalizeProgressSource(input); actual != expected {
			t.Fatalf("normalizeProgressSource(%q) = %q, expected %q", input, actual, expected)
		}
	}
}

func TestVisibleStreak(t *testing.T) {
	now := time.Date(2026, time.May, 13, 10, 0, 0, 0, time.UTC)
	today := pgtype.Date{Time: now, Valid: true}
	yesterday := pgtype.Date{Time: now.AddDate(0, 0, -1), Valid: true}
	twoDaysAgo := pgtype.Date{Time: now.AddDate(0, 0, -2), Valid: true}

	if got := visibleStreak(5, pgtype.Date{}, now); got != 0 {
		t.Fatalf("expected 0 for invalid last day, got %d", got)
	}
	if got := visibleStreak(3, today, now); got != 3 {
		t.Fatalf("expected 3 for today streak, got %d", got)
	}
	if got := visibleStreak(4, yesterday, now); got != 4 {
		t.Fatalf("expected 4 for yesterday streak, got %d", got)
	}
	if got := visibleStreak(6, twoDaysAgo, now); got != 0 {
		t.Fatalf("expected 0 for stale streak, got %d", got)
	}
}
