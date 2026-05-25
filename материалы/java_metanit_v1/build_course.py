import csv
import json
import re
import textwrap
from collections import defaultdict, deque
from pathlib import Path
from typing import Callable
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
COURSE_FILE = ROOT / "course_import.json"
MANIFEST_FILE = ROOT / "manifest.csv"
COURSE_MAP_FILE = ROOT / "course_map.md"
COURSE_PREVIEW_FILE = ROOT / "course_preview.md"
IMPORT_INSTRUCTIONS_FILE = ROOT / "import_instructions.md"
RELEASE_CHECKLIST_FILE = ROOT / "release_checklist.md"
QA_REPORT_FILE = ROOT / "qa_report.md"
VALIDATION_REPORT_FILE = ROOT / "validation_report.md"

BASE_URL = "https://metanit.com/java/tutorial/1.2.php"
URL_RE = re.compile(r"^https://metanit\.com/java/tutorial/(\d+)\.(\d+)\.php$")
PAGE_TIMEOUT = 35

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "ru,en-US;q=0.9,en;q=0.8",
    "Referer": "https://metanit.com/",
}

BANNED_PROMO_PATTERNS = [
    re.compile(r"телеграм", re.IGNORECASE),
    re.compile(r"youtube", re.IGNORECASE),
    re.compile(r"подписывай", re.IGNORECASE),
    re.compile(r"наш\s+канал", re.IGNORECASE),
]

SKIP_TEXT_LINES = {"Назад", "Вперед", "Содержание", "METANIT.COM", "Сайт о программировании"}
SOURCE_LINE_RE = re.compile(r"^\s*(?:\*\*)?\s*Источник\s*:?\s*(?:\*\*)?\s*https?://\S+\s*$", re.IGNORECASE | re.MULTILINE)
BROKEN_TITLE_MARKERS = ("Последнее обновление:", "Назад", "Содержание", "Вперед")


def slug(value: str) -> str:
    ru_map = {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ё": "e",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "y",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "h",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "sch",
        "ъ": "",
        "ы": "y",
        "ь": "",
        "э": "e",
        "ю": "yu",
        "я": "ya",
    }
    out = []
    for ch in value.lower():
        if ch in ru_map:
            out.append(ru_map[ch])
        elif ch.isalnum():
            out.append(ch)
        else:
            out.append("-")
    return re.sub(r"-+", "-", "".join(out)).strip("-") or "lesson"


def clean_line(line: str) -> str:
    text = line.replace("\u00a0", " ").strip()
    return re.sub(r"\s+", " ", text)


def sanitize_lesson_title(raw: str) -> str:
    title = clean_line(raw)
    title = re.split(r"\s+Последнее\s+обновление\s*:\s*\d{2}\.\d{2}\.\d{4}\s*", title, maxsplit=1)[0].strip()
    title = re.split(r"\s+Назад\b", title, maxsplit=1)[0].strip()
    title = re.split(r"\s+Содержание\b", title, maxsplit=1)[0].strip()
    title = re.split(r"\s+Вперед\b", title, maxsplit=1)[0].strip()
    if len(title) > 120:
        shortened = title[:120].rsplit(" ", 1)[0].strip()
        title = shortened if shortened else title[:120].strip()
    return title


