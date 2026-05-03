# IDE plugin spec v14

Плагин проверяет конкретные артефакты, а не общие обещания.

## Обязательные проверки
- required_files с уникальным `scenario_id`;
- команды `python -m pytest`, `git status --porcelain`, `docker compose config` по типу задания;
- SQL fixtures и временные SQLite-базы;
- FastAPI route checks через TestClient;
- Dockerfile, compose, healthcheck, deploy script;
- Git workflow: branch, merge, rebase, conflict markers, clean worktree;
- CI/CD: test job, image build job, deploy job;
- final gates: required docs, pass/fail criteria, AI-review rubric.
