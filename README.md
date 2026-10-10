# DW3 Save Workshop

A browser-local save patcher for **Dynasty Warriors 3: Complete Edition Remastered** on Windows Steam. Choose a save, select **Legal Max** or **Experimental Overlimit**, and download a verified output, the original backup, and a report. Save contents stay in browser memory.

## What both presets include

- All supported unlocks: 42 officers, 108 known selectable stages, three side stories, 39 supported Musou clears, unique weapons, items, known collections, costumes, and bodyguard appearance/color choices.
- Every officer equipped with their own fifth weapon and five foot-combat items, avoiding duplication of the equipped weapon's rare bonus.
- Each existing bodyguard team equipped with third-tier weapons for all five families and Healing Scroll, which provides one self-heal.
- Existing rare officer weapon bonuses, weapon identities, acquisition times, and permanent officer Musou preserved.

Third-tier bodyguard weapons have five distinct definitions: Elder Sword, Crescent Blade, Tiger's Chin, Gale Bow, and Wind Crossbow. Saves may contain duplicate copies.

## Presets and predictable switching

**Legal Max** normalizes inherited overlimit values, uses exact supported values and rank counts, standardizes each weapon to its native single element or Lightning, and uses Balanced bodyguard growth `[8, 7, 7, 3, 3, 3]` within the 25-point allocation budget.

**Experimental Overlimit** uses the tested foot-combat numeric profile, +255 bodyguard weapon bonuses, and bodyguard growth `[11, 11, 11, 3, 3, 3]`. Without mixing, its element selection matches the canonical single-element rule. The optional four-element setting applies all four element bits to officer weapons, including fifth weapons. Other flags are preserved. Both presets normalize collection snapshots to their declared profile so switching modes does not depend on the previous mode.

Repeating the same preset produces byte-identical output. Switching to a target preset produces the same output as applying that target directly to the reference input. This guarantee covers the tested real private fixture; broader inventory layouts still benefit from additional user fixtures.

Permanent health stays at 250. Permanent Musou is preserved. No paid DLC ownership, Steam achievements, invented story routes, or challenge leaderboard results are fabricated.

## Verification

### Tested game version

| Evidence                                | Recorded value                                                     |
| --------------------------------------- | ------------------------------------------------------------------ |
| Edition / platform                      | Dynasty Warriors 3: Complete Edition Remastered, Windows Steam     |
| Steam App ID                            | 3841510                                                            |
| Steam build ID                          | 25630985                                                           |
| Windows executable file/product version | 1.0.2.0                                                            |
| Executable SHA-256                      | `ca1a65a53242a7cf42493bd2006b8c555d87597387468e4b7a07c52d4eefe92e` |
| Save engine header                      | Unreal Engine 5.6.1                                                |
| Serialization versions                  | GVAS 3; UE4 522; UE5 1017                                          |
| Acceptance date                         | October 10, 2026                                                   |

Game load/display/resave evidence applies to the prior Overlimit candidate on this build. Native and browser transformation tests use a real save with 42 officers and four bodyguard teams. Newly standardized elements, the new item-equipment preset, and optional four-element mixing still need separate gameplay verification. Other Steam builds, demo saves, and console editions have not been verified. The save header does not reliably identify a Steam build, so the report's tested environment is a reference snapshot, not an inferred build for every uploaded file.

Acceptance focuses on this project's composition, mode switching, idempotence, browser migration, and UI lifecycle. Unmodified upstream features are recorded as dependencies and are not independently requalified.

The native acceptance suite covers the three configurations (Legal, Overlimit, Overlimit with mixing), three repeat-patch checks, and six cross-configuration transitions. The exact WASM/JavaScript AES stack matches the native output. Actual browser file selection, patch generation, and downloads are checked against the same hashes. Private fixtures and fixture hashes are excluded from the published source and assets.

The previous Overlimit candidate was tested in-game by the user, including bodyguard resave preservation. Newly standardized elements and optional four-element mixing remain experimental pending gameplay checks. A displayed +255 value does not prove an uncapped combat effect.

Input validation checks the supported container, class, serialization versions, structure, array boundaries, and equipment references. No known native authenticity signature is available, so this cannot authenticate a save's origin or detect every structurally plausible scalar error.

## Toolchain

Resolved released versions on October 10, 2026:

| Tool       | Pinned version        |
| ---------- | --------------------- |
| mise       | 2026.10.7             |
| Node.js    | 26.11.1               |
| pnpm       | 12.10.1               |
| Vite+      | 1.1.0                 |
| TypeScript | 7.0.2                 |
| Oxlint     | 1.87.0, through Vite+ |
| Oxfmt      | 0.72.0, through Vite+ |
| Rolldown   | 1.2.12, through Vite+ |

mise owns Node.js and pnpm. Use the project-local Vite+ CLI through package scripts. TypeScript uses `strict`, unchecked-index and exact-optional checks, unused-code checks, implicit-override and return checks, side-effect import checks, and full dependency declaration checks. DOM and worker configurations are separate; `skipLibCheck` is false. The Pyodide bridge exposes a narrow, runtime-checked API instead of weakening TypeScript to accommodate unrelated runtime declarations.

```sh
mise install
mise exec -- pnpm install --frozen-lockfile
mise exec -- pnpm run check
mise exec -- pnpm run test
mise exec -- pnpm run build
mise exec -- pnpm run dev
```

For private acceptance tests, set `DW3_PRIVATE_FIXTURE` to an absolute save path outside the repository, run `python tests_acceptance.py`, and run `pnpm run acceptance:browser`. The latter exercises the same WASM/JavaScript engine under Node; actual browser UI/download evidence is recorded separately. Never commit fixtures.

## Design and release gates

The interface follows an editorial workbench direction documented in `PRODUCT.md` and `DESIGN.md`. Impeccable's product-context, craft-floor, technical-audit, and bounded-inspection principles informed the process. Accessibility, responsive behavior, processing/error states, source/output distinction, contrast, and privacy are explicit acceptance gates. This is not a claim that a full Impeccable critique command was run.

Release requires passing strict type checks, Oxlint, Oxfmt, tests, production build, browser output comparison, stale-result invalidation, cancellation, malformed-file rejection, and responsive/keyboard checks. Four-element mixing must remain labeled experimental until independently tested in-game.

All copy is standard American English except the original Chinese title of the first credit. No product release numbers are invented.

## Credits

- [真三国无双2复刻版强力初始存档最终版](https://bbs.3dmgame.com/thread-6706994-1-1.html), by **hanjigang** — original modified-save reference and author-reported gameplay findings.
- [Universal Koei Tecmo Save Editor](https://github.com/MMexicann/Universal-Koei-Tecmo-Save-Editor), by **Mexican** and contributors — MIT-licensed native parser, codec, tagged patch workflow, and rules research. Reference commit: `ef08e2ee391d1a01f701d9f751a68ab1c6cc4d00`.

## License

Project code is MIT licensed. Reused upstream code retains its MIT notice. Runtime and font dependencies retain their own licenses; see `THIRD_PARTY_NOTICES.md` and the shipped license files. The original save and game assets are not redistributed or relicensed.
