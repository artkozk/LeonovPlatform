# Duplication report v18_STRICT_PEDAGOGY

- duplicate groups before: legacy groups included renderer polymorphism, cache/inventory/state/retry task families, generic theory value/print blocks, and theory-pair collisions.
- near-duplicate theory pairs before this pass: 141
- repeated theory tails before this pass: 289

## After
- exact duplicate practice/project bodies after: 0
- normalized duplicate practice/project bodies after: 0
- exact/normalized duplicate solutions after: 0
- max structural solution group after: 1
- max AI structural group after: 1
- near-duplicate theory pairs after: 0
- repeated theory tails/paragraph/code-pair issues after: 0
- max duplicate group after: 1 for practice/project/solution structures under the validator gates.

## Rewritten groups
- Redis/S3/algorithm/structure task families were replaced with topic-specific tasks in earlier passes.
- This pass rewrote duplicated theory roles: concept step and minimal-example step now carry separate responsibilities.
- Repeated tails such as pre-practice boilerplate were removed or rewritten as lesson-specific explanation.

## Final result
- PASS


## Review method
- Exact body duplicates are counted only for practice/project steps because theory may share structural headings but must not share near-identical content inside one lesson.
- Normalized body duplicates remove numbers, technical step ids and function-like names before comparison, so superficial renaming does not hide copied tasks.
- Solution duplicates normalize function/class identifiers and imports. A repeated checked solution in two practice/project steps is a blocker.
- Theory-pair duplication is checked separately with similarity ratio, repeated-tail detection, repeated-paragraph detection and same-code-block detection inside one lesson.
- Remaining repeated headings such as section titles are allowed only when paragraph content, code, checker and learning role differ.