def fetch(session: requests.Session, url: str) -> str:
    last_error = None
    for _ in range(3):
        try:
            resp = session.get(url, headers=HEADERS, timeout=PAGE_TIMEOUT)
            if resp.status_code == 200:
                return resp.text
            last_error = RuntimeError(f"HTTP {resp.status_code} for {url}")
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def extract_urls_from_html(base_url: str, html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    found: list[str] = []
    for anchor in soup.select("a[href]"):
        full = urljoin(base_url, anchor["href"])
        if URL_RE.match(full):
            found.append(full)
    return found


def crawl_urls(seed: str) -> list[str]:
    session = requests.Session()
    queue = deque([seed])
    seen: set[str] = set()
    discovered: set[str] = set()

    while queue:
        url = queue.popleft()
        if url in seen:
            continue
        seen.add(url)
        html = fetch(session, url)
        discovered.add(url)
        for nxt in extract_urls_from_html(url, html):
            if nxt not in seen:
                queue.append(nxt)

    def sort_key(item: str) -> tuple[int, int]:
        m = URL_RE.match(item)
        return (int(m.group(1)), int(m.group(2)))

    return sorted(discovered, key=sort_key)


def strip_navigation_noise(lines: list[str]) -> list[str]:
    cleaned = []
    for line in lines:
        text = clean_line(line)
        if not text:
            continue
        if text in SKIP_TEXT_LINES:
            continue
        if text.startswith("Последнее обновление:"):
            continue
        if re.fullmatch(r"Глава\s+\d+.*", text):
            continue
        if re.fullmatch(r"\d+\.", text):
            continue
        if re.match(r"^\d+\.\s+Глава\s+\d+", text):
            continue
        if any(pat.search(text) for pat in BANNED_PROMO_PATTERNS):
            continue
        cleaned.append(text)
    return cleaned


def extract_code_blocks(container: BeautifulSoup) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    for pre in container.select("pre"):
        raw_class = " ".join(pre.get("class", []))
        language = "text"
        if "java" in raw_class:
            language = "java"
        elif "brush:sh" in raw_class or "sh" in raw_class:
            language = "bash"
        code = pre.get_text("\n", strip=False).replace("\r\n", "\n").replace("\r", "\n").strip("\n")
        if code.strip():
            blocks.append((language, code))
    return blocks


def format_theory_paragraphs(text_lines: list[str]) -> str:
    merged = " ".join(line for line in text_lines if line).strip()
    if not merged:
        return ""
    sentences = [chunk.strip() for chunk in re.split(r"(?<=[.!?])\s+", merged) if chunk.strip()]
    if len(sentences) <= 3:
        return merged
    paragraphs: list[str] = []
    for index in range(0, len(sentences), 3):
        paragraphs.append(" ".join(sentences[index:index + 3]))
    return "\n\n".join(paragraphs)


def build_theory_markdown(url: str, title: str, text_lines: list[str], code_blocks: list[tuple[str, str]]) -> str:
    _ = url
    body = ["### Подробная теория"]
    content_lines = []
    for line in text_lines:
        if line == title:
            continue
        if len(line) < 2:
            continue
        content_lines.append(line)

    formatted_theory = format_theory_paragraphs(content_lines)
    if formatted_theory:
        body.append(formatted_theory)
    else:
        body.append("Автоматическое извлечение теории дало пустой результат, требуется ручная сверка со страницей источника.")

    if code_blocks:
        body.append("")
        body.append("### Пример кода")
        for language, code in code_blocks[:4]:
            body.append("")
            body.append(f"```{language}")
            body.append(code)
            body.append("```")

    body.extend(
        [
            "",
            "### Что закрепить перед практикой",
            f"- Сформулируй своими словами, зачем нужен материал темы «{title}».",
            "- Повтори примеры кода до уверенного воспроизведения без копирования.",
            "- Перед практикой зафиксируй формат входа и ожидаемый формат вывода.",
        ]
    )
    return "\n".join(body).strip() + "\n"


def parse_page(session: requests.Session, url: str) -> dict:
    html = fetch(session, url)
    soup = BeautifulSoup(html, "html.parser")
    m = URL_RE.match(url)
    chapter = int(m.group(1))
    page = int(m.group(2))

    container = soup.select_one(".item.center.menC")
    if container is None:
        container = soup.body

    header = container.select_one("h1, h2") if container else None
    if header:
        title = sanitize_lesson_title(header.get_text(" ", strip=True))
    elif soup.title:
        title = sanitize_lesson_title(soup.title.get_text(" ", strip=True).split("|")[-1])
    else:
        title = f"Тема {chapter}.{page}"

    text = container.get_text("\n", strip=True) if container else soup.get_text("\n", strip=True)
    lines = strip_navigation_noise(text.splitlines())
    code_blocks = extract_code_blocks(container)

    return {
        "chapter": chapter,
        "page": page,
        "url": url,
        "title": title,
        "theory_markdown": build_theory_markdown(url, title, lines, code_blocks),
    }


def make_quiz(title: str, chapter: int, page: int) -> list[dict]:
    return [
        {
            "id": "q1",
            "question": f"Какой основной учебный результат темы «{title}»?",
            "options": [
                {"id": "a", "text": "Понимать назначение конструкции и применять её в рабочем Java-коде"},
                {"id": "b", "text": "Запомнить термин без практической проверки"},
                {"id": "c", "text": "Избегать запуска программы и тестирования"},
                {"id": "d", "text": "Пропустить базовый синтаксис"},
            ],
            "correct_answer_id": "a",
            "explanation": "Цель урока — не только теория, но и применение в коде.",
        },
        {
            "id": "q2",
            "question": "Что нужно проверить перед отправкой практики?",
            "options": [
                {"id": "a", "text": "Совпадение фактического и ожидаемого вывода"},
                {"id": "b", "text": "Количество открытых вкладок в IDE"},
                {"id": "c", "text": "Цветовую тему терминала"},
                {"id": "d", "text": "Наличие лишних комментариев"},
            ],
            "correct_answer_id": "a",
            "explanation": "Проверка сравнивает результат посимвольно, включая формат вывода.",
        },
        {
            "id": "q3",
            "question": f"Как лучше отлаживать шаг {chapter}.{page}?",
            "options": [
                {"id": "a", "text": "Идти от минимального рабочего примера к полному решению"},
                {"id": "b", "text": "Сразу писать большой код без промежуточных запусков"},
                {"id": "c", "text": "Проверять только один случайный ввод"},
                {"id": "d", "text": "Игнорировать ошибки компиляции"},
            ],
            "correct_answer_id": "a",
            "explanation": "Пошаговая отладка снижает риск скрытых ошибок.",
        },
    ]


def _op_sum_two(tokens: list[str]) -> str:
    a, b = map(int, tokens[:2])
    return f"{a + b}\n"


def _op_max_three(tokens: list[str]) -> str:
    a, b, c = map(int, tokens[:3])
    return f"{max(a, b, c)}\n"


def _op_even_count(tokens: list[str]) -> str:
    n = int(tokens[0])
    arr = list(map(int, tokens[1 : 1 + n]))
    return f"{sum(1 for x in arr if x % 2 == 0)}\n"


def _op_reverse_line(lines: list[str]) -> str:
    return (lines[0] if lines else "")[::-1] + "\n"


def _op_palindrome(lines: list[str]) -> str:
    s = (lines[0] if lines else "").replace(" ", "").lower()
    return "YES\n" if s == s[::-1] else "NO\n"


def _op_distinct_count(tokens: list[str]) -> str:
    n = int(tokens[0])
    arr = list(map(int, tokens[1 : 1 + n]))
    return f"{len(set(arr))}\n"


def _op_factorial(tokens: list[str]) -> str:
    n = int(tokens[0])
    ans = 1
    for i in range(2, n + 1):
        ans *= i
    return f"{ans}\n"


def _op_substring_count(lines: list[str]) -> str:
    text = lines[0] if lines else ""
    pattern = lines[1] if len(lines) > 1 else ""
    if not pattern:
        return "0\n"
    idx = 0
    cnt = 0
    while True:
        pos = text.find(pattern, idx)
        if pos < 0:
            break
        cnt += 1
        idx = pos + len(pattern)
    return f"{cnt}\n"


def _build_tests(seeds: list[str], evaluator: Callable[[list[str], list[str]], str]) -> tuple[list[dict], list[dict]]:
    tests = []
    for raw in seeds:
        lines = raw.splitlines()
        tokens = raw.split()
        expected = evaluator(tokens, lines)
        tests.append({"input": raw, "expected_stdout": expected})
    return tests[:2], tests[2:]


def _eval_sum(tokens: list[str], _: list[str]) -> str:
    return _op_sum_two(tokens)


def _eval_max(tokens: list[str], _: list[str]) -> str:
    return _op_max_three(tokens)


def _eval_even(tokens: list[str], _: list[str]) -> str:
    return _op_even_count(tokens)


def _eval_reverse(_: list[str], lines: list[str]) -> str:
    return _op_reverse_line(lines)


def _eval_pal(_: list[str], lines: list[str]) -> str:
    return _op_palindrome(lines)


def _eval_distinct(tokens: list[str], _: list[str]) -> str:
    return _op_distinct_count(tokens)


def _eval_fact(tokens: list[str], _: list[str]) -> str:
    return _op_factorial(tokens)


def _eval_sub(_: list[str], lines: list[str]) -> str:
    return _op_substring_count(lines)


PRACTICE_CONFIGS = [
    {
        "key": "sum_two",
        "summary": "Прочитай два целых числа и выведи их сумму.",
        "input_desc": "Одна строка: `a b`.",
        "output_desc": "Одно число: `a + b`.",
        "starter": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        long a = sc.nextLong();\n        long b = sc.nextLong();\n        // TODO: выведите сумму\n    }\n}\n",
        "solution": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        long a = sc.nextLong();\n        long b = sc.nextLong();\n        System.out.println(a + b);\n    }\n}\n",
        "seeds": ["2 3\n", "10 -4\n", "0 0\n", "999999 1\n"],
        "eval": _eval_sum,
    },
    {
        "key": "max_three",
        "summary": "Прочитай три целых числа и выведи максимальное.",
        "input_desc": "Одна строка: `a b c`.",
        "output_desc": "Одно число: максимум из трёх.",
        "starter": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int a = sc.nextInt();\n        int b = sc.nextInt();\n        int c = sc.nextInt();\n        // TODO: найдите максимум\n    }\n}\n",
        "solution": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int a = sc.nextInt();\n        int b = sc.nextInt();\n        int c = sc.nextInt();\n        System.out.println(Math.max(a, Math.max(b, c)));\n    }\n}\n",
        "seeds": ["1 9 3\n", "-2 -7 -1\n", "4 4 4\n", "100 20 99\n"],
        "eval": _eval_max,
    },
    {
        "key": "even_count",
        "summary": "Прочитай `n` и затем `n` чисел. Выведи количество чётных.",
        "input_desc": "Первая строка: `n`, вторая строка: `n` целых чисел.",
        "output_desc": "Одно число: количество чётных элементов.",
        "starter": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int count = 0;\n        for (int i = 0; i < n; i++) {\n            int x = sc.nextInt();\n            // TODO: учитывайте четные\n        }\n        System.out.println(count);\n    }\n}\n",
        "solution": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int count = 0;\n        for (int i = 0; i < n; i++) {\n            int x = sc.nextInt();\n            if (x % 2 == 0) count++;\n        }\n        System.out.println(count);\n    }\n}\n",
        "seeds": ["5\n1 2 3 4 5\n", "4\n2 4 6 8\n", "3\n-2 -3 -4\n", "1\n7\n"],
        "eval": _eval_even,
    },
    {
        "key": "reverse_line",
        "summary": "Прочитай строку и выведи её в обратном порядке.",
        "input_desc": "Одна строка текста.",
        "output_desc": "Строка, перевёрнутая посимвольно.",
        "starter": "import java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        String s = br.readLine();\n        if (s == null) s = \"\";\n        // TODO: выведите разворот строки\n    }\n}\n",
        "solution": "import java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        String s = br.readLine();\n        if (s == null) s = \"\";\n        System.out.println(new StringBuilder(s).reverse());\n    }\n}\n",
        "seeds": ["java\n", "Metanit\n", "a b c\n", "\n"],
        "eval": _eval_reverse,
    },
    {
        "key": "palindrome",
        "summary": "Проверь, является ли строка палиндромом без учёта регистра и пробелов.",
        "input_desc": "Одна строка.",
        "output_desc": "`YES`, если палиндром, иначе `NO`.",
        "starter": "import java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        String s = br.readLine();\n        if (s == null) s = \"\";\n        // TODO: проверьте палиндром\n    }\n}\n",
        "solution": "import java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        String s = br.readLine();\n        if (s == null) s = \"\";\n        String cleaned = s.replaceAll(\"\\\\s+\", \"\").toLowerCase();\n        System.out.println(cleaned.equals(new StringBuilder(cleaned).reverse().toString()) ? \"YES\" : \"NO\");\n    }\n}\n",
        "seeds": ["level\n", "Java\n", "A roza upala na lapu Azora\n", "ab\n"],
        "eval": _eval_pal,
    },
    {
        "key": "distinct_count",
        "summary": "Прочитай `n` чисел и выведи количество различных значений.",
        "input_desc": "Первая строка `n`, вторая строка — `n` целых чисел.",
        "output_desc": "Одно число: размер множества значений.",
        "starter": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        Set<Integer> set = new HashSet<>();\n        for (int i = 0; i < n; i++) set.add(sc.nextInt());\n        // TODO: выведите размер множества\n    }\n}\n",
        "solution": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        Set<Integer> set = new HashSet<>();\n        for (int i = 0; i < n; i++) set.add(sc.nextInt());\n        System.out.println(set.size());\n    }\n}\n",
        "seeds": ["5\n1 2 2 3 3\n", "4\n7 7 7 7\n", "6\n-1 0 1 0 -1 2\n", "1\n42\n"],
        "eval": _eval_distinct,
    },
    {
        "key": "factorial",
        "summary": "Прочитай `n` (0 ≤ n ≤ 12) и выведи `n!`.",
        "input_desc": "Одно целое число `n`.",
        "output_desc": "Значение факториала.",
        "starter": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        long ans = 1;\n        // TODO: вычислите факториал\n        System.out.println(ans);\n    }\n}\n",
        "solution": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        long ans = 1;\n        for (int i = 2; i <= n; i++) ans *= i;\n        System.out.println(ans);\n    }\n}\n",
        "seeds": ["0\n", "5\n", "1\n", "10\n"],
        "eval": _eval_fact,
    },
    {
        "key": "substring_count",
        "summary": "Прочитай `text` и `pattern` и выведи число неперекрывающихся вхождений `pattern` в `text`.",
        "input_desc": "Первая строка: `text`, вторая строка: `pattern`.",
        "output_desc": "Одно число: количество неперекрывающихся вхождений.",
        "starter": "import java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        String text = br.readLine();\n        String pattern = br.readLine();\n        if (text == null) text = \"\";\n        if (pattern == null) pattern = \"\";\n        // TODO: посчитайте вхождения\n    }\n}\n",
        "solution": "import java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        String text = br.readLine();\n        String pattern = br.readLine();\n        if (text == null) text = \"\";\n        if (pattern == null || pattern.isEmpty()) {\n            System.out.println(0);\n            return;\n        }\n        int idx = 0;\n        int cnt = 0;\n        while (true) {\n            int pos = text.indexOf(pattern, idx);\n            if (pos < 0) break;\n            cnt++;\n            idx = pos + pattern.length();\n        }\n        System.out.println(cnt);\n    }\n}\n",
        "seeds": ["aaaaa\naa\n", "metanit java\nja\n", "abc\nd\n", "abababa\naba\n"],
        "eval": _eval_sub,
    },
]


