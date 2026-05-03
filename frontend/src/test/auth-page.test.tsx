import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { AuthPage } from "../pages/AuthPage";

describe("AuthPage", () => {
  it("renders auth heading", () => {
    render(
      <MemoryRouter>
        <AuthPage />
      </MemoryRouter>
    );

    expect(screen.getByRole("heading", { name: /^Вход$/i })).toBeTruthy();
  });
});
