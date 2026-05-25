package config

import (
	"fmt"
	"os"
	"strconv"
	"time"
)

type Config struct {
	AppName                       string
	Environment                   string
	HTTPPort                      int
	MaxRequestBodyBytes           int
	MaxSubmissionSourceBytes      int
	DBURL                         string
	RedisURL                      string
	JWTAccessSecret               string
	JWTRefreshSecret              string
	JWTAccessTTL                  time.Duration
	JWTRefreshTTL                 time.Duration
	FrontendURL                   string
	EnableAutoMigrate             bool
	EnableAutoSeed                bool
	SubmissionQueueName           string
	SubmissionProcessingQueueName string
	SubmissionMaxAttempts         int
	SubmissionReconcileInterval   time.Duration
	SubmissionReconcileBatch      int
	JavaTimeoutSeconds            int
	JudgeMode                     string
	IDECheckerAllowedCommands     string
	DailyFreeSubmissions          int
	AuthRateLimitPerMinute        int
	AIHintRateLimitPerMinute      int
	WebhookRateLimitPerMinute     int
	CardlinkBaseURL               string
	CardlinkMerchantID            string
	CardlinkShopID                string
	CardlinkAPIToken              string
	CardlinkSecret                string
	CardlinkWebhookToken          string
	CardlinkRequireSignature      bool
	CardlinkCurrencyIn            string
	CardlinkLocale                string
	CardlinkBillTTLSeconds        int
	CardlinkReturnURL             string
	CardlinkSuccessURL            string
	CardlinkFailURL               string
	SupportEmail                  string
	OpenAIAPIKey                  string
	OpenAIBaseURL                 string
	OpenAIModel                   string
	OpenAIHTTPProxy               string
	OpenAIProxyHost               string
	OpenAIProxyPort               string
	OpenAIProxyUsername           string
	OpenAIProxyPassword           string
	GoogleClientID                string
	ExposeDemoTokens              bool
	// Support chat feature flags and operational limits.
	SupportChatEnabled                  bool
	SupportChatMaxAttachmentsPerMessage int
	SupportChatMaxAttachmentBytes       int64
	SupportChatMaxMessagePayloadBytes   int64
	SupportChatStorageDir               string
}

