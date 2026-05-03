const fs = require('fs');

const INPUT_PATH = 'C:/Users/Artemy/AppData/Local/Temp/python_course_platform_v10_import.json';
const OUT_PATH = 'C:/prog/Comercial/LeonovCarePlatform/backend/migrations/023_reseed_python_zero_v10_polished_full.sql';

const COURSE_OVERRIDE = {
  slug: 'python-zero',
  title: 'Python с нуля до Middle-ready backend-разработчика — v10 polished',
};

const FORBIDDEN_BODY_MARKERS = ['Шаблон', 'Подсказки', 'Эталон', 'Автотесты', 'Скрытые тесты'];
const FORBIDDEN_PHRASE = 'Для этого шага пока нет автопроверки';
const SUPPORTED_CHECKERS = new Set(['python_stdout', 'python_pytest', 'sql_query', 'http_api', 'ide_plugin', 'quiz_single']);

function readText(path) {
  return fs.readFileSync(path, 'utf8').replace(/\r\n/g, '\n').replace(/\r/g, '\n');
}

function normalizeSpaces(value) {
  return String(value ?? '')
    .replace(/\u00a0/g, ' ')
    .replace(/[ \t]+/g, ' ')
    .trim();
}

function sanitizeMultilineText(value) {
  return String(value ?? '').replace(/\r/g, '');
}

function toInt(value, fallback = 0) {
  const n = Number(value);
  if (!Number.isFinite(n)) return fallback;
  return Math.trunc(n);
}

function clampInt(value, min, max, fallback) {
  const n = toInt(value, fallback);
  return Math.min(max, Math.max(min, n));
}

function dollarQuote(input, tagBase) {
  const source = String(input ?? '');
  const normalizedTagBase = String(tagBase ?? 'q')
    .replace(/[^A-Za-z0-9_]/g, '_')
    .replace(/^([^A-Za-z_])/, '_$1');
  let tag = normalizedTagBase || 'q';
  let counter = 0;
  while (source.includes(`$${tag}$`)) {
    counter += 1;
    tag = `${normalizedTagBase}_${counter}`;
  }
  return `$${tag}$${source}$${tag}$`;
}

function normalizeBlockType(rawType) {
  const value = normalizeSpaces(rawType).toLowerCase();
  if (value === 'practice') return 'practice';
  if (value === 'quiz') return 'quiz';
  if (value === 'project') return 'project';
  if (value === 'summary') return 'summary';
  return 'theory';
}

function normalizeTaskLanguage(raw) {
  const value = normalizeSpaces(raw).toLowerCase();
  if (value === 'python3' || value === 'py') return 'python';
  if (value === 'postgresql' || value === 'postgres' || value === 'sqlite' || value === 'mysql' || value === 'sql') {
    return 'sql';
  }
  if (value === 'python') return 'python';
  return 'python';
}

function pickTaskLanguage(step) {
  const checker = step.checker || {};
  const checkerType = normalizeSpaces(checker.type).toLowerCase();
  if (checkerType === 'sql_query') return 'sql';
  if (checkerType === 'http_api') return 'python';
  if (checkerType === 'python_stdout' || checkerType === 'python_pytest') return 'python';
  if (checkerType === 'ide_plugin') {
    if (normalizeTaskLanguage(checker.language) === 'sql') return 'sql';
    return 'python';
  }
  const byCheckerLanguage = normalizeTaskLanguage(checker.language || checker.dialect);
  return byCheckerLanguage || 'python';
}

function ensureTrailingNewline(text) {
  const value = sanitizeMultilineText(text).replace(/\u0000/g, '');
  if (value === '') return '';
  return value.endsWith('\n') ? value : `${value}\n`;
}

function extractQuizQuestion(bodyMarkdown, fallbackTitle) {
  const body = sanitizeMultilineText(bodyMarkdown);
  const questionRegexes = [
    /(?:^|\n)\*\*Вопрос:\*\*\s*(.+)$/imu,
    /(?:^|\n)###\s*Вопрос\s*\n([\s\S]*?)(?=\n###\s|$)/iu,
    /(?:^|\n)Вопрос\s*:\s*(.+)$/imu,
  ];
  for (const re of questionRegexes) {
    const match = body.match(re);
    if (match && normalizeSpaces(match[1]) !== '') {
      return normalizeSpaces(match[1]);
    }
  }
  return normalizeSpaces(fallbackTitle) || 'Выберите правильный вариант';
}

