const fs = require("fs");

const mdPath = "C:/Users/Artemy/Downloads/osnovy_python_platform_ready_v3 (1).md";
const outPath = "C:/prog/Comercial/LeonovCarePlatform/backend/migrations/015_seed_python_module1_lessons_2_13.sql";

function readMarkdown(filePath) {
  return fs.readFileSync(filePath, "utf8").replace(/\r\n/g, "\n");
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

function extractSection(stepText, heading) {
  const headerRegex = new RegExp(`^###\\s+${heading}\\s*$`, "m");
  const startIndex = stepText.search(headerRegex);
  if (startIndex === -1) return "";
  const headerMatch = stepText.slice(startIndex).match(headerRegex);
  if (!headerMatch) return "";
  const afterStart = startIndex + headerMatch[0].length;
  const tail = stepText.slice(afterStart);
  const endMatch = tail.match(/\n###\s+|\n<details>|\n##\s+Шаг\s+/);
  return (endMatch ? tail.slice(0, endMatch.index) : tail).trim();
}

function normalizeBlockType(kindRaw) {
  const value = String(kindRaw ?? "").trim().toLowerCase();
  if (value.includes("тест")) return "quiz";
  if (value.includes("практика") || value.includes("исправление") || value.includes("контроль")) return "practice";
  if (value.includes("итог")) return "summary";
  return "theory";
}

function cleanStepContent(stepText) {
  return String(stepText ?? "")
    .replace(/<details>[\s\S]*?<\/details>/g, "")
    .replace(/^\*\*Вид:\*\*.*$/m, "")
    .replace(/^\s+|\s+$/g, "")
    .replace(/\n{3,}/g, "\n\n");
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
    });
  }

  for (let i = 0; i < lessonStarts.length; i += 1) {
    lessonStarts[i].endLineIndex = i + 1 < lessonStarts.length ? lessonStarts[i + 1].lineIndex : lines.length;
  }

  const lessons = [];
  for (const lessonStart of lessonStarts) {
    const lessonLines = lines.slice(lessonStart.lineIndex, lessonStart.endLineIndex);
    const lessonText = lessonLines.join("\n");

    const shortDescription =
      (lessonText.match(/^\*\*Короткое описание:\*\*\s*(.+)$/m) || [])[1]?.trim() ??
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
      const current = stepStarts[i];
      const nextLineIndex = i + 1 < stepStarts.length ? stepStarts[i + 1].lineIndex : lessonLines.length;
      const stepBody = lessonLines.slice(current.lineIndex + 1, nextLineIndex).join("\n").trim();

      const kindRaw = ((stepBody.match(/\*\*Вид:\*\*\s*([^\n]+)/) || [])[1] || "").split("·")[0].trim();
      const blockType = normalizeBlockType(kindRaw);

      let quizPayload = null;
      if (blockType === "quiz") {
        const question = extractSection(stepBody, "Вопрос").replace(/\n+/g, " ").trim();
        const optionsSection = extractSection(stepBody, "Варианты");
        const options = [...optionsSection.matchAll(/^\s*\d+\.\s+(.+)$/gm)].map((match, index) => ({
          id: String.fromCharCode(65 + index),
          text: match[1].trim(),
        }));

        const correctRaw = Number(((stepBody.match(/\*\*Правильный ответ:\*\*\s*(\d+)/) || [])[1] || "1"));
        const correctIndex = Number.isFinite(correctRaw) ? Math.max(0, correctRaw - 1) : 0;
        const explanation = (stepBody.match(/\*\*Объяснение:\*\*\s*(.+)$/m) || [])[1]?.trim() || "";

        if (question && options.length > 0) {
          const correctedIndex = Math.min(correctIndex, options.length - 1);
          quizPayload = {
            question,
            options,
            correctOptionId: options[correctedIndex].id,
            explanation,
          };
        }
      }

      blocks.push({
        position: current.position,
        blockType,
        title: current.title,
        contentMd: cleanStepContent(stepBody),
        quizPayload,
      });
    }

    lessons.push({
      number: lessonStart.number,
      title: lessonStart.title,
      contentMd: shortDescription,
      blocks,
    });
  }

  return lessons;
}

