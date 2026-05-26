const fs = require("fs");
const path = require("path");

const INPUT_PATH = path.resolve(__dirname, "../../материалы/java_metanit_v1/course_import.json");
const MIGRATIONS_DIR = path.resolve(__dirname, "../migrations");
const REPORT_PATH = path.resolve(
  __dirname,
  "../../docs/operations/JAVA_METANIT_V1_IMPORT_VALIDATION_2026_05_22.md"
);
const SOURCE_LINE_RE = /^\s*(?:\*\*)?\s*Источник\s*:?\s*(?:\*\*)?\s*https?:\/\/\S+\s*$/imu;
const BROKEN_TITLE_MARKER_RE = /(Последнее обновление:|Назад\s+Содержание\s+Вперед)/iu;
const PRACTICE_TEMPLATE_RE = /template=([a-z0-9_\-]+)/iu;

function resolveMigrationPath() {
  const files = fs
    .readdirSync(MIGRATIONS_DIR)
    .filter((name) => /^\d+_reseed_java_zero_core_metanit_v1.*\.sql$/i.test(name))
    .sort();
  if (files.length === 0) {
    throw new Error(`No java reseed migration found in ${MIGRATIONS_DIR}`);
  }
  return path.join(MIGRATIONS_DIR, files[files.length - 1]);
}

const MIGRATION_PATH = resolveMigrationPath();