function extractQuizOptions(bodyMarkdown) {
  const body = sanitizeMultilineText(bodyMarkdown);
  const lines = body.split('\n').map((line) => line.trim()).filter(Boolean);

  const options = [];
  for (const line of lines) {
    const alpha = line.match(/^([A-ZА-Я])\.\s+(.+)$/u);
    if (alpha) {
      options.push({
        id: String.fromCharCode(65 + options.length),
        text: normalizeSpaces(alpha[2]),
      });
      continue;
    }
  }

  if (options.length >= 2) return options;

  const bulletOptions = [];
  for (const line of lines) {
    const bullet = line.match(/^[-*]\s+(.+)$/);
    if (bullet) {
      bulletOptions.push(normalizeSpaces(bullet[1]));
    }
  }

  if (bulletOptions.length >= 2) {
    return bulletOptions.map((text, idx) => ({ id: String.fromCharCode(65 + idx), text }));
  }

  return [];
}

function resolveCorrectOptionIndex(correctOptionRaw, optionCount) {
  let index = toInt(correctOptionRaw, 0);
  if (index >= 0 && index < optionCount) {
    return index;
  }
  if (index >= 1 && index <= optionCount) {
    return index - 1;
  }
  return 0;
}

function buildQuizPayload(step, modulePosition, lessonPosition, stepPosition) {
  const checker = step.checker || {};
  const options = extractQuizOptions(step.body_markdown);
  if (options.length < 2) {
    throw new Error(`Quiz options parse failed at m${modulePosition} l${lessonPosition} s${stepPosition} (${step.title})`);
  }

  const correctIdx = resolveCorrectOptionIndex(checker.correct_option, options.length);
  const question = {
    id: 'q1',
    question: extractQuizQuestion(step.body_markdown, step.title),
    options,
    correctOptionId: options[correctIdx].id,
  };

  const explanation = normalizeSpaces(checker.explanation);
  if (explanation) {
    question.explanation = explanation;
  }

  const payload = {
    type: 'single_choice',
    questions: [question],
  };

  if (explanation) {
    payload.explanation = explanation;
  }

  return payload;
}

function validateStep(step, modulePosition, lessonPosition, stepPosition) {
  const stepType = normalizeBlockType(step.type);
  const checker = step.checker || null;
  const checkerType = normalizeSpaces(checker?.type).toLowerCase();
  const body = sanitizeMultilineText(step.body_markdown);

  if (body.includes(FORBIDDEN_PHRASE)) {
    throw new Error(`Forbidden phrase in body at m${modulePosition} l${lessonPosition} s${stepPosition}: ${FORBIDDEN_PHRASE}`);
  }

  for (const marker of FORBIDDEN_BODY_MARKERS) {
    if (body.includes(marker)) {
      throw new Error(`Forbidden marker "${marker}" in body at m${modulePosition} l${lessonPosition} s${stepPosition}`);
    }
  }

  if (stepType === 'practice') {
    if (!checker) {
      throw new Error(`Practice step without checker at m${modulePosition} l${lessonPosition} s${stepPosition}`);
    }
    if (!SUPPORTED_CHECKERS.has(checkerType)) {
      throw new Error(`Unsupported checker type "${checkerType}" at m${modulePosition} l${lessonPosition} s${stepPosition}`);
    }
  }

  if (stepType === 'project') {
    const aiReview = step.ai_review_config || {};
    if (!checker) {
      throw new Error(`Project step without checker at m${modulePosition} l${lessonPosition} s${stepPosition}`);
    }
    if (checkerType !== 'ide_plugin') {
      throw new Error(`Project step checker must be ide_plugin at m${modulePosition} l${lessonPosition} s${stepPosition}`);
    }
    if (!aiReview.enabled) {
      throw new Error(`Project step requires ai_review_config.enabled=true at m${modulePosition} l${lessonPosition} s${stepPosition}`);
    }
  }

  if (stepType === 'quiz') {
    if (!checker || checkerType !== 'quiz_single') {
      throw new Error(`Quiz step must have checker.type=quiz_single at m${modulePosition} l${lessonPosition} s${stepPosition}`);
    }
  }
}

