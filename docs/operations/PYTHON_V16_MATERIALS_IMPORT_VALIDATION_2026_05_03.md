# Python v16 Materials Import Validation — 2026-05-03

## Source Inputs
- materials json: `C:\prog\Comercial\LeonovCarePlatform\материалы\course_import.json`
- generated migration: `C:\prog\Comercial\LeonovCarePlatform\backend\migrations\025_reseed_python_zero_v16_materials.sql`

## Parsed Materials Stats
- modules: 5
- lessons: 150
- steps: 1800
- tasks (practice + project): 1050
- quiz steps: 300
- executable tests (python_stdout + sql_query): 1622
- stepTypeCounts: {"theory":300,"practice":750,"test":300,"project":300,"summary":150}
- checkerCounts: {"python_stdout":351,"quiz_single":300,"ide_plugin":384,"python_pytest":111,"http_api":95,"sql_query":109}

## Migration Structure Stats
- block type tags: 1800
- task policy tags: 1050
- testcase expected tags: 1622
- checker_type counts in SQL: {"python_stdout":351,"python_pytest":111,"sql_query":109,"http_api":95,"ide_plugin":384}
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
