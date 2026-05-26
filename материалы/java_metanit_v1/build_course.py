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


def _op_abs_sum_two(tokens: list[str]) -> str:
    a, b = map(int, tokens[:2])
    return f"{abs(a) + abs(b)}\n"


def _op_product_two(tokens: list[str]) -> str:
    a, b = map(int, tokens[:2])
    return f"{a * b}\n"


def _op_min_three(tokens: list[str]) -> str:
    a, b, c = map(int, tokens[:3])
    return f"{min(a, b, c)}\n"


def _op_middle_three(tokens: list[str]) -> str:
    a, b, c = map(int, tokens[:3])
    return f"{sorted([a, b, c])[1]}\n"


def _op_odd_count(tokens: list[str]) -> str:
    n = int(tokens[0])
    arr = list(map(int, tokens[1 : 1 + n]))
    return f"{sum(1 for x in arr if x % 2 != 0)}\n"


def _op_positive_count(tokens: list[str]) -> str:
    n = int(tokens[0])
    arr = list(map(int, tokens[1 : 1 + n]))
    return f"{sum(1 for x in arr if x > 0)}\n"


def _op_upper_line(lines: list[str]) -> str:
    return (lines[0] if lines else "").upper() + "\n"


def _op_word_count(lines: list[str]) -> str:
    text = (lines[0] if lines else "").strip()
    if not text:
        return "0\n"
    return f"{len(text.split())}\n"


def _op_sum_to_n(tokens: list[str]) -> str:
    n = int(tokens[0])
    return f"{(n * (n + 1)) // 2}\n"


def _op_fibonacci(tokens: list[str]) -> str:
    n = int(tokens[0])
    if n <= 0:
        return "0\n"
    if n == 1:
        return "1\n"
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return f"{b}\n"


def _op_char_count(lines: list[str]) -> str:
    text = lines[0] if lines else ""
    raw_ch = lines[1] if len(lines) > 1 else ""
    ch = raw_ch[0] if raw_ch else ""
    return f"{text.count(ch)}\n"


def _op_substring_overlap(lines: list[str]) -> str:
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
        idx = pos + 1
    return f"{cnt}\n"


def _op_digit_sum(tokens: list[str]) -> str:
    n = abs(int(tokens[0]))
    total = 0
    for ch in str(n):
        total += int(ch)
    return f"{total}\n"


def _op_gcd_two(tokens: list[str]) -> str:
    a, b = map(abs, map(int, tokens[:2]))
    while b:
        a, b = b, a % b
    return f"{a}\n"


def _op_lcm_two(tokens: list[str]) -> str:
    a_raw, b_raw = map(int, tokens[:2])
    if a_raw == 0 or b_raw == 0:
        return "0\n"
    a, b = abs(a_raw), abs(b_raw)
    x, y = a, b
    while y:
        x, y = y, x % y
    return f"{(a // x) * b}\n"


def _op_unique_once_count(tokens: list[str]) -> str:
    n = int(tokens[0])
    arr = list(map(int, tokens[1 : 1 + n]))
    freq = {}
    for value in arr:
        freq[value] = freq.get(value, 0) + 1
    return f"{sum(1 for value in arr if freq[value] == 1)}\n"


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


def _eval_abs_sum(tokens: list[str], _: list[str]) -> str:
    return _op_abs_sum_two(tokens)


def _eval_product(tokens: list[str], _: list[str]) -> str:
    return _op_product_two(tokens)


def _eval_min(tokens: list[str], _: list[str]) -> str:
    return _op_min_three(tokens)


def _eval_middle(tokens: list[str], _: list[str]) -> str:
    return _op_middle_three(tokens)


def _eval_odd(tokens: list[str], _: list[str]) -> str:
    return _op_odd_count(tokens)


def _eval_positive(tokens: list[str], _: list[str]) -> str:
    return _op_positive_count(tokens)


def _eval_upper(_: list[str], lines: list[str]) -> str:
    return _op_upper_line(lines)


def _eval_words(_: list[str], lines: list[str]) -> str:
    return _op_word_count(lines)


def _eval_sum_to_n(tokens: list[str], _: list[str]) -> str:
    return _op_sum_to_n(tokens)


def _eval_fib(tokens: list[str], _: list[str]) -> str:
    return _op_fibonacci(tokens)


def _eval_char_count(_: list[str], lines: list[str]) -> str:
    return _op_char_count(lines)


def _eval_sub_overlap(_: list[str], lines: list[str]) -> str:
    return _op_substring_overlap(lines)