function buildSourcePolicy(step, language) {
  const checker = step.checker || {};
  const checkerType = normalizeSpaces(checker.type).toLowerCase();
  const hints = Array.isArray(step.hints)
    ? step.hints.map((item) => normalizeSpaces(item)).filter(Boolean)
    : [];

  return {
    language,
    import_source: 'python_course_platform_v10_import.json',
    checker_type: checkerType,
    checker,
    hints,
    hints_visibility: 'button_or_after_failed_attempts',
    ai_hint_config: step.ai_hint_config || {
      mode: 'socratic',
      no_full_solution: true,
    },
    ai_review_config: step.ai_review_config || null,
    admin_notes: step.admin_notes || null,
  };
}

function buildTaskTests(step, task) {
  const checker = step.checker || {};
  const checkerType = normalizeSpaces(checker.type).toLowerCase();

  if (checkerType === 'python_stdout') {
    const tests = Array.isArray(checker.tests) ? checker.tests : [];
    return tests.map((item, index) => ({
      inputData: sanitizeMultilineText(item.input || ''),
      expectedOutput: sanitizeMultilineText(item.expected_stdout || ''),
      isHidden: String(item.visibility || 'public').toLowerCase() !== 'public',
      position: index + 1,
    }));
  }

  if (checkerType === 'sql_query') {
    const checks = Array.isArray(checker.checks) ? checker.checks : [];
    return checks.map((item, index) => {
      const expectedRaw = normalizeSpaces(item.expected).toLowerCase() === 'match_solution_behavior'
        ? task.solutionCode
        : sanitizeMultilineText(item.expected || task.solutionCode);
      return {
        inputData: sanitizeMultilineText(checker.init_sql || ''),
        expectedOutput: expectedRaw,
        isHidden: String(item.visibility || 'hidden').toLowerCase() !== 'public',
        position: index + 1,
      };
    });
  }

  return [];
}

function buildLessonContent(lesson, moduleTitle) {
  const lines = [];
  lines.push(`Материалы урока "${normalizeSpaces(lesson.title) || 'Урок'}".`);
  if (normalizeSpaces(moduleTitle)) {
    lines.push(`Модуль: ${normalizeSpaces(moduleTitle)}.`);
  }
  const hours = Number(lesson.estimated_hours || 0);
  if (Number.isFinite(hours) && hours > 0) {
    lines.push(`Оценка времени: ${hours} ч.`);
  }
  if (Array.isArray(lesson.outcomes) && lesson.outcomes.length > 0) {
    const cleanOutcomes = lesson.outcomes.map((item) => normalizeSpaces(item)).filter(Boolean);
    if (cleanOutcomes.length > 0) {
      lines.push('Результаты урока:');
      for (const outcome of cleanOutcomes) {
        lines.push(`- ${outcome}`);
      }
    }
  }
  return lines.join('\n');
}

function ensureUniqueTaskTitles(course) {
  for (const moduleItem of course.modules) {
    for (const lesson of moduleItem.lessons) {
      const counters = new Map();
      for (const block of lesson.blocks) {
        if (!block.task) continue;
        const base = normalizeSpaces(block.task.title) || `Практика ${block.position}`;
        const count = (counters.get(base) || 0) + 1;
        counters.set(base, count);
        block.task.title = count === 1 ? base : `${base} (шаг ${block.position})`;
      }
    }
  }
}

