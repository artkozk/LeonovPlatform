export type CodeStyleHint = {
  line: number;
  message: string;
};

function buildCompoundAssignHint(variable: string, operator: string, rhs: string): string {
  const cleanRhs = rhs.trim();
  if (operator === "+") return `Лучше так: ${variable} += ${cleanRhs}`;
  if (operator === "-") return `Лучше так: ${variable} -= ${cleanRhs}`;
  if (operator === "*") return `Лучше так: ${variable} *= ${cleanRhs}`;
  if (operator === "/") return `Лучше так: ${variable} /= ${cleanRhs}`;
  if (operator === "//") return `Лучше так: ${variable} //= ${cleanRhs}`;
  if (operator === "%") return `Лучше так: ${variable} %= ${cleanRhs}`;
  if (operator === "**") return `Лучше так: ${variable} **= ${cleanRhs}`;
  return "Можно сократить запись через составное присваивание.";
}

export function analyzePythonStyleHints(source: string): CodeStyleHint[] {
  const lines = source.replace(/\r\n/g, "\n").replace(/\r/g, "\n").split("\n");
  const hints: CodeStyleHint[] = [];

  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;

    const match = line.match(
      /^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\1\s*(\+|-|\*|\/|\/\/|%|\*\*)\s*(.+?)\s*$/
    );
    if (!match) continue;

    const variable = match[1];
    const operator = match[2];
    const rhs = match[3];
    if (!rhs) continue;

    hints.push({
      line: i + 1,
      message: buildCompoundAssignHint(variable, operator, rhs),
    });
  }

  return hints;
}

