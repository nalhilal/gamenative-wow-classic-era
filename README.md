# WoW Classic Era on GameNative — Galaxy S24 Ultra

A reproducible guide to the **stock GameNative 1.3.0** setup that reached the EU Classic Era game world on a **Galaxy S24 Ultra / Adreno 750**, with ConsolePort and a **Razer Kishi V3**.

Two components were crucial: a Wine runtime with the ARM64 copied-syscall fix, and a Turnip driver with the shader scheduler fix. An ordinary Proton 11 label or a newer-looking driver is not enough to identify either fix.

**Start here: [step-by-step installation](docs/installation.md).** It covers game-file preparation, verified downloads, importing components, first launch, display, and controls. No custom APK build is required.

## What was demonstrated

On 26–27 October 2026, Classic Era **1.15.9.70003** reached login, character selection, and the game world. Full-width in-world rendering and touch sticks were confirmed. After installing the patched driver, keyboard movement and user-operated Kishi movement worked without the previously captured pipeline crash. This was limited play validation, not a long-term stability or cross-device guarantee.

The desktop ARM64 preparation helper was also exercised against the separate **1.15.9.70576** installation during repository preparation. See [validation](docs/validation.md) for the exact result and limitations; preparation is distinct from an in-game test of that newer build.

## Tested baseline

| Setting | Value |
|---|---|
| Device / OS | Galaxy S24 Ultra SM-S928B, Adreno 750, Android 17 |
| Application | [GameNative 1.3.0](https://github.com/utkarshdalal/GameNative/releases/tag/v1.3.0), `app.gamenative` |
| Container | Bionic |
| Wine selection | `proton-11.0-90624-arm64ec-1` |
| Game | `_classic_era_/WowClassic-arm64.exe` |
| Arguments | `-d3d11` |
| Graphics | Wrapper → `Turnip-WoW-scheduler-test`; Vulkan display renderer |
| DXVK | `2.4.1-wowfix-1` **ARM64 only** |
| Desktop | Custom `1560×720` |
| Environment | `WINEESYNC=0`, `TU_DEBUG=noconform`; normal launch `WINEDEBUG=-all` |
| Addon / controller | ConsolePort 3.3.12 / Razer Kishi V3 |
| Tested account region | Europe; English (EU) |

The [sanitized settings reference](configs/gamenative-settings.json) retains additional inherited settings from the successful report. It is **not an importable container configuration**. The [file inventory](docs/file-inventory.md) explains every supplied file and every installation change.

## Download verified components

Clone this repository, open a terminal in it, and run Python **3.9 or newer** (`py -3` can replace `python3` on Windows):

```sh
python3 tools/fetch_components.py --dest downloads
python3 tools/fetch_components.py --dest downloads --verify-only
```

The helper retrieves the pinned APK, Proton, DXVK, Turnip and ConsolePort archives from their credited upstream hosts. It checks SHA-256 before finalizing each file. [Manifest and download links](components/manifest.json) · [checksums](components/SHA256SUMS).

You provide your own up-to-date Classic Era installation and Battle.net account with the required game access. Blizzard game files, accounts, login details and personal Wine prefixes are not distributed here. Installable components remain upstream downloads rather than files committed to this repository.

## Guide index

- [Installation from a fresh GameNative setup](docs/installation.md)
- [Acquire and transfer the matching ARM64 game files](docs/game-files.md)
- [Display, config merging, and UI scale](docs/display.md)
- [ConsolePort, Kishi layout, save/restore, and command recipe](docs/controls.md)
- [Troubleshooting and bounded local diagnostics](docs/troubleshooting.md)
- [Why the runtime and driver fixes matter](docs/technical-background.md)
- [Validation history and outstanding checks](docs/validation.md)
- [All modified files, settings, and rollback destinations](docs/file-inventory.md)

## Credits

This setup depends on **Utkarsh Dalal and GameNative contributors**, **jaredgei's WoW Forever Android project and the RP6 community runtime work**, **Wine/Proton**, **DXVK**, **Mesa/Turnip**, **seblindfors and ConsolePort contributors**, and **Blizzard Entertainment**. Device testing and this integration guide are by **[nalhilal](https://github.com/nalhilal)**.

See [attribution and exact source references](ATTRIBUTION.md) and [third-party notices](THIRD_PARTY_NOTICES.md). The compatibility fixes are credited to their upstream sources; this repository documents their integration on the tested phone. Unofficial community guide; no affiliation with Blizzard, Samsung, Razer, or the upstream projects is implied.

## Repository checks

```sh
python3 -m unittest discover -s tests -v
python3 tools/check_repository.py
```

Original guide text is CC BY 4.0, original helpers MIT, and the adapted client-preparation helper GPL-3.0-only. See [license scope](LICENSE).
