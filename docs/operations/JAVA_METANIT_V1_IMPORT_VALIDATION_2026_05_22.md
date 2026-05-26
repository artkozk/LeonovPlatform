# Java Metanit v1 Import Validation — 2026-05-22

## Source Inputs
- materials json: `C:\prog\Comercial\LeonovCarePlatform\материалы\java_metanit_v1\course_import.json`
- generated migration: `C:\prog\Comercial\LeonovCarePlatform\backend\migrations\041_reseed_java_zero_core_metanit_v1_practice_refresh.sql`

## Parsed Materials Stats
- modules: 16
- lessons: 154
- steps: 462
- tasks (practice): 154
- quiz steps: 154
- executable tests (java_stdout): 616
- stepTypeCounts: {"theory":154,"test":154,"practice":154}
- checkerCounts: {"quiz_single":154,"java_stdout":154}
- long lesson titles: 0
- broken lesson titles: 0
- theory steps with source links: 0
- practice steps with broken intro: 0
- practice template diversity: 24
- practice adjacent template repeats: 0
- max practice template reuse: 9

## Migration Structure Stats
- block type tags: 462
- task policy tags: 154
- testcase expected tags: 616
- checker_type counts in SQL: {"java_stdout":154,"quiz_single":0}
- has quiz questions payload: true

## Verdict
- PASS: all validation checks passed.

## Check Flags
- stepCountMatches: PASS
- taskCountMatches: PASS
- testCountMatches: PASS
- checkerCountsMatchJavaStdout: PASS
- quizPayloadQuestionsPresent: PASS
- noLongLessonTitles: PASS
- noBrokenLessonTitles: PASS
- noTheorySourceLinks: PASS
- noPracticeBrokenIntro: PASS
- practiceTemplateDiversityOk: PASS
- noPracticeAdjacentTemplateRepeats: PASS
- practiceTemplateMaxReuseOk: PASS
