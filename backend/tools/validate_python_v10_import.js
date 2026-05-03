const fs = require('fs');

const INPUT_PATH = 'C:/Users/Artemy/AppData/Local/Temp/python_course_platform_v10_import.json';
const MIGRATION_PATH = 'C:/prog/Comercial/LeonovCarePlatform/backend/migrations/023_reseed_python_zero_v10_polished_full.sql';
const REPORT_PATH = 'C:/prog/Comercial/LeonovCarePlatform/docs/operations/PYTHON_V10_IMPORT_VALIDATION_2026_04_30.md';

const FORBIDDEN_BODY_MARKERS = ['Шаблон', 'Подсказки', 'Эталон', 'Автотесты', 'Скрытые тесты'];
const FORBIDDEN_PHRASE = 'Для этого шага пока нет автопроверки';

function loadJSON(path) {
  return JSON.parse(fs.readFileSync(path, 'utf8'));
}

function countUniqueRegexTags(text, regex) {
  const matches = text.match(regex) || [];
  return new Set(matches).size;
}

function main() {
  const data = loadJSON(INPUT_PATH);
  const migration = fs.readFileSync(MIGRATION_PATH, 'utf8');

  const stats = {
    modules: 0,
    lessons: 0,
    steps: 0,
    byType: {},
    byChecker: {},
    taskCount: 0,
    generatedTestsCount: 0,
    practiceWithoutChecker: 0,
    projectWithoutChecker: 0,
    projectWithoutAIReview: 0,
    forbiddenBodyMarkers: 0,
    forbiddenPhrase: 0,
  };

  for (const moduleItem of data.modules || []) {
    stats.modules += 1;
    for (const lesson of moduleItem.lessons || []) {
      stats.lessons += 1;
      for (const step of lesson.steps || []) {
        stats.steps += 1;
        const stepType = String(step.type || 'theory').toLowerCase();
        stats.byType[stepType] = (stats.byType[stepType] || 0) + 1;

        const checkerType = String(step.checker?.type || '').toLowerCase();
        if (checkerType) {
          stats.byChecker[checkerType] = (stats.byChecker[checkerType] || 0) + 1;
        }

        const body = String(step.body_markdown || '');
        if (body.includes(FORBIDDEN_PHRASE)) stats.forbiddenPhrase += 1;
        if (FORBIDDEN_BODY_MARKERS.some((marker) => body.includes(marker))) stats.forbiddenBodyMarkers += 1;

        if (stepType === 'practice') {
          stats.taskCount += 1;
          if (!step.checker) {
            stats.practiceWithoutChecker += 1;
          }
          if (checkerType === 'python_stdout') {
            stats.generatedTestsCount += Array.isArray(step.checker?.tests) ? step.checker.tests.length : 0;
          }
          if (checkerType === 'sql_query') {
            stats.generatedTestsCount += Array.isArray(step.checker?.checks) ? step.checker.checks.length : 0;
          }
        }

        if (stepType === 'project') {
          stats.taskCount += 1;
          if (!step.checker || checkerType !== 'ide_plugin') {
            stats.projectWithoutChecker += 1;
          }
          if (!step.ai_review_config || step.ai_review_config.enabled !== true) {
            stats.projectWithoutAIReview += 1;
          }
        }
      }
    }
  }

  const migrationBlockCount = countUniqueRegexTags(migration, /\$m\d+_l\d+_b\d+_type\$/g);
  const migrationTaskCount = countUniqueRegexTags(migration, /\$m\d+_l\d+_t\d+_policy\$/g);
  const migrationTestCount = countUniqueRegexTags(migration, /\$m\d+_l\d+_test_\d+_\d+_expected\$/g);

  const checks = {
    stepCountsMatch: migrationBlockCount === stats.steps,
    taskCountsMatch: migrationTaskCount === stats.taskCount,
    testCountsMatch: migrationTestCount === stats.generatedTestsCount,
    noPracticeWithoutChecker: stats.practiceWithoutChecker === 0,
    noBrokenProjects: stats.projectWithoutChecker === 0 && stats.projectWithoutAIReview === 0,
    noForbiddenMarkersInBody: stats.forbiddenBodyMarkers === 0,
    noForbiddenPhraseInBody: stats.forbiddenPhrase === 0,
  };

  const failedChecks = Object.entries(checks).filter(([, ok]) => !ok).map(([name]) => name);

  const report = [
    '# Python v10 Import Validation — 2026-04-30',
    '',
    '## Source Inputs',
    `- import json: \`${INPUT_PATH}\``,
    `- generated migration: \`${MIGRATION_PATH}\``,
    '',
    '## Parsed Content Stats',
    `- modules: ${stats.modules}`,
    `- lessons: ${stats.lessons}`,
    `- steps: ${stats.steps}`,
    `- tasks (practice+project): ${stats.taskCount}`,
    `- generated executable tests (python_stdout + sql_query): ${stats.generatedTestsCount}`,
    `- byType: ${JSON.stringify(stats.byType)}`,
    `- byChecker: ${JSON.stringify(stats.byChecker)}`,
    '',
    '## Migration Structure Stats',
    `- lesson block tags in SQL: ${migrationBlockCount}`,
    `- task policy tags in SQL: ${migrationTaskCount}`,
    `- testcase expected tags in SQL: ${migrationTestCount}`,
    '',
    '## Quality Gates',
    `- practice without checker: ${stats.practiceWithoutChecker}`,
    `- project without ide_plugin checker: ${stats.projectWithoutChecker}`,
    `- project without ai_review.enabled=true: ${stats.projectWithoutAIReview}`,
    `- body_markdown with forbidden markers: ${stats.forbiddenBodyMarkers}`,
    `- body_markdown with forbidden phrase: ${stats.forbiddenPhrase}`,
    '',
    '## Verdict',
    failedChecks.length === 0
      ? '- PASS: all validation checks passed.'
      : `- FAIL: ${failedChecks.join(', ')}`,
    '',
    '## Check Flags',
    ...Object.entries(checks).map(([name, ok]) => `- ${name}: ${ok ? 'PASS' : 'FAIL'}`),
    '',
  ].join('\n');

  fs.writeFileSync(REPORT_PATH, report, 'utf8');
  console.log(report);
  console.log(`Saved report: ${REPORT_PATH}`);

  if (failedChecks.length > 0) {
    process.exitCode = 1;
  }
}

main();
