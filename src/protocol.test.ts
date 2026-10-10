import { describe, expect, it } from "vite-plus/test";
import { response, validFile, friendlyError } from "./protocol";
describe("Patcher boundaries", () => {
  it("turns engine tracebacks into actionable messages without implementation details", () => {
    const message = friendlyError(
      "Traceback: File /engine/save_parser.py line 235\nmodels.SaveError: Invalid save envelope, signature or padding.",
    );
    expect(message).toContain("Choose the original GameStatusData.sav");
    expect(message).not.toContain("/engine/");
    expect(message).not.toContain("Traceback");
  });
  it("rejects malformed file inputs before invoking the engine", () => {
    expect(validFile("save.sav", 16)).toBe(true);
    for (const [name, size] of [
      ["save.txt", 16],
      ["save.sav", 0],
      ["save.sav", 17],
      ["save.sav", 16 * 1024 * 1024 + 16],
    ] as const)
      expect(validFile(name, size)).toBe(false);
  });
  it("accepts only complete typed worker results", () => {
    expect(response({ id: 1, type: "ready" })).toEqual({ id: 1, type: "ready" });
    for (const data of [
      null,
      { id: "1", type: "ready" },
      { id: 1, type: "generated", bytes: "unsafe" },
      { id: 1, type: "validated", summary: { teams: 4 } },
    ])
      expect(() => response(data)).toThrow();
  });
});
