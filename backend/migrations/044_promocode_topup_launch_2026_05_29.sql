-- 044_promocode_topup_launch_2026_05_29.sql
--
-- Цель:
-- 1) Сохранить пул одноразовых промокодов для ручного launch-тестирования после smoke-прогона.
-- 2) Добавить дополнительные коды без изменения уже существующих записей.

WITH
start_plan AS (
    SELECT id FROM plans WHERE code = 'pro' LIMIT 1
),
premium_plan AS (
    SELECT id FROM plans WHERE code = 'premium' LIMIT 1
),
seed(code, plan_code, description) AS (
    VALUES
        ('START26R2T4Y', 'pro', 'Top-up одноразовый промокод для Start'),
        ('START26M5N7P', 'pro', 'Top-up одноразовый промокод для Start'),
        ('START26V8C3X', 'pro', 'Top-up одноразовый промокод для Start'),
        ('START26L4J9K', 'pro', 'Top-up одноразовый промокод для Start'),
        ('START26H6Q1W', 'pro', 'Top-up одноразовый промокод для Start'),
        ('PREM26Q8W2E1', 'premium', 'Top-up одноразовый промокод для Premium'),
        ('PREM26T5Y7U3', 'premium', 'Top-up одноразовый промокод для Premium'),
        ('PREM26I4O9P2', 'premium', 'Top-up одноразовый промокод для Premium'),
        ('PREM26A7S3D8', 'premium', 'Top-up одноразовый промокод для Premium'),
        ('PREM26F6G2H5', 'premium', 'Top-up одноразовый промокод для Premium')
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