func Load() (Config, error) {
	cfg := Config{
		AppName:                       getOr("APP_NAME", "Leonov Care Platform"),
		Environment:                   getOr("APP_ENV", "development"),
		HTTPPort:                      getIntOr("HTTP_PORT", 8080),
		MaxRequestBodyBytes:           getIntOr("MAX_REQUEST_BODY_BYTES", 16777216),
		MaxSubmissionSourceBytes:      getIntOr("MAX_SUBMISSION_SOURCE_BYTES", 8388608),
		DBURL:                         os.Getenv("DATABASE_URL"),
		RedisURL:                      getOr("REDIS_URL", "redis://localhost:6379/0"),
		JWTAccessSecret:               os.Getenv("JWT_ACCESS_SECRET"),
		JWTRefreshSecret:              os.Getenv("JWT_REFRESH_SECRET"),
		JWTAccessTTL:                  getDurationOr("JWT_ACCESS_TTL", 15*time.Minute),
		JWTRefreshTTL:                 getDurationOr("JWT_REFRESH_TTL", 24*time.Hour*30),
		FrontendURL:                   getOr("FRONTEND_URL", "http://localhost:5173"),
		EnableAutoMigrate:             getBoolOr("AUTO_MIGRATE", false),
		EnableAutoSeed:                getBoolOr("AUTO_SEED", false),
		SubmissionQueueName:           getOr("SUBMISSION_QUEUE", "submission_jobs"),
		SubmissionProcessingQueueName: getOr("SUBMISSION_PROCESSING_QUEUE", "submission_jobs_processing"),
		SubmissionMaxAttempts:         getIntOr("SUBMISSION_MAX_ATTEMPTS", 30),
		SubmissionReconcileInterval:   getDurationOr("SUBMISSION_RECONCILE_INTERVAL", 30*time.Second),
		SubmissionReconcileBatch:      getIntOr("SUBMISSION_RECONCILE_BATCH", 200),
		JavaTimeoutSeconds:            getIntOr("JAVA_TIMEOUT_SECONDS", 4),
		JudgeMode:                     getOr("JUDGE_MODE", "local"),
		IDECheckerAllowedCommands:     getOr("IDE_CHECKER_ALLOWED_COMMANDS", ""),
		DailyFreeSubmissions:          getIntOr("FREE_DAILY_SUBMISSIONS", 20),
		AuthRateLimitPerMinute:        getIntOr("AUTH_RATE_LIMIT_PER_MINUTE", 60),
		AIHintRateLimitPerMinute:      getIntOr("AI_HINT_RATE_LIMIT_PER_MINUTE", 20),
		WebhookRateLimitPerMinute:     getIntOr("WEBHOOK_RATE_LIMIT_PER_MINUTE", 120),
		CardlinkBaseURL:               getOr("CARDLINK_BASE_URL", "https://api.cardlink.example"),
		CardlinkMerchantID:            os.Getenv("CARDLINK_MERCHANT_ID"),
		CardlinkShopID:                getOr("CARDLINK_SHOP_ID", os.Getenv("CARDLINK_MERCHANT_ID")),
		CardlinkAPIToken:              getOr("CARDLINK_API_TOKEN", os.Getenv("CARDLINK_SECRET")),
		CardlinkSecret:                os.Getenv("CARDLINK_SECRET"),
		CardlinkWebhookToken:          getOr("CARDLINK_WEBHOOK_TOKEN", "change-me"),
		CardlinkRequireSignature:      getBoolOr("CARDLINK_REQUIRE_SIGNATURE", true),
		CardlinkCurrencyIn:            getOr("CARDLINK_CURRENCY_IN", "RUB"),
		CardlinkLocale:                getOr("CARDLINK_LOCALE", "ru"),
		CardlinkBillTTLSeconds:        getIntOr("CARDLINK_BILL_TTL_SECONDS", 1800),
		CardlinkReturnURL:             os.Getenv("CARDLINK_RETURN_URL"),
		CardlinkSuccessURL:            os.Getenv("CARDLINK_SUCCESS_URL"),
		CardlinkFailURL:               os.Getenv("CARDLINK_FAIL_URL"),
		SupportEmail:                  getOr("SUPPORT_EMAIL", "support@leonovcare.local"),
		OpenAIAPIKey:                  os.Getenv("OPENAI_API_KEY"),
		OpenAIBaseURL:                 getOr("OPENAI_BASE_URL", "https://api.openai.com"),
		OpenAIModel:                   getOr("OPENAI_MODEL", "gpt-5.4-mini"),
		OpenAIHTTPProxy:               os.Getenv("OPENAI_HTTP_PROXY"),
		OpenAIProxyHost:               os.Getenv("OPENAI_PROXY_HOST"),
		OpenAIProxyPort:               os.Getenv("OPENAI_PROXY_PORT"),
		OpenAIProxyUsername:           os.Getenv("OPENAI_PROXY_USERNAME"),
		OpenAIProxyPassword:           os.Getenv("OPENAI_PROXY_PASSWORD"),
		GoogleClientID:                os.Getenv("GOOGLE_CLIENT_ID"),
		ExposeDemoTokens:              getBoolOr("EXPOSE_DEMO_TOKENS", false),
		SupportChatEnabled:                  getBoolOr("SUPPORT_CHAT_ENABLED", true),
		SupportChatMaxAttachmentsPerMessage: getIntOr("SUPPORT_CHAT_MAX_ATTACHMENTS_PER_MESSAGE", 5),
		SupportChatMaxAttachmentBytes:       getInt64Or("SUPPORT_CHAT_MAX_ATTACHMENT_BYTES", 10*1024*1024),
		SupportChatMaxMessagePayloadBytes:   getInt64Or("SUPPORT_CHAT_MAX_MESSAGE_PAYLOAD_BYTES", 52*1024*1024),
		SupportChatStorageDir:               getOr("SUPPORT_CHAT_STORAGE_DIR", "/var/lib/leonovcare/support"),
	}
	cfg = applySecurityDefaults(cfg)

	if cfg.DBURL == "" {
		return cfg, fmt.Errorf("DATABASE_URL is required")
	}
	if cfg.JWTAccessSecret == "" || cfg.JWTRefreshSecret == "" {
		return cfg, fmt.Errorf("JWT_ACCESS_SECRET and JWT_REFRESH_SECRET are required")
	}

	return cfg, nil
}

