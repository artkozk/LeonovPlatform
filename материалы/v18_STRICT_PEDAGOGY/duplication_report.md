# Duplication report v18_STRICT_PEDAGOGY

## Automated Result
- practice/project steps checked: 1146
- repeated title groups > 5 after: 0
- sql_query outside SQL-like context after: 0
- exact duplicate bodies after: 0
- normalized duplicate bodies after: 0
- exact duplicate solutions after: 0
- normalized duplicate solutions after: 0
- max duplicate group after: 1

## Cleanup Notes
- Before this iteration the package still had mass visible placeholder-like titles in hands-on steps.
- The current package rewrites exact generic titles into lesson-specific titles and adds validator gates so exact practice/project title groups larger than five fail.
- SQL-context cleanup replaces raw sql_query checkers outside SQL-like lessons with topic-aligned python_pytest, http_api, or ide_plugin checks.
- Remaining repeated concepts are acceptable only when they are different endpoint methods, different project gates, or different topic-specific checks.
- This report is generated from course_import.json, not from Markdown preview.

## Rewritten Groups In This Iteration
- m01_l026: branch state, feature history, dirty worktree and branch-flow checks.
- m01_l027: restore, restore --staged, reset --soft, revert and undo-audit checks.
- m01_l028: fast-forward, merge commit, README conflict, rebase and conflict-marker scan checks.
- m01_l029: origin, upstream, fetch, non-fast-forward, release tag and PR checklist checks.
- m01_l030: add/list/done/delete behavior and package-level CLI checks.
- m01_l031: Python helpers, error handling, terminal run, Git release state, CLI package and pass/fail rubric.
- Module 4 and Module 5 non-topic sql_query tasks were converted to topic-aligned checks.
- Generic project titles were renamed and backed by concrete required_files and commands where the checker is ide_plugin.

## Remaining Risk
- This automated report cannot replace staging import and real IDE-plugin smoke testing.
- Later course batches still need the same manual pedagogy pass as Module 1 Git/CLI.

## Final Status
- READY_FOR_STUDENT_TEST for the current batch.
