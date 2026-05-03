const fs = require('fs');
const path = require('path');

const INPUT_PATH = path.resolve(__dirname, '../../материалы/v18_STRICT_PEDAGOGY/course_import.json');
const OUT_PATH = path.resolve(__dirname, '../migrations/026_reseed_python_zero_v18_strict_pedagogy.sql');
const COURSE_SLUG = 'python-zero';

const SUPPORTED_CHECKERS = new Set([
  'python_stdout',
  'python_pytest',
  'sql_query',
  'http_api',
  'ide_plugin',
  'quiz_single',
]);

function readText(filePath) {
  return fs.readFileSync(filePath, 'utf8').replace(/\r\n/g, '\n').replace(/\r/g, '\n');
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

function ensureTrailingNewline(value) {
  const text = sanitizeMultilineText(value).replace(/\u0000/g, '');
  if (text === '') return '';
  return text.endsWith('\n') ? text : `${text}\n`;
}

function ensureArray(value) {
  return Array.isArray(value) ? value : [];
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

function normalizeStepType(raw) {
  const value = normalizeSpaces(raw).toLowerCase();
  if (value === 'practice') return 'practice';
  if (value === 'project') return 'project';
  if (value === 'summary') return 'summary';
  if (value === 'test' || value === 'quiz') return 'quiz';
  return 'theory';
}

function normalizeCheckerType(raw) {
  return normalizeSpaces(raw).toLowerCase();
}

function normalizeTaskLanguage(raw) {
  const value = normalizeSpaces(raw).toLowerCase();
  if (value === 'python3' || value === 'py' || value === 'python') return 'python';
  if (value === 'sql' || value === 'sqlite' || value === 'postgres' || value === 'postgresql' || value === 'mysql') return 'sql';
  return 'python';
}

function pickTaskLanguage(rawCheckerType) {
  const checkerType = normalizeCheckerType(rawCheckerType);
  if (checkerType === 'sql_query') return 'sql';
  return 'python';
}

function normalizeOptionId(raw, index) {
  const text = normalizeSpaces(raw);
  if (text !== '') {
    return text.toUpperCase();
  }
  return String.fromCharCode(65 + (index % 26));
}

function collectStepHints(step) {
  return ensureArray(step.hints)
    .map((item) => normalizeSpaces(item))
    .filter(Boolean);
}

function toTestsWithVisibility(publicTests, hiddenTests) {
  const out = [];
  for (const item of ensureArray(publicTests)) {
    out.push({
      ...item,
      visibility: 'public',
    });
  }
  for (const item of ensureArray(hiddenTests)) {
    out.push({
      ...item,
      visibility: 'hidden',
    });
  }
  return out;
}

function convertHTTPTests(publicTests, hiddenTests) {
  return toTestsWithVisibility(publicTests, hiddenTests).map((item) => {
    const expectedJson =
      item.expected_json !== undefined ? item.expected_json : item.expected_json_subset !== undefined ? item.expected_json_subset : null;
    return {
      method: normalizeSpaces(item.method).toUpperCase() || 'GET',
      path: String(item.path ?? ''),
      json: item.json ?? null,
      expected_status: toInt(item.expected_status, 200),
      expected_json: expectedJson,
      visibility: normalizeSpaces(item.visibility).toLowerCase() === 'public' ? 'public' : 'hidden',
    };
  });
}

function convertSQLChecks(publicTests, hiddenTests) {
  return toTestsWithVisibility(publicTests, hiddenTests).map((item) => ({
    query: normalizeSpaces(item.query || item.name || 'student_query') || 'student_query',
    expected: 'match_solution_behavior',
    visibility: normalizeSpaces(item.visibility).toLowerCase() === 'public' ? 'public' : 'hidden',
    compare: normalizeSpaces(item.compare) || 'ordered_rows',
    name: normalizeSpaces(item.name),
  }));
}

function convertChecker(step, checker, checkerType) {
  if (checkerType === 'python_stdout') {
    return {
      type: 'python_stdout',
      language: 'python',
      timeout_sec: toInt(checker.timeout_sec, 2),
      compare: checker.compare || {
        mode: 'exact_stdout',
        ignore_final_newline: true,
        rstrip_lines: true,
        extra_output_is_error: true,
      },
      tests: toTestsWithVisibility(checker.public_tests, checker.hidden_tests).map((item) => ({
        input: String(item.input ?? ''),
        expected_stdout: String(item.expected_stdout ?? ''),
        visibility: normalizeSpaces(item.visibility).toLowerCase() === 'public' ? 'public' : 'hidden',
      })),
    };
  }

  if (checkerType === 'python_pytest') {
    return {
      type: 'python_pytest',
      language: 'python',
      timeout_sec: toInt(checker.timeout_sec, 8),
      required_files: ensureArray(checker.required_files)
        .map((item) => normalizeSpaces(item))
        .filter(Boolean),
      pytest_code: sanitizeMultilineText(checker.pytest_code || checker.test_code || ''),
      public_tests: ensureArray(checker.public_tests),
      hidden_tests: ensureArray(checker.hidden_tests),
    };
  }

  if (checkerType === 'http_api') {
    return {
      type: 'http_api',
      language: 'python',
      framework: 'fastapi',
      timeout_sec: toInt(checker.timeout_sec, 12),
      app_import: normalizeSpaces(checker.app_import) || 'app.main:app',
      tests: convertHTTPTests(checker.public_tests, checker.hidden_tests),
    };
  }

  if (checkerType === 'ide_plugin') {
    const commands = ensureArray(checker.commands)
      .map((item) => ({
        cmd: String(item?.cmd ?? ''),
        timeout_sec: toInt(item?.timeout_sec, toInt(checker.timeout_sec, 15)),
      }))
      .filter((item) => normalizeSpaces(item.cmd) !== '');

    return {
      type: 'ide_plugin',
      timeout_sec: toInt(checker.timeout_sec, 20),
      required_files: ensureArray(checker.required_files)
        .map((item) => normalizeSpaces(item))
        .filter(Boolean),
      required_dirs: ensureArray(checker.required_dirs)
        .map((item) => normalizeSpaces(item))
        .filter(Boolean),
      forbidden_files: ensureArray(checker.forbidden_files)
        .map((item) => normalizeSpaces(item))
        .filter(Boolean),
      commands,
      hidden_checks: ensureArray(checker.hidden_checks),
      git_checks: ensureArray(checker.git_checks),
      send_to_server_for_hidden_tests: true,
    };
  }

  if (checkerType === 'sql_query') {
    const initSQL = [sanitizeMultilineText(checker.schema_sql), sanitizeMultilineText(checker.seed_sql)]
      .filter((item) => normalizeSpaces(item) !== '')
      .join('\n');
    return {
      type: 'sql_query',
      dialect: normalizeSpaces(checker.dialect) || 'sqlite',
      timeout_sec: toInt(checker.timeout_sec, 5),
      init_sql: initSQL,
      checks: convertSQLChecks(checker.public_tests, checker.hidden_tests),
      schema_sql: sanitizeMultilineText(checker.schema_sql || ''),
      seed_sql: sanitizeMultilineText(checker.seed_sql || ''),
    };
  }

  if (checkerType === 'quiz_single') {
    return {
      type: 'quiz_single',
      min_score_percent: clampInt(checker.min_score_percent, 0, 100, 70),
    };
  }

  return checker;
}

function validateStep(step, modulePosition, lessonPosition, stepPosition) {
  const stepType = normalizeStepType(step.type);
  if ((stepType === 'practice' || stepType === 'project') && !step.checker) {
    throw new Error(`Missing checker at m${modulePosition} l${lessonPosition} s${stepPosition}`);
  }
  if (stepType === 'quiz' && (!step.questions || !Array.isArray(step.questions) || step.questions.length === 0)) {
    throw new Error(`Quiz step must have questions[] at m${modulePosition} l${lessonPosition} s${stepPosition}`);
  }
  const checkerType = normalizeCheckerType(step.checker?.type);
  if (checkerType && !SUPPORTED_CHECKERS.has(checkerType)) {
    throw new Error(`Unsupported checker "${checkerType}" at m${modulePosition} l${lessonPosition} s${stepPosition}`);
  }
}

function buildQuizPayload(step, modulePosition, lessonPosition, stepPosition) {
  const questions = ensureArray(step.questions).map((question, qIdx) => {
    const optionList = ensureArray(question.options)
      .map((option, idx) => ({
        id: normalizeOptionId(option.id, idx),
        text: normalizeSpaces(option.text),
      }))
      .filter((option) => option.text !== '');
    if (optionList.length < 2) {
      throw new Error(`Quiz options parse failed at m${modulePosition} l${lessonPosition} s${stepPosition} q${qIdx + 1}`);
    }
    const fallbackCorrect = optionList[0].id;
    const correctId = normalizeOptionId(question.correct_answer_id, 0);
    const normalizedCorrect = optionList.some((option) => option.id === correctId) ? correctId : fallbackCorrect;
    return {
      id: normalizeSpaces(question.id) || `q${qIdx + 1}`,
      question: normalizeSpaces(question.question) || normalizeSpaces(step.title) || `Вопрос ${qIdx + 1}`,
      options: optionList,
      correctOptionId: normalizedCorrect,
      explanation: normalizeSpaces(question.explanation),
    };
  });

  return {
    type: 'single_choice',
    minScorePercent: clampInt(step.checker?.min_score_percent, 0, 100, 70),
    questions,
  };
}

function buildLessonContent(lesson, moduleTitle) {
  const lines = [];
  lines.push(`Материалы урока "${normalizeSpaces(lesson.title) || 'Урок'}".`);
  if (normalizeSpaces(moduleTitle) !== '') {
    lines.push(`Модуль: ${normalizeSpaces(moduleTitle)}.`);
  }
  const estimatedHours = Number(lesson.estimated_hours || 0);
  if (Number.isFinite(estimatedHours) && estimatedHours > 0) {
    lines.push(`Оценка времени: ${estimatedHours} ч.`);
  }
  const roadmapTopics = ensureArray(lesson.roadmap_topics)
    .map((topic) => normalizeSpaces(topic))
    .filter(Boolean);
  if (roadmapTopics.length > 0) {
    lines.push('Темы roadmap:');
    for (const topic of roadmapTopics) {
      lines.push(`- ${topic}`);
    }
  }
  return lines.join('\n');
}

function buildSourcePolicy(step, checkerType, checkerConverted, language) {
  const hints = collectStepHints(step);
  return {
    language,
    import_source: 'materials/v18_STRICT_PEDAGOGY/course_import.json',
    checker_type: checkerType,
    checker: checkerConverted,
    hints,
    hints_visibility: 'button_or_after_failed_attempts',
    ai_hint_config: step.ai_hint_config || {
      mode: 'socratic',
      no_full_solution: true,
    },
    ai_review_config: step.ai_review_config || null,
    ide_plugin_check: step.ide_plugin_check || null,
    skill_tags: ensureArray(step.skill_tags)
      .map((item) => normalizeSpaces(item))
      .filter(Boolean),
    admin_notes: step.admin_notes || null,
  };
}

function buildTaskTests(checkerType, checkerConverted, task) {
  if (checkerType === 'python_stdout') {
    const tests = ensureArray(checkerConverted.tests);
    return tests
      .map((item, index) => ({
        inputData: String(item.input ?? ''),
        expectedOutput: String(item.expected_stdout ?? ''),
        isHidden: normalizeSpaces(item.visibility).toLowerCase() !== 'public',
        position: index + 1,
      }))
      .filter((item) => normalizeSpaces(item.expectedOutput) !== '');
  }

  if (checkerType === 'sql_query') {
    const checks = ensureArray(checkerConverted.checks);
    const initSQL = String(checkerConverted.init_sql ?? '');
    const solutionQuery = sanitizeMultilineText(task.solutionCode || '').trim();
    const tests = checks.map((item, index) => ({
      inputData: initSQL,
      expectedOutput: solutionQuery || String(item.expected ?? ''),
      isHidden: normalizeSpaces(item.visibility).toLowerCase() !== 'public',
      position: index + 1,
    }));
    const normalized = tests.filter((item) => normalizeSpaces(item.expectedOutput) !== '');
    if (normalized.length > 0) {
      return normalized;
    }
    if (solutionQuery) {
      return [
        {
          inputData: initSQL,
          expectedOutput: solutionQuery,
          isHidden: true,
          position: 1,
        },
      ];
    }
    return [];
  }

  return [];
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

function prepareCourse(rawRoot) {
  const rawCourse = rawRoot?.course;
  if (!rawCourse || !Array.isArray(rawCourse.modules)) {
    throw new Error('Invalid input: expected { course: { modules: [...] } }');
  }

  const modules = rawCourse.modules
    .slice()
    .sort((a, b) => toInt(a.order, 0) - toInt(b.order, 0))
    .map((moduleItem, moduleIndex) => {
      const modulePosition = toInt(moduleItem.order, moduleIndex + 1);
      const moduleTitle = normalizeSpaces(moduleItem.title) || `Модуль ${modulePosition}`;

      const lessons = ensureArray(moduleItem.lessons)
        .slice()
        .sort((a, b) => toInt(a.order, 0) - toInt(b.order, 0))
        .map((lessonItem, lessonIndex) => {
          const lessonPosition = toInt(lessonItem.order, lessonIndex + 1);
          const lessonTitle = normalizeSpaces(lessonItem.title) || `Урок ${lessonPosition}`;

          const blocks = ensureArray(lessonItem.steps)
            .slice()
            .sort((a, b) => toInt(a.order, 0) - toInt(b.order, 0))
            .map((stepItem, stepIndex) => {
              const position = toInt(stepItem.order, stepIndex + 1);
              validateStep(stepItem, modulePosition, lessonPosition, position);

              const blockType = normalizeStepType(stepItem.type);
              const title = normalizeSpaces(stepItem.title) || `Шаг ${position}`;
              const contentMd = sanitizeMultilineText(stepItem.body_markdown || '').trim();
              const checkerType = normalizeCheckerType(stepItem.checker?.type);
              const checkerConverted = convertChecker(stepItem, stepItem.checker || {}, checkerType);

              let task = null;
              if (blockType === 'practice' || blockType === 'project') {
                const language = pickTaskLanguage(checkerType);
                const sourcePolicy = buildSourcePolicy(stepItem, checkerType, checkerConverted, language);
                task = {
                  title,
                  statementMd: contentMd,
                  starterCode: ensureTrailingNewline(stepItem.editor_initial_code || ''),
                  solutionCode: ensureTrailingNewline(stepItem.solution_code || ''),
                  difficulty: clampInt(stepItem.difficulty, 1, 10, 2),
                  xpReward: Math.max(10, toInt(stepItem.xp, 50) || 50),
                  topic: `${moduleTitle} — ${lessonTitle}`,
                  language,
                  sourcePolicy,
                };
                task.tests = buildTaskTests(checkerType, checkerConverted, task);
              }

              let quizPayload = null;
              if (blockType === 'quiz') {
                quizPayload = buildQuizPayload(stepItem, modulePosition, lessonPosition, position);
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
            lessonContent: buildLessonContent(lessonItem, moduleTitle),
            blocks,
          };
        });

      return {
        modulePosition,
        moduleTitle,
        lessons,
      };
    });

  const course = {
    slug: COURSE_SLUG,
    title: normalizeSpaces(rawCourse.title) || 'Python с нуля — Backend + AI',
    description:
      normalizeSpaces(rawCourse.description) ||
      'Практический backend-курс Python с автопроверкой, AI-подсказками и проектными шагами для IDE-плагина.',
    modules,
  };

  ensureUniqueTaskTitles(course);
  return course;
}

function buildTaskSeedValues(courseSlug, modulePosition, lessonPosition, lesson) {
  const tasks = lesson.blocks.filter((block) => block.task);
  if (tasks.length === 0) {
    return '';
  }

  let sql = '), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (\n';
  sql += '  VALUES\n';
  for (let i = 0; i < tasks.length; i += 1) {
    const block = tasks[i];
    const task = block.task;
    const suffix = i + 1 < tasks.length ? ',' : '';
    sql += `  (${dollarQuote(task.title, `m${modulePosition}_l${lessonPosition}_t${block.position}_title`)}, `;
    sql += `${dollarQuote(task.statementMd, `m${modulePosition}_l${lessonPosition}_t${block.position}_stmt`)}, `;
    sql += `${dollarQuote(task.starterCode, `m${modulePosition}_l${lessonPosition}_t${block.position}_starter`)}, `;
    sql += `${dollarQuote(task.solutionCode, `m${modulePosition}_l${lessonPosition}_t${block.position}_solution`)}, `;
    sql += `${task.difficulty}, ${task.xpReward}, `;
    sql += `${dollarQuote(task.topic, `m${modulePosition}_l${lessonPosition}_t${block.position}_topic`)}, `;
    sql += `'${task.language}', `;
    sql += `${dollarQuote(JSON.stringify(task.sourcePolicy), `m${modulePosition}_l${lessonPosition}_t${block.position}_policy`)}::jsonb)${suffix}\n`;
  }
  return sql;
}

function buildTestSeedValues(modulePosition, lessonPosition, lesson) {
  const rows = [];
  for (const block of lesson.blocks) {
    if (!block.task) continue;
    for (const test of ensureArray(block.task.tests)) {
      rows.push({
        taskTitle: block.task.title,
        inputData: String(test.inputData ?? ''),
        expectedOutput: String(test.expectedOutput ?? ''),
        isHidden: Boolean(test.isHidden),
        position: toInt(test.position, rows.length + 1),
      });
    }
  }

  if (rows.length === 0) {
    return '';
  }

  let sql = '\nWITH lesson_ref AS (\n';
  sql += '  SELECT l.id AS lesson_id\n';
  sql += '  FROM lessons l\n';
  sql += '  JOIN modules m ON m.id = l.module_id\n';
  sql += `  JOIN courses c ON c.id = m.course_id AND c.slug = '${COURSE_SLUG}'\n`;
  sql += `  WHERE m.position = ${modulePosition} AND l.position = ${lessonPosition}\n`;
  sql += '), task_ref AS (\n';
  sql += '  SELECT t.id AS task_id, t.title\n';
  sql += '  FROM tasks t\n';
  sql += '  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id\n';
  sql += '  WHERE t.is_published = TRUE\n';
  sql += '), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (\n';
  sql += '  VALUES\n';
  for (let i = 0; i < rows.length; i += 1) {
    const row = rows[i];
    const suffix = i + 1 < rows.length ? ',' : '';
    sql += `  (${dollarQuote(row.taskTitle, `m${modulePosition}_l${lessonPosition}_test_${i + 1}_task`)}, `;
    sql += `${dollarQuote(row.inputData, `m${modulePosition}_l${lessonPosition}_test_${i + 1}_input`)}, `;
    sql += `${dollarQuote(row.expectedOutput, `m${modulePosition}_l${lessonPosition}_test_${i + 1}_expected`)}, `;
    sql += `${row.isHidden ? 'TRUE' : 'FALSE'}, ${row.position})${suffix}\n`;
  }
  sql += ')\n';
  sql += 'INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)\n';
  sql += 'SELECT tr.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position\n';
  sql += 'FROM test_seed ts\n';
  sql += 'JOIN task_ref tr ON tr.title = ts.task_title\n';
  sql += 'ON CONFLICT (task_id, position) DO UPDATE\n';
  sql += 'SET input_data = EXCLUDED.input_data,\n';
  sql += '    expected_output = EXCLUDED.expected_output,\n';
  sql += '    is_hidden = EXCLUDED.is_hidden;\n';
  return sql;
}

function buildBlockSeedValues(modulePosition, lessonPosition, lesson) {
  let sql = 'WITH lesson_ref AS (\n';
  sql += '  SELECT l.id AS lesson_id\n';
  sql += '  FROM lessons l\n';
  sql += '  JOIN modules m ON m.id = l.module_id\n';
  sql += `  JOIN courses c ON c.id = m.course_id AND c.slug = '${COURSE_SLUG}'\n`;
  sql += `  WHERE m.position = ${modulePosition} AND l.position = ${lessonPosition}\n`;
  sql += '), task_ref AS (\n';
  sql += '  SELECT t.id AS task_id, t.title\n';
  sql += '  FROM tasks t\n';
  sql += '  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id\n';
  sql += '  WHERE t.is_published = TRUE\n';
  sql += '), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (\n';
  sql += '  VALUES\n';
  for (let i = 0; i < lesson.blocks.length; i += 1) {
    const block = lesson.blocks[i];
    const suffix = i + 1 < lesson.blocks.length ? ',' : '';
    const taskTitleValue = block.task ? dollarQuote(block.task.title, `m${modulePosition}_l${lessonPosition}_b${block.position}_task`) : 'NULL';
    const quizValue = block.quizPayload
      ? `${dollarQuote(JSON.stringify(block.quizPayload), `m${modulePosition}_l${lessonPosition}_b${block.position}_quiz`)}::jsonb`
      : 'NULL::jsonb';
    sql += `  (${block.position}, ${dollarQuote(block.blockType, `m${modulePosition}_l${lessonPosition}_b${block.position}_type`)}, `;
    sql += `${dollarQuote(block.title, `m${modulePosition}_l${lessonPosition}_b${block.position}_title`)}, `;
    sql += `${dollarQuote(block.contentMd, `m${modulePosition}_l${lessonPosition}_b${block.position}_content`)}, `;
    sql += `${taskTitleValue}, ${quizValue})${suffix}\n`;
  }
  sql += ')\n';
  sql += 'INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)\n';
  sql += 'SELECT lr.lesson_id, bs.block_type, bs.title, bs.content_md, tr.task_id, bs.quiz_payload, bs.position, TRUE\n';
  sql += 'FROM block_seed bs\n';
  sql += 'CROSS JOIN lesson_ref lr\n';
  sql += 'LEFT JOIN task_ref tr ON tr.title = bs.task_title\n';
  sql += 'ON CONFLICT (lesson_id, position) DO UPDATE\n';
  sql += 'SET block_type = EXCLUDED.block_type,\n';
  sql += '    title = EXCLUDED.title,\n';
  sql += '    content_md = EXCLUDED.content_md,\n';
  sql += '    task_id = EXCLUDED.task_id,\n';
  sql += '    quiz_payload = EXCLUDED.quiz_payload,\n';
  sql += '    is_published = TRUE,\n';
  sql += '    updated_at = NOW();\n';
  return sql;
}

function buildMigrationSql(course) {
  let sql = '';
  sql += '-- 026_reseed_python_zero_v18_strict_pedagogy.sql\n';
  sql += '-- Generated from materials/v18_STRICT_PEDAGOGY/course_import.json\n';
  sql += '-- Purpose: fully reseed python-zero from v18 strict pedagogy package with runtime-compatible checker configs.\n';
  sql += `-- Generated at: ${new Date().toISOString()}\n\n`;

  sql += "ALTER TABLE tasks DROP CONSTRAINT IF EXISTS chk_tasks_language;\n";
  sql += "ALTER TABLE tasks ADD CONSTRAINT chk_tasks_language CHECK (language IN ('java', 'python', 'python3', 'py', 'sql'));\n\n";
  sql += 'ALTER TABLE tasks ADD COLUMN IF NOT EXISTS source_policy JSONB;\n';
  sql += 'ALTER TABLE tasks ADD COLUMN IF NOT EXISTS language TEXT NOT NULL DEFAULT \'java\';\n';
  sql += 'ALTER TABLE lesson_blocks ADD COLUMN IF NOT EXISTS quiz_payload JSONB;\n\n';

  sql += 'INSERT INTO courses(slug, title, description, is_published)\n';
  sql += `VALUES ('${COURSE_SLUG}', ${dollarQuote(course.title, 'course_title')}, ${dollarQuote(course.description, 'course_desc')}, TRUE)\n`;
  sql += 'ON CONFLICT (slug) DO UPDATE\n';
  sql += 'SET title = EXCLUDED.title,\n';
  sql += '    description = EXCLUDED.description,\n';
  sql += '    is_published = TRUE,\n';
  sql += '    updated_at = NOW();\n\n';

  sql += 'WITH course_ref AS (\n';
  sql += `  SELECT id AS course_id FROM courses WHERE slug = '${COURSE_SLUG}'\n`;
  sql += ')\n';
  sql += 'UPDATE lesson_blocks lb\n';
  sql += 'SET is_published = FALSE,\n';
  sql += '    updated_at = NOW()\n';
  sql += 'FROM lessons l\n';
  sql += 'JOIN modules m ON m.id = l.module_id\n';
  sql += 'JOIN course_ref cr ON cr.course_id = m.course_id\n';
  sql += 'WHERE lb.lesson_id = l.id;\n\n';

  sql += 'WITH course_ref AS (\n';
  sql += `  SELECT id AS course_id FROM courses WHERE slug = '${COURSE_SLUG}'\n`;
  sql += ')\n';
  sql += 'UPDATE tasks t\n';
  sql += 'SET is_published = FALSE,\n';
  sql += '    updated_at = NOW()\n';
  sql += 'FROM lessons l\n';
  sql += 'JOIN modules m ON m.id = l.module_id\n';
  sql += 'JOIN course_ref cr ON cr.course_id = m.course_id\n';
  sql += 'WHERE t.lesson_id = l.id;\n\n';

  sql += 'WITH course_ref AS (\n';
  sql += `  SELECT id AS course_id FROM courses WHERE slug = '${COURSE_SLUG}'\n`;
  sql += ')\n';
  sql += 'UPDATE lessons l\n';
  sql += 'SET is_published = FALSE,\n';
  sql += '    updated_at = NOW()\n';
  sql += 'FROM modules m\n';
  sql += 'JOIN course_ref cr ON cr.course_id = m.course_id\n';
  sql += 'WHERE l.module_id = m.id;\n\n';

  sql += 'WITH course_ref AS (\n';
  sql += `  SELECT id AS course_id FROM courses WHERE slug = '${COURSE_SLUG}'\n`;
  sql += '), module_seed(position, title) AS (\n';
  sql += '  VALUES\n';
  const modules = course.modules.slice().sort((a, b) => a.modulePosition - b.modulePosition);
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
    sql += `  WHERE c.slug = '${COURSE_SLUG}' AND m.position = ${moduleItem.modulePosition}\n`;
    sql += '), lesson_seed(position, title, content_md) AS (\n';
    sql += '  VALUES\n';
    for (let i = 0; i < lessons.length; i += 1) {
      const lesson = lessons[i];
      const suffix = i + 1 < lessons.length ? ',' : '';
      sql += `  (${lesson.lessonPosition}, ${dollarQuote(lesson.lessonTitle, `m${moduleItem.modulePosition}_l${lesson.lessonPosition}_title`)}, `;
      sql += `${dollarQuote(lesson.lessonContent, `m${moduleItem.modulePosition}_l${lesson.lessonPosition}_content`)})${suffix}\n`;
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
      sql += `-- m${moduleItem.modulePosition}_l${lesson.lessonPosition}: ${lesson.lessonTitle}\n`;
      sql += 'WITH lesson_ref AS (\n';
      sql += '  SELECT l.id AS lesson_id\n';
      sql += '  FROM lessons l\n';
      sql += '  JOIN modules m ON m.id = l.module_id\n';
      sql += `  JOIN courses c ON c.id = m.course_id AND c.slug = '${COURSE_SLUG}'\n`;
      sql += `  WHERE m.position = ${moduleItem.modulePosition} AND l.position = ${lesson.lessonPosition}\n`;
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
      sql += `  JOIN courses c ON c.id = m.course_id AND c.slug = '${COURSE_SLUG}'\n`;
      sql += `  WHERE m.position = ${moduleItem.modulePosition} AND l.position = ${lesson.lessonPosition}\n`;
      sql += ')\n';
      sql += 'UPDATE tasks t\n';
      sql += 'SET is_published = FALSE,\n';
      sql += '    updated_at = NOW()\n';
      sql += 'FROM lesson_ref lr\n';
      sql += 'WHERE t.lesson_id = lr.lesson_id;\n\n';

      const taskSeedSql = buildTaskSeedValues(COURSE_SLUG, moduleItem.modulePosition, lesson.lessonPosition, lesson);
      if (taskSeedSql !== '') {
        sql += 'WITH lesson_ref AS (\n';
        sql += '  SELECT l.id AS lesson_id\n';
        sql += '  FROM lessons l\n';
        sql += '  JOIN modules m ON m.id = l.module_id\n';
        sql += `  JOIN courses c ON c.id = m.course_id AND c.slug = '${COURSE_SLUG}'\n`;
        sql += `  WHERE m.position = ${moduleItem.modulePosition} AND l.position = ${lesson.lessonPosition}\n`;
        sql += taskSeedSql;
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
        sql += `  JOIN courses c ON c.id = m.course_id AND c.slug = '${COURSE_SLUG}'\n`;
        sql += `  WHERE m.position = ${moduleItem.modulePosition} AND l.position = ${lesson.lessonPosition}\n`;
        sql += ')\n';
        sql += 'DELETE FROM task_test_cases tc\n';
        sql += 'USING tasks t, lesson_ref lr\n';
        sql += 'WHERE tc.task_id = t.id\n';
        sql += '  AND t.lesson_id = lr.lesson_id\n';
        sql += '  AND t.is_published = TRUE;\n';

        sql += buildTestSeedValues(moduleItem.modulePosition, lesson.lessonPosition, lesson);
      }

      sql += buildBlockSeedValues(moduleItem.modulePosition, lesson.lessonPosition, lesson);
      sql += '\n';
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
    checkerTypes: {},
    languages: {},
  };

  for (const moduleItem of course.modules) {
    stats.lessons += moduleItem.lessons.length;
    for (const lesson of moduleItem.lessons) {
      stats.blocks += lesson.blocks.length;
      for (const block of lesson.blocks) {
        if (!block.task) continue;
        stats.tasks += 1;
        const checkerType = normalizeCheckerType(block.task.sourcePolicy?.checker_type);
        if (checkerType) {
          stats.checkerTypes[checkerType] = (stats.checkerTypes[checkerType] || 0) + 1;
        }
        const lang = normalizeTaskLanguage(block.task.language);
        stats.languages[lang] = (stats.languages[lang] || 0) + 1;
        stats.tests += ensureArray(block.task.tests).length;
      }
    }
  }
  return stats;
}

function main() {
  const raw = JSON.parse(readText(INPUT_PATH));
  const course = prepareCourse(raw);
  const migrationSQL = buildMigrationSql(course);
  fs.writeFileSync(OUT_PATH, migrationSQL, 'utf8');

  const stats = summarize(course);
  console.log('Generated migration:', OUT_PATH);
  console.log(`Course: ${course.slug} -> ${course.title}`);
  console.log(`Modules: ${stats.modules}`);
  console.log(`Lessons: ${stats.lessons}`);
  console.log(`Blocks: ${stats.blocks}`);
  console.log(`Tasks: ${stats.tasks}`);
  console.log(`Executable tests: ${stats.tests}`);
  console.log('Task languages:', JSON.stringify(stats.languages));
  console.log('Checker types:', JSON.stringify(stats.checkerTypes));
}

main();