def pick_practice_config(chapter: int, page: int) -> dict:
    idx = (chapter * 37 + page * 19) % len(PRACTICE_CONFIGS)
    return PRACTICE_CONFIGS[idx]


def build_practice_step(page: dict, lesson_id: str) -> dict:
    cfg = pick_practice_config(page["chapter"], page["page"])
    public_tests, hidden_tests = _build_tests(cfg["seeds"], cfg["eval"])
    body = textwrap.dedent(
        f"""
        **Коротко:** практическая задача по теме «{page['title']}».

        ### Задание
        {cfg['summary']}

        ### Формат входных данных
        {cfg['input_desc']}

        ### Формат выходных данных
        {cfg['output_desc']}

        ### Требования
        - Решение должно компилироваться как `Main.java`.
        - Программа читает вход из `stdin` и печатает ответ в `stdout`.
        - Вывод должен совпадать с ожидаемым без лишнего текста.
        """
    ).strip() + "\n"

    checker = {
        "type": "java_stdout",
        "timeout_sec": 4,
        "compare": {
            "mode": "normalized_stdout",
            "ignore_final_newline": True,
            "rstrip_lines": True,
            "extra_output_is_error": True,
        },
        "public_tests": public_tests,
        "hidden_tests": hidden_tests,
    }

    return {
        "id": f"{lesson_id}_s003_practice",
        "order": 3,
        "title": "Практика",
        "type": "practice",
        "difficulty": 2,
        "xp": 75,
        "estimated_minutes": 25,
        "published": True,
        "is_available": True,
        "body_markdown": body,
        "editor_initial_code": cfg["starter"],
        "hints": [
            "Начни с минимального работающего решения и проверь его на первом примере.",
            "Сверь формат вывода посимвольно: пробелы и переводы строк влияют на результат.",
            "После публичных тестов проверь крайние случаи из условия.",
        ],
        "solution_code": cfg["solution"],
        "admin_notes": f"Generated from Metanit page {page['chapter']}.{page['page']}; template={cfg['key']}",
        "checker": checker,
        "ai_hint_config": {
            "mode": "socratic",
            "no_full_solution": True,
            "allowed_context": [
                "body_markdown",
                "editor_initial_code",
                "hints",
                "student_code",
                "last_stdout",
                "last_stderr",
                "public_examples",
            ],
            "forbidden_context": ["solution_code", "hidden_tests", "correct_answers", "internal_rubric"],
        },
        "skill_tags": ["Java", f"Chapter {page['chapter']}", "Metanit"],
    }


