const fs = require("fs");
const { spawnSync } = require("child_process");

const MD_PATH = "C:/Users/Artemy/Downloads/python_course_platform_v4_full.md";
const MANIFEST_PATH = "C:/Users/Artemy/Downloads/import_manifest.csv";
const OUT_PATH = "C:/prog/Comercial/LeonovCarePlatform/backend/migrations/020_reseed_python_zero_full_v4_sql_checker_and_gap_reduction.sql";

const COURSE = {
  slug: "python-zero",
  title: "Python с нуля — Full Stack + AI",
  description:
    "Полный курс на 5 месяцев: Python Core, Python Hard, SQL/сети, FastAPI/DevOps, финальный проект и AI-интеграция.",
};

const MODULE_CONFIG = {
  "03_month_1_python_core_existing_v3.md": {
    position: 1,
    title: "Месяц 1. Python Core",
    defaultLanguage: "python",
  },
  "04_month_2_python_hard.md": {
    position: 2,
    title: "Месяц 2. Python Hard",
    defaultLanguage: "python",
  },
  "05_month_3_sql_networks.md": {
    position: 3,
    title: "Месяц 3. SQL и сети",
    defaultLanguage: "sql",
  },
  "06_month_4_fastapi_devops.md": {
    position: 4,
    title: "Месяц 4. FastAPI и DevOps",
    defaultLanguage: "python",
  },
  "07_month_5_final_ai_deploy.md": {
    position: 5,
    title: "Месяц 5. Финальный проект, AI и деплой",
    defaultLanguage: "python",
  },
};

const PRACTICE_BODY_FORBIDDEN = [
  "Шаблон",
  "Подсказки",
  "Эталон",
  "Автотесты",
  "Админ",
  "Скрытые тесты",
  "AI-инструкция",
];

function readText(path) {
  return fs.readFileSync(path, "utf8").replace(/\r\n/g, "\n").replace(/\r/g, "\n");
}

