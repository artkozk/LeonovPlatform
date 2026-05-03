const fs = require('fs');

const INPUTS = [
  {
    path: 'C:/Users/Artemy/Downloads/java_course_platform_v1_import.json',
    slug: 'java-zero-core',
    title: 'Java с нуля — Core, Spring Boot, SQL и DevOps',
    description:
      'Пятимесячный курс: Java Core, ООП, коллекции, SQL/JDBC, Spring Boot, инфраструктура и финальный проект.',
  },
  {
    path: 'C:/Users/Artemy/Downloads/frontend_course_platform_v1_import.json',
    slug: 'frontend-zero',
    title: 'Frontend с нуля — HTML, CSS, JS, React и TypeScript',
    description:
      'Пятимесячный курс: web-основы, JavaScript, TypeScript, React и production-практики с финальным проектом.',
  },
  {
    path: 'C:/Users/Artemy/Downloads/go_course_platform_v1_import.json',
    slug: 'go-zero-backend',
    title: 'Go с нуля — Backend, SQL, Concurrency и DevOps',
    description:
      'Пятимесячный курс: Go Core, concurrency, SQL/HTTP, production backend, инфраструктура и финальный проект.',
  },
];

const OUT_PATH =
  'C:/prog/Comercial/LeonovCarePlatform/backend/migrations/022_seed_java_frontend_go_v1_catalog_and_sql_practice.sql';

function readText(path) {
  return fs.readFileSync(path, 'utf8').replace(/\r\n/g, '\n').replace(/\r/g, '\n');
}

function normalizeSpaces(value) {
  return String(value ?? '')
    .replace(/\u00a0/g, ' ')
    .replace(/[ \t]+/g, ' ')
    .trim();
}

function toInt(value, fallback) {
  const n = Number(value);
  if (!Number.isFinite(n)) return fallback;
  return Math.trunc(n);
}

function clampInt(value, min, max, fallback) {
  const n = toInt(value, fallback);
  if (!Number.isFinite(n)) return fallback;
  return Math.min(max, Math.max(min, n));
}

function sanitizeMultilineText(value) {
  return String(value ?? '').replace(/\r/g, '');
}

