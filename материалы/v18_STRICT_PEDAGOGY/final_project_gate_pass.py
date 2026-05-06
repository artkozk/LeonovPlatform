import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
COURSE_PATH = ROOT / "course_import.json"


def replace_text(value: str, replacements: dict[str, str]) -> str:
    text = value
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def patch_checker_strings(value, replacements: dict[str, str]):
    if isinstance(value, str):
        return replace_text(value, replacements)
    if isinstance(value, list):
        return [patch_checker_strings(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: patch_checker_strings(item, replacements) for key, item in value.items()}
    return value


def gate_questions(step_id: str, gate: str) -> list[dict]:
    return [
        {
            "id": f"{step_id}_q1",
            "question": f"Что должно быть главным результатом gate `{gate}`?",
            "options": [
                {
                    "id": "a",
                    "text": "конкретный файл, endpoint, команда, конфигурация или критерий pass/fail",
                },
                {"id": "b", "text": "общий текст о том, что проект почти готов"},
                {"id": "c", "text": "устное объяснение без артефакта"},
                {"id": "d", "text": "скриншот без команды проверки"},
            ],
            "correct_answer_id": "a",
            "correctOptionId": "a",
            "explanation": f"Gate `{gate}` принимается только тогда, когда ментор и IDE-проверка видят конкретную сдачу.",
        },
        {
            "id": f"{step_id}_q2",
            "question": f"Зачем для gate `{gate}` нужен отрицательный путь?",
            "options": [
                {
                    "id": "a",
                    "text": "он показывает, что решение обрабатывает ошибку, запрет, пустой ввод или сбойный сценарий",
                },
                {"id": "b", "text": "он заменяет основную реализацию"},
                {"id": "c", "text": "он нужен только для красоты README"},
                {"id": "d", "text": "он скрывает незавершённые части проекта"},
            ],
            "correct_answer_id": "a",
            "correctOptionId": "a",
            "explanation": "Без отрицательного пути легко принять happy path, который ломается при первом нестандартном действии.",
        },
        {
            "id": f"{step_id}_q3",
            "question": f"Почему нельзя сдавать gate `{gate}` как общий отчёт без команды или критерия проверки?",
            "options": [
                {
                    "id": "a",
                    "text": "такую сдачу нельзя воспроизвести и честно проверить на платформе",
                },
                {"id": "b", "text": "потому что короткие ответы всегда неверны"},
                {"id": "c", "text": "потому что ментору не нужен контекст"},
                {"id": "d", "text": "потому что файл README запрещён"},
            ],
            "correct_answer_id": "a",
            "correctOptionId": "a",
            "explanation": "Финальный проект проверяется через воспроизводимые артефакты: файл, route, команду, тест или критерий pass/fail.",
        },
    ]


def main() -> None:
    course = json.loads(COURSE_PATH.read_text(encoding="utf-8"))
    changed = 0

    for module in course["course"]["modules"]:
        for lesson in module["lessons"]:
            title = lesson.get("title", "")
            if not title.startswith("Финальный проект:"):
                continue

            gate = title.split(":", 1)[1].strip()
            gate_slug = lesson.get("id", "").replace("m05_l", "m05-l")
            replacements = {
                "SQL сценарий": "Проверочный сценарий",
                "SQL-файл": "Проверочный файл",
                "sql-scenariy": "proverochnyy-scenariy",
                "без подмены SQL-задачей": "как конкретную сдачу",
                "проверяемый результат": "конкретный результат",
                "проверяемым результатом": "главным результатом",
                "проверяемого результата": "конкретного результата",
                "проверяемом артефакте": "сданном файле",
                "проверяемый артефакт": "сданный артефакт",
                "Этот шаг проверяет содержание финального проекта, а не учебный запрос к таблице users.": "Этот шаг проверяет конкретный gate финального проекта: артефакт, команду проверки и отрицательный путь.",
                "Что нужно проверить в SQL-уроке": "Что нужно проверить в gate",
                "SQL-задаче": "проектном gate",
                "SQL-теме": "проектном gate",
                "SQL-решении": "проектном решении",
                "SQL-запрос": "результат сдачи",
            }

            lesson["skill_checkpoints"] = [
                replace_text(str(item), replacements) for item in lesson.get("skill_checkpoints", [])
            ]

            for step in lesson.get("steps", []):
                before = json.dumps(step, ensure_ascii=False, sort_keys=True)

                if isinstance(step.get("title"), str):
                    step["title"] = replace_text(step["title"], replacements)
                if isinstance(step.get("body_markdown"), str):
                    step["body_markdown"] = replace_text(step["body_markdown"], replacements)
                if isinstance(step.get("solution_code"), str):
                    step["solution_code"] = replace_text(step["solution_code"], replacements)
                if isinstance(step.get("checker"), dict):
                    step["checker"] = patch_checker_strings(step["checker"], replacements)

                if step.get("type") == "test":
                    questions = gate_questions(step["id"], gate)
                    stage = step.get("title", "контроль")
                    step["body_markdown"] = (
                        f"Проверь понимание gate `{gate}` на этапе `{stage}`. Вопросы проверяют, "
                        "что ты сдаёшь конкретный файл, endpoint, команду или критерий pass/fail, "
                        "а также отдельно описываешь отрицательный путь."
                    )
                    step["questions"] = [
                        {
                            "id": f"q{index + 1}",
                            "question": item["question"],
                            "options": [
                                {"id": option["id"], "text": option["text"]}
                                for option in item["options"]
                            ],
                            "correct_answer_id": item["correct_answer_id"],
                            "explanation": item["explanation"],
                        }
                        for index, item in enumerate(questions)
                    ]
                    step["checker"] = {
                        "type": "quiz_single",
                        "questions": questions,
                    }

                if step.get("type") == "project" and "Фокус gate" not in step.get("body_markdown", ""):
                    step["body_markdown"] = (
                        step.get("body_markdown", "").rstrip()
                        + "\n\n### Фокус gate\n"
                        + f"Проверь именно `{gate}`. В сдаче должен быть один файл, route, "
                        + "одна команда или критерий проверки и один отрицательный путь."
                    )

                after = json.dumps(step, ensure_ascii=False, sort_keys=True)
                if after != before:
                    changed += 1

    COURSE_PATH.write_text(
        json.dumps(course, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"final_project_gate_changes={changed}")


if __name__ == "__main__":
    main()
