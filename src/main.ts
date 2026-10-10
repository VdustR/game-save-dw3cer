import "@fontsource/fraunces/latin-400.css";
import "@fontsource/fraunces/latin-400-italic.css";
import "@fontsource/source-sans-3/latin-400.css";
import "@fontsource/source-sans-3/latin-600.css";
import "./style.css";
import { response, validFile, modeValue } from "./protocol";
import type { Request, Report } from "./protocol";
import { readIfCurrent } from "./file-read";
function element<T extends HTMLElement>(id: string, type: { new (): T }): T {
  const value = document.getElementById(id);
  if (!(value instanceof type)) throw new Error("Missing interface element: " + id);
  return value;
}
const file = element("save-file", HTMLInputElement),
  options = element("preset-options", HTMLFieldSetElement),
  mixed = element("mixed", HTMLInputElement);
const generate = element("generate", HTMLButtonElement),
  cancel = element("cancel", HTMLButtonElement),
  result = element("result", HTMLElement);
const status = element("status", HTMLElement),
  dot = element("status-dot", HTMLElement),
  summary = element("file-summary", HTMLElement);
let worker: Worker,
  serial = 0,
  pending = 0,
  busy = false,
  input: ArrayBuffer | undefined,
  output: ArrayBuffer | undefined,
  report: Report | undefined,
  sourceHash = "";
function setStatus(message: string, kind: "idle" | "busy" | "success" | "error" = "idle"): void {
  status.textContent = message;
  dot.dataset["state"] = kind;
  status.dataset["state"] = kind;
}
function invalidate(): void {
  output = undefined;
  report = undefined;
  result.hidden = true;
}
function setBusy(value: boolean): void {
  busy = value;
  file.disabled = value;
  options.disabled = value || input === undefined;
  generate.disabled = value || input === undefined;
  cancel.hidden = !value;
}
function send(message: Request): void {
  pending = message.id;
  worker.postMessage(message);
}
function selectedMode(): "legal" | "overlimit" {
  const selected = document.querySelector<HTMLInputElement>('input[name="mode"]:checked');
  return modeValue(selected?.value);
}
function save(data: BlobPart, name: string, type = "application/octet-stream"): void {
  const url = URL.createObjectURL(new Blob([data], { type })),
    link = document.createElement("a");
  link.href = url;
  link.download = name;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 15000);
}
function startWorker(): void {
  worker = new Worker(new URL("./engine.worker.ts", import.meta.url), { type: "module" });
  file.disabled = true;
  worker.onmessage = async (event: MessageEvent<unknown>): Promise<void> => {
    try {
      const message = response(event.data);
      if (message.id !== pending) return;
      if (message.type === "ready") {
        file.disabled = false;
        setStatus("Ready. Choose your save to begin.");
        return;
      }
      if (message.type === "error") {
        setBusy(false);
        input = undefined;
        options.disabled = true;
        generate.disabled = true;
        invalidate();
        summary.hidden = true;
        setStatus("Unable to process this file. " + message.message.slice(-500), "error");
        return;
      }
      if (message.type === "validated") {
        sourceHash = message.summary.sourceHash;
        setBusy(false);
        summary.hidden = false;
        element("team-count", HTMLElement).textContent = "42 / " + message.summary.teams;
        element("source-hash", HTMLElement).textContent = sourceHash;
        setStatus("File verified. Choose a preset, then patch your save.", "success");
        return;
      }
      const expectedId = pending;
      const digest = await crypto.subtle.digest("SHA-256", message.bytes);
      const actual = Array.from(new Uint8Array(digest), (byte) =>
        byte.toString(16).padStart(2, "0"),
      ).join("");
      if (expectedId !== pending) return;
      if (actual !== message.report.outputHash || message.report.sourceHash !== sourceHash)
        throw new Error("The output integrity check failed. Choose the file again.");
      output = message.bytes;
      report = message.report;
      setBusy(false);
      result.hidden = false;
      element("output-hash", HTMLElement).textContent = actual;
      element("result-description", HTMLElement).textContent =
        `${report.mode === "legal" ? "Legal Max" : "Experimental Overlimit"} · 42 officers with fifth weapons · ${report.teams} bodyguard teams with third-tier weapons${report.mixed ? " · Four-element mixing enabled" : ""}. All supported unlocks and equipped items included.`;
      setStatus("Patch complete. Output integrity verified.", "success");
      result.scrollIntoView({
        behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth",
        block: "nearest",
      });
    } catch (error) {
      setBusy(false);
      invalidate();
      generate.disabled = true;
      setStatus(
        error instanceof Error
          ? error.message
          : "Unexpected processing response. Choose the file again.",
        "error",
      );
    }
  };
  worker.onerror = (): void => {
    setBusy(false);
    invalidate();
    input = undefined;
    options.disabled = true;
    generate.disabled = true;
    setStatus("The local engine could not start. Refresh the page to retry.", "error");
  };
  send({ id: ++serial, type: "init" });
}
file.addEventListener("change", async (): Promise<void> => {
  const selected = file.files?.[0];
  if (!selected || busy) return;
  invalidate();
  input = undefined;
  summary.hidden = true;
  sourceHash = "";
  element("file-name", HTMLElement).textContent =
    selected.name + " · " + (selected.size / 1048576).toFixed(2) + " MB";
  file.value = "";
  if (!validFile(selected.name, selected.size)) {
    options.disabled = true;
    generate.disabled = true;
    setStatus("Choose a nonempty .sav file up to 16 MB with a valid AES block length.", "error");
    return;
  }
  setBusy(true);
  setStatus("Validating structure, version, and equipment references…", "busy");
  const readId = ++serial;
  pending = readId;
  try {
    const bytes = await readIfCurrent(selected.arrayBuffer(), () => pending === readId);
    if (!bytes) return;
    input = bytes;
    send({ id: readId, type: "validate", bytes: input.slice(0) });
  } catch {
    if (pending !== readId) return;
    setBusy(false);
    input = undefined;
    setStatus("The file could not be read. Choose it again.", "error");
  }
});
options.addEventListener("change", (): void => {
  invalidate();
  const legal = selectedMode() === "legal";
  mixed.disabled = legal;
  if (legal) mixed.checked = false;
  setStatus("Settings updated. Patch again to create a matching output.");
});
generate.addEventListener("click", (): void => {
  if (!input || busy) return;
  invalidate();
  setBusy(true);
  setStatus("Applying the preset and verifying the new file…", "busy");
  send({
    id: ++serial,
    type: "generate",
    mode: selectedMode(),
    mixed: mixed.checked,
    bytes: input.slice(0),
  });
});
cancel.addEventListener("click", (): void => {
  worker.terminate();
  pending = ++serial;
  input = undefined;
  sourceHash = "";
  element("file-name", HTMLElement).textContent = "A .sav file, up to 16 MB";
  invalidate();
  summary.hidden = true;
  setBusy(false);
  setStatus("Processing canceled. Your original file is unchanged.");
  startWorker();
});
element("download", HTMLButtonElement).onclick = (): void => {
  if (output) save(output, "GameStatusData.sav");
};
element("backup", HTMLButtonElement).onclick = (): void => {
  if (input) save(input, "Original_GameStatusData.sav");
};
element("report", HTMLButtonElement).onclick = (): void => {
  if (report) save(report.raw, "DW3-validation.json", "application/json");
};
startWorker();