function buildMigration(lessons) {
  const targetLessons = lessons.filter((lesson) => lesson.number >= 2 && lesson.number <= 13);

  let sql = "";
  sql += "-- 015_seed_python_module1_lessons_2_13.sql\n";
  sql += "-- Generated from osnovy_python_platform_ready_v3 (1).md\n";
  sql += "-- Purpose: add module 1 lessons 2-13 with lesson blocks and quiz payload.\n\n";

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

  for (let i = 0; i < targetLessons.length; i += 1) {
    const lesson = targetLessons[i];
    const suffix = i + 1 < targetLessons.length ? "," : "";
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

  sql += "WITH lesson_ref AS (\n";
  sql += "    SELECT l.id\n";
  sql += "    FROM lessons l\n";
  sql += "    JOIN modules m ON m.id = l.module_id\n";
  sql += "    JOIN courses c ON c.id = m.course_id\n";
  sql += "    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position BETWEEN 2 AND 13\n";
  sql += ")\n";
  sql += "DELETE FROM lesson_blocks lb\n";
  sql += "USING lesson_ref lr\n";
  sql += "WHERE lb.lesson_id = lr.id;\n\n";

  for (const lesson of targetLessons) {
    sql += `-- Lesson ${lesson.number}: ${lesson.title}\n`;
    sql += "WITH lesson_ref AS (\n";
    sql += "    SELECT l.id AS lesson_id\n";
    sql += "    FROM lessons l\n";
    sql += "    JOIN modules m ON m.id = l.module_id\n";
    sql += "    JOIN courses c ON c.id = m.course_id\n";
    sql += `    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = ${lesson.number}\n`;
    sql += "), block_seed(position, block_type, title, content_md, quiz_payload) AS (\n";
    sql += "    VALUES\n";

    for (let i = 0; i < lesson.blocks.length; i += 1) {
      const block = lesson.blocks[i];
      const suffix = i + 1 < lesson.blocks.length ? "," : "";
      const quizSQL = block.quizPayload ? `${dollarQuote(JSON.stringify(block.quizPayload), `l${lesson.number}_b${block.position}_quiz`)}::jsonb` : "NULL::jsonb";
      sql += `    (${block.position}, '${block.blockType}', ${dollarQuote(block.title, `l${lesson.number}_b${block.position}_title`)}, ${dollarQuote(block.contentMd, `l${lesson.number}_b${block.position}_content`)}, ${quizSQL})${suffix}\n`;
    }

    sql += ")\n";
    sql += "INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)\n";
    sql += "SELECT\n";
    sql += "    lr.lesson_id,\n";
    sql += "    bs.block_type,\n";
    sql += "    bs.title,\n";
    sql += "    bs.content_md,\n";
    sql += "    NULL,\n";
    sql += "    bs.quiz_payload,\n";
    sql += "    bs.position,\n";
    sql += "    TRUE\n";
    sql += "FROM lesson_ref lr\n";
    sql += "CROSS JOIN block_seed bs\n";
    sql += "ON CONFLICT (lesson_id, position) DO UPDATE\n";
    sql += "SET block_type = EXCLUDED.block_type,\n";
    sql += "    title = EXCLUDED.title,\n";
    sql += "    content_md = EXCLUDED.content_md,\n";
    sql += "    task_id = EXCLUDED.task_id,\n";
    sql += "    quiz_payload = EXCLUDED.quiz_payload,\n";
    sql += "    is_published = TRUE,\n";
    sql += "    updated_at = NOW();\n\n";
  }

  return { sql, targetLessons };
}

function main() {
  const markdown = readMarkdown(mdPath);
  const lessons = parseLessons(markdown);
  const { sql, targetLessons } = buildMigration(lessons);
  fs.writeFileSync(outPath, sql, "utf8");

  console.log(`Generated migration: ${outPath}`);
  console.log(`Lessons parsed: ${lessons.length}`);
  for (const lesson of targetLessons) {
    console.log(`L${lesson.number}: ${lesson.blocks.length} blocks`);
  }
}

main();
