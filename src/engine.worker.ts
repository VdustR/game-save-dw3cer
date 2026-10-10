import CryptoJS from "crypto-js";
import { record, text, integer, modeValue, friendlyError } from "./protocol";
import type { Request, Response } from "./protocol";
// Narrow, checked boundary: only the WASM API this application uses is exposed.
interface PythonRuntime {
  FS: {
    mkdir(path: string): void;
    writeFile(path: string, data: string | Uint8Array): void;
    readFile(path: string): Uint8Array;
    unlink(path: string): void;
  };
  runPython(code: string): unknown;
  globals: { set(name: string, value: string | boolean): void };
}
type Loader = (options: { indexURL: string }) => Promise<unknown>;
function pythonRuntime(value: unknown): PythonRuntime {
  const p = record(value),
    fs = record(p["FS"]),
    globals = record(p["globals"]);
  if (
    typeof p["runPython"] !== "function" ||
    typeof globals["set"] !== "function" ||
    ["mkdir", "writeFile", "readFile", "unlink"].some((name) => typeof fs[name] !== "function")
  )
    throw new Error("Invalid processing runtime.");
  return value as PythonRuntime;
}
let py: PythonRuntime | undefined;
let ready: Promise<void> | undefined;
const dwAES = (hex: string, key: string, direction: string): string => {
  const data = CryptoJS.enc.Hex.parse(hex),
    k = CryptoJS.enc.Hex.parse(key);
  const options = { mode: CryptoJS.mode.ECB, padding: CryptoJS.pad.NoPadding };
  const output =
    direction === "decrypt"
      ? CryptoJS.AES.decrypt({ ciphertext: data } as CryptoJS.lib.CipherParams, k, options)
      : CryptoJS.AES.encrypt(data, k, options).ciphertext;
  return output.toString(CryptoJS.enc.Hex);
};
Object.assign(globalThis, { dwAES });
async function initialize(): Promise<void> {
  const base = new URL(import.meta.env.BASE_URL, self.location.origin);
  const runtime = new URL("runtime/", base).href;
  const loaded = record(await import(/* @vite-ignore */ runtime + "pyodide.mjs"));
  const loader = loaded["loadPyodide"];
  if (typeof loader !== "function") throw new Error("The processing runtime could not load.");
  py = pythonRuntime(await (loader as Loader)({ indexURL: runtime }));
  const runtimePython = py;
  runtimePython.FS.mkdir("/engine");
  const manifest: unknown = await (await fetch(new URL("engine-manifest.json", base))).json();
  if (!Array.isArray(manifest) || manifest.length > 40) throw new Error("Invalid engine manifest.");
  await Promise.all(
    manifest.map(async (value: unknown) => {
      const name = text(value);
      if (!/^[a-z_]+\.(py|json)$/.test(name)) throw new Error("Invalid engine module name.");
      const file = await fetch(new URL("engine/" + name, base));
      if (!file.ok) throw new Error("A processing module could not load.");
      runtimePython.FS.writeFile("/engine/" + name, new Uint8Array(await file.arrayBuffer()));
    }),
  );
  const codec = await fetch(new URL("browser_codec.py", base));
  if (!codec.ok) throw new Error("The browser codec could not load.");
  py.FS.writeFile("/engine/save_codec.py", await codec.text());
  py.runPython(
    "import sys;sys.path.insert(0,'/engine');import json,hashlib;from pathlib import Path;from preset_engine import validate,preset",
  );
}
function request(value: unknown): Request {
  const data = record(value),
    id = integer(data["id"]);
  if (data["type"] === "init") return { id, type: "init" };
  if (!(data["bytes"] instanceof ArrayBuffer)) throw new Error("Missing file contents.");
  if (data["type"] === "validate") return { id, type: "validate", bytes: data["bytes"] };
  if (data["type"] === "generate" && typeof data["mixed"] === "boolean")
    return {
      id,
      type: "generate",
      bytes: data["bytes"],
      mode: modeValue(data["mode"]),
      mixed: data["mixed"],
    };
  throw new Error("Unknown processing request.");
}
function send(message: Response, transfer: Transferable[] = []): void {
  self.postMessage(message, transfer);
}
self.onmessage = async (event: MessageEvent<unknown>): Promise<void> => {
  let id = -1;
  try {
    const data = request(event.data);
    id = data.id;
    ready ??= initialize();
    await ready;
    if (!py) throw new Error("Processing runtime unavailable.");
    if (data.type === "init") {
      send({ id, type: "ready" });
      return;
    }
    py.FS.writeFile("/input.sav", new Uint8Array(data.bytes));
    if (data.type === "validate") {
      const rawResult: unknown = py.runPython(
        "raw=Path('/input.sav').read_bytes()\nd=validate(raw)\njson.dumps({'sha256':hashlib.sha256(raw).hexdigest(),'teams':len(d.records('GuardDataArray'))})",
      );
      const summary = record(JSON.parse(text(rawResult)) as unknown);
      send({
        id,
        type: "validated",
        summary: { sourceHash: text(summary["sha256"]), teams: integer(summary["teams"]) },
      });
    } else {
      py.globals.set("selected_mode", data.mode);
      py.globals.set("selected_mixed", data.mixed);
      const result: unknown = py.runPython(
        "raw=Path('/input.sav').read_bytes()\noutput,report=preset(raw,selected_mode,selected_mixed)\nPath('/output.sav').write_bytes(output)\njson.dumps(report,ensure_ascii=False)",
      );
      const raw = text(result),
        report = record(JSON.parse(raw) as unknown);
      const bytes = py.FS.readFile("/output.sav").slice().buffer as ArrayBuffer;
      send(
        {
          id,
          type: "generated",
          bytes,
          report: {
            mode: data.mode,
            mixed: data.mixed,
            sourceHash: text(report["source_sha256"]),
            outputHash: text(report["output_sha256"]),
            teams: integer(report["guard_teams"]),
            raw,
          },
        },
        [bytes],
      );
    }
  } catch (error) {
    send({
      id,
      type: "error",
      message: friendlyError(error instanceof Error ? error.message : ""),
    });
  } finally {
    if (py) {
      for (const name of ["/input.sav", "/output.sav"]) {
        try {
          py.FS.unlink(name);
        } catch {
          /* No file was created. */
        }
      }
      py.runPython(
        "for _name in ('raw','output','d','report'):globals().pop(_name,None)\nimport gc;gc.collect()",
      );
    }
  }
};
