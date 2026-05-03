import { describe, expect, it } from "vitest";
import { analyzePythonStyleHints } from "./codeStyleHints";

describe("analyzePythonStyleHints", () => {
  it("detects compound assignment candidates", () => {
    const hints = analyzePythonStyleHints("a = a + 3\nb = b * 10");
    expect(hints).toEqual([
      { line: 1, message: "Лучше так: a += 3" },
      { line: 2, message: "Лучше так: b *= 10" },
    ]);
  });

  it("ignores comments and unrelated lines", () => {
    const hints = analyzePythonStyleHints("# a = a + 3\nprint('ok')\nname = input()");
    expect(hints).toEqual([]);
  });
});

