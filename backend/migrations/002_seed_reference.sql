-- 002_seed_reference.sql

INSERT INTO plans (code, title, description, price_rub, daily_submission_limit, has_priority_queue, has_personal_hints, has_extended_analytics)
VALUES
('free', 'Free', 'Базовый доступ к первым урокам и ограничение на отправки в день', 0, 20, FALSE, FALSE, FALSE),
('pro', 'Pro', 'Полный доступ к задачам и расширенная статистика', 1290, 200, TRUE, FALSE, TRUE),
('premium', 'Premium', 'Все возможности Pro + персональные подсказки и ранний доступ', 2490, 500, TRUE, TRUE, TRUE)
ON CONFLICT (code) DO UPDATE
SET title = EXCLUDED.title,
    description = EXCLUDED.description,
    price_rub = EXCLUDED.price_rub,
    daily_submission_limit = EXCLUDED.daily_submission_limit,
    has_priority_queue = EXCLUDED.has_priority_queue,
    has_personal_hints = EXCLUDED.has_personal_hints,
    has_extended_analytics = EXCLUDED.has_extended_analytics,
    updated_at = NOW();

INSERT INTO achievements (code, title, description)
VALUES
('first_task', 'Первая задача', 'Вы решили первую задачу'),
('ten_clean', '10 без ошибок', 'Вы решили 10 задач подряд без ошибок'),
('level_10', 'Уровень 10', 'Вы достигли 10 уровня')
ON CONFLICT (code) DO UPDATE
SET title = EXCLUDED.title,
    description = EXCLUDED.description;
