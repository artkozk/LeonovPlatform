import json
from pathlib import Path

from build_course import VALIDATION_REPORT_FILE, validate_course, write_validation_report

ROOT = Path(__file__).resolve().parent
COURSE_FILE = ROOT / "course_import.json"


def main() -> None:
    if not COURSE_FILE.exists():
        raise SystemExit(f"Missing file: {COURSE_FILE}")
    course = json.loads(COURSE_FILE.read_text(encoding="utf-8"))
    errors = validate_course(course)
    write_validation_report(course, errors)
    print(f"Validated: {COURSE_FILE}")
    print(f"Report: {VALIDATION_REPORT_FILE}")
    print(f"Errors: {len(errors)}")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
