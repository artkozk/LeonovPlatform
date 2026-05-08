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

func TestLoad_DefaultAutoMigrateIsDisabled(t *testing.T) {
	setRequiredEnv(t)
	t.Setenv("AUTO_MIGRATE", "")

	cfg, err := Load()
	if err != nil {
		t.Fatalf("Load() returned error: %v", err)
	}
	if cfg.EnableAutoMigrate {
		t.Fatalf("expected AUTO_MIGRATE default to be false")
	}
}

func TestLoad_ClampsSecurityCriticalNumericConfig(t *testing.T) {
	setRequiredEnv(t)
	t.Setenv("MAX_REQUEST_BODY_BYTES", "-1")
	t.Setenv("MAX_SUBMISSION_SOURCE_BYTES", "0")
	t.Setenv("AUTH_RATE_LIMIT_PER_MINUTE", "-5")
	t.Setenv("AI_HINT_RATE_LIMIT_PER_MINUTE", "0")
	t.Setenv("WEBHOOK_RATE_LIMIT_PER_MINUTE", "-120")
	t.Setenv("CARDLINK_BILL_TTL_SECONDS", "0")

	cfg, err := Load()
	if err != nil {
		t.Fatalf("Load() returned error: %v", err)
	}
	if cfg.MaxRequestBodyBytes != 16*1024*1024 {
		t.Fatalf("expected max request body default clamp, got %d", cfg.MaxRequestBodyBytes)
	}
	if cfg.MaxSubmissionSourceBytes != 8*1024*1024 {
		t.Fatalf("expected max submission source default clamp, got %d", cfg.MaxSubmissionSourceBytes)
	}
	if cfg.AuthRateLimitPerMinute != 60 {
		t.Fatalf("expected auth rate limit clamp, got %d", cfg.AuthRateLimitPerMinute)
	}
	if cfg.AIHintRateLimitPerMinute != 20 {
		t.Fatalf("expected ai hint rate limit clamp, got %d", cfg.AIHintRateLimitPerMinute)
	}
	if cfg.WebhookRateLimitPerMinute != 120 {
		t.Fatalf("expected webhook rate limit clamp, got %d", cfg.WebhookRateLimitPerMinute)
	}
	if cfg.CardlinkBillTTLSeconds != 1800 {
		t.Fatalf("expected cardlink bill ttl clamp, got %d", cfg.CardlinkBillTTLSeconds)
	}
}
