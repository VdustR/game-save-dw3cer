import { expect, it } from "vite-plus/test";
import { readIfCurrent } from "./file-read";
it("cannot restore a canceled source when a pending read completes", async () => {
  let current = true;
  let finish: ((bytes: ArrayBuffer) => void) | undefined;
  const read = new Promise<ArrayBuffer>((resolve) => {
    finish = resolve;
  });
  const pending = readIfCurrent(read, () => current);
  current = false;
  if (!finish) throw new Error("Deferred read unavailable");
  finish(new ArrayBuffer(16));
  expect(await pending).toBeUndefined();
});
it("keeps the exact bytes of the current source", async () => {
  const bytes = new ArrayBuffer(16);
  expect(await readIfCurrent(Promise.resolve(bytes), () => true)).toBe(bytes);
});
