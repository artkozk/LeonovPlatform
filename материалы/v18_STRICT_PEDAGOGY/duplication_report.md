# Duplication report v18_STRICT_PEDAGOGY

- duplicate groups before current theory-code fix: internal theory code blocks 109; repeated theory code blocks across lessons 22; repeated generic paragraphs 156.
- duplicate code blocks inside one step after: 0
- repeated code blocks across lessons after: 0
- repeated generic paragraphs after: 0
- exact duplicate practice/project bodies after: 0
- normalized duplicate practice/project bodies after: 0
- normalized duplicate solutions after: 0
- max structural solution group after: 1
- max AI structural group after: 1

## Rewritten groups
- FastAPI/testing healthcheck examples separated into refresh, pagination, TestClient, integration, OpenAPI, Postman and CRUD examples.
- SQLAlchemy examples separated into session lifecycle, models, relationships, transactions, repository/UoW and Alembic migrations.
- Docker examples separated into Dockerfile, run/env, volumes, multistage and Compose.
- SQLite examples separated into .db file, CLI, DDL, CRUD, transaction/PRAGMA and repository.
- AI examples separated into messages, schema, mock provider, retry/timeout, RAG, vector search, LangGraph and safe review.

## Final result
- PASS

## Review note
- Remaining similarity is checked by four separate gates: exact practice/project body, normalized practice/project body, normalized solution and theory code block reuse.
- The maximum allowed duplicate group for practice/project materials is one; this keeps the validator from accepting tasks that only differ by id, title or route name.
- Theory examples now have the same rule for fenced code blocks: the same normalized code block cannot appear in two different lessons.
- If a future author intentionally needs a repeated command, they should write a new example around the current lesson's concrete artifact instead of copying the old block.
