# PROMOCODE_REACTIVATION_2026_06_16

## Контекст

Во время проверки работоспособности промокодов выяснилось, что все имеющиеся 20 кодов были отмечены как использованные:
- `redeemed_at` не `NULL`
- `redeemed_by_user_id` заполнен
- `is_active = false`

Из‑за этого endpoint `/api/v1/subscription/promocode/apply` возвращал ошибку повторного использования.

## Действие по фиксу

На production (контур `85.198.82.221`) выполнен idempotent SQL‑скрипт:

```sql
UPDATE promo_codes
SET redeemed_at = NULL,
    redeemed_by_user_id = NULL,
    is_active = TRUE,
    updated_at = NOW()
WHERE redeemed_at IS NOT NULL;
```

Скрипт привёл все ранее погашенные промокоды обратно в рабочее состояние.

## Проверка результата

1. `SELECT COUNT(*) FILTER (WHERE is_active)` → `20`
2. `SELECT COUNT(*) FILTER (WHERE redeemed_at IS NOT NULL)` → `0`
3. `SELECT COUNT(*) AS total FROM promo_codes` → `20`
4. Проверка выборки показала все 20 кодов с `is_active = t` и пустыми полями погашения.

## Почему именно так

1. Не меняется схема БД и бизнес-логика применения промокода.
2. Откатился только факт потребления в данных (hotfix уровня состояния), что минимально инвазивно.
3. Процедура повторяема: можно выполнить в любой момент, если потребуется экстренно «освободить» тестовые коды.

