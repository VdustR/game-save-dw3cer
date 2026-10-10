// Runs the exact browser Python codec/preset stack under the same WASM runtime.
// Real browser UI/download evidence is collected separately.
import { loadPyodide } from "pyodide";
import CryptoJS from "crypto-js";
import { readFile, readdir, writeFile } from "node:fs/promises";
globalThis.dwAES = (hex, key, direction) => {
  const data = CryptoJS.enc.Hex.parse(hex),
    k = CryptoJS.enc.Hex.parse(key);
  const options = { mode: CryptoJS.mode.ECB, padding: CryptoJS.pad.NoPadding };
  return (
    direction === "decrypt"
      ? CryptoJS.AES.decrypt({ ciphertext: data }, k, options)
      : CryptoJS.AES.encrypt(data, k, options).ciphertext
  ).toString(CryptoJS.enc.Hex);
};
const py = await loadPyodide();
py.FS.mkdir("/engine");
for (const name of (await readdir("public/engine")).filter((n) => /\.(py|json)$/.test(n))) {
  py.FS.writeFile("/engine/" + name, new Uint8Array(await readFile("public/engine/" + name)));
}
py.FS.writeFile("/engine/save_codec.py", await readFile("public/browser_codec.py", "utf8"));
py.runPython(
  "import sys;sys.path.insert(0,'/engine');from preset_engine import preset;from pathlib import Path;import json,hashlib",
);
const input = await readFile(process.env.DW3_PRIVATE_FIXTURE);
py.FS.writeFile("/input.sav", input);
const expected = JSON.parse(await readFile("ACCEPTANCE_NATIVE.json", "utf8"));
const results = {};
for (const [name, mode, mixed] of [
  ["legal", "legal", false],
  ["overlimit", "overlimit", false],
  ["mixed", "overlimit", true],
]) {
  py.globals.set("mode", mode);
  py.globals.set("mixed", mixed);
  const hash = py.runPython(
    "raw=Path('/input.sav').read_bytes()\noutput,report=preset(raw,mode,mixed)\nhashlib.sha256(output).hexdigest()",
  );
  if (hash !== expected.results[name].sha256)
    throw Error("Browser runtime output differs: " + name);
  results[name] = { sha256: hash, byte_identity_with_native: true };
  console.log(name, "WASM/JavaScript AES parity passed");
  py.runPython("del raw,output,report;import gc;gc.collect()");
}
await writeFile(
  "ACCEPTANCE_BROWSER.json",
  JSON.stringify({ real_browser_ui: "pending", wasm_engine: results }, null, 2),
);
