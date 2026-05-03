-- 024_light_theme_only.sql
--
-- The product UI is light-only from 2026-05-02. Keep the historical
-- user_settings.theme column for backwards API compatibility, but normalize
-- stored values and future defaults so dark mode cannot leak into clients.

ALTER TABLE user_settings
    ALTER COLUMN theme SET DEFAULT 'light';

UPDATE user_settings
SET theme = 'light',
    updated_at = NOW()
WHERE theme <> 'light';