def _eval_digit_sum(tokens: list[str], _: list[str]) -> str:
    return _op_digit_sum(tokens)


def _eval_gcd(tokens: list[str], _: list[str]) -> str:
    return _op_gcd_two(tokens)


def _eval_lcm(tokens: list[str], _: list[str]) -> str:
    return _op_lcm_two(tokens)


def _eval_unique_once(tokens: list[str], _: list[str]) -> str:
    return _op_unique_once_count(tokens)


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
    {
        "key": "abs_sum_two",
        "summary": "Прочитай два целых числа и выведи сумму их модулей.",
        "input_desc": "Одна строка: `a b`.",
        "output_desc": "Одно число: `|a| + |b|`.",
        "starter": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        long a = sc.nextLong();\n        long b = sc.nextLong();\n        // TODO: выведите сумму модулей\n    }\n}\n",
        "solution": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        long a = sc.nextLong();\n        long b = sc.nextLong();\n        System.out.println(Math.abs(a) + Math.abs(b));\n    }\n}\n",
        "seeds": ["-2 3\n", "-10 -4\n", "0 0\n", "999999 -1\n"],
        "eval": _eval_abs_sum,
    },
    {
        "key": "product_two",
        "summary": "Прочитай два целых числа и выведи их произведение.",
        "input_desc": "Одна строка: `a b`.",
        "output_desc": "Одно число: `a * b`.",
        "starter": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        long a = sc.nextLong();\n        long b = sc.nextLong();\n        // TODO: выведите произведение\n    }\n}\n",
        "solution": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        long a = sc.nextLong();\n        long b = sc.nextLong();\n        System.out.println(a * b);\n    }\n}\n",
        "seeds": ["2 3\n", "-5 4\n", "0 7\n", "-9 -8\n"],
        "eval": _eval_product,
    },
    {
        "key": "min_three",
        "summary": "Прочитай три целых числа и выведи минимальное.",
        "input_desc": "Одна строка: `a b c`.",
        "output_desc": "Одно число: минимум из трёх.",
        "starter": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int a = sc.nextInt();\n        int b = sc.nextInt();\n        int c = sc.nextInt();\n        // TODO: найдите минимум\n    }\n}\n",
        "solution": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int a = sc.nextInt();\n        int b = sc.nextInt();\n        int c = sc.nextInt();\n        System.out.println(Math.min(a, Math.min(b, c)));\n    }\n}\n",
        "seeds": ["1 9 3\n", "-2 -7 -1\n", "4 4 4\n", "100 20 99\n"],
        "eval": _eval_min,
    },
    {
        "key": "middle_three",
        "summary": "Прочитай три целых числа и выведи среднее по значению (медиану).",
        "input_desc": "Одна строка: `a b c`.",
        "output_desc": "Одно число: элемент между минимумом и максимумом.",
        "starter": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int a = sc.nextInt();\n        int b = sc.nextInt();\n        int c = sc.nextInt();\n        // TODO: выведите медиану трех чисел\n    }\n}\n",
        "solution": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int a = sc.nextInt();\n        int b = sc.nextInt();\n        int c = sc.nextInt();\n        int[] arr = new int[]{a, b, c};\n        Arrays.sort(arr);\n        System.out.println(arr[1]);\n    }\n}\n",
        "seeds": ["1 9 3\n", "-2 -7 -1\n", "4 4 4\n", "100 20 99\n"],
        "eval": _eval_middle,
    },
    {
        "key": "odd_count",
        "summary": "Прочитай `n` и затем `n` чисел. Выведи количество нечётных.",
        "input_desc": "Первая строка: `n`, вторая строка: `n` целых чисел.",
        "output_desc": "Одно число: количество нечётных элементов.",
        "starter": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int count = 0;\n        for (int i = 0; i < n; i++) {\n            int x = sc.nextInt();\n            // TODO: учитывайте нечетные\n        }\n        System.out.println(count);\n    }\n}\n",
        "solution": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int count = 0;\n        for (int i = 0; i < n; i++) {\n            int x = sc.nextInt();\n            if (x % 2 != 0) count++;\n        }\n        System.out.println(count);\n    }\n}\n",
        "seeds": ["5\n1 2 3 4 5\n", "4\n2 4 6 8\n", "3\n-2 -3 -4\n", "1\n7\n"],
        "eval": _eval_odd,
    },
    {
        "key": "positive_count",
        "summary": "Прочитай `n` и затем `n` чисел. Выведи количество положительных.",
        "input_desc": "Первая строка: `n`, вторая строка: `n` целых чисел.",
        "output_desc": "Одно число: количество чисел `> 0`.",
        "starter": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int count = 0;\n        for (int i = 0; i < n; i++) {\n            int x = sc.nextInt();\n            // TODO: учитывайте положительные значения\n        }\n        System.out.println(count);\n    }\n}\n",
        "solution": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int count = 0;\n        for (int i = 0; i < n; i++) {\n            int x = sc.nextInt();\n            if (x > 0) count++;\n        }\n        System.out.println(count);\n    }\n}\n",
        "seeds": ["5\n1 0 -3 7 9\n", "4\n0 0 0 0\n", "3\n-2 -3 -4\n", "1\n7\n"],
        "eval": _eval_positive,
    },
    {
        "key": "uppercase_line",
        "summary": "Прочитай строку и выведи её в верхнем регистре.",
        "input_desc": "Одна строка текста.",
        "output_desc": "Та же строка, преобразованная в `UPPERCASE`.",
        "starter": "import java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        String s = br.readLine();\n        if (s == null) s = \"\";\n        // TODO: выведите строку в верхнем регистре\n    }\n}\n",
        "solution": "import java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        String s = br.readLine();\n        if (s == null) s = \"\";\n        System.out.println(s.toUpperCase());\n    }\n}\n",
        "seeds": ["java\n", "Metanit\n", "a b c\n", "\n"],
        "eval": _eval_upper,
    },
    {
        "key": "word_count",
        "summary": "Прочитай строку и выведи количество слов (разделитель — пробелы).",
        "input_desc": "Одна строка текста.",
        "output_desc": "Одно число: число слов в строке.",
        "starter": "import java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        String s = br.readLine();\n        if (s == null) s = \"\";\n        // TODO: выведите количество слов\n    }\n}\n",
        "solution": "import java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        String s = br.readLine();\n        if (s == null) s = \"\";\n        s = s.trim();\n        if (s.isEmpty()) {\n            System.out.println(0);\n            return;\n        }\n        System.out.println(s.split(\"\\\\s+\").length);\n    }\n}\n",
        "seeds": ["hello world\n", "one\n", "  two   spaces here  \n", "\n"],
        "eval": _eval_words,
    },
    {
        "key": "sum_to_n",
        "summary": "Прочитай `n` и выведи сумму чисел от `1` до `n`.",
        "input_desc": "Одно целое число `n`.",
        "output_desc": "Одно число: `1 + 2 + ... + n`.",
        "starter": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        long n = sc.nextLong();\n        // TODO: вычислите сумму от 1 до n\n    }\n}\n",
        "solution": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        long n = sc.nextLong();\n        System.out.println((n * (n + 1)) / 2);\n    }\n}\n",
        "seeds": ["1\n", "5\n", "10\n", "100\n"],
        "eval": _eval_sum_to_n,
    },
    {
        "key": "fibonacci_n",
        "summary": "Прочитай `n` и выведи `n`-е число Фибоначчи (`F0 = 0`, `F1 = 1`).",
        "input_desc": "Одно целое число `n` (`0 ≤ n ≤ 45`).",
        "output_desc": "Одно число: значение `Fn`.",
        "starter": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        // TODO: вычислите n-е число Фибоначчи\n    }\n}\n",
        "solution": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        if (n <= 0) {\n            System.out.println(0);\n            return;\n        }\n        if (n == 1) {\n            System.out.println(1);\n            return;\n        }\n        int a = 0;\n        int b = 1;\n        for (int i = 2; i <= n; i++) {\n            int c = a + b;\n            a = b;\n            b = c;\n        }\n        System.out.println(b);\n    }\n}\n",
        "seeds": ["0\n", "1\n", "7\n", "10\n"],
        "eval": _eval_fib,
    },
    {
        "key": "char_count",
        "summary": "Прочитай строку `text` и символ `ch`, выведи количество вхождений `ch` в `text`.",
        "input_desc": "Первая строка: `text`, вторая строка: `ch`.",
        "output_desc": "Одно число: сколько раз `ch` встречается в `text`.",
        "starter": "import java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        String text = br.readLine();\n        String rawCh = br.readLine();\n        if (text == null) text = \"\";\n        if (rawCh == null) rawCh = \"\";\n        // TODO: выведите количество вхождений символа\n    }\n}\n",
        "solution": "import java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        String text = br.readLine();\n        String rawCh = br.readLine();\n        if (text == null) text = \"\";\n        if (rawCh == null || rawCh.isEmpty()) {\n            System.out.println(0);\n            return;\n        }\n        char ch = rawCh.charAt(0);\n        int count = 0;\n        for (int i = 0; i < text.length(); i++) {\n            if (text.charAt(i) == ch) count++;\n        }\n        System.out.println(count);\n    }\n}\n",
        "seeds": ["banana\na\n", "metanit\nt\n", "abc\nd\n", "\na\n"],
        "eval": _eval_char_count,
    },
    {
        "key": "substring_overlap",
        "summary": "Прочитай `text` и `pattern` и выведи число вхождений `pattern` в `text` с учётом перекрытий.",
        "input_desc": "Первая строка: `text`, вторая строка: `pattern`.",
        "output_desc": "Одно число: количество вхождений с перекрытиями.",
        "starter": "import java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        String text = br.readLine();\n        String pattern = br.readLine();\n        if (text == null) text = \"\";\n        if (pattern == null) pattern = \"\";\n        // TODO: посчитайте вхождения с перекрытиями\n    }\n}\n",
        "solution": "import java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        String text = br.readLine();\n        String pattern = br.readLine();\n        if (text == null) text = \"\";\n        if (pattern == null || pattern.isEmpty()) {\n            System.out.println(0);\n            return;\n        }\n        int idx = 0;\n        int cnt = 0;\n        while (true) {\n            int pos = text.indexOf(pattern, idx);\n            if (pos < 0) break;\n            cnt++;\n            idx = pos + 1;\n        }\n        System.out.println(cnt);\n    }\n}\n",
        "seeds": ["aaaaa\naa\n", "abababa\naba\n", "abc\nd\n", "zzzz\nzz\n"],
        "eval": _eval_sub_overlap,
    },
    {
        "key": "digit_sum",
        "summary": "Прочитай целое число `n` и выведи сумму его цифр.",
        "input_desc": "Одно целое число `n`.",
        "output_desc": "Одно число: сумма цифр `|n|`.",
        "starter": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        // TODO: вычислите сумму цифр\n    }\n}\n",
        "solution": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = Math.abs(sc.nextInt());\n        int sum = 0;\n        while (n > 0) {\n            sum += n % 10;\n            n /= 10;\n        }\n        System.out.println(sum);\n    }\n}\n",
        "seeds": ["0\n", "123\n", "-908\n", "99999\n"],
        "eval": _eval_digit_sum,
    },
    {
        "key": "gcd_two",
        "summary": "Прочитай два целых числа и выведи их НОД.",
        "input_desc": "Одна строка: `a b`.",
        "output_desc": "Одно число: `gcd(|a|, |b|)`.",
        "starter": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int a = sc.nextInt();\n        int b = sc.nextInt();\n        // TODO: вычислите НОД\n    }\n}\n",
        "solution": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int a = Math.abs(sc.nextInt());\n        int b = Math.abs(sc.nextInt());\n        while (b != 0) {\n            int t = a % b;\n            a = b;\n            b = t;\n        }\n        System.out.println(a);\n    }\n}\n",
        "seeds": ["12 18\n", "7 5\n", "0 10\n", "-24 36\n"],
        "eval": _eval_gcd,
    },
    {
        "key": "lcm_two",
        "summary": "Прочитай два целых числа и выведи их НОК.",
        "input_desc": "Одна строка: `a b`.",
        "output_desc": "Одно число: `lcm(a, b)`.",
        "starter": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        long a = sc.nextLong();\n        long b = sc.nextLong();\n        // TODO: вычислите НОК\n    }\n}\n",
        "solution": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        long a = sc.nextLong();\n        long b = sc.nextLong();\n        if (a == 0 || b == 0) {\n            System.out.println(0);\n            return;\n        }\n        long x = Math.abs(a);\n        long y = Math.abs(b);\n        while (y != 0) {\n            long t = x % y;\n            x = y;\n            y = t;\n        }\n        System.out.println((Math.abs(a) / x) * Math.abs(b));\n    }\n}\n",
        "seeds": ["12 18\n", "7 5\n", "0 10\n", "-24 36\n"],
        "eval": _eval_lcm,
    },
    {
        "key": "unique_once_count",
        "summary": "Прочитай `n` и затем `n` чисел. Выведи, сколько значений встречается ровно один раз.",
        "input_desc": "Первая строка: `n`, вторая строка: `n` целых чисел.",
        "output_desc": "Одно число: количество элементов с частотой `1`.",
        "starter": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] arr = new int[n];\n        for (int i = 0; i < n; i++) arr[i] = sc.nextInt();\n        // TODO: посчитайте элементы, встречающиеся один раз\n    }\n}\n",
        "solution": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] arr = new int[n];\n        Map<Integer, Integer> freq = new HashMap<>();\n        for (int i = 0; i < n; i++) {\n            arr[i] = sc.nextInt();\n            freq.put(arr[i], freq.getOrDefault(arr[i], 0) + 1);\n        }\n        int ans = 0;\n        for (int value : arr) {\n            if (freq.get(value) == 1) ans++;\n        }\n        System.out.println(ans);\n    }\n}\n",
        "seeds": ["5\n1 2 2 3 3\n", "4\n7 7 7 7\n", "6\n-1 0 1 0 -1 2\n", "1\n42\n"],
        "eval": _eval_unique_once,
    },
]


