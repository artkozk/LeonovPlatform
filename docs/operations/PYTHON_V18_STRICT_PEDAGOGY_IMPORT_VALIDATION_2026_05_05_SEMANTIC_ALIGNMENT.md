# Python v18 Strict Pedagogy Import Validation — 2026-05-05 Semantic Alignment

## Source Inputs
- materials json: `C:\prog\Comercial\LeonovCarePlatform\материалы\v18_STRICT_PEDAGOGY\course_import.json`
- generated migration: `C:\prog\Comercial\LeonovCarePlatform\backend\migrations\030_reseed_python_zero_v18_semantic_alignment.sql`

## Parsed Materials Stats
- modules: 5
- lessons: 169
- steps: 1960
- tasks (practice + project): 1146
- quiz steps: 307
- executable tests (python_stdout + sql_query): 565
- stepTypeCounts: {"theory":338,"test":307,"practice":818,"project":328,"summary":169}
- checkerCounts: {"quiz_single":307,"python_stdout":45,"ide_plugin":412,"python_pytest":348,"sql_query":221,"http_api":120}

## Migration Structure Stats
- block type tags: 1960
- task policy tags: 1146
- testcase expected tags: 565
- checker_type counts in SQL: {"python_stdout":45,"python_pytest":348,"sql_query":221,"http_api":120,"ide_plugin":412}
- has pytest_code key: true
- has legacy test_code key: false
- has transformed http_api tests[]: true
- has quiz questions payload: true

## Verdict
- PASS: all validation checks passed.

## Check Flags
- stepCountMatches: PASS
- taskCountMatches: PASS
- testCountMatches: PASS
- checkerCountsMatchPythonStdout: PASS
- checkerCountsMatchPythonPytest: PASS
- checkerCountsMatchSQLQuery: PASS
- checkerCountsMatchHTTPAPI: PASS
- checkerCountsMatchIDEPlugin: PASS
- transformedPytestKeyPresent: PASS
- transformedHTTPTestsPresent: PASS
- quizPayloadQuestionsPresent: PASS
