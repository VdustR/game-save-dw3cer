# Website review — October 11, 2026

The website is a simple local save tool with restrained game-inspired colors and typography. Character artwork is reserved for the future OG image. This review covered homepage layout and metadata, the file/preset/download flow, root documentation, release guidance, and owned code comments. Third-party engine modules were not rewritten.

## Final design

- A compact “Prepare your save” heading and the full supported game/platform name lead directly into the workbench.
- Dark green, antique gold, crimson actions, and the shared favicon/header icon provide game identity. The oversized campaign headline, framed game-title panel, corner ornaments, and duplicate hero link were removed.
- File selection and preset comparison remain the two main steps. Included changes use a native disclosure, closed initially; installation and verification guidance stay accessible below.
- Search and sharing metadata name the tool's purpose. Experimental behavior and structural-validation limits remain explicit.
- README repetition was consolidated without losing bodyguard resave evidence or effective-combat-cap limits. Comments explain asynchronous stale-result rejection and source/preset matching.

## Verification

Strict DOM/worker TypeScript checks, Oxlint, Oxfmt, all five existing tests, production build, and deployment/privacy checks passed. The production artifact was served locally at the GitHub Pages base path `/game-save-dw3cer/`, using an isolated agent-browser Chromium session.

Desktop 1440 × 1000 and mobile 360 × 800 captures were inspected together. The mobile file button ends at y=516, compared with y=762 in the earlier design. No horizontal overflow was observed. Navigation links are 48px high, the file button is 48px high, and native radios/checkboxes retain visible labels. Viewport emulation does not establish physical-device behavior.

Main text contrast is 14.81:1; muted text 9.03:1; muted text on a selected preset 6.57:1; primary button 6.57:1; primary hover 4.97:1; error text 10.13:1. The engine reaches ready state, keyboard focus is visible, and malformed-file selection hides output and keeps generation disabled.

For real save acceptance, the project's [public original release ZIP](https://github.com/VdustR/game-save-dw3cer/releases/tag/steam-build-25630985) was downloaded and its ZIP/save hashes checked against the checked-in release manifest. The fixture was kept outside the repository. Browser-generated Legal Max output matches the published Perfect reference, the downloaded backup is byte-identical to the input, and the report's source/output hashes match those files. The browser-generated Experimental Overlimit download also matches the corresponding public release reference. Changing the preset hides stale output and enables the Overlimit-only element option. Canceling a new patch removes source/output state, disables generation and presets, and restarts the engine for another file.

These are local production-build checks. They do not establish deployment of this change, in-game behavior on another build, or compatibility with every inventory layout. Historical gameplay evidence remains in [ACCEPTANCE.md](../ACCEPTANCE.md).

## Process and next asset

The Impeccable launcher engine download failed during the original design pass. Seed and detector checks remain unverified; no results were fabricated. Independent agents applied the finish-review and documentation references because the harness did not expose the packaged custom roles. The current simplification refines the established palette and controls rather than introducing another visual world. The final independent review returned `ship` for the inspected website, including valid desktop/mobile result captures; it does not establish completion of the unavailable formal gates.

The [Lu Bu and OG image brief](visual-direction.md) records references, costume details, and candidate compositions. After the website was completed and its first revision pushed, the built-in image tool generated the OG cover. The asset and executed prompt are recorded in [ogimage-generation.json](ogimage-generation.json); Open Graph and large-card metadata reference it. Character artwork stays out of the website UI.
