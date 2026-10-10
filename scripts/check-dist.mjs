import assert from "node:assert/strict";
import { readFile, readdir, stat } from "node:fs/promises";
import { join } from "node:path";

const base = process.env.PATCHER_BASE ?? "/";
const html = await readFile("dist/index.html", "utf8");
assert(html.includes(`${base}assets/`), "The HTML must use the deployment base path.");
for (const path of [
  "runtime/pyodide.mjs",
  "runtime/pyodide.asm.wasm",
  "runtime/python_stdlib.zip",
  "engine-manifest.json",
  "browser_codec.py",
  "engine/LICENSE",
]) {
  assert((await stat(join("dist", path))).size > 0, `Missing deployed asset: ${path}`);
}
const manifest = JSON.parse(await readFile("dist/engine-manifest.json", "utf8"));
assert(Array.isArray(manifest) && manifest.includes("preset_engine.py"));
for (const name of manifest) {
  assert(typeof name === "string" && /^[a-z_]+\.(py|json)$/.test(name));
  await stat(join("dist/engine", name));
}
async function inspect(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    assert(
      !/\.sav$|^\.env|^\.openai$|^\.acceptance-private$|^ACCEPTANCE_.*\.json$|^__pycache__$|\.map$/i.test(
        entry.name,
      ),
      `Private or development artifact found: ${entry.name}`,
    );
    if (entry.isDirectory()) await inspect(join(directory, entry.name));
  }
}
await inspect("dist");
console.log(`Static deployment checks passed for ${base}`);
