/** Cancellation must fence pending file reads as well as worker messages. */
export async function readIfCurrent(
  read: Promise<ArrayBuffer>,
  current: () => boolean,
): Promise<ArrayBuffer | undefined> {
  const bytes = await read;
  return current() ? bytes : undefined;
}