function readJSON(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function countUnique(text, regex) {
  const matches = text.match(regex) || [];
  return new Set(matches).size;
}

function main() {
  const input = readJSON(INPUT_PATH);
  const migration = fs.readFileSync(MIGRATION_PATH, "utf8");

  const stats = {
    modules: 0,
    lessons: 0,
    steps: 0,
    tasks: 0,
    quizzes: 0,
    executableTests: 0,
    checkerCounts: {},
    stepTypeCounts: {},
    longLessonTitles: 0,
    brokenLessonTitles: 0,
    theoryWithSourceLinks: 0,
    practiceWithBrokenIntro: 0,
    practiceTemplateDiversity: 0,
    practiceAdjacentTemplateRepeats: 0,
  };
  const practiceTemplateCounts = {};

  for (const moduleItem of input?.course?.modules || []) {
    let previousPracticeTemplate = "";
    stats.modules += 1;
    for (const lesson of moduleItem?.lessons || []) {
      stats.lessons += 1;
      const lessonTitle = String(lesson?.title ?? "");
      if (lessonTitle.length > 140) stats.longLessonTitles += 1;
      if (BROKEN_TITLE_MARKER_RE.test(lessonTitle)) stats.brokenLessonTitles += 1;
      for (const step of lesson?.steps || []) {
        stats.steps += 1;
        const stepType = String(step?.type || "").toLowerCase();
        const bodyMd = String(step?.body_markdown ?? "");
        stats.stepTypeCounts[stepType] = (stats.stepTypeCounts[stepType] || 0) + 1;

        const checkerType = String(step?.checker?.type || "").toLowerCase();
        if (checkerType) {
          stats.checkerCounts[checkerType] = (stats.checkerCounts[checkerType] || 0) + 1;
        }

        if (stepType === "practice") stats.tasks += 1;
        if (stepType === "test" || stepType === "quiz") stats.quizzes += 1;
        if (stepType === "theory" && SOURCE_LINE_RE.test(bodyMd)) stats.theoryWithSourceLinks += 1;
        if (stepType === "practice" && BROKEN_TITLE_MARKER_RE.test(bodyMd)) stats.practiceWithBrokenIntro += 1;
        if (stepType === "practice") {
          const notes = String(step?.admin_notes || "");
          const templateMatch = notes.match(PRACTICE_TEMPLATE_RE);
          if (templateMatch && templateMatch[1]) {
            const templateKey = templateMatch[1].toLowerCase();
            practiceTemplateCounts[templateKey] = (practiceTemplateCounts[templateKey] || 0) + 1;
            if (previousPracticeTemplate && previousPracticeTemplate === templateKey) {
              stats.practiceAdjacentTemplateRepeats += 1;
            }
            previousPracticeTemplate = templateKey;
          }
        }

        if (checkerType === "java_stdout") {
          const publicTests = Array.isArray(step?.checker?.public_tests) ? step.checker.public_tests.length : 0;
          const hiddenTests = Array.isArray(step?.checker?.hidden_tests) ? step.checker.hidden_tests.length : 0;
          stats.executableTests += publicTests + hiddenTests;
        }
      }
    }
  }

  const migrationStats = {
    blockTypeTags: countUnique(migration, /\$m\d+_l\d+_b\d+_type\$/g),
    taskPolicyTags: countUnique(migration, /\$m\d+_l\d+_t\d+_policy\$/g),
    testExpectedTags: countUnique(migration, /\$m\d+_l\d+_test_\d+_expected\$/g),
    checkerJavaStdout: (migration.match(/"checker_type":"java_stdout"/g) || []).length,
    checkerQuizSingle: (migration.match(/"checker_type":"quiz_single"/g) || []).length,
    hasQuizPayloadQuestions: migration.includes('"questions":[{'),
  };
  stats.practiceTemplateDiversity = Object.keys(practiceTemplateCounts).length;
  const maxPracticeTemplateReuse = Math.max(0, ...Object.values(practiceTemplateCounts));

  const checks = {
    stepCountMatches: migrationStats.blockTypeTags === stats.steps,
    taskCountMatches: migrationStats.taskPolicyTags === stats.tasks,
    testCountMatches: migrationStats.testExpectedTags === stats.executableTests,
    checkerCountsMatchJavaStdout: migrationStats.checkerJavaStdout === (stats.checkerCounts.java_stdout || 0),
    quizPayloadQuestionsPresent: migrationStats.hasQuizPayloadQuestions,
    noLongLessonTitles: stats.longLessonTitles === 0,
    noBrokenLessonTitles: stats.brokenLessonTitles === 0,
    noTheorySourceLinks: stats.theoryWithSourceLinks === 0,
    noPracticeBrokenIntro: stats.practiceWithBrokenIntro === 0,
    practiceTemplateDiversityOk: stats.practiceTemplateDiversity >= 12,
    noPracticeAdjacentTemplateRepeats: stats.practiceAdjacentTemplateRepeats === 0,
    practiceTemplateMaxReuseOk: stats.tasks < 40 || maxPracticeTemplateReuse <= 12,
  };

  const failed = Object.entries(checks)
    .filter(([, ok]) => !ok)
    .map(([name]) => name);

  const reportLines = [
    "# Java Metanit v1 Import Validation — 2026-05-22",
    "",
    "## Source Inputs",
    `- materials json: \`${INPUT_PATH}\``,
    `- generated migration: \`${MIGRATION_PATH}\``,
    "",
    "## Parsed Materials Stats",
    `- modules: ${stats.modules}`,
    `- lessons: ${stats.lessons}`,
    `- steps: ${stats.steps}`,
    `- tasks (practice): ${stats.tasks}`,
    `- quiz steps: ${stats.quizzes}`,
    `- executable tests (java_stdout): ${stats.executableTests}`,
    `- stepTypeCounts: ${JSON.stringify(stats.stepTypeCounts)}`,
    `- checkerCounts: ${JSON.stringify(stats.checkerCounts)}`,
    `- long lesson titles: ${stats.longLessonTitles}`,
    `- broken lesson titles: ${stats.brokenLessonTitles}`,
    `- theory steps with source links: ${stats.theoryWithSourceLinks}`,
    `- practice steps with broken intro: ${stats.practiceWithBrokenIntro}`,
    `- practice template diversity: ${stats.practiceTemplateDiversity}`,
    `- practice adjacent template repeats: ${stats.practiceAdjacentTemplateRepeats}`,
    `- max practice template reuse: ${maxPracticeTemplateReuse}`,
    "",
    "## Migration Structure Stats",
    `- block type tags: ${migrationStats.blockTypeTags}`,
    `- task policy tags: ${migrationStats.taskPolicyTags}`,
    `- testcase expected tags: ${migrationStats.testExpectedTags}`,
    `- checker_type counts in SQL: ${JSON.stringify({
      java_stdout: migrationStats.checkerJavaStdout,
      quiz_single: migrationStats.checkerQuizSingle,
    })}`,
    `- has quiz questions payload: ${migrationStats.hasQuizPayloadQuestions}`,
    "",
    "## Verdict",
    failed.length === 0 ? "- PASS: all validation checks passed." : `- FAIL: ${failed.join(", ")}`,
    "",
    "## Check Flags",
    ...Object.entries(checks).map(([name, ok]) => `- ${name}: ${ok ? "PASS" : "FAIL"}`),
    "",
  ];

  const report = reportLines.join("\n");
  fs.writeFileSync(REPORT_PATH, report, "utf8");
  console.log(report);
  console.log(`Saved report: ${REPORT_PATH}`);

  if (failed.length > 0) {
    process.exitCode = 1;
  }
}

main();