function escapeRegExp(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function normalizeSpaces(value) {
  return String(value ?? "")
    .replace(/\u00a0/g, " ")
    .replace(/[ \t]+/g, " ")
    .trim();
}

function normalizeKey(value) {
  return normalizeSpaces(value)
    .toLowerCase()
    .replace(/[ё]/g, "е")
    .replace(/[`"'«»]/g, "")
    .replace(/[^\p{L}\p{N}]+/gu, " ")
    .trim();
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

function parseCsvManifest(csvRaw) {
  const lines = csvRaw.split("\n").filter((line) => line.trim() !== "");
  const rows = lines.slice(1).map((line, index) => {
    const parts = line.split(",");
    if (parts.length < 6) {
      throw new Error(`CSV parse error on line ${index + 2}: ${line}`);
    }
    return {
      file: parts[0].trim(),
      lessonNum: Number(parts[1] || "0"),
      lessonTitle: parts[2].trim(),
      stepNum: parts[3] ? Number(parts[3]) : 0,
      stepTitle: parts[4].trim(),
      blockType: parts[5].trim().toLowerCase(),
    };
  });

  const fileOrder = [];
  const files = new Map();
  for (const row of rows) {
    if (!files.has(row.file)) {
      files.set(row.file, {
        file: row.file,
        lessons: [],
        lessonByKey: new Map(),
      });
      fileOrder.push(row.file);
    }
    const fileData = files.get(row.file);
    const lessonKey = `${row.lessonNum}:${normalizeKey(row.lessonTitle)}`;
    if (!fileData.lessonByKey.has(lessonKey)) {
      const lesson = {
        lessonNum: row.lessonNum,
        lessonTitle: row.lessonTitle,
        steps: [],
      };
      fileData.lessonByKey.set(lessonKey, lesson);
      fileData.lessons.push(lesson);
    }
    if (row.blockType === "step") {
      fileData.lessonByKey.get(lessonKey).steps.push({
        stepNum: row.stepNum,
        stepTitle: row.stepTitle,
      });
    }
  }

  return fileOrder.map((file) => files.get(file));
}

function parseLessonsFromMarkdown(markdown) {
  const lines = markdown.split("\n");

  const lessonRegexes = [
    /^#{1,3}\s+Урок\s+(\d+)\s*[.\-:]\s*(.+)$/u,
    /^#{1,3}\s+Урок\s+(\d+)\s+(.+)$/u,
  ];
  const stepRegexes = [
    /^#{2,4}\s+Шаг\s+(\d+)\s*[.\-:]\s*(.+)$/u,
    /^#{2,4}\s+Шаг\s+(\d+)\s+(.+)$/u,
  ];

  const lessons = [];
  const lessonStarts = [];
  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    let match = null;
    for (const re of lessonRegexes) {
      match = line.match(re);
      if (match) break;
    }
    if (!match) continue;
    lessonStarts.push({
      startLine: i,
      lessonNum: Number(match[1]),
      lessonTitle: normalizeSpaces(match[2]),
    });
  }

  for (let i = 0; i < lessonStarts.length; i += 1) {
    const current = lessonStarts[i];
    const endLine = i + 1 < lessonStarts.length ? lessonStarts[i + 1].startLine : lines.length;
    const lessonLines = lines.slice(current.startLine, endLine);
    const lessonText = lessonLines.join("\n");

    const stepStarts = [];
    for (let j = 0; j < lessonLines.length; j += 1) {
      const line = lessonLines[j];
      let stepMatch = null;
      for (const re of stepRegexes) {
        stepMatch = line.match(re);
        if (stepMatch) break;
      }
      if (!stepMatch) continue;
      stepStarts.push({
        localLine: j,
        stepNum: Number(stepMatch[1]),
        stepTitle: normalizeSpaces(stepMatch[2]),
      });
    }

    const steps = [];
    for (let j = 0; j < stepStarts.length; j += 1) {
      const currentStep = stepStarts[j];
      const nextLocalLine = j + 1 < stepStarts.length ? stepStarts[j + 1].localLine : lessonLines.length;
      const rawStepBody = lessonLines.slice(currentStep.localLine + 1, nextLocalLine).join("\n").trim();
      steps.push({
        stepNum: currentStep.stepNum,
        stepTitle: currentStep.stepTitle,
        rawStepBody,
      });
    }

    lessons.push({
      lessonNum: current.lessonNum,
      lessonTitle: current.lessonTitle,
      rawLessonText: lessonText,
      steps,
    });
  }

  return lessons;
}

function extractLessonDescription(rawLessonText, lessonNum) {
  const short =
    (rawLessonText.match(/^\*\*Короткое описание:\*\*\s*(.+)$/imu) || [])[1] ||
    (rawLessonText.match(/^\*\*Коротко:\*\*\s*(.+)$/imu) || [])[1] ||
    "";
  if (short.trim() !== "") return normalizeSpaces(short);
  return `Материалы урока ${lessonNum}.`;
}

function matchManifestToParsedLessons(manifestFiles, parsedLessons) {
  const result = [];
  let cursor = 0;

  for (const fileData of manifestFiles) {
    if (!MODULE_CONFIG[fileData.file]) {
      throw new Error(`No module config for file "${fileData.file}"`);
    }
    const moduleCfg = MODULE_CONFIG[fileData.file];
    const moduleLessons = [];

    for (const expectedLesson of fileData.lessons) {
      const expectedKey = `${expectedLesson.lessonNum}:${normalizeKey(expectedLesson.lessonTitle)}`;
      let found = null;
      for (let i = cursor; i < parsedLessons.length; i += 1) {
        const candidate = parsedLessons[i];
        const candidateKey = `${candidate.lessonNum}:${normalizeKey(candidate.lessonTitle)}`;
        if (candidateKey === expectedKey) {
          found = { index: i, lesson: candidate };
          break;
        }
      }
      if (!found) {
        throw new Error(
          `Cannot match lesson from manifest: file=${fileData.file}, lesson=${expectedLesson.lessonNum}. ${expectedLesson.lessonTitle}`
        );
      }
      cursor = found.index + 1;

      const parsedStepsByNum = new Map();
      for (const parsedStep of found.lesson.steps) {
        if (!parsedStepsByNum.has(parsedStep.stepNum)) parsedStepsByNum.set(parsedStep.stepNum, []);
        parsedStepsByNum.get(parsedStep.stepNum).push(parsedStep);
      }

      const matchedSteps = [];
      for (const expectedStep of expectedLesson.steps) {
        const candidates = parsedStepsByNum.get(expectedStep.stepNum) || [];
        let matched = candidates.find((step) => normalizeKey(step.stepTitle) === normalizeKey(expectedStep.stepTitle));
        if (!matched && candidates.length > 0) matched = candidates[0];
        if (!matched) {
          throw new Error(
            `Cannot match step from manifest: file=${fileData.file}, lesson=${expectedLesson.lessonNum} "${expectedLesson.lessonTitle}", step=${expectedStep.stepNum} "${expectedStep.stepTitle}"`
          );
        }
        matchedSteps.push({
          stepNum: expectedStep.stepNum,
          stepTitle: expectedStep.stepTitle,
          rawStepBody: matched.rawStepBody,
        });
      }

      moduleLessons.push({
        file: fileData.file,
        modulePosition: moduleCfg.position,
        moduleTitle: moduleCfg.title,
        defaultLanguage: moduleCfg.defaultLanguage,
        lessonNum: expectedLesson.lessonNum,
        lessonTitle: expectedLesson.lessonTitle,
        lessonContent: extractLessonDescription(found.lesson.rawLessonText, expectedLesson.lessonNum),
        steps: matchedSteps,
      });
    }

    result.push({
      file: fileData.file,
      modulePosition: moduleCfg.position,
      moduleTitle: moduleCfg.title,
      defaultLanguage: moduleCfg.defaultLanguage,
      lessons: moduleLessons,
    });
  }

  return result;
}

function parseStepMeta(rawStepBody) {
  const metaLine =
    ((rawStepBody.match(/^\s*(?:\*\*)?Вид:(?:\*\*)?\s*(.+)$/imu) || [])[1] || "").trim();
  const metaPlain = metaLine.replace(/\*\*/g, "");
  const segments = metaPlain
    .split("·")
    .map((segment) => normalizeSpaces(segment))
    .filter((segment) => segment !== "");

  const rawType = segments.length > 0 ? segments[0] : "Теория";
  const difficulty = Number(((metaPlain.match(/Difficulty\s*:\s*(\d+)/iu) || [])[1] || "0"));
  const xp = Number(((metaPlain.match(/XP\s*:\s*(\d+)/iu) || [])[1] || "0"));
  const language = ((metaPlain.match(/Language\s*:\s*([^\s·]+)/iu) || [])[1] || "")
    .trim()
    .toLowerCase();

  return {
    rawType,
    difficulty: Number.isFinite(difficulty) && difficulty > 0 ? difficulty : 0,
    xp: Number.isFinite(xp) && xp > 0 ? xp : 0,
    language,
  };
}

function normalizeBlockType(rawType) {
  const value = normalizeKey(rawType);
  if (value.includes("теория")) return "theory";
  if (value.includes("практика")) return "practice";
  if (value.includes("исправление")) return "practice";
  if (value.includes("контроль")) return "practice";
  if (value.includes("тест")) return "quiz";
  if (value.includes("проект")) return "project";
  if (value.includes("итог")) return "summary";
  if (value.includes("ai check")) return "project";
  if (value.includes("чеклист")) return "summary";
  if (value.includes("устная защита")) return "summary";
  if (value.includes("рубрика")) return "summary";
  return "theory";
}

function stripAdminAndService(rawStepBody) {
  let studentText = String(rawStepBody ?? "");
  const adminChunks = [];

  const detailsRegex = /<details>[\s\S]*?<\/details>/giu;
  studentText = studentText.replace(detailsRegex, (chunk) => {
    if (/админ|admin/iu.test(chunk)) adminChunks.push(chunk);
    return "";
  });

  const adminFenceRegex = /:::\s*admin[\s\S]*?:::/giu;
  studentText = studentText.replace(adminFenceRegex, (chunk) => {
    adminChunks.push(chunk);
    return "";
  });

  studentText = studentText
    .replace(/^\*\*Вид:\*\*.*$/gimu, "")
    .replace(/^\s+|\s+$/g, "")
    .replace(/\n{3,}/g, "\n\n");

  return {
    studentText,
    adminText: adminChunks.join("\n\n").trim(),
  };
}

function canonicalSectionName(rawName) {
  const key = normalizeKey(rawName);
  if (key === "ввод") return "Вход";
  if (key === "выходные данные") return "Выход";
  if (key === "что должно получиться") return "Выход";
  if (key === "задание") return "Условие";
  if (key === "критерии зачета") return "Критерии зачёта";
  if (key === "ai инструкция") return "AI-инструкция";
  if (key === "ученик видит") return "Ученик видит";
  if (key === "коротко") return "Коротко";
  if (key === "условие") return "Условие";
  if (key === "вход") return "Вход";
  if (key === "выход") return "Выход";
  if (key === "шаблон") return "Шаблон";
  if (key === "подсказки") return "Подсказки";
  if (key === "эталон") return "Эталон";
  if (key === "автотесты") return "Автотесты";
  if (key === "скрытые тесты") return "Скрытые тесты";
  if (key === "проверка") return "Проверка";
  if (key === "методический комментарий") return "Методический комментарий";
  return rawName;
}

function splitSections(rawText) {
  const text = String(rawText ?? "");
  const lines = text.split("\n");

  const knownNames = [
    "Коротко",
    "Условие",
    "Вход",
    "Ввод",
    "Выход",
    "Выходные данные",
    "Что должно получиться",
    "Задание",
    "Шаблон",
    "Подсказки",
    "Эталон",
    "Автотесты",
    "Скрытые тесты",
    "Ученик видит",
    "Проверка",
    "Критерии зачёта",
    "Критерии зачета",
    "Методический комментарий",
    "AI-инструкция",
  ];
  const knownGroup = knownNames.map(escapeRegExp).join("|");

  const exampleOnlyRe = /^\s*(?:#{2,6}\s+|\*\*\s*)?Пример\s+(\d+)(?:\s*\*\*)?\s*:?\s*$/iu;
  const knownOnlyLooseRe = new RegExp(
    `^\\s*(?:#{2,6}\\s+|\\*\\*\\s*)?(${knownGroup})(?:\\s*\\*\\*)?\\s*:?\\s*$`,
    "iu"
  );
  const knownOnlyStrictRe = new RegExp(
    `^\\s*(?:#{2,6}\\s+|\\*\\*\\s*)(${knownGroup})(?:\\s*\\*\\*)?\\s*:?\\s*$`,
    "iu"
  );
  const knownInlineLooseRe = new RegExp(
    `^\\s*(?:#{2,6}\\s+|\\*\\*\\s*)?(${knownGroup})(?:\\s*\\*\\*)?\\s*:\\s*(.+)\\s*$`,
    "iu"
  );
  const knownInlineStrictRe = new RegExp(
    `^\\s*(?:#{2,6}\\s+|\\*\\*\\s*)(${knownGroup})(?:\\s*\\*\\*)?\\s*:\\s*(.+)\\s*$`,
    "iu"
  );

  const sections = [];
  let current = { name: "__preamble", lines: [] };

  const pushCurrent = () => {
    const body = current.lines.join("\n").trim();
    sections.push({
      name: current.name,
      body,
    });
  };

  for (const line of lines) {
    const exampleOnly = line.match(exampleOnlyRe);
    if (exampleOnly) {
      pushCurrent();
      current = { name: `Пример ${Number(exampleOnly[1])}`, lines: [] };
      continue;
    }

    const insideExample = /^Пример\s+\d+$/u.test(current.name);
    const knownOnly = line.match(insideExample ? knownOnlyStrictRe : knownOnlyLooseRe);
    if (knownOnly) {
      pushCurrent();
      current = { name: canonicalSectionName(knownOnly[1]), lines: [] };
      continue;
    }

    const knownInline = line.match(insideExample ? knownInlineStrictRe : knownInlineLooseRe);
    if (knownInline) {
      pushCurrent();
      current = { name: canonicalSectionName(knownInline[1]), lines: [knownInline[2].trim()] };
      continue;
    }

    current.lines.push(line);
  }

  pushCurrent();
  return sections.filter((section) => section.name !== "__preamble" || section.body !== "");
}

function getSectionBodies(sections, name) {
  return sections
    .filter((section) => section.name === name)
    .map((section) => section.body.trim())
    .filter((body) => body !== "");
}

function extractFirstCodeBlock(rawText) {
  const match = String(rawText ?? "").match(/```([^\n]*)\n([\s\S]*?)```/u);
  if (!match) {
    return { language: "", code: "" };
  }
  return {
    language: normalizeSpaces(match[1]).toLowerCase(),
    code: match[2].replace(/^\n+/, "").replace(/\n+$/, ""),
  };
}

function extractTextLikeCodeBlock(rawText) {
  const text = String(rawText ?? "");
  const codeBlocks = [...text.matchAll(/```([^\n]*)\n([\s\S]*?)```/gu)];
  for (const block of codeBlocks) {
    const lang = normalizeSpaces(block[1]).toLowerCase();
    if (lang === "" || lang === "text" || lang === "txt" || lang === "stdout" || lang === "output") {
      return block[2].replace(/^\n+/, "").replace(/\n+$/, "");
    }
  }
  return "";
}

function parseHints(rawHintText) {
  const lines = String(rawHintText ?? "")
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line !== "");
  const hints = [];
  for (const line of lines) {
    const normalized = line.replace(/^\d+\.\s*/, "").replace(/^[-*]\s*/, "").trim();
    if (normalized !== "") hints.push(normalized);
  }
  return hints;
}

function extractFieldCode(rawText, labels) {
  const text = String(rawText ?? "");
  const fence = "```";
  for (const label of labels) {
    const labelEscaped = escapeRegExp(label);
    const fenceRe = new RegExp(`${labelEscaped}\\s*:\\s*\\n+\\s*${escapeRegExp(fence)}[^\\n]*\\n([\\s\\S]*?)${escapeRegExp(fence)}`, "iu");
    const fenceMatch = text.match(fenceRe);
    if (fenceMatch) {
      return fenceMatch[1].replace(/^\n+/, "").replace(/\n+$/, "");
    }
    const inlineCodeRe = new RegExp(`${labelEscaped}\\s*:\\s*\`([^\`]+)\``, "iu");
    const inlineMatch = text.match(inlineCodeRe);
    if (inlineMatch) return inlineMatch[1].trim();
  }
  return "";
}

function parseTestsFromText(rawText, isHiddenByDefault) {
  const text = String(rawText ?? "").trim();
  if (text === "") return [];

  const tests = [];
  const markerRe = /^\s*(?:\*\*|#{2,6}\s*)?Тест\s+(\d+)(?:\*\*)?\s*:?\s*$/gimu;
  const markers = [...text.matchAll(markerRe)];

  const chunks = [];
  if (markers.length > 0) {
    for (let i = 0; i < markers.length; i += 1) {
      const start = (markers[i].index || 0) + markers[i][0].length;
      const end = i + 1 < markers.length ? markers[i + 1].index || text.length : text.length;
      chunks.push(text.slice(start, end));
    }
  } else {
    chunks.push(text);
  }

  for (const chunkRaw of chunks) {
    const chunk = chunkRaw.trim();
    if (chunk === "") continue;
    let inputData = extractFieldCode(chunk, ["Ввод", "Input"]);
    let expectedOutput = extractFieldCode(chunk, ["Ожидаемый вывод", "Вывод", "Expected output", "stdout"]);

    if (expectedOutput === "") {
      const stdoutInlineMatch = chunk.match(/тест\s+stdout\s*:\s*`([^`]+)`/iu);
      if (stdoutInlineMatch) expectedOutput = stdoutInlineMatch[1].trim();
    }

    if (inputData === "" && expectedOutput === "") continue;
    tests.push({
      inputData,
      expectedOutput,
      isHidden: !!isHiddenByDefault,
    });
  }

  return tests;
}

function parseExampleIO(exampleBody) {
  const input = extractFieldCode(exampleBody, ["Ввод", "Input"]);
  const output = extractFieldCode(exampleBody, ["Вывод", "Ожидаемый вывод", "Expected output"]);
  if (input === "" && output === "") return null;
  return { inputData: input, expectedOutput: output };
}

function inferFallbackTestFromSections(inputData, outputData, condition) {
  const expectedFromOutput = extractTextLikeCodeBlock(outputData);
  const expectedFromCondition = extractTextLikeCodeBlock(condition);
  const expectedOutput = expectedFromOutput || expectedFromCondition;
  if (expectedOutput.trim() === "") return null;

  const inputFromSection = extractTextLikeCodeBlock(inputData);
  const inputDataValue = inputFromSection.trim() === "" ? "" : inputFromSection;

  return {
    inputData: inputDataValue,
    expectedOutput,
    isHidden: false,
  };
}

function inferPythonStdoutTestFromSolution(solutionCode, inputData) {
  const source = String(solutionCode ?? "").trim();
  if (source === "") return null;

  const inputFromSection = extractTextLikeCodeBlock(inputData);
  const hasInputCall = /\binput\s*\(/u.test(source);
  if (hasInputCall && inputFromSection.trim() === "") return null;

  const run = spawnSync("python", ["-c", source], {
    input: inputFromSection.replace(/\r/g, ""),
    encoding: "utf8",
    timeout: 2500,
    maxBuffer: 512 * 1024,
    windowsHide: true,
  });

  if (run.error) return null;
  if (typeof run.status === "number" && run.status !== 0) return null;

  const stdout = String(run.stdout ?? "").replace(/\r/g, "");
  if (stdout.trim() === "") return null;

  return {
    inputData: inputFromSection.replace(/\r/g, ""),
    expectedOutput: stdout,
    isHidden: false,
  };
}

function inferPythonSourceEquivalenceTest(solutionCode) {
  const source = String(solutionCode ?? "").trim();
  if (source === "") return null;
  return {
    inputData: "",
    expectedOutput: `__SOURCE_EQ__\n${source}`,
    isHidden: true,
  };
}

function detectTaskLanguage(moduleDefaultLanguage, templateLang, solutionLang, metaLang) {
  const candidates = [metaLang, templateLang, solutionLang, moduleDefaultLanguage]
    .map((value) => normalizeSpaces(value).toLowerCase())
    .filter((value) => value !== "");
  const first = candidates[0] || "python";
  if (first === "py" || first === "python3") return "python";
  if (first === "js") return "javascript";
  if (first === "sh" || first === "shell") return "bash";
  return first;
}

function buildPracticeBody(shortText, condition, inputData, outputData, examples) {
  const parts = [];
  if (shortText) parts.push(`**Коротко:** ${shortText}`);
  if (condition) parts.push(`### Условие\n\n${condition}`);
  if (inputData) parts.push(`### Вход\n\n${inputData}`);
  if (outputData) parts.push(`### Выход\n\n${outputData}`);

  const visibleExamples = examples
    .slice()
    .sort((a, b) => a.order - b.order)
    .slice(0, 3);
  for (const example of visibleExamples) {
    if (!example.body) continue;
    parts.push(`### Пример ${example.order}\n\n${example.body}`);
  }
  return parts.join("\n\n").trim();
}

function assertPracticeBodySafe(bodyMarkdown, contextLabel) {
  const text = String(bodyMarkdown ?? "");
  const forbiddenRe = /(?:^|\n)\s*(?:#{1,6}\s*)?(Шаблон|Подсказки|Эталон|Автотесты|Админ|Скрытые тесты|AI-инструкция)\b/iu;
  const match = text.match(forbiddenRe);
  if (match) {
    throw new Error(`${contextLabel}: body_markdown contains forbidden section "${match[1]}"`);
  }
}

function parsePracticeBlock(step, moduleCtx, lessonTitle) {
  const { studentText, adminText } = stripAdminAndService(step.rawStepBody);
  const sections = splitSections(studentText);
  const adminSections = splitSections(adminText);

  const shortInline =
    ((studentText.match(/^\s*\*\*Коротко:\*\*\s*(.+)$/imu) || [])[1] || (studentText.match(/^\s*Коротко:\s*(.+)$/imu) || [])[1] || "").trim();
  const shortSection = getSectionBodies(sections, "Коротко")[0] || "";
  const shortText = normalizeSpaces(shortInline || shortSection);

  const condition = getSectionBodies(sections, "Условие")[0] || "";
  const inputData = getSectionBodies(sections, "Вход")[0] || "";
  const outputData = getSectionBodies(sections, "Выход")[0] || "";

  const studentVisible = getSectionBodies(sections, "Ученик видит")[0] || "";
  const fallbackCondition = condition || studentVisible || "";

  const examples = sections
    .filter((section) => /^Пример\s+\d+$/u.test(section.name))
    .map((section) => ({
      order: Number((section.name.match(/\d+/u) || [0])[0]),
      body: section.body.trim(),
    }))
    .filter((example) => example.order > 0);

  const templateSection = getSectionBodies(sections, "Шаблон")[0] || "";
  const templateCodeBlock = extractFirstCodeBlock(templateSection);
  const editorInitialCode = templateCodeBlock.code;

  const hintChunks = [
    ...getSectionBodies(sections, "Подсказки"),
    ...getSectionBodies(adminSections, "Подсказки"),
  ];
  const hints = Array.from(new Set(parseHints(hintChunks.join("\n\n"))));

  const etalonChunks = [
    ...getSectionBodies(adminSections, "Эталон"),
    ...getSectionBodies(sections, "Эталон"),
  ];
  const etalonText = etalonChunks.length > 0 ? etalonChunks.join("\n\n") : adminText;
  const solutionCodeBlock = extractFirstCodeBlock(etalonText);
  const solutionCode = solutionCodeBlock.code;
  const taskLanguage = detectTaskLanguage(
    moduleCtx.defaultLanguage,
    templateCodeBlock.language,
    solutionCodeBlock.language,
    moduleCtx.metaLanguage
  );

  const openTests = [];
  for (const example of examples) {
    const parsed = parseExampleIO(example.body);
    if (!parsed) continue;
    openTests.push({
      inputData: parsed.inputData,
      expectedOutput: parsed.expectedOutput,
      isHidden: false,
    });
  }

  const autoTestText = [
    ...getSectionBodies(adminSections, "Автотесты"),
    ...getSectionBodies(sections, "Автотесты"),
  ].join("\n\n");
  const hiddenTestText = [
    ...getSectionBodies(adminSections, "Скрытые тесты"),
    ...getSectionBodies(sections, "Скрытые тесты"),
  ].join("\n\n");

  let tests = [];
  tests.push(...parseTestsFromText(autoTestText, false));
  tests.push(...parseTestsFromText(hiddenTestText, true));
  if (tests.length === 0) {
    tests.push(...parseTestsFromText(adminText, false));
  }
  if (tests.length === 0) {
    tests.push(...parseTestsFromText(studentText, false));
  }
  if (tests.length === 0) {
    tests = openTests.slice();
  }
  if (tests.length === 0) {
    const fallbackTest = inferFallbackTestFromSections(inputData, outputData, fallbackCondition);
    if (fallbackTest) tests.push(fallbackTest);
  }
  if (tests.length === 0 && taskLanguage === "python") {
    const executedTest = inferPythonStdoutTestFromSolution(solutionCode, inputData);
    if (executedTest) tests.push(executedTest);
  }
  if (tests.length === 0 && taskLanguage === "python") {
    const sourceEqTest = inferPythonSourceEquivalenceTest(solutionCode);
    if (sourceEqTest) tests.push(sourceEqTest);
  }

  const hasExplicitHidden = tests.some((item) => item.isHidden);
  if (!hasExplicitHidden && tests.length > 1) {
    tests = tests.map((item, index) => ({ ...item, isHidden: index > 0 }));
  }

  const bodyMarkdown = buildPracticeBody(shortText, fallbackCondition, inputData, outputData, examples);
  assertPracticeBodySafe(bodyMarkdown, `${lessonTitle} / шаг ${step.stepNum} "${step.stepTitle}"`);

  const difficulty = moduleCtx.metaDifficulty > 0 ? Math.min(10, moduleCtx.metaDifficulty) : 2;
  const xpReward = moduleCtx.metaXP > 0 ? moduleCtx.metaXP : 50;

  const sourcePolicy = {
    language: taskLanguage,
    emptySourceMessage: "Код пока пуст. Добавьте решение и запустите проверку снова.",
    ignoreCommentOnlyLines: true,
    hints,
    ai_hint_config: {
      mode: "socratic",
      no_full_solution: true,
    },
  };

  let normalizedTests = tests
    .map((item, index) => ({
      inputData: String(item.inputData ?? "").replace(/\r/g, ""),
      expectedOutput: String(item.expectedOutput ?? "").replace(/\r/g, ""),
      isHidden: !!item.isHidden,
      position: index + 1,
    }))
    .filter((item) => item.inputData !== "" || item.expectedOutput !== "");

  if (taskLanguage === "sql") {
    const reference = solutionCode.trim();
    normalizedTests = reference
      ? [
          {
            inputData: "",
            expectedOutput: reference,
            isHidden: true,
            position: 1,
          },
        ]
      : [];
  }

  const canCreateTask = ["python", "java", "sql"].includes(taskLanguage) && normalizedTests.length > 0;
  const taskDiagnostics = {
    language: taskLanguage,
    testsCount: normalizedTests.length,
    solutionPresent: solutionCode.trim() !== "",
    hasExamples: examples.length > 0,
    hasTemplate: editorInitialCode.trim() !== "",
    hasHints: hints.length > 0,
  };

  return {
    contentMd: bodyMarkdown,
    adminNotes: adminText,
    taskDiagnostics,
    task:
      canCreateTask
        ? {
            title: step.stepTitle,
            statementMd: bodyMarkdown,
            starterCode: editorInitialCode.trim() ? `${editorInitialCode.replace(/\n+$/g, "")}\n` : "",
            solutionCode: solutionCode.trim() ? `${solutionCode.replace(/\n+$/g, "")}\n` : "",
            difficulty,
            xpReward,
            topic: `${moduleCtx.moduleTitle} — ${lessonTitle}`,
            language: taskLanguage,
            sourcePolicy,
            tests: normalizedTests,
          }
        : null,
  };
}

function parseTheoryBlock(step) {
  const { studentText, adminText } = stripAdminAndService(step.rawStepBody);
  const sections = splitSections(studentText);

  const studentVisible = getSectionBodies(sections, "Ученик видит")[0] || "";
  const content = (studentVisible || studentText)
    .replace(/^\*\*Вид:\*\*.*$/gimu, "")
    .replace(/^\s+|\s+$/g, "")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
  return {
    contentMd: content,
    adminNotes: adminText,
  };
}

function parseQuizFromSections(sections) {
  const questionText = getSectionBodies(sections, "Вопрос")[0] || "";
  const optionsText = getSectionBodies(sections, "Варианты")[0] || "";
  const options = [...optionsText.matchAll(/^\s*(?:[-*]|\d+\.)\s*(.+)$/gmu)].map((match, index) => ({
    id: String.fromCharCode(65 + index),
    text: match[1].trim(),
  }));
  const correctRaw = Number(((questionText + "\n" + optionsText).match(/Ответ:\s*(\d+)/iu) || [])[1] || "1");
  const correctIndex = Math.max(0, Math.min(options.length - 1, correctRaw - 1));
  if (!questionText || options.length < 2) return null;
  return {
    questions: [
      {
        id: "q1",
        question: questionText.replace(/\n+/g, " ").trim(),
        options,
        correctOptionId: options[correctIndex].id,
      },
    ],
  };
}

function parseQuizByInlineQuestions(rawText) {
  const text = String(rawText ?? "");
  const chunkRe = /(?:^|\n)\s*(\d+)\.\s+([\s\S]*?)(?=(?:\n\s*\d+\.\s+)|$)/gmu;
  const chunks = [...text.matchAll(chunkRe)];
  if (chunks.length === 0) return null;

  const questions = [];
  for (let idx = 0; idx < chunks.length; idx += 1) {
    const chunk = chunks[idx][2].trim();
    if (!chunk) continue;
    const lines = chunk.split("\n").map((line) => line.trim()).filter((line) => line !== "");
    if (lines.length === 0) continue;
    const question = lines[0];

    const optionMatches = [...chunk.matchAll(/^\s*-\s*([A-Za-zА-Яа-я])\.\s+(.+)$/gmu)];
    const options = optionMatches.map((match) => ({
      id: match[1].toUpperCase(),
      text: match[2].trim(),
    }));
    if (options.length < 2) continue;

    const correctRaw = ((chunk.match(/Ответ:\s*([A-Za-zА-Яа-я])/iu) || [])[1] || "").toUpperCase();
    let correctOptionId = correctRaw;
    if (!options.some((option) => option.id === correctOptionId)) {
      correctOptionId = options[0].id;
    }

    questions.push({
      id: `q${idx + 1}`,
      question,
      options,
      correctOptionId,
    });
  }

  if (questions.length === 0) return null;
  return { questions };
}

function parseQuizBlock(step) {
  const { studentText, adminText } = stripAdminAndService(step.rawStepBody);
  const sections = splitSections(studentText);

  const fromSections = parseQuizFromSections(sections);
  const fromInline = parseQuizByInlineQuestions(studentText);
  const quizPayload = fromSections || fromInline;
  return {
    contentMd: studentText
      .replace(/^\*\*Вид:\*\*.*$/gimu, "")
      .replace(/^\s+|\s+$/g, "")
      .replace(/\n{3,}/g, "\n\n")
      .trim(),
    adminNotes: adminText,
    quizPayload,
  };
}

function parseProjectBlock(step) {
  const { studentText, adminText } = stripAdminAndService(step.rawStepBody);
  const sections = splitSections(studentText);
  const studentVisible = getSectionBodies(sections, "Ученик видит")[0] || "";
  const content = (studentVisible || studentText)
    .replace(/^\*\*Вид:\*\*.*$/gimu, "")
    .replace(/^\s+|\s+$/g, "")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
  return {
    contentMd: content,
    adminNotes: adminText,
  };
}

function buildStepPayload(step, lesson, moduleCtx) {
  const meta = parseStepMeta(step.rawStepBody);
  const blockType = normalizeBlockType(meta.rawType);
  const context = {
    moduleTitle: moduleCtx.moduleTitle,
    defaultLanguage: moduleCtx.defaultLanguage,
    metaLanguage: meta.language,
    metaDifficulty: meta.difficulty,
    metaXP: meta.xp,
  };

  if (blockType === "practice") {
    const practice = parsePracticeBlock(step, context, lesson.lessonTitle);
    return {
      position: step.stepNum,
      title: step.stepTitle,
      blockType,
      contentMd: practice.contentMd,
      adminNotes: practice.adminNotes,
      quizPayload: null,
      taskDiagnostics: practice.taskDiagnostics,
      task: practice.task,
    };
  }
  if (blockType === "quiz") {
    const quiz = parseQuizBlock(step);
    return {
      position: step.stepNum,
      title: step.stepTitle,
      blockType,
      contentMd: quiz.contentMd,
      adminNotes: quiz.adminNotes,
      quizPayload: quiz.quizPayload,
      task: null,
    };
  }
  if (blockType === "project") {
    const project = parseProjectBlock(step);
    return {
      position: step.stepNum,
      title: step.stepTitle,
      blockType,
      contentMd: project.contentMd,
      adminNotes: project.adminNotes,
      quizPayload: null,
      task: null,
    };
  }
  const theory = parseTheoryBlock(step);
  return {
    position: step.stepNum,
    title: step.stepTitle,
    blockType,
    contentMd: theory.contentMd,
    adminNotes: theory.adminNotes,
    quizPayload: null,
    task: null,
  };
}

function validatePreparedCourse(modules) {
  const errors = [];
  for (const moduleItem of modules) {
    for (const lesson of moduleItem.lessons) {
      for (const block of lesson.blocks) {
        if (block.blockType === "practice") {
          try {
            assertPracticeBodySafe(block.contentMd, `${lesson.lessonTitle} / шаг ${block.position}`);
          } catch (err) {
            errors.push(err.message);
          }
        }
      }
    }
  }
  if (errors.length > 0) {
    throw new Error(`Validation failed:\n- ${errors.join("\n- ")}`);
  }
}

function ensureUniqueTaskTitles(modules) {
  for (const moduleItem of modules) {
    for (const lesson of moduleItem.lessons) {
      const counts = new Map();
      for (const block of lesson.blocks) {
        if (!block.task) continue;
        const baseTitle = normalizeSpaces(block.task.title) || `Шаг ${block.position}`;
        block.task.title = baseTitle;
        counts.set(baseTitle, (counts.get(baseTitle) || 0) + 1);
      }

      for (const block of lesson.blocks) {
        if (!block.task) continue;
        const baseTitle = block.task.title;
        if ((counts.get(baseTitle) || 0) <= 1) continue;
        block.task.title = `${baseTitle} (шаг ${block.position})`;
      }
    }
  }
}

function prepareCourseData(manifestModules, parsedLessons) {
  const mappedModules = matchManifestToParsedLessons(manifestModules, parsedLessons);

  const preparedModules = mappedModules.map((moduleItem) => ({
    file: moduleItem.file,
    modulePosition: moduleItem.modulePosition,
    moduleTitle: moduleItem.moduleTitle,
    defaultLanguage: moduleItem.defaultLanguage,
    lessons: moduleItem.lessons.map((lesson) => ({
      lessonNum: lesson.lessonNum,
      lessonTitle: lesson.lessonTitle,
      lessonContent: lesson.lessonContent,
      blocks: lesson.steps.map((step) => buildStepPayload(step, lesson, moduleItem)),
    })),
  }));

  ensureUniqueTaskTitles(preparedModules);
  validatePreparedCourse(preparedModules);
  return preparedModules;
}

function buildMigrationSql(modules) {
  let sql = "";
  sql += "-- 020_reseed_python_zero_full_v4_sql_checker_and_gap_reduction.sql\n";
  sql += "-- Generated from python_course_platform_v4_full.md + import_manifest.csv\n";
  sql += "-- Purpose: full-course import with whitelist body parsing and separated system fields.\n\n";
  sql += "-- Required for SQL tasks reseeded by this migration.\n";
  sql += "ALTER TABLE tasks DROP CONSTRAINT IF EXISTS chk_tasks_language;\n";
  sql += "ALTER TABLE tasks\n";
  sql += "    ADD CONSTRAINT chk_tasks_language\n";
  sql += "    CHECK (language IN ('java', 'python', 'python3', 'py', 'sql'));\n\n";

  sql += "INSERT INTO courses(slug, title, description, is_published)\n";
  sql += `VALUES ('${COURSE.slug}', ${dollarQuote(COURSE.title, "course_title")}, ${dollarQuote(COURSE.description, "course_desc")}, TRUE)\n`;
  sql += "ON CONFLICT (slug) DO UPDATE\n";
  sql += "SET title = EXCLUDED.title,\n";
  sql += "    description = EXCLUDED.description,\n";
  sql += "    is_published = TRUE,\n";
  sql += "    updated_at = NOW();\n\n";

  sql += "WITH course_ref AS (\n";
  sql += "  SELECT id AS course_id FROM courses WHERE slug = 'python-zero'\n";
  sql += "), module_seed(position, title) AS (\n";
  sql += "  VALUES\n";
  const moduleRows = modules.slice().sort((a, b) => a.modulePosition - b.modulePosition);
  for (let i = 0; i < moduleRows.length; i += 1) {
    const item = moduleRows[i];
    const suffix = i + 1 < moduleRows.length ? "," : "";
    sql += `  (${item.modulePosition}, ${dollarQuote(item.moduleTitle, `m${item.modulePosition}_title`)})${suffix}\n`;
  }
  sql += ")\n";
  sql += "INSERT INTO modules(course_id, title, position)\n";
  sql += "SELECT cr.course_id, ms.title, ms.position\n";
  sql += "FROM course_ref cr\n";
  sql += "CROSS JOIN module_seed ms\n";
  sql += "ON CONFLICT (course_id, position) DO UPDATE\n";
  sql += "SET title = EXCLUDED.title,\n";
  sql += "    updated_at = NOW();\n\n";

  for (const moduleItem of moduleRows) {
    sql += `-- Module ${moduleItem.modulePosition}: ${moduleItem.moduleTitle}\n`;
    sql += "WITH module_ref AS (\n";
    sql += "  SELECT m.id AS module_id\n";
    sql += "  FROM modules m\n";
    sql += "  JOIN courses c ON c.id = m.course_id\n";
    sql += `  WHERE c.slug = 'python-zero' AND m.position = ${moduleItem.modulePosition}\n`;
    sql += "), lesson_seed(position, title, content_md) AS (\n";
    sql += "  VALUES\n";
    for (let i = 0; i < moduleItem.lessons.length; i += 1) {
      const lesson = moduleItem.lessons[i];
      const suffix = i + 1 < moduleItem.lessons.length ? "," : "";
      sql += `  (${lesson.lessonNum}, ${dollarQuote(lesson.lessonTitle, `m${moduleItem.modulePosition}_l${lesson.lessonNum}_title`)}, ${dollarQuote(
        lesson.lessonContent,
        `m${moduleItem.modulePosition}_l${lesson.lessonNum}_content`
      )})${suffix}\n`;
    }
    sql += ")\n";
    sql += "INSERT INTO lessons(module_id, title, content_md, position, is_published)\n";
    sql += "SELECT mr.module_id, ls.title, ls.content_md, ls.position, TRUE\n";
    sql += "FROM module_ref mr\n";
    sql += "CROSS JOIN lesson_seed ls\n";
    sql += "ON CONFLICT (module_id, position) DO UPDATE\n";
    sql += "SET title = EXCLUDED.title,\n";
    sql += "    content_md = EXCLUDED.content_md,\n";
    sql += "    is_published = TRUE,\n";
    sql += "    updated_at = NOW();\n\n";

    for (const lesson of moduleItem.lessons) {
      const lessonPrefix = `m${moduleItem.modulePosition}_l${lesson.lessonNum}`;
      const practiceBlocks = lesson.blocks.filter((block) => block.blockType === "practice" && block.task);

      sql += `-- Module ${moduleItem.modulePosition}, lesson ${lesson.lessonNum}: ${lesson.lessonTitle}\n`;
      sql += "WITH lesson_ref AS (\n";
      sql += "  SELECT l.id AS lesson_id\n";
      sql += "  FROM lessons l\n";
      sql += "  JOIN modules m ON m.id = l.module_id\n";
      sql += "  JOIN courses c ON c.id = m.course_id\n";
      sql += `  WHERE c.slug = 'python-zero' AND m.position = ${moduleItem.modulePosition} AND l.position = ${lesson.lessonNum}\n`;
      sql += ")\n";
      sql += "UPDATE lesson_blocks lb\n";
      sql += "SET is_published = FALSE,\n";
      sql += "    updated_at = NOW()\n";
      sql += "FROM lesson_ref lr\n";
      sql += "WHERE lb.lesson_id = lr.lesson_id;\n\n";

      if (practiceBlocks.length > 0) {
        sql += "WITH lesson_ref AS (\n";
        sql += "  SELECT l.id AS lesson_id\n";
        sql += "  FROM lessons l\n";
        sql += "  JOIN modules m ON m.id = l.module_id\n";
        sql += "  JOIN courses c ON c.id = m.course_id\n";
        sql += `  WHERE c.slug = 'python-zero' AND m.position = ${moduleItem.modulePosition} AND l.position = ${lesson.lessonNum}\n`;
        sql += "), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (\n";
        sql += "  VALUES\n";
        for (let i = 0; i < practiceBlocks.length; i += 1) {
          const block = practiceBlocks[i];
          const task = block.task;
          const suffix = i + 1 < practiceBlocks.length ? "," : "";
          sql += `  (${dollarQuote(task.title, `${lessonPrefix}_t${block.position}_title`)}, ${dollarQuote(
            task.statementMd,
            `${lessonPrefix}_t${block.position}_statement`
          )}, ${dollarQuote(task.starterCode, `${lessonPrefix}_t${block.position}_starter`)}, ${dollarQuote(
            task.solutionCode,
            `${lessonPrefix}_t${block.position}_solution`
          )}, ${task.difficulty}, ${task.xpReward}, ${dollarQuote(task.topic, `${lessonPrefix}_t${block.position}_topic`)}, ${dollarQuote(
            task.language,
            `${lessonPrefix}_t${block.position}_lang`
          )}, ${dollarQuote(JSON.stringify(task.sourcePolicy), `${lessonPrefix}_t${block.position}_policy`)}::jsonb)${suffix}\n`;
        }
        sql += ")\n";
        sql += "INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)\n";
        sql += "SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE\n";
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
        sql += "  SELECT l.id AS lesson_id\n";
        sql += "  FROM lessons l\n";
        sql += "  JOIN modules m ON m.id = l.module_id\n";
        sql += "  JOIN courses c ON c.id = m.course_id\n";
        sql += `  WHERE c.slug = 'python-zero' AND m.position = ${moduleItem.modulePosition} AND l.position = ${lesson.lessonNum}\n`;
        sql += "), target_tasks AS (\n";
        sql += "  SELECT t.id\n";
        sql += "  FROM tasks t\n";
        sql += "  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id\n";
        sql += "  WHERE t.title IN (\n";
        for (let i = 0; i < practiceBlocks.length; i += 1) {
          const block = practiceBlocks[i];
          const suffix = i + 1 < practiceBlocks.length ? "," : "";
          sql += `    ${dollarQuote(block.task.title, `${lessonPrefix}_ttitle_${block.position}`)}${suffix}\n`;
        }
        sql += "  )\n";
        sql += ")\n";
        sql += "DELETE FROM task_test_cases tc\n";
        sql += "USING target_tasks tt\n";
        sql += "WHERE tc.task_id = tt.id;\n\n";

        const allTests = [];
        for (const block of practiceBlocks) {
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
        if (allTests.length > 0) {
          sql += "WITH lesson_ref AS (\n";
          sql += "  SELECT l.id AS lesson_id\n";
          sql += "  FROM lessons l\n";
          sql += "  JOIN modules m ON m.id = l.module_id\n";
          sql += "  JOIN courses c ON c.id = m.course_id\n";
          sql += `  WHERE c.slug = 'python-zero' AND m.position = ${moduleItem.modulePosition} AND l.position = ${lesson.lessonNum}\n`;
          sql += "), task_lookup AS (\n";
          sql += "  SELECT t.id AS task_id, t.title\n";
          sql += "  FROM tasks t\n";
          sql += "  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id\n";
          sql += "), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (\n";
          sql += "  VALUES\n";
          for (let i = 0; i < allTests.length; i += 1) {
            const test = allTests[i];
            const suffix = i + 1 < allTests.length ? "," : "";
            sql += `  (${dollarQuote(test.taskTitle, `${lessonPrefix}_test_${test.blockPosition}_${test.position}_title`)}, ${dollarQuote(
              test.inputData,
              `${lessonPrefix}_test_${test.blockPosition}_${test.position}_input`
            )}, ${dollarQuote(test.expectedOutput, `${lessonPrefix}_test_${test.blockPosition}_${test.position}_expected`)}, ${
              test.isHidden ? "TRUE" : "FALSE"
            }, ${test.position})${suffix}\n`;
          }
          sql += ")\n";
          sql += "INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)\n";
          sql += "SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position\n";
          sql += "FROM test_seed ts\n";
          sql += "JOIN task_lookup tl ON tl.title = ts.task_title\n";
          sql += "ORDER BY tl.task_id, ts.position;\n\n";
        }
      }

      sql += "WITH lesson_ref AS (\n";
      sql += "  SELECT l.id AS lesson_id\n";
      sql += "  FROM lessons l\n";
      sql += "  JOIN modules m ON m.id = l.module_id\n";
      sql += "  JOIN courses c ON c.id = m.course_id\n";
      sql += `  WHERE c.slug = 'python-zero' AND m.position = ${moduleItem.modulePosition} AND l.position = ${lesson.lessonNum}\n`;
      sql += "), task_lookup AS (\n";
      sql += "  SELECT t.title, t.id AS task_id\n";
      sql += "  FROM tasks t\n";
      sql += "  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id\n";
      sql += "), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (\n";
      sql += "  VALUES\n";
      for (let i = 0; i < lesson.blocks.length; i += 1) {
        const block = lesson.blocks[i];
        const suffix = i + 1 < lesson.blocks.length ? "," : "";
        const taskTitleSql = block.task ? dollarQuote(block.task.title, `${lessonPrefix}_b${block.position}_task_title`) : "NULL";
        const quizSql = block.quizPayload ? `${dollarQuote(JSON.stringify(block.quizPayload), `${lessonPrefix}_b${block.position}_quiz`)}::jsonb` : "NULL::jsonb";
        sql += `  (${block.position}, ${dollarQuote(block.blockType, `${lessonPrefix}_b${block.position}_type`)}, ${dollarQuote(
          block.title,
          `${lessonPrefix}_b${block.position}_title`
        )}, ${dollarQuote(block.contentMd, `${lessonPrefix}_b${block.position}_content`)}, ${taskTitleSql}, ${quizSql})${suffix}\n`;
      }
      sql += "), resolved AS (\n";
      sql += "  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload\n";
      sql += "  FROM block_seed bs\n";
      sql += "  LEFT JOIN task_lookup tl ON tl.title = bs.task_title\n";
      sql += ")\n";
      sql += "INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)\n";
      sql += "SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE\n";
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
  }

  return sql;
}

function summarize(modules) {
  let lessonCount = 0;
  let blockCount = 0;
  let practiceCount = 0;
  let taskCount = 0;
  let testCount = 0;

  for (const moduleItem of modules) {
    lessonCount += moduleItem.lessons.length;
    for (const lesson of moduleItem.lessons) {
      blockCount += lesson.blocks.length;
      for (const block of lesson.blocks) {
        if (block.blockType === "practice") practiceCount += 1;
        if (!block.task) continue;
        taskCount += 1;
        testCount += block.task.tests.length;
      }
    }
  }
  return { lessonCount, blockCount, practiceCount, taskCount, testCount };
}

function reportTaskGaps(modules) {
  const gaps = [];
  for (const moduleItem of modules) {
    for (const lesson of moduleItem.lessons) {
      for (const block of lesson.blocks) {
        if (block.blockType !== "practice") continue;
        if (block.task) continue;
        gaps.push({
          modulePosition: moduleItem.modulePosition,
          lessonNum: lesson.lessonNum,
          lessonTitle: lesson.lessonTitle,
          stepNum: block.position,
          stepTitle: block.title,
          ...((block.taskDiagnostics || {})),
        });
      }
    }
  }
  return gaps;
}

function main() {
  const markdown = readText(MD_PATH);
  const manifest = parseCsvManifest(readText(MANIFEST_PATH));
  const parsedLessons = parseLessonsFromMarkdown(markdown);
  const modules = prepareCourseData(manifest, parsedLessons);
  const sql = buildMigrationSql(modules);

  fs.writeFileSync(OUT_PATH, sql, "utf8");
  const stats = summarize(modules);
  const gaps = reportTaskGaps(modules);

  console.log(`Generated migration: ${OUT_PATH}`);
  console.log(`Modules: ${modules.length}`);
  console.log(`Lessons: ${stats.lessonCount}`);
  console.log(`Blocks: ${stats.blockCount}`);
  console.log(`Practice blocks: ${stats.practiceCount}`);
  console.log(`Tasks created: ${stats.taskCount}`);
  console.log(`Tests created: ${stats.testCount}`);
  console.log(`Practice blocks without task binding: ${gaps.length}`);

  if (process.env.REPORT_TASK_GAPS === "1") {
    const preview = gaps.slice(0, 80);
    for (const gap of preview) {
      console.log(
        `GAP m${gap.modulePosition}/l${gap.lessonNum}/s${gap.stepNum} "${gap.stepTitle}" ` +
          `(lang=${gap.language || "?"}, tests=${gap.testsCount || 0}, examples=${gap.hasExamples ? "yes" : "no"}, ` +
          `solution=${gap.solutionPresent ? "yes" : "no"}, template=${gap.hasTemplate ? "yes" : "no"})`
      );
    }
    if (gaps.length > preview.length) {
      console.log(`...and ${gaps.length - preview.length} more gap rows`);
    }
  }
}

main();
