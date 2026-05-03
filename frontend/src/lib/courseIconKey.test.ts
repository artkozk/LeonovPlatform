import { describe, expect, it } from "vitest";
import { resolveCourseIconKey } from "./courseIconKey";

describe("resolveCourseIconKey", () => {
  it("prioritizes direction/track/language over title text", () => {
    const iconKey = resolveCourseIconKey({
      direction: "frontend",
      title: "Java с нуля — Core, Spring Boot, SQL и DevOps",
      description: "Курс по backend",
    });

    expect(iconKey).toBe("frontend");
  });

  it("does not classify frontend as java when description contains JavaScript", () => {
    const iconKey = resolveCourseIconKey({
      title: "Frontend с нуля — HTML, CSS, JS, React и TypeScript",
      description: "Пятимесячный курс: web-основы, JavaScript, TypeScript, React",
    });

    expect(iconKey).toBe("frontend");
  });

  it("classifies java by explicit java/spring markers", () => {
    const iconKey = resolveCourseIconKey({
      title: "Java с нуля — Core, Spring Boot, SQL и DevOps",
      description: "Пятимесячный курс: Java Core, OOP, JDBC, Spring Boot",
    });

    expect(iconKey).toBe("java");
  });

  it("classifies go by go/golang markers", () => {
    const iconKey = resolveCourseIconKey({
      title: "Go с нуля — Backend, SQL, Concurrency и DevOps",
      description: "Пятимесячный курс: Go Core, concurrency, SQL/HTTP",
    });

    expect(iconKey).toBe("go");
  });

  it("classifies frontend by explicit language marker JavaScript", () => {
    const iconKey = resolveCourseIconKey({
      language: "javascript",
      title: "Основы веба",
      description: "Курс по frontend-разработке",
    });

    expect(iconKey).toBe("frontend");
  });
});
