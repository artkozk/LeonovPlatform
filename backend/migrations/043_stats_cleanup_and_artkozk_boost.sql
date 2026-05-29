-- 043_stats_cleanup_and_artkozk_boost.sql
--
-- Цель:
-- 1) Подчистить мусорную статистику и выровнять XP/уровни по фактическим событиям.
-- 2) Гарантированно поднять пользователя artkozk на первое место лидерборда.

-- Удаляем неконсистентные XP-события:
-- если событие привязано к submission другого пользователя, оно не должно участвовать в рейтинге.
DELETE FROM xp_events x
WHERE x.submission_id IS NOT NULL
  AND EXISTS (
      SELECT 1
      FROM submissions s
      WHERE s.id = x.submission_id
        AND s.user_id <> x.user_id
  );

-- Нормализуем XP и level по чистому набору xp_events.
WITH xp_totals AS (
    SELECT
        u.id AS user_id,
        COALESCE(SUM(x.points), 0)::INTEGER AS xp_total
    FROM users u
    LEFT JOIN xp_events x ON x.user_id = u.id
    GROUP BY u.id
)
UPDATE users u
SET
    xp = xt.xp_total,
    level = GREATEST(1, FLOOR(SQRT(xt.xp_total / 120.0))::int + 1),
    updated_at = NOW()
FROM xp_totals xt
WHERE u.id = xt.user_id;

-- Пересчитываем streak в дневной семантике активности по accepted submissions.
WITH accepted_days AS (
    SELECT
        s.user_id,
        (s.created_at AT TIME ZONE 'UTC')::date AS day
    FROM submissions s
    WHERE s.status = 'accepted'
    GROUP BY s.user_id, (s.created_at AT TIME ZONE 'UTC')::date
),
ranked AS (
    SELECT
        ad.user_id,
        ad.day,
        ROW_NUMBER() OVER (PARTITION BY ad.user_id ORDER BY ad.day DESC) AS rn
    FROM accepted_days ad
),
grouped AS (
    SELECT
        r.user_id,
        r.day,
        (r.day + (r.rn || ' day')::interval)::date AS grp,
        r.rn
    FROM ranked r
),
latest AS (
    SELECT
        g.user_id,
        g.day AS latest_day,
        g.grp AS latest_group
    FROM grouped g
    WHERE g.rn = 1
),
streak_lengths AS (
    SELECT
        l.user_id,
        l.latest_day,
        COUNT(*)::int AS streak_days
    FROM latest l
    JOIN grouped g
      ON g.user_id = l.user_id
     AND g.grp = l.latest_group
    GROUP BY l.user_id, l.latest_day
)
UPDATE users u
SET
    streak_last_active_day = sl.latest_day,
    streak = CASE
        WHEN sl.latest_day < ((NOW() AT TIME ZONE 'UTC')::date - 1) THEN 0
        ELSE sl.streak_days
    END,
    updated_at = NOW()
FROM streak_lengths sl
WHERE u.id = sl.user_id;

UPDATE users
SET
    streak = 0,
    streak_last_active_day = NULL,
    updated_at = NOW()
WHERE id NOT IN (
    SELECT DISTINCT s.user_id
    FROM submissions s
    WHERE s.status = 'accepted'
);

-- Продуктовое требование: владелец аккаунта artkozk всегда первый в рейтинге.
UPDATE users
SET
    xp = 2147483647,
    level = 9999,
    streak = GREATEST(streak, 3650),
    streak_last_active_day = (NOW() AT TIME ZONE 'UTC')::date,
    updated_at = NOW()
WHERE LOWER(COALESCE(nickname, '')) = 'artkozk';
