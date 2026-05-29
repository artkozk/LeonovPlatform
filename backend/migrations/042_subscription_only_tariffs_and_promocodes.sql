-- 042_subscription_only_tariffs_and_promocodes.sql
--
-- Цель:
-- 1) Перевести продукт на модель "все материалы только по подписке".
-- 2) Сделать минимальный платный план с доступом ровно к одному курсу.
-- 3) Добавить одноразовые промокоды для бесплатного тестирования подписок.

ALTER TABLE plans
    ADD COLUMN IF NOT EXISTS max_courses INTEGER;

ALTER TABLE plans
    ADD COLUMN IF NOT EXISTS is_public BOOLEAN NOT NULL DEFAULT TRUE;

UPDATE plans
SET
    title = 'Без подписки',
    description = 'Технический план без доступа к материалам. Для обучения нужна активная подписка.',
    price_rub = 0,
    daily_submission_limit = 0,
    has_priority_queue = FALSE,
    has_personal_hints = FALSE,
    has_extended_analytics = FALSE,
    max_courses = 0,
    is_public = FALSE,
    updated_at = NOW()
WHERE code = 'free';

UPDATE plans
SET
    title = 'Start',
    description = 'Минимальная подписка: доступ к одному курсу, практике и автопроверке.',
    max_courses = 1,
    is_public = TRUE,
    updated_at = NOW()
WHERE code = 'pro';

UPDATE plans
SET
    title = 'Premium',
    description = 'Полный доступ ко всем курсам, расширенной практике и AI-подсказкам.',
    max_courses = NULL,
    is_public = TRUE,
    updated_at = NOW()
WHERE code = 'premium';

CREATE TABLE IF NOT EXISTS promo_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    plan_id UUID NOT NULL REFERENCES plans(id),
    description TEXT NOT NULL DEFAULT '',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    redeemed_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    redeemed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_promo_codes_upper_code_unique
    ON promo_codes ((UPPER(code)));

WITH
start_plan AS (
    SELECT id FROM plans WHERE code = 'pro' LIMIT 1
),
premium_plan AS (
    SELECT id FROM plans WHERE code = 'premium' LIMIT 1
),
seed(code, plan_code, description) AS (
    VALUES
        ('START26A1B2C', 'pro', 'Тестовый одноразовый промокод для Start'),
        ('START26D3E4F', 'pro', 'Тестовый одноразовый промокод для Start'),
        ('START26G5H6J', 'pro', 'Тестовый одноразовый промокод для Start'),
        ('START26K7L8M', 'pro', 'Тестовый одноразовый промокод для Start'),
        ('START26N9P0Q', 'pro', 'Тестовый одноразовый промокод для Start'),
        ('PREM26R1S2T3', 'premium', 'Тестовый одноразовый промокод для Premium'),
        ('PREM26U4V5W6', 'premium', 'Тестовый одноразовый промокод для Premium'),
        ('PREM26X7Y8Z9', 'premium', 'Тестовый одноразовый промокод для Premium'),
        ('PREM26A0B1C2', 'premium', 'Тестовый одноразовый промокод для Premium'),
        ('PREM26D3E4F5', 'premium', 'Тестовый одноразовый промокод для Premium')
)
INSERT INTO promo_codes(code, plan_id, description, is_active)
SELECT
    s.code,
    CASE
        WHEN s.plan_code = 'pro' THEN (SELECT id FROM start_plan)
        ELSE (SELECT id FROM premium_plan)
    END AS plan_id,
    s.description,
    TRUE
FROM seed s
ON CONFLICT (code) DO UPDATE
SET
    plan_id = EXCLUDED.plan_id,
    description = EXCLUDED.description,
    is_active = TRUE,
    updated_at = NOW();
