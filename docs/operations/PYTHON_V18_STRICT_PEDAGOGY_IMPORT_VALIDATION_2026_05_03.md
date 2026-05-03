# Python v18 Strict Pedagogy Import Validation — 2026-05-03

## Source Inputs
- materials json: `C:\prog\Comercial\LeonovCarePlatform\материалы\v18_STRICT_PEDAGOGY\course_import.json`
- generated migration: `C:\prog\Comercial\LeonovCarePlatform\backend\migrations\026_reseed_python_zero_v18_strict_pedagogy.sql`

## Parsed Materials Stats
- modules: 5
- lessons: 169
- steps: 1963
- tasks (practice + project): 1153
- quiz steps: 304
- executable tests (python_stdout + sql_query): 511
- stepTypeCounts: {"theory":337,"test":304,"practice":815,"project":338,"summary":169}
- checkerCounts: {"quiz_single":304,"python_stdout":33,"ide_plugin":422,"python_pytest":357,"sql_query":221,"http_api":120}

## Migration Structure Stats
- block type tags: 1963
- task policy tags: 1153
- testcase expected tags: 511
- checker_type counts in SQL: {"python_stdout":33,"python_pytest":357,"sql_query":221,"http_api":120,"ide_plugin":422}
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