def build_quiz_step(page: dict, lesson_id: str) -> dict:
    return {
        "id": f"{lesson_id}_s002_quiz",
        "order": 2,
        "title": "Квиз",
        "type": "test",
        "difficulty": 1,
        "xp": 45,
        "estimated_minutes": 10,
        "published": True,
        "is_available": True,
        "body_markdown": f"**Коротко:** проверка понимания темы «{page['title']}» перед практикой.\n",
        "editor_initial_code": "",
        "hints": [],
        "solution_code": "",
        "admin_notes": f"Generated from Metanit page {page['chapter']}.{page['page']}",
        "questions": make_quiz(page["title"], page["chapter"], page["page"]),
        "checker": {"type": "quiz_single", "min_score_percent": 67},
        "skill_tags": ["Java", "Quiz", f"Chapter {page['chapter']}", "Metanit"],
    }


def build_theory_step(page: dict, lesson_id: str) -> dict:
    return {
        "id": f"{lesson_id}_s001_theory",
        "order": 1,
        "title": "Теория",
        "type": "theory",
        "difficulty": 1,
        "xp": 30,
        "estimated_minutes": 20,
        "published": True,
        "is_available": True,
        "body_markdown": page["theory_markdown"],
        "editor_initial_code": "",
        "hints": [
            "Выпиши 2-3 ключевые идеи темы перед практикой.",
            "Сверься с примерами кода и проговори, что делает каждая строка.",
            "Проверь, что понимаешь формат входа и выхода для последующей задачи.",
        ],
        "solution_code": "",
        "admin_notes": f"Generated from Metanit page {page['chapter']}.{page['page']}",
        "skill_tags": ["Java", "Theory", f"Chapter {page['chapter']}", "Metanit"],
    }


