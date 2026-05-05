package config

import "testing"

func setRequiredEnv(t *testing.T) {
	t.Helper()
	t.Setenv("DATABASE_URL", "postgres://user:pass@127.0.0.1:5432/db?sslmode=disable")
	t.Setenv("JWT_ACCESS_SECRET", "access-secret")
	t.Setenv("JWT_REFRESH_SECRET", "refresh-secret")
}

func TestLoad_DefaultIDECheckerAllowedCommandsIsEmpty(t *testing.T) {
	setRequiredEnv(t)
	t.Setenv("IDE_CHECKER_ALLOWED_COMMANDS", "")

	cfg, err := Load()
	if err != nil {
		t.Fatalf("Load() returned error: %v", err)
	}
	if cfg.IDECheckerAllowedCommands != "" {
		t.Fatalf("expected empty IDE checker allowlist by default, got %q", cfg.IDECheckerAllowedCommands)
	}
}

func TestLoad_UsesExplicitIDECheckerAllowlist(t *testing.T) {
	setRequiredEnv(t)
	t.Setenv("IDE_CHECKER_ALLOWED_COMMANDS", "pytest,python -m pytest")

	cfg, err := Load()
	if err != nil {
		t.Fatalf("Load() returned error: %v", err)
	}
	if cfg.IDECheckerAllowedCommands != "pytest,python -m pytest" {
		t.Fatalf("expected explicit IDE checker allowlist to be preserved, got %q", cfg.IDECheckerAllowedCommands)
	}
}

