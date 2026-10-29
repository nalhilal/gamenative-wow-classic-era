# File and setting inventory

## Files supplied by this repository

| File/group | Purpose | Install/use | Restore |
|---|---|---|---|
| `configs/Config.wtf` | Five-setting sanitized starter | Import to Game Directory `_classic_era_/WTF/Config.wtf`, game closed | Import private previous config |
| `configs/Config.wtf.fragment` | Same keys for existing installations | Merge, rather than overwriting unrelated values | Original exported config |
| `configs/ui-scale.wtf.fragment` | Optional recovered S24 Ultra readability preference, about 1.15 | Replace its two keys in a private config copy; game closed | Original config or Graphics menu UI Scale |
| `configs/gamenative-settings.json` | Sanitized successful container reference | Read alongside Edit container; not an import format | Re-select previous settings |
| `configs/controller-commands.txt` | Recreate final Xbox/trigger/menu layout | Execute slash commands in order after ConsolePort setup | Private bindings and SavedVariables backup |
| `components/manifest.json`, `SHA256SUMS` | Pinned upstream URLs, versions, hashes | Fetch/verify on computer; no game installation changes | No installation rollback needed |
| `tools/fetch_components.py` | Standard-library verified package downloader | Python 3.9+, computer; writes only chosen download folder | Delete downloaded copies if unwanted |
| `tools/prepare_client.py` | Stage matching Era ARM64 EXE/DLL files | Python 3.9+, computer; separate output, source read-only | Original matching game copy |
| `tools/merge_config.py` | Merge five settings without printing personal entries | Computer; separate input/output files | Input remains original backup |
| `tools/check_repository.py`, `tests/` | Validate repo/helpers | Computer; no phone or account needed | No game changes |
| `docs/`, `evidence/`, license/attribution files | Guide, bounded excerpts, provenance | Read only | No game changes |

The starter config and reference JSON are deliberately reconstructed/sanitized artifacts, not the author's full exported account files. Credentials, account/character identifiers and bindings cache files are excluded. The optional UI-scale fragment contains only the recovered nonpersonal readability settings.

## Third-party files the reader obtains

| Component | Source and destination | Change | Backup / verification |
|---|---|---|---|
| Stock GameNative APK | Official release → Android installer | Installs `app.gamenative` | Pin APK hash; do not uninstall to roll back casually because app data may be lost |
| Patched Proton WCP | Reference components-v1 → Contents Manager | Installs complete runtime; select `proton-11.0-90624-arm64ec-1` | Keep older runtime available; match archive SHA-256 |
| Official WoW DXVK WCP | GameNative downloads → Contents Manager | Select ARM64 `2.4.1-wowfix-1` | Keep previous component available; match exact archive hash |
| Turnip driver ZIP | Reference components-v1 → Driver Manager | Select Wrapper driver `Turnip-WoW-scheduler-test` | Old `Turnip v26.2.0 R4` remained installed during testing; reselect if needed |
| ConsolePort ZIP | Official 3.3.12 release → mod manager | Installs nine folders under Era `Interface/AddOns` | Backup existing addons; verify TOC placement and interface 11509 |
| Blizzard game files | Reader's installation + matching official CDN payloads | Imports matching Era client/data/metadata | Keep untouched complete source copy and preparation hash report |

No GameNative APK source file, Blizzard executable, runtime DLL, registry file, or driver source file was edited to achieve the final GameNative result. Whole upstream components were selected/imported. Source code was inspected for diagnosis, not installed as a local app patch.

## Settings and private generated files

| Location | What changes | Persistence / recovery |
|---|---|---|
| GameNative container settings | Runtime, DXVK, Wrapper driver, display renderer, desktop, launch args, esync | Save in app; private raw Export config can help your own rollback |
| `_classic_era_/WTF/Config.wtf` | D3D11, window/maximize, resolution, gamepad; game also writes other CVars | Back up/export before import; close game before restore |
| Account `bindings-cache.wtf` or character equivalent | Native PAD bindings via `SetBinding` and `CPAPI.SaveBindings` | Save active binding set; keep private file backup |
| Account `SavedVariables/ConsolePort*.lua` | Device, cursor, menu and shared addon preferences | `/reload` or clean exit writes state |
| Character `SavedVariables/ConsolePort*.lua` | Character layout, utility rings, bar/target settings as declared by each TOC | Back up the correct character subtree and `.bak` companions |
| GameNative overlay/controller profile | Mouse/sticks mode and detected controller | Verify sticks enabled and Xbox device selected |

Account-wide variables include ConsolePortSettings, ConsolePortDevices, ConsolePortShared and ConsolePortBindingIcons; per-character variables include ConsolePortCharacterSettings and ConsolePortUtility. Other modules declare additional variables. Back up all relevant module files, not just those four names.

Our final trigger layout uses LT/RT modifiers. Earlier LB/LT modifiers, B camera zoom, and an unpatched Turnip driver are historical states rather than the target configuration.

## Excluded artifacts

Game binaries/data, runtime archives, full Wine prefixes, accounts, login files, complete logcat/Wine reports, raw device exports, network endpoints, device serials and unredacted screenshots stay outside Git. Runtime packages download into ignored `downloads/`; private work belongs outside the checkout or under ignored `private/`. Scan staged files before publishing, even with these ignore rules.