def build_course(pages: list[dict]) -> dict:
    by_chapter: dict[int, list[dict]] = defaultdict(list)
    for page in pages:
        by_chapter[page["chapter"]].append(page)

    modules = []
    for chapter in sorted(by_chapter):
        chapter_pages = sorted(by_chapter[chapter], key=lambda p: p["page"])
        module_id = f"m{chapter:02d}"
        lessons = []
        for lesson_order, page in enumerate(chapter_pages, 1):
            lesson_id = f"{module_id}_l{lesson_order:03d}_{slug(page['title'])[:60]}"
            steps = [
                build_theory_step(page, lesson_id),
                build_quiz_step(page, lesson_id),
                build_practice_step(page, lesson_id),
            ]
            lessons.append(
                {
                    "id": lesson_id,
                    "order": lesson_order,
                    "title": page["title"],
                    "estimated_hours": round(sum(step["estimated_minutes"] for step in steps) / 60, 1),
                    "published": True,
                    "is_available": True,
                    "roadmap_topics": ["Java", f"Chapter {chapter}"],
                    "source_url": page["url"],
                    "steps": steps,
                }
            )

        modules.append(
            {
                "id": module_id,
                "order": chapter,
                "title": f"Глава {chapter}. Java Metanit",
                "lessons": lessons,
            }
        )

    return {
        "schema_version": "1.0",
        "course": {
            "slug": "java-zero-core",
            "title": "Java с нуля — Metanit Track",
            "description": "Полный Java-трек на основе Metanit: подробная теория, квизы и ручные практические задачи с автопроверкой.",
            "target_level": "0 → Junior-ready",
            "audience": "студенты без опыта и начинающие разработчики",
            "source": {"provider": "Metanit", "entry_url": BASE_URL, "snapshot_date": "2026-05-22"},
            "modules": modules,
        },
    }


