# Validation record

## Historical device validation: 26–27 October 2026

| Item | Evidence / result |
|---|---|
| Hardware/software | Galaxy S24 Ultra SM-S928B, SM8650 / Adreno 750, Android 17, stock GameNative 1.3.0 |
| Game build | Classic Era 1.15.9.70003, Windows ARM64 |
| Launch/login | Region/language dialogs, cinematic, EU login, character selection and world reached |
| Runtime | Whole `proton-11.0-90624-arm64ec.wcp` imported; copied-syscall implementation checked in actual binary |
| DXVK | Official ARM64-only `2.4.1-wowfix-1` selected |
| Display | User confirmed full-width world at 1560×720; login art could retain bars |
| Touch sticks | Both worked after switching overlay to gamepad mode |
| Old movement failure | Keyboard W with Kishi attached reproduced Mesa compile failure and Wine Vulkan pipeline assertion; WoW code 3 |
| Patched driver | Live launch path and report selected `Turnip-WoW-scheduler-test` |
| Movement after correction | Repeated keyboard W succeeded; user confirmed physical Kishi movement/camera without that crash |
| End of validation | Intentional `/quit`, WoW code 0; full validation log lacked the old fatal signatures |
| Return to normal play | `WINEDEBUG=-all`, `WINEESYNC=0`, patched driver, no active watchdog/capture |
| ConsolePort persistence | Xbox setup retained after stationary `/reload`; later final layout saved and reloaded |
| Final bindings | Live queries confirmed repair/trigger settings; broad manual menu/ability tests remained incomplete |

Sources are the retained diagnosis/conversation, compact fault files and full local reports. Public [evidence excerpts](../evidence/README.md) omit personal identifiers. No raw report was uploaded as part of the original local diagnosis.

## Repository verification: 29 October 2026

- The connected phone reported stock GameNative **1.3.0**. Existing config backups and local diagnostic exports remained present. Private app storage was protected from ordinary `run-as` access.
- The sanitized [container reference](../configs/gamenative-settings.json) preserves selected safe fields from the successful report, including inherited graphics/audio/environment settings. Its provenance is explicit; it is not presented as a fresh raw export or an import schema.
- A fresh **Export config** through stock GameNative's UI was pulled privately on 29 October. Every `tested_settings` field matched the historical successful configuration, including the full environment, runtime, driver, DXVK, display, resolution and executable/arguments. The raw export stays outside Git.
- A fresh **Export Files** of global `WTF/Config.wtf` confirmed all five starter values and the persisted stick-click/Ctrl settings. It also recovered `useUiScale=1` and stored `uiScale=1.1499999761581` (about 1.15), now documented as an optional readability fragment. The raw file remains private; no game settings were changed for these exports.
- The preparation helper selected **`wow_classic_era`** rather than the simultaneously active **`wowf`** desktop product.
- Its dry-run inspected build **1.15.9.70576** and found **12 Windows ARM64 EXE/DLL payloads**, totaling **207,264,960 decoded bytes**.
- The full preparation downloaded and verified all 12 files to a separate temporary staging directory, including packed-archive fallback after a loose CDN lookup returned 403. The source game directory was not modified.
- The prepared `WowClassic-arm64.exe` PE machine field was independently checked as **`0xaa64` (native ARM64)**. The helper now enforces this check too.
- All **five pinned component packages** were locally verified with the published SHA-256 values. The fetch workflow downloaded the APK and exact official DXVK archive and verified retained runtime/driver/addon copies; `--verify-only` passed for the complete set. The DXVK host required an explicit HTTP user-agent, which the helper supplies.
- Synthetic tests cover product ambiguity, architecture filtering, unsafe/colliding paths, install/encoding/BLTE parsing, failed content hashes, archive-range validation, isolated output, config preservation and download cleanup.
- The published controller slash commands fit the 255-character limit and execute against a Lua API stand-in that checks the final overrides, modifier/menu values, save-before-reload, and preservation of keyboard keys. This simulation does not load the real addon or validate UI navigation in the game.
- Final layout review checked the raw install-manifest paths against the existing Era product directory. The helper stages nested support files under `_classic_era_/Utils`, merging the manifest's `UTILS`/`Utils` spelling, rather than placing them at the shared installation root. A dedicated regression test covers this case.
- A second complete preparation with the corrected layout passed all 12 content checks and the ARM64 PE check; every staged file was rechecked against its recorded SHA-256 on disk.
- **23 automated tests passed** locally, including the Lua simulation. Repository checks passed for component pins, local documentation links, command lengths and public artifact boundaries.

The desktop preparation is **not** an in-world test of build 1.15.9.70576. The guide's new fresh-install sequence was reconstructed and checked against historical evidence; the working phone was not reset for an independent clean-install test.

## Reproduce repository checks

Requires Python 3.9+. Lua 5.2+ is optional locally for the command simulation; CI installs Lua 5.4.

```sh
python3 -m unittest discover -s tests -v
python3 tools/check_repository.py
python3 tools/fetch_components.py --dest downloads --verify-only
```

The first two checks use synthetic fixtures and repository files; no Battle.net account or phone is required. The last requires the five previously downloaded packages and verifies local checksums without network access.

## Manual acceptance checklist for a fresh reader

Record phone/Android/app versions, game product/build, and component hashes first. Then verify:

- [ ] Required game root/hidden metadata and ARM64 EXE present.
- [ ] Runtime, DXVK, driver, arguments, esync and renderer selections saved.
- [ ] Login → character selection → world succeeds.
- [ ] Display fit checked in world; UI scale adjusted for readability.
- [ ] All ConsolePort modules load, Xbox selected, gamepad enabled.
- [ ] Touch and physical sticks move/turn without the old pipeline failure.
- [ ] A/B/Start, bags, shoulder navigation, trigger layers and X checked manually.
- [ ] Ordinary keyboard bindings retained.
- [ ] `/reload` and clean exit preserve addon/native settings.
- [ ] Normal Play has diagnostic logging disabled.

Rear-paddle zoom, comprehensive ability/hostile-interaction checks, long-term stability, broad performance, other GPUs, later app versions and later game builds remain outside the demonstrated result until independently tested and recorded.
