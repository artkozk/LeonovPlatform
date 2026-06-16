-- 045_promocode_unlimited_20_codes_2026_06_17.sql
--
-- Цель:
-- 1) Поддержать многократное использование фиксированного набора промокодов.
-- 2) Сохранять одноразовый режим для других промокодов по умолчанию.
--
-- Что меняется:
-- - добавляется флаг is_reusable в promo_codes (по умолчанию false),
-- - 20 целевых кодов переводятся в is_reusable=true,
-- - очищаются исторические redemption-поля для этих кодов.

ALTER TABLE promo_codes
    ADD COLUMN IF NOT EXISTS is_reusable BOOLEAN NOT NULL DEFAULT FALSE;

WITH target_codes(code) AS (
    VALUES
        ('START26A1B2C'),
        ('START26D3E4F'),
        ('START26G5H6J'),
        ('START26K7L8M'),
        ('START26N9P0Q'),
        ('PREM26R1S2T3'),
        ('PREM26U4V5W6'),
        ('PREM26X7Y8Z9'),
        ('PREM26A0B1C2'),
        ('PREM26D3E4F5'),
        ('START26R2T4Y'),
        ('START26M5N7P'),
        ('START26V8C3X'),
        ('START26L4J9K'),
        ('START26H6Q1W'),
        ('PREM26Q8W2E1'),
        ('PREM26T5Y7U3'),
        ('PREM26I4O9P2'),
        ('PREM26A7S3D8'),
        ('PREM26F6G2H5')
)
UPDATE promo_codes pc
SET
    is_reusable = TRUE,
    redeemed_by_user_id = NULL,
    redeemed_at = NULL,
    updated_at = NOW()
FROM target_codes tc
WHERE UPPER(pc.code) = tc.code;
