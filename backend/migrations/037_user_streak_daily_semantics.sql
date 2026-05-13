-- 037_user_streak_daily_semantics.sql
-- Convert streak semantics from "accepted submissions in a row" to "consecutive active days".
-- Adds an explicit last-active day marker and backfills streak values from historical accepted submissions.

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS streak_last_active_day DATE;

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
SET streak_last_active_day = sl.latest_day,
    streak = CASE
        WHEN sl.latest_day < ((NOW() AT TIME ZONE 'UTC')::date - 1) THEN 0
        ELSE sl.streak_days
    END,
    updated_at = NOW()
FROM streak_lengths sl
WHERE u.id = sl.user_id;

UPDATE users
SET streak = 0,
    streak_last_active_day = NULL,
    updated_at = NOW()
WHERE id NOT IN (
    SELECT DISTINCT s.user_id
    FROM submissions s
    WHERE s.status = 'accepted'
);