def pick_practice_config(chapter: int, page: int, title: str, avoid_template_key: str = "") -> dict:
    mix = f"{chapter}:{page}:{title}".encode("utf-8")
    digest = 0
    for byte in mix:
        digest = (digest * 131 + byte) % 1_000_000_007
    idx = digest % len(PRACTICE_CONFIGS)
    if avoid_template_key and len(PRACTICE_CONFIGS) > 1 and PRACTICE_CONFIGS[idx]["key"] == avoid_template_key:
        idx = (idx + 1 + (chapter + page) % (len(PRACTICE_CONFIGS) - 1)) % len(PRACTICE_CONFIGS)
    return PRACTICE_CONFIGS[idx]


def build_practice_step(page: dict, lesson_id: str, avoid_template_key: str = "") -> dict:
    cfg = pick_practice_config(page["chapter"], page["page"], page["title"], avoid_template_key)
    public_tests, hidden_tests = _build_tests(cfg["seeds"], cfg["eval"])
    practice_context = [
        f"Применяя идею темы «{page['title']}», выполни упражнение: ",
        f"Для закрепления темы «{page['title']}» реши задачу: ",
        f"Проверь понимание темы «{page['title']}» на практике: ",
        f"Сделай короткий кодовый шаг по теме «{page['title']}»: ",
    ][(page["chapter"] * 13 + page["page"] * 7) % 4]
    body = textwrap.dedent(
        f"""
        **Коротко:** практическая задача по теме «{page['title']}».

        ### Задание
        {practice_context}{cfg['summary']}

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
        previous_practice_template = ""
        for lesson_order, page in enumerate(chapter_pages, 1):
            lesson_id = f"{module_id}_l{lesson_order:03d}_{slug(page['title'])[:60]}"
            practice_step = build_practice_step(page, lesson_id, previous_practice_template)
            if "template=" in practice_step["admin_notes"]:
                previous_practice_template = practice_step["admin_notes"].split("template=", 1)[1].strip()
            steps = [
                build_theory_step(page, lesson_id),
                build_quiz_step(page, lesson_id),
                practice_step,
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
    practice_template_counts: dict[str, int] = {}
    practice_total = 0
    practice_adjacent_repeats = 0
    for module in modules:
        seen_lesson_orders = set()
        previous_practice_template = ""
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
                    notes = str(step.get("admin_notes", ""))
                    match = re.search(r"template=([a-z0-9_\\-]+)", notes, flags=re.IGNORECASE)
                    template_key = match.group(1).lower() if match else ""
                    if not template_key:
                        errors.append(f"Practice without template key in admin notes: {sid}")
                    else:
                        practice_total += 1
                        practice_template_counts[template_key] = practice_template_counts.get(template_key, 0) + 1
                        if previous_practice_template and previous_practice_template == template_key:
                            practice_adjacent_repeats += 1
                        previous_practice_template = template_key

    if practice_total > 0:
        if len(practice_template_counts) < 12:
            errors.append(
                f"Practice diversity too low: {len(practice_template_counts)} templates for {practice_total} practice steps"
            )
        if practice_adjacent_repeats > 0:
            errors.append(f"Practice has adjacent template repeats: {practice_adjacent_repeats}")
        max_reuse = max(practice_template_counts.values()) if practice_template_counts else 0
        if practice_total >= 40 and max_reuse > 12:
            errors.append(f"Practice template reused too often: max={max_reuse}")
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
        "- practice templates are diverse and do not repeat back-to-back inside module flow",
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