function prepareCourse(raw) {
  const modules = (raw.modules || [])
    .slice()
    .sort((a, b) => toInt(a.order, 0) - toInt(b.order, 0))
    .map((moduleItem, moduleIdx) => {
      const modulePosition = toInt(moduleItem.order, moduleIdx + 1);
      const moduleTitle = normalizeSpaces(moduleItem.title) || `Модуль ${modulePosition}`;

      const lessons = (moduleItem.lessons || [])
        .slice()
        .sort((a, b) => toInt(a.order, 0) - toInt(b.order, 0))
        .map((lesson, lessonIdx) => {
          const lessonPosition = toInt(lesson.order, lessonIdx + 1);
          const lessonTitle = normalizeSpaces(lesson.title) || `Урок ${lessonPosition}`;

          const blocks = (lesson.steps || [])
            .slice()
            .sort((a, b) => toInt(a.order, 0) - toInt(b.order, 0))
            .map((step, stepIdx) => {
              const position = toInt(step.order, stepIdx + 1);
              validateStep(step, modulePosition, lessonPosition, position);

              const blockType = normalizeBlockType(step.type);
              const title = normalizeSpaces(step.title) || `Шаг ${position}`;
              const contentMd = sanitizeMultilineText(step.body_markdown).trim();

              let quizPayload = null;
              if (blockType === 'quiz') {
                quizPayload = buildQuizPayload(step, modulePosition, lessonPosition, position);
              }

              let task = null;
              if (blockType === 'practice' || blockType === 'project') {
                const language = pickTaskLanguage(step);
                const starterCode = ensureTrailingNewline(step.editor_initial_code || '');
                const solutionCode = ensureTrailingNewline(step.solution_code || '');
                const sourcePolicy = buildSourcePolicy(step, language);

                task = {
                  title,
                  statementMd: contentMd,
                  starterCode,
                  solutionCode,
                  difficulty: clampInt(step.difficulty, 1, 10, 2),
                  xpReward: Math.max(10, toInt(step.xp, 50) || 50),
                  topic: `${moduleTitle} — ${lessonTitle}`,
                  language,
                  sourcePolicy,
                };
                task.tests = buildTaskTests(step, task);
              }

              return {
                position,
                blockType,
                title,
                contentMd,
                quizPayload,
                task,
              };
            });

          return {
            lessonPosition,
            lessonTitle,
            lessonContent: buildLessonContent(lesson, moduleTitle),
            blocks,
          };
        });

      return {
        modulePosition,
        moduleTitle,
        lessons,
      };
    });

  const courseTitle = normalizeSpaces(COURSE_OVERRIDE.title || raw?.course?.title) || 'Python с нуля';
  const courseDescription = normalizeSpaces(raw?.course?.description) || 'Практический курс по Python.';

  const course = {
    slug: COURSE_OVERRIDE.slug,
    title: courseTitle,
    description: courseDescription,
    modules,
  };

  ensureUniqueTaskTitles(course);
  return course;
}

