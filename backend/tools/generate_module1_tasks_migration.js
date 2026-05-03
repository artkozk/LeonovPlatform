const fs = require("fs");

const mdPath = "C:/Users/Artemy/Downloads/osnovy_python_platform_ready_v3 (1).md";
const outPath = "C:/prog/Comercial/LeonovCarePlatform/backend/migrations/016_seed_python_module1_tasks_bindings_and_tests.sql";

function readMarkdown(filePath) {
  return fs.readFileSync(filePath, "utf8").replace(/\r\n/g, "\n").replace(/\r/g, "\n");
}

function escapeRegExp(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function normalizeCodeBlock(value) {
  const source = String(value ?? "").replace(/\r\n/g, "\n").replace(/\r/g, "\n");
  return source.replace(/^\n+/, "").replace(/\n+$/, "");
}

function ensureTrailingNewline(value) {
  const source = normalizeCodeBlock(value);
  if (!source) return "";
  return source.endsWith("\n") ? source : `${source}\n`;
}

function normalizeTestIO(value) {
  return normalizeCodeBlock(value);
}

function stripAdminDetails(stepText) {
  return String(stepText ?? "").replace(/<details>[\s\S]*?<\/details>/g, "");
}

function cleanStepContent(stepText) {
  return stripAdminDetails(stepText)
    .replace(/^\*\*Вид:\*\*.*$/m, "")
    .replace(/^\s+|\s+$/g, "")
    .replace(/\n{3,}/g, "\n\n");
}

function extractSection(stepText, heading) {
  const headerRegex = new RegExp(`^###\\s+${escapeRegExp(heading)}\\s*$`, "m");
  const startIndex = stepText.search(headerRegex);
  if (startIndex === -1) return "";
  const headerMatch = stepText.slice(startIndex).match(headerRegex);
  if (!headerMatch) return "";

  const afterStart = startIndex + headerMatch[0].length;
  const tail = stepText.slice(afterStart);
  const endMatch = tail.match(/\n###\s+|\n<details>|\n##\s+Шаг\s+|\n#\s+Урок\s+/);
  return (endMatch ? tail.slice(0, endMatch.index) : tail).trim();
}

function extractFirstCodeBlock(text) {
  const match = String(text ?? "").match(/```[^\n]*\n([\s\S]*?)```/);
  if (!match) return "";
  return normalizeCodeBlock(match[1]);
}

function extractCodeAfterLabel(text, label) {
  const fence = "\\`\\`\\`";
  const re = new RegExp(`${escapeRegExp(label)}:\\s*\\n+\\s*${fence}[^\\n]*\\n([\\s\\S]*?)${fence}`, "m");
  const match = String(text ?? "").match(re);
  if (!match) return "";
  return normalizeTestIO(match[1]);
}

function extractAdminSection(stepText) {
  const match = String(stepText ?? "").match(/<details>\s*<summary>\s*Админ:[\s\S]*?<\/summary>([\s\S]*?)<\/details>/);
  return match ? match[1].trim() : "";
}

function parseTestsFromAdmin(adminSection) {
  const section = extractSection(adminSection, "Автотесты") || adminSection;
  const testRegex = /\*\*Тест\s+\d+\*\*/g;
  const markers = [...section.matchAll(testRegex)];
  const tests = [];

  if (markers.length === 0) {
    const input = extractCodeAfterLabel(section, "Ввод");
    const expected = extractCodeAfterLabel(section, "Ожидаемый вывод") || extractCodeAfterLabel(section, "Вывод");
    if (input !== "" || expected !== "") {
      tests.push({ inputData: input, expectedOutput: expected });
    }
    return tests;
  }

  for (let i = 0; i < markers.length; i += 1) {
    const start = markers[i].index + markers[i][0].length;
    const end = i + 1 < markers.length ? markers[i + 1].index : section.length;
    const chunk = section.slice(start, end);
    const input = extractCodeAfterLabel(chunk, "Ввод");
    const expected = extractCodeAfterLabel(chunk, "Ожидаемый вывод") || extractCodeAfterLabel(chunk, "Вывод");
    if (input === "" && expected === "") {
      continue;
    }
    tests.push({ inputData: input, expectedOutput: expected });
  }

  return tests;
}

function parseTestsFromExamples(stepContent) {
  const tests = [];
  const re = /###\s+Пример\s+\d+\s*([\s\S]*?)(?=\n###\s+|\n##\s+Шаг\s+|\n#\s+Урок\s+|$)/g;
  const matches = [...String(stepContent ?? "").matchAll(re)];
  for (const match of matches) {
    const chunk = match[1];
    const input = extractCodeAfterLabel(chunk, "Ввод");
    const expected = extractCodeAfterLabel(chunk, "Вывод");
    if (input === "" && expected === "") continue;
    tests.push({ inputData: input, expectedOutput: expected });
  }
  return tests;
}

function normalizeBlockType(kindRaw) {
  const value = String(kindRaw ?? "").trim().toLowerCase();
  if (value.includes("тест")) return "quiz";
  if (value.includes("практика") || value.includes("исправление") || value.includes("контроль")) return "practice";
  if (value.includes("итог")) return "summary";
  return "theory";
}

function isPracticeType(blockType) {
  return String(blockType ?? "").toLowerCase() === "practice";
}

function parseQuizPayload(stepText) {
  const question = extractSection(stepText, "Вопрос").replace(/\n+/g, " ").trim();
  const optionsSection = extractSection(stepText, "Варианты");
  const options = [...optionsSection.matchAll(/^\s*\d+\.\s+(.+)$/gm)].map((match, index) => ({
    id: String.fromCharCode(65 + index),
    text: match[1].trim(),
  }));
  const correctRaw = Number((stepText.match(/\*\*Правильный ответ:\*\*\s*(\d+)/) || [])[1] || "1");
  const correctIndex = Number.isFinite(correctRaw) ? Math.max(0, correctRaw - 1) : 0;
  const explanation = (stepText.match(/\*\*Объяснение:\*\*\s*(.+)$/m) || [])[1]?.trim() || "";

  if (!question || options.length === 0) return null;
  const resolvedIndex = Math.min(correctIndex, options.length - 1);
  return {
    question,
    options,
    correctOptionId: options[resolvedIndex].id,
    explanation,
  };
}

function extractStarterCode(contentMd) {
  const candidates = [
    extractSection(contentMd, "Шаблон"),
    extractSection(contentMd, "Код с ошибкой"),
    extractSection(contentMd, "Код"),
    extractSection(contentMd, "Стартовый код"),
    contentMd,
  ];
  for (const candidate of candidates) {
    const code = extractFirstCodeBlock(candidate);
    if (code.trim() !== "") {
      return ensureTrailingNewline(code);
    }
  }
  return "";
}

function parseLessons(markdown) {
  const lines = markdown.split("\n");
  const lessonStarts = [];
  for (let i = 0; i < lines.length; i += 1) {
    const match = lines[i].match(/^#\s+Урок\s+(\d+)\.\s+(.+)$/);
    if (!match) continue;
    lessonStarts.push({
      lineIndex: i,
      number: Number(match[1]),
      title: `Урок ${match[1]}. ${match[2].trim()}`,
      shortTitle: match[2].trim(),
      endLineIndex: lines.length,
    });
  }

  for (let i = 0; i < lessonStarts.length - 1; i += 1) {
    lessonStarts[i].endLineIndex = lessonStarts[i + 1].lineIndex;
  }

  const lessons = [];
  for (const lessonStart of lessonStarts) {
    const lessonLines = lines.slice(lessonStart.lineIndex, lessonStart.endLineIndex);
    const lessonText = lessonLines.join("\n");
    const lessonDescription =
      (lessonText.match(/^\*\*Короткое описание:\*\*\s*(.+)$/m) || [])[1]?.trim() ||
      `Материалы урока ${lessonStart.number}.`;

    const stepStarts = [];
    for (let i = 0; i < lessonLines.length; i += 1) {
      const stepMatch = lessonLines[i].match(/^##\s+Шаг\s+(\d+)\.\s+(.+)$/);
      if (!stepMatch) continue;
      stepStarts.push({
        lineIndex: i,
        position: Number(stepMatch[1]),
        title: stepMatch[2].trim(),
      });
    }

    const blocks = [];
    for (let i = 0; i < stepStarts.length; i += 1) {
      const step = stepStarts[i];
      const nextLineIndex = i + 1 < stepStarts.length ? stepStarts[i + 1].lineIndex : lessonLines.length;
      const stepText = lessonLines.slice(step.lineIndex + 1, nextLineIndex).join("\n").trim();
      const kindRaw = ((stepText.match(/\*\*Вид:\*\*\s*([^\n]+)/) || [])[1] || "").split("·")[0].trim();
      const blockType = normalizeBlockType(kindRaw);
      const contentMd = cleanStepContent(stepText);
      const difficultyRaw = Number((stepText.match(/\*\*Difficulty:\*\*\s*(\d+)/i) || [])[1] || "0");
      const xpRaw = Number((stepText.match(/\*\*XP:\*\*\s*(\d+)/i) || [])[1] || "0");
      const quizPayload = blockType === "quiz" ? parseQuizPayload(stepText) : null;

      let task = null;
      if (isPracticeType(blockType)) {
        const admin = extractAdminSection(stepText);
        const statementMd = contentMd;
        const starterCode = extractStarterCode(contentMd);
        const solutionCode = ensureTrailingNewline(extractFirstCodeBlock(extractSection(admin, "Эталон")));
        let tests = parseTestsFromAdmin(admin);
        if (tests.length === 0) {
          tests = parseTestsFromExamples(contentMd);
        }

        task = {
          title: step.title,
          statementMd,
          starterCode,
          solutionCode,
          difficulty: Number.isFinite(difficultyRaw) && difficultyRaw > 0 ? Math.min(10, difficultyRaw) : 2,
          xpReward: Number.isFinite(xpRaw) && xpRaw > 0 ? xpRaw : 50,
          topic: `Python M1 — ${lessonStart.shortTitle}`,
          language: "python",
          tests: tests.map((item, index) => ({
            inputData: normalizeTestIO(item.inputData),
            expectedOutput: normalizeTestIO(item.expectedOutput),
            isHidden: index > 0,
            position: index + 1,
          })),
        };
      }

      blocks.push({
        position: step.position,
        blockType,
        title: step.title,
        contentMd,
        quizPayload,
        task,
      });
    }

    lessons.push({
      number: lessonStart.number,
      title: lessonStart.title,
      shortTitle: lessonStart.shortTitle,
      contentMd: lessonDescription,
      blocks,
    });
  }

  return lessons;
}

function dollarQuote(input, tagBase) {
  const source = String(input ?? "");
  let tag = tagBase;
  let counter = 0;
  while (source.includes(`$${tag}$`)) {
    counter += 1;
    tag = `${tagBase}_${counter}`;
  }
  return `$${tag}$${source}$${tag}$`;
}

function validateLessons(lessons) {
  const errors = [];
  for (const lesson of lessons) {
    for (const block of lesson.blocks) {
      if (!isPracticeType(block.blockType)) continue;
      if (!block.task) {
        errors.push(`L${lesson.number} step ${block.position} "${block.title}": practice block has no task payload`);
        continue;
      }
      if (!block.task.starterCode.trim()) {
        errors.push(`L${lesson.number} step ${block.position} "${block.title}": starter code is empty`);
      }
      if (!block.task.solutionCode.trim()) {
        errors.push(`L${lesson.number} step ${block.position} "${block.title}": solution code is empty`);
      }
      if (!Array.isArray(block.task.tests) || block.task.tests.length === 0) {
        errors.push(`L${lesson.number} step ${block.position} "${block.title}": test cases are empty`);
      }
      for (const test of block.task.tests) {
        if (typeof test.expectedOutput !== "string") {
          errors.push(`L${lesson.number} step ${block.position} "${block.title}": invalid expected output`);
        }
      }
    }
  }
  if (errors.length > 0) {
    throw new Error(`Validation failed:\n- ${errors.join("\n- ")}`);
  }
}

function buildMigration(lessons) {
  let sql = "";
  sql += "-- 016_seed_python_module1_tasks_bindings_and_tests.sql\n";
  sql += "-- Generated from osnovy_python_platform_ready_v3 (1).md\n";
  sql += "-- Purpose:\n";
  sql += "-- 1) Seed full task catalog for python-zero module 1 lessons 2-13.\n";
  sql += "-- 2) Attach every practice block to a real task_id.\n";
  sql += "-- 3) Seed task test-cases from admin examples for platform auto-check.\n";
  sql += "-- 4) Keep lesson blocks synchronized with current markdown import source.\n\n";

  sql += "INSERT INTO courses(slug, title, description, is_published)\n";
  sql += "VALUES (\n";
  sql += "    'python-zero',\n";
  sql += "    'Python с нуля',\n";
  sql += "    'Стартовый курс по Python: вывод, переменные, ввод и первые вычисления.',\n";
  sql += "    TRUE\n";
  sql += ")\n";
  sql += "ON CONFLICT (slug) DO UPDATE\n";
  sql += "SET title = EXCLUDED.title,\n";
  sql += "    description = EXCLUDED.description,\n";
  sql += "    is_published = TRUE,\n";
  sql += "    updated_at = NOW();\n\n";

  sql += "WITH course_ref AS (\n";
  sql += "    SELECT id AS course_id\n";
  sql += "    FROM courses\n";
  sql += "    WHERE slug = 'python-zero'\n";
  sql += ")\n";
  sql += "INSERT INTO modules(course_id, title, position)\n";
  sql += "SELECT course_id, 'Модуль 1. Базовый синтаксис', 1\n";
  sql += "FROM course_ref\n";
  sql += "ON CONFLICT (course_id, position) DO UPDATE\n";
  sql += "SET title = EXCLUDED.title,\n";
  sql += "    updated_at = NOW();\n\n";

  sql += "WITH module_ref AS (\n";
  sql += "    SELECT m.id AS module_id\n";
  sql += "    FROM modules m\n";
  sql += "    JOIN courses c ON c.id = m.course_id\n";
  sql += "    WHERE c.slug = 'python-zero' AND m.position = 1\n";
  sql += "), lesson_seed(position, title, content_md) AS (\n";
  sql += "    VALUES\n";

  for (let i = 0; i < lessons.length; i += 1) {
    const lesson = lessons[i];
    const suffix = i + 1 < lessons.length ? "," : "";
    sql += `    (${lesson.number}, ${dollarQuote(lesson.title, `l${lesson.number}_title`)}, ${dollarQuote(lesson.contentMd, `l${lesson.number}_content`)})${suffix}\n`;
  }

  sql += ")\n";
  sql += "INSERT INTO lessons(module_id, title, content_md, position, is_published)\n";
  sql += "SELECT\n";
  sql += "    mr.module_id,\n";
  sql += "    ls.title,\n";
  sql += "    ls.content_md,\n";
  sql += "    ls.position,\n";
  sql += "    TRUE\n";
  sql += "FROM module_ref mr\n";
  sql += "CROSS JOIN lesson_seed ls\n";
  sql += "ON CONFLICT (module_id, position) DO UPDATE\n";
  sql += "SET title = EXCLUDED.title,\n";
  sql += "    content_md = EXCLUDED.content_md,\n";
  sql += "    is_published = TRUE,\n";
  sql += "    updated_at = NOW();\n\n";

  for (const lesson of lessons) {
    const practiceBlocks = lesson.blocks.filter((block) => isPracticeType(block.blockType) && block.task);
    const lessonPrefix = `l${lesson.number}`;

    sql += `-- Lesson ${lesson.number}: ${lesson.title}\n`;
    sql += "WITH lesson_ref AS (\n";
    sql += "    SELECT l.id AS lesson_id\n";
    sql += "    FROM lessons l\n";
    sql += "    JOIN modules m ON m.id = l.module_id\n";
    sql += "    JOIN courses c ON c.id = m.course_id\n";
    sql += `    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = ${lesson.number}\n`;
    sql += "), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (\n";
    sql += "    VALUES\n";

    for (let i = 0; i < practiceBlocks.length; i += 1) {
      const block = practiceBlocks[i];
      const task = block.task;
      const suffix = i + 1 < practiceBlocks.length ? "," : "";
      const sourcePolicy = JSON.stringify({
        language: "python",
        emptySourceMessage: "Код пока пуст. Добавьте решение и запустите проверку снова.",
        ignoreCommentOnlyLines: true,
      });
      sql += `    (${dollarQuote(task.title, `${lessonPrefix}_t${block.position}_title`)}, ${dollarQuote(task.statementMd, `${lessonPrefix}_t${block.position}_statement`)}, ${dollarQuote(task.starterCode, `${lessonPrefix}_t${block.position}_starter`)}, ${dollarQuote(task.solutionCode, `${lessonPrefix}_t${block.position}_solution`)}, ${task.difficulty}, ${task.xpReward}, ${dollarQuote(task.topic, `${lessonPrefix}_t${block.position}_topic`)}, 'python', ${dollarQuote(sourcePolicy, `${lessonPrefix}_t${block.position}_policy`)}::jsonb)${suffix}\n`;
    }

    sql += ")\n";
    sql += "INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)\n";
    sql += "SELECT\n";
    sql += "    lr.lesson_id,\n";
    sql += "    ts.title,\n";
    sql += "    ts.statement_md,\n";
    sql += "    ts.starter_code,\n";
    sql += "    ts.solution_code,\n";
    sql += "    ts.difficulty,\n";
    sql += "    ts.xp_reward,\n";
    sql += "    ts.topic,\n";
    sql += "    ts.language,\n";
    sql += "    ts.source_policy,\n";
    sql += "    TRUE\n";
    sql += "FROM lesson_ref lr\n";
    sql += "CROSS JOIN task_seed ts\n";
    sql += "ON CONFLICT (lesson_id, title) DO UPDATE\n";
    sql += "SET statement_md = EXCLUDED.statement_md,\n";
    sql += "    starter_code = EXCLUDED.starter_code,\n";
    sql += "    solution_code = EXCLUDED.solution_code,\n";
    sql += "    difficulty = EXCLUDED.difficulty,\n";
    sql += "    xp_reward = EXCLUDED.xp_reward,\n";
    sql += "    topic = EXCLUDED.topic,\n";
    sql += "    language = EXCLUDED.language,\n";
    sql += "    source_policy = EXCLUDED.source_policy,\n";
    sql += "    is_published = TRUE,\n";
    sql += "    updated_at = NOW();\n\n";

    sql += "WITH lesson_ref AS (\n";
    sql += "    SELECT l.id AS lesson_id\n";
    sql += "    FROM lessons l\n";
    sql += "    JOIN modules m ON m.id = l.module_id\n";
    sql += "    JOIN courses c ON c.id = m.course_id\n";
    sql += `    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = ${lesson.number}\n`;
    sql += "), target_tasks AS (\n";
    sql += "    SELECT t.id\n";
    sql += "    FROM tasks t\n";
    sql += "    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id\n";
    sql += "    WHERE t.title IN (\n";
    for (let i = 0; i < practiceBlocks.length; i += 1) {
      const suffix = i + 1 < practiceBlocks.length ? "," : "";
      sql += `        ${dollarQuote(practiceBlocks[i].task.title, `${lessonPrefix}_t${practiceBlocks[i].position}_delete_title`)}${suffix}\n`;
    }
    sql += "    )\n";
    sql += ")\n";
    sql += "DELETE FROM task_test_cases tc\n";
    sql += "USING target_tasks tt\n";
    sql += "WHERE tc.task_id = tt.id;\n\n";

    sql += "WITH lesson_ref AS (\n";
    sql += "    SELECT l.id AS lesson_id\n";
    sql += "    FROM lessons l\n";
    sql += "    JOIN modules m ON m.id = l.module_id\n";
    sql += "    JOIN courses c ON c.id = m.course_id\n";
    sql += `    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = ${lesson.number}\n`;
    sql += "), task_lookup AS (\n";
    sql += "    SELECT t.id, t.title\n";
    sql += "    FROM tasks t\n";
    sql += "    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id\n";
    sql += "), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (\n";
    sql += "    VALUES\n";
    const allTests = [];
    for (const block of practiceBlocks) {
      for (const test of block.task.tests) {
        allTests.push({
          taskTitle: block.task.title,
          inputData: test.inputData,
          expectedOutput: test.expectedOutput,
          isHidden: test.isHidden,
          position: test.position,
          blockPosition: block.position,
        });
      }
    }
    for (let i = 0; i < allTests.length; i += 1) {
      const item = allTests[i];
      const suffix = i + 1 < allTests.length ? "," : "";
      sql += `    (${dollarQuote(item.taskTitle, `${lessonPrefix}_test_${item.blockPosition}_${item.position}_title`)}, ${dollarQuote(item.inputData, `${lessonPrefix}_test_${item.blockPosition}_${item.position}_input`)}, ${dollarQuote(item.expectedOutput, `${lessonPrefix}_test_${item.blockPosition}_${item.position}_expected`)}, ${item.isHidden ? "TRUE" : "FALSE"}, ${item.position})${suffix}\n`;
    }
    sql += "), resolved AS (\n";
    sql += "    SELECT\n";
    sql += "        tl.id AS task_id,\n";
    sql += "        ts.input_data,\n";
    sql += "        ts.expected_output,\n";
    sql += "        ts.is_hidden,\n";
    sql += "        ts.position\n";
    sql += "    FROM test_seed ts\n";
    sql += "    JOIN task_lookup tl ON tl.title = ts.task_title\n";
    sql += ")\n";
    sql += "INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)\n";
    sql += "SELECT task_id, input_data, expected_output, is_hidden, position\n";
    sql += "FROM resolved\n";
    sql += "ORDER BY task_id, position;\n\n";

    sql += "WITH lesson_ref AS (\n";
    sql += "    SELECT l.id AS lesson_id\n";
    sql += "    FROM lessons l\n";
    sql += "    JOIN modules m ON m.id = l.module_id\n";
    sql += "    JOIN courses c ON c.id = m.course_id\n";
    sql += `    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = ${lesson.number}\n`;
    sql += "), task_lookup AS (\n";
    sql += "    SELECT t.title, t.id AS task_id\n";
    sql += "    FROM tasks t\n";
    sql += "    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id\n";
    sql += "), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (\n";
    sql += "    VALUES\n";
    for (let i = 0; i < lesson.blocks.length; i += 1) {
      const block = lesson.blocks[i];
      const suffix = i + 1 < lesson.blocks.length ? "," : "";
      const taskTitleSQL = block.task ? dollarQuote(block.task.title, `${lessonPrefix}_b${block.position}_task`) : "NULL";
      const quizSQL = block.quizPayload
        ? `${dollarQuote(JSON.stringify(block.quizPayload), `${lessonPrefix}_b${block.position}_quiz`)}::jsonb`
        : "NULL::jsonb";
      sql += `    (${block.position}, '${block.blockType}', ${dollarQuote(block.title, `${lessonPrefix}_b${block.position}_title`)}, ${dollarQuote(block.contentMd, `${lessonPrefix}_b${block.position}_content`)}, ${taskTitleSQL}, ${quizSQL})${suffix}\n`;
    }
    sql += "), resolved AS (\n";
    sql += "    SELECT\n";
    sql += "        bs.position,\n";
    sql += "        bs.block_type,\n";
    sql += "        bs.title,\n";
    sql += "        bs.content_md,\n";
    sql += "        tl.task_id,\n";
    sql += "        bs.quiz_payload\n";
    sql += "    FROM block_seed bs\n";
    sql += "    LEFT JOIN task_lookup tl ON tl.title = bs.task_title\n";
    sql += ")\n";
    sql += "INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)\n";
    sql += "SELECT\n";
    sql += "    lr.lesson_id,\n";
    sql += "    r.block_type,\n";
    sql += "    r.title,\n";
    sql += "    r.content_md,\n";
    sql += "    r.task_id,\n";
    sql += "    r.quiz_payload,\n";
    sql += "    r.position,\n";
    sql += "    TRUE\n";
    sql += "FROM lesson_ref lr\n";
    sql += "CROSS JOIN resolved r\n";
    sql += "ON CONFLICT (lesson_id, position) DO UPDATE\n";
    sql += "SET block_type = EXCLUDED.block_type,\n";
    sql += "    title = EXCLUDED.title,\n";
    sql += "    content_md = EXCLUDED.content_md,\n";
    sql += "    task_id = EXCLUDED.task_id,\n";
    sql += "    quiz_payload = EXCLUDED.quiz_payload,\n";
    sql += "    is_published = TRUE,\n";
    sql += "    updated_at = NOW();\n\n";
  }

  return sql;
}

function summarize(lessons) {
  let taskCount = 0;
  let testCount = 0;
  for (const lesson of lessons) {
    for (const block of lesson.blocks) {
      if (!block.task) continue;
      taskCount += 1;
      testCount += block.task.tests.length;
    }
  }
  return { lessonCount: lessons.length, taskCount, testCount };
}

function main() {
  const markdown = readMarkdown(mdPath);
  const allLessons = parseLessons(markdown);
  const lessons = allLessons.filter((lesson) => lesson.number >= 2 && lesson.number <= 13);

  validateLessons(lessons);
  const sql = buildMigration(lessons);
  fs.writeFileSync(outPath, sql, "utf8");

  const stats = summarize(lessons);
  console.log(`Generated migration: ${outPath}`);
  console.log(`Lessons: ${stats.lessonCount}`);
  console.log(`Tasks: ${stats.taskCount}`);
  console.log(`Tests: ${stats.testCount}`);
}

main();
