const fs = require("fs");
const path = require("path");

function readEnvFile(filePath) {
  const out = {};
  if (!fs.existsSync(filePath)) {
    return out;
  }

  const raw = fs.readFileSync(filePath, "utf8");
  for (const line of raw.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) {
      continue;
    }
    const eq = trimmed.indexOf("=");
    if (eq <= 0) {
      continue;
    }
    const key = trimmed.slice(0, eq).trim();
    let value = trimmed.slice(eq + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    out[key] = value;
  }

  return out;
}

const envPath = path.resolve(__dirname, "../../backend/.env");
const fileEnv = readEnvFile(envPath);
function pickEnv(key, fallback = "") {
  const runtime = process.env[key];
  if (runtime !== undefined && runtime !== null && String(runtime).trim() !== "") {
    return String(runtime);
  }
  const fileValue = fileEnv[key];
  if (fileValue !== undefined && fileValue !== null && String(fileValue).trim() !== "") {
    return String(fileValue);
  }
  return fallback;
}

function pickPositiveInt(key, fallback) {
  const raw = pickEnv(key, String(fallback));
  const parsed = Number.parseInt(String(raw), 10);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return fallback;
  }
  return parsed;
}

const sharedEnv = {
  APP_ENV: pickEnv("APP_ENV", "production"),
  HTTP_PORT: pickEnv("HTTP_PORT", "8510"),
  DATABASE_URL:
    pickEnv("DATABASE_URL", "postgres://postgres:postgres@127.0.0.1:5432/leonovcare_platform?sslmode=disable"),
  REDIS_URL: pickEnv("REDIS_URL", "redis://127.0.0.1:6379/0"),
  JWT_ACCESS_SECRET: pickEnv("JWT_ACCESS_SECRET", "change-this-access-secret"),
  JWT_REFRESH_SECRET: pickEnv("JWT_REFRESH_SECRET", "change-this-refresh-secret"),
  JWT_ACCESS_TTL: pickEnv("JWT_ACCESS_TTL", "15m"),
  JWT_REFRESH_TTL: pickEnv("JWT_REFRESH_TTL", "720h"),
  FRONTEND_URL: pickEnv("FRONTEND_URL", "http://85.198.82.221:8511"),
  AUTO_MIGRATE: pickEnv("AUTO_MIGRATE", "false"),
  AUTO_SEED: pickEnv("AUTO_SEED", "false"),
  SUBMISSION_QUEUE: pickEnv("SUBMISSION_QUEUE", "submission_jobs"),
  SUBMISSION_PROCESSING_QUEUE: pickEnv("SUBMISSION_PROCESSING_QUEUE", "submission_jobs_processing"),
  SUBMISSION_RECONCILE_INTERVAL: pickEnv("SUBMISSION_RECONCILE_INTERVAL", "30s"),
  SUBMISSION_RECONCILE_BATCH: pickEnv("SUBMISSION_RECONCILE_BATCH", "200"),
  SUBMISSION_MAX_ATTEMPTS: pickEnv("SUBMISSION_MAX_ATTEMPTS", "30"),
  JAVA_TIMEOUT_SECONDS: pickEnv("JAVA_TIMEOUT_SECONDS", "4"),
  JUDGE_MODE: pickEnv("JUDGE_MODE", "auto"),
  // Keep default empty so backend safe policy can allow valid training commands
  // (python main.py, safe printf|python, pytest) without hard-coded per-task env tuning.
  IDE_CHECKER_ALLOWED_COMMANDS: pickEnv("IDE_CHECKER_ALLOWED_COMMANDS", ""),
  FREE_DAILY_SUBMISSIONS: pickEnv("FREE_DAILY_SUBMISSIONS", "20"),
  AUTH_RATE_LIMIT_PER_MINUTE: pickEnv("AUTH_RATE_LIMIT_PER_MINUTE", "60"),
  AI_HINT_RATE_LIMIT_PER_MINUTE: pickEnv("AI_HINT_RATE_LIMIT_PER_MINUTE", "20"),
  WEBHOOK_RATE_LIMIT_PER_MINUTE: pickEnv("WEBHOOK_RATE_LIMIT_PER_MINUTE", "120"),
  CARDLINK_BASE_URL: pickEnv("CARDLINK_BASE_URL", "https://api.cardlink.example"),
  CARDLINK_MERCHANT_ID: pickEnv("CARDLINK_MERCHANT_ID", ""),
  CARDLINK_SHOP_ID: pickEnv("CARDLINK_SHOP_ID", ""),
  CARDLINK_API_TOKEN: pickEnv("CARDLINK_API_TOKEN", ""),
  CARDLINK_SECRET: pickEnv("CARDLINK_SECRET", ""),
  CARDLINK_WEBHOOK_TOKEN: pickEnv("CARDLINK_WEBHOOK_TOKEN", "change-cardlink-token"),
  CARDLINK_REQUIRE_SIGNATURE: pickEnv("CARDLINK_REQUIRE_SIGNATURE", "true"),
  CARDLINK_CURRENCY_IN: pickEnv("CARDLINK_CURRENCY_IN", "RUB"),
  CARDLINK_LOCALE: pickEnv("CARDLINK_LOCALE", "ru"),
  CARDLINK_BILL_TTL_SECONDS: pickEnv("CARDLINK_BILL_TTL_SECONDS", "1800"),
  CARDLINK_RETURN_URL: pickEnv("CARDLINK_RETURN_URL", ""),
  CARDLINK_SUCCESS_URL: pickEnv("CARDLINK_SUCCESS_URL", ""),
  CARDLINK_FAIL_URL: pickEnv("CARDLINK_FAIL_URL", ""),
  SUPPORT_EMAIL: pickEnv("SUPPORT_EMAIL", "support@leonovcare.ru"),
  OPENAI_API_KEY: pickEnv("OPENAI_API_KEY", ""),
  OPENAI_BASE_URL: pickEnv("OPENAI_BASE_URL", "https://api.openai.com"),
  OPENAI_MODEL: pickEnv("OPENAI_MODEL", "gpt-5.4-mini"),
  OPENAI_HTTP_PROXY: pickEnv("OPENAI_HTTP_PROXY", ""),
  OPENAI_PROXY_HOST: pickEnv("OPENAI_PROXY_HOST", ""),
  OPENAI_PROXY_PORT: pickEnv("OPENAI_PROXY_PORT", ""),
  OPENAI_PROXY_USERNAME: pickEnv("OPENAI_PROXY_USERNAME", ""),
  OPENAI_PROXY_PASSWORD: pickEnv("OPENAI_PROXY_PASSWORD", ""),
  GOOGLE_CLIENT_ID: pickEnv("GOOGLE_CLIENT_ID", ""),
  EXPOSE_DEMO_TOKENS: pickEnv("EXPOSE_DEMO_TOKENS", "false"),

  GIN_MODE: pickEnv("GIN_MODE", "release"),
  NODE_ENV: pickEnv("NODE_ENV", "production"),
  SUPPORT_CHAT_ENABLED: pickEnv("SUPPORT_CHAT_ENABLED", "true"),
  SUPPORT_CHAT_MAX_ATTACHMENTS_PER_MESSAGE: pickEnv("SUPPORT_CHAT_MAX_ATTACHMENTS_PER_MESSAGE", "5"),
  SUPPORT_CHAT_MAX_ATTACHMENT_BYTES: pickEnv("SUPPORT_CHAT_MAX_ATTACHMENT_BYTES", "10485760"),
  SUPPORT_CHAT_MAX_MESSAGE_PAYLOAD_BYTES: pickEnv("SUPPORT_CHAT_MAX_MESSAGE_PAYLOAD_BYTES", "52428800"),
  SUPPORT_CHAT_STORAGE_DIR: pickEnv("SUPPORT_CHAT_STORAGE_DIR", "/var/lib/leonovcare/support"),
};

module.exports = {
  apps: [
    {
      name: "leonovcare-api",
      script: "./backend/bin/leonovcare-api",
      cwd: "/opt/leonovcare-platform/current",
      env: { ...sharedEnv },
      instances: 1,
      exec_mode: "fork",
      autorestart: true,
      max_restarts: 20,
      max_memory_restart: "700M",
      kill_timeout: 10000,
      watch: false,
    },
    {
      name: "leonovcare-worker",
      script: "./backend/bin/leonovcare-worker",
      cwd: "/opt/leonovcare-platform/current",
      env: { ...sharedEnv },
      instances: pickPositiveInt("WORKER_INSTANCES", 4),
      exec_mode: "fork",
      autorestart: true,
      max_restarts: 20,
      max_memory_restart: "900M",
      kill_timeout: 10000,
      watch: false,
    },
    {
      name: "leonovcare-frontend",
      script: "npm",
      args: "run preview -- --host 0.0.0.0 --port 8511",
      cwd: "/opt/leonovcare-platform/current/frontend",
      autorestart: true,
      max_restarts: 20,
      watch: false,
    },
  ],
};
