-- 006_billing_subscription_hardening.sql
--
-- Purpose:
-- 1) Harden payment uniqueness and lookup performance.
-- 2) Link active subscription lifecycle to source payment.
-- 3) Normalize stale active subscriptions that are already expired by time.

ALTER TABLE payments
    ADD COLUMN IF NOT EXISTS provider_bill_id TEXT;

ALTER TABLE subscriptions
    ADD COLUMN IF NOT EXISTS source_payment_id UUID REFERENCES payments(id);

-- Keep the latest row for duplicate provider/payment identifiers before enforcing uniqueness.
WITH ranked AS (
    SELECT
        id,
        ROW_NUMBER() OVER (
            PARTITION BY provider, provider_payment_id
            ORDER BY created_at DESC, id DESC
        ) AS rn
    FROM payments
    WHERE provider_payment_id IS NOT NULL
      AND provider_payment_id <> ''
)
DELETE FROM payments p
USING ranked r
WHERE p.id = r.id
  AND r.rn > 1;

CREATE UNIQUE INDEX IF NOT EXISTS idx_payments_provider_payment_id_unique
    ON payments (provider, provider_payment_id)
    WHERE provider_payment_id IS NOT NULL AND provider_payment_id <> '';

CREATE INDEX IF NOT EXISTS idx_payments_provider_bill_id
    ON payments (provider_bill_id);

CREATE INDEX IF NOT EXISTS idx_payments_user_status_created
    ON payments (user_id, status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_subscriptions_source_payment_id
    ON subscriptions (source_payment_id);

UPDATE subscriptions
SET status = 'expired',
    auto_renew = FALSE,
    updated_at = NOW()
WHERE status = 'active'
  AND ends_at IS NOT NULL
  AND ends_at <= NOW();
