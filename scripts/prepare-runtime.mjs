import { copyFile, mkdir, readdir, writeFile, realpath, rm } from "node:fs/promises";
import path from "node:path";
const root = new URL("../", import.meta.url);
const engine = await realpath(new URL("public/engine/", root));
const cache = path.join(engine, "__pycache__");
if (!cache.startsWith(engine + path.sep)) throw new Error("Unexpected cache location.");
await rm(cache, { recursive: true, force: true });
await mkdir(new URL("public/runtime/", root), { recursive: true });
for (const name of [
  "pyodide.mjs",
  "pyodide.asm.mjs",
  "pyodide.asm.wasm",
  "pyodide-lock.json",
  "python_stdlib.zip",
]) {
  await copyFile(
    new URL("node_modules/pyodide/" + name, root),
    new URL("public/runtime/" + name, root),
  );
}
const files = (await readdir(new URL("public/engine/", root)))
  .filter((name) => /\.(py|json)$/.test(name))
  .sort();
await writeFile(new URL("public/engine-manifest.json", root), JSON.stringify(files));
