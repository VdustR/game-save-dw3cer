## Choose a save

| ZIP                | Contents                                                          |
| ------------------ | ----------------------------------------------------------------- |
| **0% Original**    | Untouched new-game save. No stage or Musou clears.                |
| **100% Perfect**   | Legal Max values and all supported unlocks. Start here.           |
| **101% Overlimit** | The same unlocks, with bonuses above normal limits. Experimental. |

Both patched saves equip all 42 officers with their own fifth weapons and five items. All four bodyguard teams receive third-tier weapons and Healing Scroll. Four-element mixing is off.

The percentages are package labels, not completion meters. The original retains content naturally granted by the installed game. Permanent Musou values are preserved; Steam achievement data and challenge scores are not edited.

## Install

1. **Close the game.**
2. **Back up the entire `SaveGames` folder.**
3. Extract **one** ZIP. Replace only `GameStatusData.sav` in:

```text
%LOCALAPPDATA%\KoeiTecmo\DW3CE_RE\Saved\SaveGames
```

Keep this game's Steam Cloud sync off while testing. Check your progress and equipment before saving. Restore your backup if anything looks wrong.

## What was tested

- **Game:** Windows Steam build **25630985**, executable **1.0.2.0**.
- **100% Perfect:** tested in-game by the project owner; no issues reported.
- **Both patched files:** repeat application, mode switching, and live-site downloads match the native reference byte for byte.
- **101% Overlimit:** uses the previously tested numeric profile. Tested in-game by the project owner on October 11, 2026; no issues reported. Displayed bonuses may exceed effective combat caps.

Each ZIP includes a short guide and `SHA256SUMS.txt`.

[Open the Patcher](https://vdustr.github.io/game-save-dw3cer/)

## Credits

- [真三国无双2复刻版强力初始存档最终版](https://bbs.3dmgame.com/thread-6706994-1-1.html) — hanjigang.
- [Universal Koei Tecmo Save Editor](https://github.com/MMexicann/Universal-Koei-Tecmo-Save-Editor) — Mexican and contributors.

Unofficial community project. Provided as is, without warranties. Keep backups. No affiliation with KOEI TECMO or Valve. Project code is MIT licensed; game saves and game assets are not relicensed.