func getOr(k, v string) string {
	val := os.Getenv(k)
	if val == "" {
		return v
	}
	return val
}

func getIntOr(k string, v int) int {
	raw := os.Getenv(k)
	if raw == "" {
		return v
	}
	n, err := strconv.Atoi(raw)
	if err != nil {
		return v
	}
	return n
}

func getInt64Or(k string, v int64) int64 {
	raw := os.Getenv(k)
	if raw == "" {
		return v
	}
	n, err := strconv.ParseInt(raw, 10, 64)
	if err != nil {
		return v
	}
	return n
}

func getBoolOr(k string, v bool) bool {
	raw := os.Getenv(k)
	if raw == "" {
		return v
	}
	parsed, err := strconv.ParseBool(raw)
	if err != nil {
		return v
	}
	return parsed
}

func getDurationOr(k string, v time.Duration) time.Duration {
	raw := os.Getenv(k)
	if raw == "" {
		return v
	}
	d, err := time.ParseDuration(raw)
	if err != nil {
		return v
	}
	return d
}

func applySecurityDefaults(cfg Config) Config {
	if cfg.HTTPPort <= 0 {
		cfg.HTTPPort = 8080
	}
	if cfg.MaxRequestBodyBytes <= 0 {
		cfg.MaxRequestBodyBytes = 16 * 1024 * 1024
	}
	if cfg.MaxSubmissionSourceBytes <= 0 {
		cfg.MaxSubmissionSourceBytes = 8 * 1024 * 1024
	}
	if cfg.SubmissionMaxAttempts <= 0 {
		cfg.SubmissionMaxAttempts = 30
	}
	if cfg.SubmissionReconcileBatch <= 0 {
		cfg.SubmissionReconcileBatch = 200
	}
	if cfg.JavaTimeoutSeconds <= 0 {
		cfg.JavaTimeoutSeconds = 4
	}
	if cfg.AuthRateLimitPerMinute <= 0 {
		cfg.AuthRateLimitPerMinute = 60
	}
	if cfg.AIHintRateLimitPerMinute <= 0 {
		cfg.AIHintRateLimitPerMinute = 20
	}
	if cfg.WebhookRateLimitPerMinute <= 0 {
		cfg.WebhookRateLimitPerMinute = 120
	}
	if cfg.CardlinkBillTTLSeconds <= 0 {
		cfg.CardlinkBillTTLSeconds = 1800
	}
	if cfg.SupportChatMaxAttachmentsPerMessage <= 0 {
		cfg.SupportChatMaxAttachmentsPerMessage = 5
	}
	if cfg.SupportChatMaxAttachmentBytes <= 0 {
		cfg.SupportChatMaxAttachmentBytes = 10 * 1024 * 1024
	}
	if cfg.SupportChatMaxMessagePayloadBytes <= 0 {
		cfg.SupportChatMaxMessagePayloadBytes = 52 * 1024 * 1024
	}
	if cfg.SupportChatStorageDir == "" {
		cfg.SupportChatStorageDir = "/var/lib/leonovcare/support"
	}
	return cfg
}