function buildMigrationSql(course) {
  const modules = course.modules.slice().sort((a, b) => a.modulePosition - b.modulePosition);

  let sql = '';
  sql += '-- 023_reseed_python_zero_v10_polished_full.sql\n';
  sql += '-- Generated from python_course_platform_v10_import.json\n';
  sql += '-- Purpose: fully reseed python-zero by v10 import with practice/project checkers and hidden quiz answers.\n';
  sql += `-- Generated at: ${new Date().toISOString()}\n\n`;

  sql += 'ALTER TABLE tasks DROP CONSTRAINT IF EXISTS chk_tasks_language;\n';
  sql += "ALTER TABLE tasks ADD CONSTRAINT chk_tasks_language CHECK (language IN ('java', 'python', 'python3', 'py', 'sql'));\n\n";

  sql += 'INSERT INTO courses(slug, title, description, is_published)\n';
  sql += `VALUES ('${course.slug}', ${dollarQuote(course.title, 'course_title')}, ${dollarQuote(course.description, 'course_desc')}, TRUE)\n`;
  sql += 'ON CONFLICT (slug) DO UPDATE\n';
  sql += 'SET title = EXCLUDED.title,\n';
  sql += '    description = EXCLUDED.description,\n';
  sql += '    is_published = TRUE,\n';
  sql += '    updated_at = NOW();\n\n';

  sql += 'WITH course_ref AS (\n';
  sql += `  SELECT id AS course_id FROM courses WHERE slug = '${course.slug}'\n`;
  sql += ')\n';
  sql += 'UPDATE lesson_blocks lb\n';
  sql += 'SET is_published = FALSE,\n';
  sql += '    updated_at = NOW()\n';
  sql += 'FROM lessons l\n';
  sql += 'JOIN modules m ON m.id = l.module_id\n';
  sql += 'JOIN course_ref cr ON cr.course_id = m.course_id\n';
  sql += 'WHERE lb.lesson_id = l.id;\n\n';

  sql += 'WITH course_ref AS (\n';
  sql += `  SELECT id AS course_id FROM courses WHERE slug = '${course.slug}'\n`;
  sql += ')\n';
  sql += 'UPDATE tasks t\n';
  sql += 'SET is_published = FALSE,\n';
  sql += '    updated_at = NOW()\n';
  sql += 'FROM lessons l\n';
  sql += 'JOIN modules m ON m.id = l.module_id\n';
  sql += 'JOIN course_ref cr ON cr.course_id = m.course_id\n';
  sql += 'WHERE t.lesson_id = l.id;\n\n';

  sql += 'WITH course_ref AS (\n';
  sql += `  SELECT id AS course_id FROM courses WHERE slug = '${course.slug}'\n`;
  sql += ')\n';
  sql += 'UPDATE lessons l\n';
  sql += 'SET is_published = FALSE,\n';
  sql += '    updated_at = NOW()\n';
  sql += 'FROM modules m\n';
  sql += 'JOIN course_ref cr ON cr.course_id = m.course_id\n';
  sql += 'WHERE l.module_id = m.id;\n\n';

  sql += 'WITH course_ref AS (\n';
  sql += `  SELECT id AS course_id FROM courses WHERE slug = '${course.slug}'\n`;
  sql += '), module_seed(position, title) AS (\n';
  sql += '  VALUES\n';
  for (let i = 0; i < modules.length; i += 1) {
    const moduleItem = modules[i];
    const suffix = i + 1 < modules.length ? ',' : '';
    sql += `  (${moduleItem.modulePosition}, ${dollarQuote(moduleItem.moduleTitle, `m${moduleItem.modulePosition}_title`)})${suffix}\n`;
  }
  sql += ')\n';
  sql += 'INSERT INTO modules(course_id, title, position)\n';
  sql += 'SELECT cr.course_id, ms.title, ms.position\n';
  sql += 'FROM course_ref cr\n';
  sql += 'CROSS JOIN module_seed ms\n';
  sql += 'ON CONFLICT (course_id, position) DO UPDATE\n';
  sql += 'SET title = EXCLUDED.title,\n';
  sql += '    updated_at = NOW();\n\n';

  for (const moduleItem of modules) {
    const lessons = moduleItem.lessons.slice().sort((a, b) => a.lessonPosition - b.lessonPosition);

    sql += `-- Module ${moduleItem.modulePosition}: ${moduleItem.moduleTitle}\n`;
    sql += 'WITH module_ref AS (\n';
    sql += '  SELECT m.id AS module_id\n';
    sql += '  FROM modules m\n';
    sql += '  JOIN courses c ON c.id = m.course_id\n';
    sql += `  WHERE c.slug = '${course.slug}' AND m.position = ${moduleItem.modulePosition}\n`;
    sql += '), lesson_seed(position, title, content_md) AS (\n';
    sql += '  VALUES\n';

    for (let i = 0; i < lessons.length; i += 1) {
      const lesson = lessons[i];
      const suffix = i + 1 < lessons.length ? ',' : '';
      sql += `  (${lesson.lessonPosition}, ${dollarQuote(
        lesson.lessonTitle,
        `m${moduleItem.modulePosition}_l${lesson.lessonPosition}_title`
      )}, ${dollarQuote(lesson.lessonContent, `m${moduleItem.modulePosition}_l${lesson.lessonPosition}_content`)})${suffix}\n`;
    }

    sql += ')\n';
    sql += 'INSERT INTO lessons(module_id, title, content_md, position, is_published)\n';
    sql += 'SELECT mr.module_id, ls.title, ls.content_md, ls.position, TRUE\n';
    sql += 'FROM module_ref mr\n';
    sql += 'CROSS JOIN lesson_seed ls\n';
    sql += 'ON CONFLICT (module_id, position) DO UPDATE\n';
    sql += 'SET title = EXCLUDED.title,\n';
    sql += '    content_md = EXCLUDED.content_md,\n';
    sql += '    is_published = TRUE,\n';
    sql += '    updated_at = NOW();\n\n';

    for (const lesson of lessons) {
      const lessonPrefix = `m${moduleItem.modulePosition}_l${lesson.lessonPosition}`;
      const taskBlocks = lesson.blocks.filter((block) => (block.blockType === 'practice' || block.blockType === 'project') && block.task);

      sql += `-- ${lessonPrefix}: ${lesson.lessonTitle}\n`;
      sql += 'WITH lesson_ref AS (\n';
      sql += '  SELECT l.id AS lesson_id\n';
      sql += '  FROM lessons l\n';
      sql += '  JOIN modules m ON m.id = l.module_id\n';
      sql += '  JOIN courses c ON c.id = m.course_id\n';
      sql += `  WHERE c.slug = '${course.slug}' AND m.position = ${moduleItem.modulePosition} AND l.position = ${lesson.lessonPosition}\n`;
      sql += ')\n';
      sql += 'UPDATE lesson_blocks lb\n';
      sql += 'SET is_published = FALSE,\n';
      sql += '    updated_at = NOW()\n';
      sql += 'FROM lesson_ref lr\n';
      sql += 'WHERE lb.lesson_id = lr.lesson_id;\n\n';

      sql += 'WITH lesson_ref AS (\n';
      sql += '  SELECT l.id AS lesson_id\n';
      sql += '  FROM lessons l\n';
      sql += '  JOIN modules m ON m.id = l.module_id\n';
      sql += '  JOIN courses c ON c.id = m.course_id\n';
      sql += `  WHERE c.slug = '${course.slug}' AND m.position = ${moduleItem.modulePosition} AND l.position = ${lesson.lessonPosition}\n`;
      sql += ')\n';
      sql += 'UPDATE tasks t\n';
      sql += 'SET is_published = FALSE,\n';
      sql += '    updated_at = NOW()\n';
      sql += 'FROM lesson_ref lr\n';
      sql += 'WHERE t.lesson_id = lr.lesson_id;\n\n';

      if (taskBlocks.length > 0) {
        sql += 'WITH lesson_ref AS (\n';
        sql += '  SELECT l.id AS lesson_id\n';
        sql += '  FROM lessons l\n';
        sql += '  JOIN modules m ON m.id = l.module_id\n';
        sql += '  JOIN courses c ON c.id = m.course_id\n';
        sql += `  WHERE c.slug = '${course.slug}' AND m.position = ${moduleItem.modulePosition} AND l.position = ${lesson.lessonPosition}\n`;
        sql += '), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (\n';
        sql += '  VALUES\n';

        for (let i = 0; i < taskBlocks.length; i += 1) {
          const block = taskBlocks[i];
          const task = block.task;
          const suffix = i + 1 < taskBlocks.length ? ',' : '';
          sql += `  (${dollarQuote(task.title, `${lessonPrefix}_t${block.position}_title`)}, ${dollarQuote(
            task.statementMd,
            `${lessonPrefix}_t${block.position}_stmt`
          )}, ${dollarQuote(task.starterCode, `${lessonPrefix}_t${block.position}_starter`)}, ${dollarQuote(
            task.solutionCode,
            `${lessonPrefix}_t${block.position}_solution`
          )}, ${task.difficulty}, ${task.xpReward}, ${dollarQuote(
            task.topic,
            `${lessonPrefix}_t${block.position}_topic`
          )}, ${dollarQuote(task.language, `${lessonPrefix}_t${block.position}_lang`)}, ${dollarQuote(
            JSON.stringify(task.sourcePolicy),
            `${lessonPrefix}_t${block.position}_policy`
          )}::jsonb)${suffix}\n`;
        }

        sql += ')\n';
        sql += 'INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)\n';
        sql += 'SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE\n';
        sql += 'FROM lesson_ref lr\n';
        sql += 'CROSS JOIN task_seed ts\n';
        sql += 'ON CONFLICT (lesson_id, title) DO UPDATE\n';
        sql += 'SET statement_md = EXCLUDED.statement_md,\n';
        sql += '    starter_code = EXCLUDED.starter_code,\n';
        sql += '    solution_code = EXCLUDED.solution_code,\n';
        sql += '    difficulty = EXCLUDED.difficulty,\n';
        sql += '    xp_reward = EXCLUDED.xp_reward,\n';
        sql += '    topic = EXCLUDED.topic,\n';
        sql += '    language = EXCLUDED.language,\n';
        sql += '    source_policy = EXCLUDED.source_policy,\n';
        sql += '    is_published = TRUE,\n';
        sql += '    updated_at = NOW();\n\n';

        sql += 'WITH lesson_ref AS (\n';
        sql += '  SELECT l.id AS lesson_id\n';
        sql += '  FROM lessons l\n';
        sql += '  JOIN modules m ON m.id = l.module_id\n';
        sql += '  JOIN courses c ON c.id = m.course_id\n';
        sql += `  WHERE c.slug = '${course.slug}' AND m.position = ${moduleItem.modulePosition} AND l.position = ${lesson.lessonPosition}\n`;
        sql += '), target_tasks AS (\n';
        sql += '  SELECT t.id\n';
        sql += '  FROM tasks t\n';
        sql += '  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id\n';
        sql += '  WHERE t.title IN (\n';
        for (let i = 0; i < taskBlocks.length; i += 1) {
          const block = taskBlocks[i];
          const suffix = i + 1 < taskBlocks.length ? ',' : '';
          sql += `    ${dollarQuote(block.task.title, `${lessonPrefix}_ttitle_${block.position}`)}${suffix}\n`;
        }
        sql += '  )\n';
        sql += ')\n';
        sql += 'DELETE FROM task_test_cases tc\n';
        sql += 'USING target_tasks tt\n';
        sql += 'WHERE tc.task_id = tt.id;\n\n';

        const allTests = [];
        for (const block of taskBlocks) {
          for (const test of block.task.tests || []) {
            allTests.push({
              taskTitle: block.task.title,
              blockPosition: block.position,
              inputData: test.inputData,
              expectedOutput: test.expectedOutput,
              isHidden: test.isHidden,
              position: test.position,
            });
          }
        }

        if (allTests.length > 0) {
          sql += 'WITH lesson_ref AS (\n';
          sql += '  SELECT l.id AS lesson_id\n';
          sql += '  FROM lessons l\n';
          sql += '  JOIN modules m ON m.id = l.module_id\n';
          sql += '  JOIN courses c ON c.id = m.course_id\n';
          sql += `  WHERE c.slug = '${course.slug}' AND m.position = ${moduleItem.modulePosition} AND l.position = ${lesson.lessonPosition}\n`;
          sql += '), task_lookup AS (\n';
          sql += '  SELECT t.id AS task_id, t.title\n';
          sql += '  FROM tasks t\n';
          sql += '  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id\n';
          sql += '), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (\n';
          sql += '  VALUES\n';

          for (let i = 0; i < allTests.length; i += 1) {
            const item = allTests[i];
            const suffix = i + 1 < allTests.length ? ',' : '';
            sql += `  (${dollarQuote(item.taskTitle, `${lessonPrefix}_test_${item.blockPosition}_${item.position}_title`)}, ${dollarQuote(
              item.inputData,
              `${lessonPrefix}_test_${item.blockPosition}_${item.position}_input`
            )}, ${dollarQuote(
              item.expectedOutput,
              `${lessonPrefix}_test_${item.blockPosition}_${item.position}_expected`
            )}, ${item.isHidden ? 'TRUE' : 'FALSE'}, ${item.position})${suffix}\n`;
          }

          sql += ')\n';
          sql += 'INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)\n';
          sql += 'SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position\n';
          sql += 'FROM test_seed ts\n';
          sql += 'JOIN task_lookup tl ON tl.title = ts.task_title\n';
          sql += 'ORDER BY tl.task_id, ts.position;\n\n';
        }
      }

      sql += 'WITH lesson_ref AS (\n';
      sql += '  SELECT l.id AS lesson_id\n';
      sql += '  FROM lessons l\n';
      sql += '  JOIN modules m ON m.id = l.module_id\n';
      sql += '  JOIN courses c ON c.id = m.course_id\n';
      sql += `  WHERE c.slug = '${course.slug}' AND m.position = ${moduleItem.modulePosition} AND l.position = ${lesson.lessonPosition}\n`;
      sql += '), task_lookup AS (\n';
      sql += '  SELECT t.title, t.id AS task_id\n';
      sql += '  FROM tasks t\n';
      sql += '  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id\n';
      sql += '), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (\n';
      sql += '  VALUES\n';

      for (let i = 0; i < lesson.blocks.length; i += 1) {
        const block = lesson.blocks[i];
        const suffix = i + 1 < lesson.blocks.length ? ',' : '';
        const taskTitleSql = block.task
          ? dollarQuote(block.task.title, `${lessonPrefix}_b${block.position}_task_title`)
          : 'NULL';
        const quizSql = block.quizPayload
          ? `${dollarQuote(JSON.stringify(block.quizPayload), `${lessonPrefix}_b${block.position}_quiz`)}::jsonb`
          : 'NULL::jsonb';

        sql += `  (${block.position}, ${dollarQuote(
          block.blockType,
          `${lessonPrefix}_b${block.position}_type`
        )}, ${dollarQuote(block.title, `${lessonPrefix}_b${block.position}_title`)}, ${dollarQuote(
          block.contentMd,
          `${lessonPrefix}_b${block.position}_content`
        )}, ${taskTitleSql}, ${quizSql})${suffix}\n`;
      }

      sql += '), resolved AS (\n';
      sql += '  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload\n';
      sql += '  FROM block_seed bs\n';
      sql += '  LEFT JOIN task_lookup tl ON tl.title = bs.task_title\n';
      sql += ')\n';
      sql += 'INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)\n';
      sql += 'SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE\n';
      sql += 'FROM lesson_ref lr\n';
      sql += 'CROSS JOIN resolved r\n';
      sql += 'ON CONFLICT (lesson_id, position) DO UPDATE\n';
      sql += 'SET block_type = EXCLUDED.block_type,\n';
      sql += '    title = EXCLUDED.title,\n';
      sql += '    content_md = EXCLUDED.content_md,\n';
      sql += '    task_id = EXCLUDED.task_id,\n';
      sql += '    quiz_payload = EXCLUDED.quiz_payload,\n';
      sql += '    is_published = TRUE,\n';
      sql += '    updated_at = NOW();\n\n';
    }
  }

  return sql;
}

