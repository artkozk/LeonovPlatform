const fs = require('fs');
const path = require('path');

const INPUT_PATH = path.resolve(__dirname, '../../материалы/v18_STRICT_PEDAGOGY/course_import.json');
const MIGRATION_PATH = path.resolve(__dirname, '../migrations/028_reseed_python_zero_v18_coursewide_quality.sql');
const REPORT_PATH = path.resolve(__dirname, '../../docs/operations/PYTHON_V18_STRICT_PEDAGOGY_IMPORT_VALIDATION_2026_05_03.md');

function readJSON(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function countUnique(text, regex) {
  const matches = text.match(regex) || [];
  return new Set(matches).size;
}

function main() {
  const input = readJSON(INPUT_PATH);
  const migration = fs.readFileSync(MIGRATION_PATH, 'utf8');

  const stats = {
    modules: 0,
    lessons: 0,
    steps: 0,
    tasks: 0,
    quizzes: 0,
    executableTests: 0,
    checkerCounts: {},
    stepTypeCounts: {},
  };

  for (const moduleItem of input?.course?.modules || []) {
    stats.modules += 1;
    for (const lesson of moduleItem?.lessons || []) {
      stats.lessons += 1;
      for (const step of lesson?.steps || []) {
        stats.steps += 1;
        const stepType = String(step?.type || '').toLowerCase();
        stats.stepTypeCounts[stepType] = (stats.stepTypeCounts[stepType] || 0) + 1;

        const checkerType = String(step?.checker?.type || '').toLowerCase();
        if (checkerType) {
          stats.checkerCounts[checkerType] = (stats.checkerCounts[checkerType] || 0) + 1;
        }

        if (stepType === 'practice' || stepType === 'project') {
          stats.tasks += 1;
        }
        if (stepType === 'test') {
          stats.quizzes += 1;
        }
        if (checkerType === 'python_stdout') {
          const publicTests = Array.isArray(step?.checker?.public_tests) ? step.checker.public_tests.length : 0;
          const hiddenTests = Array.isArray(step?.checker?.hidden_tests) ? step.checker.hidden_tests.length : 0;
          stats.executableTests += publicTests + hiddenTests;
        }
        if (checkerType === 'sql_query') {
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
    checkerPythonStdout: (migration.match(/"checker_type":"python_stdout"/g) || []).length,
    checkerPythonPytest: (migration.match(/"checker_type":"python_pytest"/g) || []).length,
    checkerSQLQuery: (migration.match(/"checker_type":"sql_query"/g) || []).length,
    checkerHTTPAPI: (migration.match(/"checker_type":"http_api"/g) || []).length,
    checkerIDEPlugin: (migration.match(/"checker_type":"ide_plugin"/g) || []).length,
    hasPytestCode: migration.includes('"pytest_code"'),
    hasLegacyTestCode: migration.includes('"test_code"'),
    hasHTTPTestsArray: migration.includes('"checker_type":"http_api"') && migration.includes('"tests":[{'),
    hasQuizPayloadQuestions: migration.includes('"questions":[{'),
  };

  const checks = {
    stepCountMatches: migrationStats.blockTypeTags === stats.steps,
    taskCountMatches: migrationStats.taskPolicyTags === stats.tasks,
    testCountMatches: migrationStats.testExpectedTags === stats.executableTests,
    checkerCountsMatchPythonStdout: migrationStats.checkerPythonStdout === (stats.checkerCounts.python_stdout || 0),
    checkerCountsMatchPythonPytest: migrationStats.checkerPythonPytest === (stats.checkerCounts.python_pytest || 0),
    checkerCountsMatchSQLQuery: migrationStats.checkerSQLQuery === (stats.checkerCounts.sql_query || 0),
    checkerCountsMatchHTTPAPI: migrationStats.checkerHTTPAPI === (stats.checkerCounts.http_api || 0),
    checkerCountsMatchIDEPlugin: migrationStats.checkerIDEPlugin === (stats.checkerCounts.ide_plugin || 0),
    transformedPytestKeyPresent: migrationStats.hasPytestCode && !migrationStats.hasLegacyTestCode,
    transformedHTTPTestsPresent: migrationStats.hasHTTPTestsArray,
    quizPayloadQuestionsPresent: migrationStats.hasQuizPayloadQuestions,
  };

  const failed = Object.entries(checks)
    .filter(([, ok]) => !ok)
    .map(([name]) => name);

  const reportLines = [
    '# Python v18 Strict Pedagogy Import Validation — 2026-05-03',
    '',
    '## Source Inputs',
    `- materials json: \`${INPUT_PATH}\``,
    `- generated migration: \`${MIGRATION_PATH}\``,
    '',
    '## Parsed Materials Stats',
    `- modules: ${stats.modules}`,
    `- lessons: ${stats.lessons}`,
    `- steps: ${stats.steps}`,
    `- tasks (practice + project): ${stats.tasks}`,
    `- quiz steps: ${stats.quizzes}`,
    `- executable tests (python_stdout + sql_query): ${stats.executableTests}`,
    `- stepTypeCounts: ${JSON.stringify(stats.stepTypeCounts)}`,
    `- checkerCounts: ${JSON.stringify(stats.checkerCounts)}`,
    '',
    '## Migration Structure Stats',
    `- block type tags: ${migrationStats.blockTypeTags}`,
    `- task policy tags: ${migrationStats.taskPolicyTags}`,
    `- testcase expected tags: ${migrationStats.testExpectedTags}`,
    `- checker_type counts in SQL: ${JSON.stringify({
      python_stdout: migrationStats.checkerPythonStdout,
      python_pytest: migrationStats.checkerPythonPytest,
      sql_query: migrationStats.checkerSQLQuery,
      http_api: migrationStats.checkerHTTPAPI,
      ide_plugin: migrationStats.checkerIDEPlugin,
    })}`,
    `- has pytest_code key: ${migrationStats.hasPytestCode}`,
    `- has legacy test_code key: ${migrationStats.hasLegacyTestCode}`,
    `- has transformed http_api tests[]: ${migrationStats.hasHTTPTestsArray}`,
    `- has quiz questions payload: ${migrationStats.hasQuizPayloadQuestions}`,
    '',
    '## Verdict',
    failed.length === 0 ? '- PASS: all validation checks passed.' : `- FAIL: ${failed.join(', ')}`,
    '',
    '## Check Flags',
    ...Object.entries(checks).map(([name, ok]) => `- ${name}: ${ok ? 'PASS' : 'FAIL'}`),
    '',
  ];

  const report = reportLines.join('\n');
  fs.writeFileSync(REPORT_PATH, report, 'utf8');
  console.log(report);
  console.log(`Saved report: ${REPORT_PATH}`);

  if (failed.length > 0) {
    process.exitCode = 1;
  }
}

main();
