-- 040_java_zero_core_content_remediation.sql
--
-- Remediation for support ticketed Java-content issues (2026-05-25):
-- 1) remove corrupted title tail fragments in java-zero-core lessons
-- 2) remove source URL lines from student-facing markdown/content
-- 3) fix corrupted practice short-intro where long scraped title leaked into statement

WITH java_lessons AS (
  SELECT
    l.id AS lesson_id,
    l.content_md,
    btrim(
      regexp_replace(
        regexp_replace(
          regexp_replace(l.title, E'\\s+Последнее\\s+обновление\\s*:\\s*[0-9]{2}\\.[0-9]{2}\\.[0-9]{4}.*$', '', 'i'),
          E'\\s+Назад\\b.*$',
          '',
          'i'
        ),
        E'\\s+(Содержание|Вперед)\\b.*$',
        '',
        'i'
      )
    ) AS clean_title
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'java-zero-core'
)
UPDATE lessons l
SET
  title = jl.clean_title,
  content_md = btrim(
    regexp_replace(
      regexp_replace(
        regexp_replace(
          l.content_md,
          E'(?m)^\\s*Source URL:\\s*https?://\\S+\\s*\\n?',
          '',
          'g'
        ),
        E'(?m)^\\s*(\\*\\*)?\\s*Источник\\s*:?\\s*(\\*\\*)?\\s*https?://\\S+\\s*\\n?',
        '',
        'g'
      ),
      E'\\n{3,}',
      E'\\n\\n',
      'g'
    )
  ),
  updated_at = NOW()
FROM java_lessons jl
WHERE l.id = jl.lesson_id
  AND (
    l.title IS DISTINCT FROM jl.clean_title
    OR l.content_md ~* E'(?m)^\\s*Source URL:\\s*https?://'
    OR l.content_md ~* E'(?m)^\\s*(\\*\\*)?\\s*Источник\\s*:?\\s*(\\*\\*)?\\s*https?://'
  );

WITH java_lessons AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'java-zero-core'
)
UPDATE lesson_blocks lb
SET
  content_md = btrim(
    regexp_replace(
      regexp_replace(
        lb.content_md,
        E'(?m)^\\s*(\\*\\*)?\\s*Источник\\s*:?\\s*(\\*\\*)?\\s*https?://\\S+\\s*\\n?',
        '',
        'g'
      ),
      E'\\n{3,}',
      E'\\n\\n',
      'g'
    )
  ),
  updated_at = NOW()
FROM java_lessons jl
WHERE lb.lesson_id = jl.lesson_id
  AND lb.block_type ILIKE 'theory'
  AND lb.content_md ~* E'(?m)^\\s*(\\*\\*)?\\s*Источник\\s*:?\\s*(\\*\\*)?\\s*https?://';

WITH java_lessons AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'java-zero-core'
)
UPDATE tasks t
SET
  statement_md = btrim(
    regexp_replace(
      regexp_replace(
        t.statement_md,
        E'(?m)^\\s*(\\*\\*)?\\s*Источник\\s*:?\\s*(\\*\\*)?\\s*https?://\\S+\\s*\\n?',
        '',
        'g'
      ),
      E'\\n{3,}',
      E'\\n\\n',
      'g'
    )
  ),
  updated_at = NOW()
FROM java_lessons jl
WHERE t.lesson_id = jl.lesson_id
  AND t.statement_md ~* E'(?m)^\\s*(\\*\\*)?\\s*Источник\\s*:?\\s*(\\*\\*)?\\s*https?://';

WITH java_lessons AS (
  SELECT
    l.id AS lesson_id,
    btrim(
      regexp_replace(
        regexp_replace(
          regexp_replace(l.title, E'\\s+Последнее\\s+обновление\\s*:\\s*[0-9]{2}\\.[0-9]{2}\\.[0-9]{4}.*$', '', 'i'),
          E'\\s+Назад\\b.*$',
          '',
          'i'
        ),
        E'\\s+(Содержание|Вперед)\\b.*$',
        '',
        'i'
      )
    ) AS clean_title
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'java-zero-core'
)
UPDATE lesson_blocks lb
SET
  content_md = regexp_replace(lb.content_md, E'(\\*\\*Коротко:\\*\\*\\s*практическая задача по теме «)[^»]+(»)', E'\\1' || jl.clean_title || E'\\2'),
  updated_at = NOW()
FROM java_lessons jl
WHERE lb.lesson_id = jl.lesson_id
  AND lb.block_type ILIKE 'practice'
  AND lb.content_md ~ E'(\\*\\*Коротко:\\*\\*\\s*практическая задача по теме «)[^»]+(»)'
  AND lb.content_md ~* E'(Последнее\\s+обновление:|Назад\\s+Содержание\\s+Вперед)';

WITH java_lessons AS (
  SELECT
    l.id AS lesson_id,
    btrim(
      regexp_replace(
        regexp_replace(
          regexp_replace(l.title, E'\\s+Последнее\\s+обновление\\s*:\\s*[0-9]{2}\\.[0-9]{2}\\.[0-9]{4}.*$', '', 'i'),
          E'\\s+Назад\\b.*$',
          '',
          'i'
        ),
        E'\\s+(Содержание|Вперед)\\b.*$',
        '',
        'i'
      )
    ) AS clean_title
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'java-zero-core'
)
UPDATE tasks t
SET
  statement_md = regexp_replace(t.statement_md, E'(\\*\\*Коротко:\\*\\*\\s*практическая задача по теме «)[^»]+(»)', E'\\1' || jl.clean_title || E'\\2'),
  updated_at = NOW()
FROM java_lessons jl
WHERE t.lesson_id = jl.lesson_id
  AND t.statement_md ~ E'(\\*\\*Коротко:\\*\\*\\s*практическая задача по теме «)[^»]+(»)'
  AND t.statement_md ~* E'(Последнее\\s+обновление:|Назад\\s+Содержание\\s+Вперед)';
