# Acceptance record

## Scope

Reference game: Windows Steam App 3841510, build 25630985. Windows executable file/product version: 1.0.2.0. Executable SHA-256: `ca1a65a53242a7cf42493bd2006b8c555d87597387468e4b7a07c52d4eefe92e`. Save header: Unreal Engine 5.6.1, GVAS 3, UE4 serialization 522, UE5 serialization 1017. Acceptance date: October 10, 2026. Browser UI/download checks used the Codex in-app browser on Windows; its exact browser-engine version was not recorded.

Only the custom preset composition, canonical switching, repeat application, browser compatibility bridge, UI lifecycle, and release tooling are independently accepted here. Unmodified upstream logic is reused at a recorded commit.

## Verified

- Three repeat-patch cases produce byte-identical output.
- Six cross-configuration transitions produce the same output as direct application of the target configuration.
- Legal, Overlimit, and mixed-element outputs match the native reference in the WASM/JavaScript AES stack.
- Actual browser-generated downloads for all three configurations match the native output hashes.
- Changing a preset removes the old output and download controls.
- Canceling active processing terminates the worker and removes the output. A unit regression test also fences pending file reads after cancellation.
- File input and worker response boundaries are covered by focused tests.
- Strict TypeScript 7 checks cover separate DOM and worker targets; Oxlint and Oxfmt pass.
- The deployed assets are self-hosted; file contents have no network upload path, analytics, or remote error reporting.

## Design audit method

Applied Impeccable-informed checks for product-specific hierarchy, accessibility, responsive layout, implementation integrity, and bounded visual review. The interface presents a file/configuration workbench rather than a marketing funnel, separates source and output, and makes experimental status explicit. Semantic controls, focus styles, reduced-motion behavior, minimum 44px button targets, and narrow-screen overflow are checked.

A full dual-agent Impeccable critique command was not invoked. Visual judgments are recorded separately from deterministic checks. No external skill was installed into the user's global configuration.

## Remaining gameplay verification

Canonical single-element changes, the new item-equipment preset, and optional four-element mixing need further in-game testing. Wider save-layout coverage needs additional real private fixtures; the current canonical-output claim is tied to the tested fixture.

## Privacy

Private fixture files and detailed hash results remain in ignored local acceptance artifacts. Published source contains no `.sav` files or fixture-specific reports. The page displays hashes locally and includes them only in user-requested report downloads.