function summarize(course) {
  const stats = {
    modules: course.modules.length,
    lessons: 0,
    blocks: 0,
    tasks: 0,
    tests: 0,
    byType: {},
    byChecker: {},
  };

  for (const moduleItem of course.modules) {
    stats.lessons += moduleItem.lessons.length;
    for (const lesson of moduleItem.lessons) {
      stats.blocks += lesson.blocks.length;
      for (const block of lesson.blocks) {
        stats.byType[block.blockType] = (stats.byType[block.blockType] || 0) + 1;
        if (!block.task) continue;
        stats.tasks += 1;
        stats.tests += (block.task.tests || []).length;
        const checkerType = normalizeSpaces(block.task.sourcePolicy?.checker_type).toLowerCase() || 'unknown';
        stats.byChecker[checkerType] = (stats.byChecker[checkerType] || 0) + 1;
      }
    }
  }

  return stats;
}

function main() {
  const raw = JSON.parse(readText(INPUT_PATH));
  const course = prepareCourse(raw);
  const sql = buildMigrationSql(course);
  fs.writeFileSync(OUT_PATH, sql, 'utf8');

  const stats = summarize(course);
  console.log(`Generated: ${OUT_PATH}`);
  console.log(`Modules: ${stats.modules}`);
  console.log(`Lessons: ${stats.lessons}`);
  console.log(`Blocks: ${stats.blocks}`);
  console.log(`Tasks: ${stats.tasks}`);
  console.log(`Task tests: ${stats.tests}`);
  console.log('By type:', stats.byType);
  console.log('By checker:', stats.byChecker);
}

main();
