export type Mode = "legal" | "overlimit";
export type Request =
  | { id: number; type: "init" }
  | { id: number; type: "validate"; bytes: ArrayBuffer }
  | { id: number; type: "generate"; bytes: ArrayBuffer; mode: Mode; mixed: boolean };
export interface Summary {
  sourceHash: string;
  teams: number;
}
export interface Report {
  mode: Mode;
  mixed: boolean;
  sourceHash: string;
  outputHash: string;
  teams: number;
  raw: string;
}
export type Response =
  | { id: number; type: "ready" }
  | { id: number; type: "validated"; summary: Summary }
  | { id: number; type: "generated"; report: Report; bytes: ArrayBuffer }
  | { id: number; type: "error"; message: string };
export function record(value: unknown): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value))
    throw new Error("Invalid processing response.");
  return value as Record<string, unknown>;
}
export function text(value: unknown): string {
  if (typeof value !== "string") throw new Error("Expected text field.");
  return value;
}
export function integer(value: unknown): number {
  if (typeof value !== "number" || !Number.isSafeInteger(value))
    throw new Error("Expected integer field.");
  return value;
}
export function modeValue(value: unknown): Mode {
  if (value !== "legal" && value !== "overlimit") throw new Error("Unknown preset.");
  return value;
}
export function response(value: unknown): Response {
  const data = record(value),
    id = integer(data["id"]);
  if (data["type"] === "ready") return { id, type: "ready" };
  if (data["type"] === "error") return { id, type: "error", message: text(data["message"]) };
  if (data["type"] === "validated") {
    const s = record(data["summary"]);
    return {
      id,
      type: "validated",
      summary: { sourceHash: text(s["sourceHash"]), teams: integer(s["teams"]) },
    };
  }
  if (data["type"] === "generated") {
    const r = record(data["report"]);
    if (!(data["bytes"] instanceof ArrayBuffer) || typeof r["mixed"] !== "boolean")
      throw new Error("Invalid output payload.");
    return {
      id,
      type: "generated",
      bytes: data["bytes"],
      report: {
        mode: modeValue(r["mode"]),
        mixed: r["mixed"],
        sourceHash: text(r["sourceHash"]),
        outputHash: text(r["outputHash"]),
        teams: integer(r["teams"]),
        raw: text(r["raw"]),
      },
    };
  }
  throw new Error("Unknown processing response.");
}
export function validFile(name: string, size: number): boolean {
  return /\.sav$/i.test(name) && size > 0 && size <= 16 * 1024 * 1024 && size % 16 === 0;
}
export function friendlyError(message: string): string {
  if (/version|save class/i.test(message))
    return "This save uses an unsupported game version. Choose a supported GameStatusData.sav file.";
  if (/envelope|signature|padding|damaged|truncated|GVAS/i.test(message))
    return "This file is damaged or is not a supported DW3 Remastered save. Choose the original GameStatusData.sav file.";
  if (/reference|identity|bonus|layout|inventory|missing/i.test(message))
    return "This save contains unsupported equipment or inventory data. It was not modified.";
  if (/runtime|module|could not load/i.test(message))
    return "The local processing engine could not load. Refresh the page to retry.";
  return "Local processing failed. Your original is unchanged. Choose the file again or refresh the page.";
}