function dollarQuote(input, tagBase) {
  const source = String(input ?? '');
  const normalizedTagBase = String(tagBase ?? '')
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

function normalizeBlockType(type) {
  const raw = normalizeSpaces(type).toLowerCase();
  if (raw === 'practice') return 'practice';
  if (raw === 'quiz') return 'quiz';
  if (raw === 'project') return 'project';
  if (raw === 'summary') return 'summary';
  return 'theory';
}

function normalizeLanguage(lang) {
  const raw = normalizeSpaces(lang).toLowerCase();
  if (raw === 'python3' || raw === 'py') return 'python';
  if (raw === 'js') return 'javascript';
  return raw || 'java';
}

function extractQuizQuestionFromBody(bodyMarkdown, fallbackTitle) {
  const body = String(bodyMarkdown ?? '');
  const sectionMatch = body.match(/(?:^|\n)###\s*Вопрос\s*\n([\s\S]*?)(?=\n###\s|$)/u);
  if (sectionMatch && normalizeSpaces(sectionMatch[1]) !== '') {
    return normalizeSpaces(sectionMatch[1]);
  }
  const inlineMatch = body.match(/(?:^|\n)\*\*Вопрос:\*\*\s*(.+)$/imu);
  if (inlineMatch && normalizeSpaces(inlineMatch[1]) !== '') {
    return normalizeSpaces(inlineMatch[1]);
  }
  return normalizeSpaces(fallbackTitle) || 'Выберите правильный вариант';
}

function buildQuizPayload(step) {
  const quiz = step.quiz;
  if (!quiz || !Array.isArray(quiz.options) || quiz.options.length < 2) return null;

  const options = quiz.options.map((opt, idx) => ({
    id: String.fromCharCode(65 + idx),
    text: normalizeSpaces(opt),
  }));
  const rawCorrect = toInt(quiz.correct_index, 0);
  const clampedCorrect = Math.min(options.length - 1, Math.max(0, rawCorrect));

  const question = {
    id: 'q1',
    question: extractQuizQuestionFromBody(step.body_markdown, step.title),
    options,
    correctOptionId: options[clampedCorrect].id,
  };

  const explanation = normalizeSpaces(quiz.explanation);
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

function buildLessonContent(lesson) {
  const lines = [];
  lines.push(`Материалы урока \"${normalizeSpaces(lesson.title) || 'Урок'}\".`);

  if (normalizeSpaces(lesson.category) !== '') {
    lines.push(`Категория: ${normalizeSpaces(lesson.category)}.`);
  }

  const targetSteps = toInt(lesson.target_steps, 0);
  if (targetSteps > 0) {
    lines.push(`План по шагам: ${targetSteps}.`);
  }

  const workload = toInt(lesson.target_workload_minutes, 0);
  if (workload > 0) {
    lines.push(`Оценка времени: ${workload} минут.`);
  }

  return lines.join('\n');
}

function buildPracticeTask(step, moduleTitle, lessonTitle) {
  const checker = step.checker || {};
  const checkerType = normalizeSpaces(checker.type).toLowerCase();
  const language = normalizeLanguage(step.language);
  const solution = sanitizeMultilineText(step.solution_code).trim();

  if (language !== 'sql' || checkerType !== 'sql_query' || solution === '') {
    return null;
  }

  const starterCodeRaw = sanitizeMultilineText(step.editor_initial_code).trimEnd();
  const starterCode = starterCodeRaw ? `${starterCodeRaw}\n` : '';

  const solutionCode = `${solution}\n`;

  const sourcePolicy = {
    language: 'sql',
    import_source: 'v1_json',
    checker_type: checkerType,
    checker,
    hints: Array.isArray(step.hints)
      ? step.hints.map((h) => normalizeSpaces(h)).filter((h) => h !== '')
      : [],
    hints_visibility: normalizeSpaces(step.hints_visibility),
    ai_hint_config: step.ai_hint_config || {
      mode: 'socratic',
      no_full_solution: true,
    },
  };

  return {
    title: normalizeSpaces(step.title) || `Практика ${toInt(step.order, 0)}`,
    statementMd: sanitizeMultilineText(step.body_markdown).trim(),
    starterCode,
    solutionCode,
    difficulty: clampInt(step.difficulty, 1, 10, 2),
    xpReward: Math.max(10, toInt(step.xp, 50) || 50),
    topic: `${normalizeSpaces(moduleTitle)} — ${normalizeSpaces(lessonTitle)}`,
    language: 'sql',
    sourcePolicy,
    tests: [
      {
        inputData: '',
        expectedOutput: solution,
        isHidden: true,
        position: 1,
      },
    ],
  };
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

function prepareCourse(inputCfg) {
  const raw = JSON.parse(readText(inputCfg.path));

  const modules = (raw.modules || [])
    .slice()
    .sort((a, b) => toInt(a.order, 0) - toInt(b.order, 0))
    .map((moduleItem) => {
      const modulePosition = toInt(moduleItem.order, 0);
      const moduleTitle = normalizeSpaces(moduleItem.title) || `Модуль ${modulePosition}`;

      const lessons = (moduleItem.lessons || [])
        .slice()
        .sort((a, b) => toInt(a.order, 0) - toInt(b.order, 0))
        .map((lesson) => {
          const lessonPosition = toInt(lesson.order, 0);
          const lessonTitle = normalizeSpaces(lesson.title) || `Урок ${lessonPosition}`;

          const blocks = (lesson.steps || [])
            .slice()
            .sort((a, b) => toInt(a.order, 0) - toInt(b.order, 0))
            .map((step, idx) => {
              const position = toInt(step.order, idx + 1);
              const blockType = normalizeBlockType(step.type);
              const contentMd = sanitizeMultilineText(step.body_markdown).trim();
              const title = normalizeSpaces(step.title) || `Шаг ${position}`;
              const quizPayload = blockType === 'quiz' ? buildQuizPayload(step) : null;
              const task =
                blockType === 'practice' ? buildPracticeTask(step, moduleTitle, lessonTitle) : null;

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
            lessonContent: buildLessonContent(lesson),
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
    slug: inputCfg.slug,
    title: inputCfg.title || normalizeSpaces(raw.title) || inputCfg.slug,
    description:
      inputCfg.description ||
      `Курс ${normalizeSpaces(raw.title) || inputCfg.slug}. Длительность: ${toInt(raw.duration_months, 5)} месяцев.`,
    modules,
  };

  ensureUniqueTaskTitles(course);
  return course;
}

function buildMigrationSql(courses) {
  let sql = '';
  sql += '-- 022_seed_java_frontend_go_v1_catalog_and_sql_practice.sql\n';
  sql += '-- Generated from *_course_platform_v1_import.json\n';
  sql += '-- Purpose: seed catalog courses/lessons/blocks for Java, Frontend and Go tracks;\n';
  sql += '--          create executable tasks only for SQL checker blocks supported by current backend judge.\n\n';

  for (const course of courses) {
    sql += `-- Course: ${course.slug} (${course.title})\n`;
    sql += 'INSERT INTO courses(slug, title, description, is_published)\n';
    sql += `VALUES ('${course.slug}', ${dollarQuote(course.title, `${course.slug}_title`)}, ${dollarQuote(
      course.description,
      `${course.slug}_desc`
    )}, TRUE)\n`;
    sql += 'ON CONFLICT (slug) DO UPDATE\n';
    sql += 'SET title = EXCLUDED.title,\n';
    sql += '    description = EXCLUDED.description,\n';
    sql += '    is_published = TRUE,\n';
    sql += '    updated_at = NOW();\n\n';

    const modules = course.modules.slice().sort((a, b) => a.modulePosition - b.modulePosition);

    sql += 'WITH course_ref AS (\n';
    sql += `  SELECT id AS course_id FROM courses WHERE slug = '${course.slug}'\n`;
    sql += '), module_seed(position, title) AS (\n';
    sql += '  VALUES\n';
    for (let i = 0; i < modules.length; i += 1) {
      const m = modules[i];
      const suffix = i + 1 < modules.length ? ',' : '';
      sql += `  (${m.modulePosition}, ${dollarQuote(m.moduleTitle, `${course.slug}_m${m.modulePosition}_title`)})${suffix}\n`;
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
      sql += `-- ${course.slug} / module ${moduleItem.modulePosition}: ${moduleItem.moduleTitle}\n`;
      sql += 'WITH module_ref AS (\n';
      sql += '  SELECT m.id AS module_id\n';
      sql += '  FROM modules m\n';
      sql += '  JOIN courses c ON c.id = m.course_id\n';
      sql += `  WHERE c.slug = '${course.slug}' AND m.position = ${moduleItem.modulePosition}\n`;
      sql += '), lesson_seed(position, title, content_md) AS (\n';
      sql += '  VALUES\n';

      const lessons = moduleItem.lessons.slice().sort((a, b) => a.lessonPosition - b.lessonPosition);
      for (let i = 0; i < lessons.length; i += 1) {
        const l = lessons[i];
        const suffix = i + 1 < lessons.length ? ',' : '';
        sql += `  (${l.lessonPosition}, ${dollarQuote(
          l.lessonTitle,
          `${course.slug}_m${moduleItem.modulePosition}_l${l.lessonPosition}_title`
        )}, ${dollarQuote(
          l.lessonContent,
          `${course.slug}_m${moduleItem.modulePosition}_l${l.lessonPosition}_content`
        )})${suffix}\n`;
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
        const lessonPrefix = `${course.slug}_m${moduleItem.modulePosition}_l${lesson.lessonPosition}`;
        const taskBlocks = lesson.blocks.filter((b) => b.blockType === 'practice' && b.task);

        sql += `-- ${course.slug} / m${moduleItem.modulePosition} / l${lesson.lessonPosition}: ${lesson.lessonTitle}\n`;
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
            for (const test of block.task.tests) {
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
            const t = allTests[i];
            const suffix = i + 1 < allTests.length ? ',' : '';
            sql += `  (${dollarQuote(t.taskTitle, `${lessonPrefix}_test_${t.blockPosition}_${t.position}_title`)}, ${dollarQuote(
              t.inputData,
              `${lessonPrefix}_test_${t.blockPosition}_${t.position}_input`
            )}, ${dollarQuote(
              t.expectedOutput,
              `${lessonPrefix}_test_${t.blockPosition}_${t.position}_expected`
            )}, ${t.isHidden ? 'TRUE' : 'FALSE'}, ${t.position})${suffix}\n`;
          }
          sql += ')\n';
          sql += 'INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)\n';
          sql += 'SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position\n';
          sql += 'FROM test_seed ts\n';
          sql += 'JOIN task_lookup tl ON tl.title = ts.task_title\n';
          sql += 'ORDER BY tl.task_id, ts.position;\n\n';
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
  }

  return sql;
}

function summarize(courses) {
  const totals = {
    courses: courses.length,
    modules: 0,
    lessons: 0,
    blocks: 0,
    tasks: 0,
    tests: 0,
  };

  for (const course of courses) {
    totals.modules += course.modules.length;
    for (const moduleItem of course.modules) {
      totals.lessons += moduleItem.lessons.length;
      for (const lesson of moduleItem.lessons) {
        totals.blocks += lesson.blocks.length;
        for (const block of lesson.blocks) {
          if (!block.task) continue;
          totals.tasks += 1;
          totals.tests += block.task.tests.length;
        }
      }
    }
  }

  return totals;
}

function main() {
  const courses = INPUTS.map((cfg) => prepareCourse(cfg));
  const sql = buildMigrationSql(courses);
  fs.writeFileSync(OUT_PATH, sql, 'utf8');

  const stats = summarize(courses);
  console.log(`Generated migration: ${OUT_PATH}`);
  console.log(`Courses: ${stats.courses}`);
  console.log(`Modules: ${stats.modules}`);
  console.log(`Lessons: ${stats.lessons}`);
  console.log(`Blocks: ${stats.blocks}`);
  console.log(`Tasks (SQL only): ${stats.tasks}`);
  console.log(`Tests: ${stats.tests}`);
}

main();