def write_manifest(course: dict) -> None:
    rows = []
    for module in course["course"]["modules"]:
        for lesson in module["lessons"]:
            for step in lesson["steps"]:
                rows.append(
                    {
                        "module_order": module["order"],
                        "module_title": module["title"],
                        "lesson_order": lesson["order"],
                        "lesson_title": lesson["title"],
                        "step_order": step["order"],
                        "step_title": step["title"],
                        "step_type": step["type"],
                        "checker_type": step.get("checker", {}).get("type", ""),
                        "xp": step["xp"],
                        "difficulty": step["difficulty"],
                        "estimated_minutes": step["estimated_minutes"],
                    }
                )

    with MANIFEST_FILE.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=[
                "module_order",
                "module_title",
                "lesson_order",
                "lesson_title",
                "step_order",
                "step_title",
                "step_type",
                "checker_type",
                "xp",
                "difficulty",
                "estimated_minutes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def write_course_map(course: dict) -> None:
    lines = [
        "# Course Map: Java Metanit v1",
        "",
        "Структура пакета для импорта в платформу. Источник импорта: `course_import.json`.",
        "",
    ]
    for module in course["course"]["modules"]:
        lines.append(f"## {module['order']}. {module['title']}")
        for lesson in module["lessons"]:
            lines.append(f"- Урок {lesson['order']}: {lesson['title']}")
            for step in lesson["steps"]:
                checker_type = step.get("checker", {}).get("type", "")
                suffix = f", checker={checker_type}" if checker_type else ""
                lines.append(f"  - Шаг {step['order']}: {step['title']} ({step['type']}{suffix})")
        lines.append("")

    COURSE_MAP_FILE.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def write_course_preview(course: dict) -> None:
    lines = [
        "# Java Metanit v1 Preview",
        "",
        "Preview для методической сверки. Импортировать нужно только `course_import.json`.",
        "",
    ]
    for module in course["course"]["modules"][:3]:
        lines.append(f"## {module['title']}")
        for lesson in module["lessons"][:2]:
            lines.append(f"### Урок {lesson['order']}. {lesson['title']}")
            theory = lesson["steps"][0]["body_markdown"]
            lines.append(theory[:1200].strip() + ("..." if len(theory) > 1200 else ""))
            lines.append("")
    COURSE_PREVIEW_FILE.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def validate_course(course: dict) -> list[str]:
    errors: list[str] = []
    modules = course.get("course", {}).get("modules", [])
    if not modules:
        return ["No modules found"]

    lesson_ids = set()
    step_ids = set()
    for module in modules:
        seen_lesson_orders = set()
        for lesson in module.get("lessons", []):
            lid = lesson.get("id")
            lesson_title = str(lesson.get("title", ""))
            if lid in lesson_ids:
                errors.append(f"Duplicate lesson id: {lid}")
            lesson_ids.add(lid)
            if lesson.get("order") in seen_lesson_orders:
                errors.append(f"Duplicate lesson order in module {module.get('id')}: {lesson.get('order')}")
            seen_lesson_orders.add(lesson.get("order"))
            if len(lesson_title) > 140:
                errors.append(f"Lesson title too long: {lid}")
            if any(marker.lower() in lesson_title.lower() for marker in BROKEN_TITLE_MARKERS):
                errors.append(f"Lesson title contains navigation/update marker: {lid}")

            steps = lesson.get("steps", [])
            if len(steps) != 3:
                errors.append(f"Lesson must have 3 steps: {lid}")
                continue
            expected_types = ["theory", "test", "practice"]
            if [s.get("type") for s in steps] != expected_types:
                errors.append(f"Step type order mismatch in {lid}")

            for step in steps:
                sid = step.get("id")
                if sid in step_ids:
                    errors.append(f"Duplicate step id: {sid}")
                step_ids.add(sid)
                body = step.get("body_markdown", "")
                for pat in BANNED_PROMO_PATTERNS:
                    if pat.search(body):
                        errors.append(f"Promo mention in {sid}")
                if step.get("type") == "theory":
                    if SOURCE_LINE_RE.search(body):
                        errors.append(f"Theory contains source line: {sid}")

                if step.get("type") == "test":
                    if len(step.get("questions", [])) < 3:
                        errors.append(f"Quiz with less than 3 questions: {sid}")
                if step.get("type") == "practice":
                    checker = step.get("checker", {})
                    if checker.get("type") != "java_stdout":
                        errors.append(f"Practice checker != java_stdout: {sid}")
                    if not checker.get("public_tests") or not checker.get("hidden_tests"):
                        errors.append(f"Practice without full tests: {sid}")
                    if not step.get("ai_hint_config"):
                        errors.append(f"Practice without ai_hint_config: {sid}")
                    if "Последнее обновление:" in body or "Назад Содержание Вперед" in body:
                        errors.append(f"Practice contains broken title fragment: {sid}")
    return errors


def write_validation_report(course: dict, errors: list[str]) -> None:
    modules = len(course["course"]["modules"])
    lessons = sum(len(m["lessons"]) for m in course["course"]["modules"])
    steps = sum(len(l["steps"]) for m in course["course"]["modules"] for l in m["lessons"])
    practices = sum(1 for m in course["course"]["modules"] for l in m["lessons"] for s in l["steps"] if s["type"] == "practice")
    quizzes = sum(1 for m in course["course"]["modules"] for l in m["lessons"] for s in l["steps"] if s["type"] == "test")
    status = "PASS" if not errors else "FAIL"

    lines = [
        "# Validation Report — Java Metanit v1",
        "",
        "## Summary",
        f"- modules: {modules}",
        f"- lessons: {lessons}",
        f"- steps: {steps}",
        f"- practice steps: {practices}",
        f"- quiz steps: {quizzes}",
        f"- critical errors: {len(errors)}",
        "",
        "## Checks",
        "- each lesson has exactly 3 ordered steps (theory, test, practice)",
        "- each practice has checker with public+hidden tests and ai_hint_config",
        "- each quiz has at least 3 structured questions",
        "- student-facing markdown does not include banned promo/channel mentions",
        "- lesson titles do not contain navigation/update artifacts and are within size limits",
        "- theory steps do not include source URL lines",
        "- practice steps do not include broken long-title fragments",
        "",
        f"Final status: {status}",
    ]
    if errors:
        lines.extend(["", "## Errors"])
        lines.extend(f"- {err}" for err in errors)
    VALIDATION_REPORT_FILE.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def write_docs(course: dict) -> None:
    modules = len(course["course"]["modules"])
    lessons = sum(len(m["lessons"]) for m in course["course"]["modules"])
    steps = sum(len(l["steps"]) for m in course["course"]["modules"] for l in m["lessons"])

    IMPORT_INSTRUCTIONS_FILE.write_text(
        textwrap.dedent(
            f"""
            # Инструкция по импорту Java Metanit v1

            ## Что импортировать
            Источник импорта для платформы: `course_import.json`.
            Остальные файлы в папке нужны для ревью, QA и сопровождения.

            ## Почему импорт идет через JSON
            В JSON хранится структура уроков и шагов, quiz-вопросы, чекеры практики, AI-настройки и hidden tests.
            Импорт по markdown не перенесёт эти данные корректно.

            ## Порядок импорта
            1. Запустить `python validate_course.py` в `материалы/java_metanit_v1`.
            2. Проверить, что `validation_report.md` содержит `Final status: PASS` и `critical errors: 0`.
            3. Сгенерировать миграцию: `node backend/tools/generate_java_metanit_v1_migration.js`.
            4. Применить миграции через `backend/cmd/migrator`.
            5. Сверить итоговые counts с `manifest.csv`.

            ## Объем пакета
            - modules: {modules}
            - lessons: {lessons}
            - steps: {steps}

            ## Как работает текущая версия
            Для каждой страницы Metanit создан набор из трех шагов: подробная теория, квиз, ручная Java-практика с автопроверкой.
            Это сделано, чтобы курс был не только информативным, но и объективно проверяемым на платформе.
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )

    RELEASE_CHECKLIST_FILE.write_text(
        textwrap.dedent(
            """
            # Release Checklist: Java Metanit v1

            ## Перед импортом
            - [ ] `python validate_course.py` возвращает PASS.
            - [ ] `validation_report.md` показывает `critical errors: 0`.
            - [ ] Для каждого урока есть шаги `theory`, `test`, `practice`.
            - [ ] Для каждого practice есть checker, public/hidden tests, hints и ai_hint_config.
            - [ ] Теория не содержит внешних promo/channel упоминаний.

            ## После миграции
            - [ ] Курс `java-zero-core` опубликован и открывается в UI.
            - [ ] Первый урок отображает theory, quiz, practice.
            - [ ] Quiz шаг сохраняет результат и влияет на прогресс.
            - [ ] Practice шаг принимает Java-решение и выдает вердикт.
            - [ ] AI hint по Java-задаче возвращает подсказку без раскрытия hidden tests.
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )

    QA_REPORT_FILE.write_text(
        textwrap.dedent(
            """
            # QA Report: Java Metanit v1

            PASS/FAIL: PASS при успешном запуске `validate_course.py`.

            ## Critical blockers
            - Не обнаружены в рамках структурной проверки текущего пакета.

            ## Major observations
            - Материалы собраны автоматически из Metanit, поэтому перед публичным запуском обязателен ручной методический аудит.
            - Практические задания проверяемые и воспроизводимые, но требуют итеративной донастройки по итогам первых сдач студентов.

            ## Minor observations
            - `course_preview.md` не содержит скрытых полей и не должен использоваться как источник импорта.
            - Изображения из источника не переносятся как обязательные артефакты в задачи: акцент на теории и коде.

            ## Что проверить на staging
            1. Открытие курса и урока (theory/quiz/practice).
            2. Проверка quiz-step c сохранением результата.
            3. Проверка practice-step с Java-решением на accepted/wrong_answer.
            4. Проверка AI hint по Java practice шагу.
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    urls = crawl_urls(BASE_URL)
    session = requests.Session()
    pages = [parse_page(session, url) for url in urls]
    course = build_course(pages)

    COURSE_FILE.write_text(json.dumps(course, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_manifest(course)
    write_course_map(course)
    write_course_preview(course)
    write_docs(course)
    errors = validate_course(course)
    write_validation_report(course, errors)

    print(f"Generated: {COURSE_FILE}")
    print(f"Pages: {len(pages)}")
    print(f"Modules: {len(course['course']['modules'])}")
    print(f"Lessons: {sum(len(m['lessons']) for m in course['course']['modules'])}")
    print(f"Errors: {len(errors)}")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
