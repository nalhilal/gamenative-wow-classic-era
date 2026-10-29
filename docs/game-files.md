# Obtain and transfer the Classic Era ARM64 client

You need your own legitimate, current Classic Era installation. This repository contains no Blizzard executable, DLL, CASC data, or credentials. Download runtime components separately through the [manifest](../components/manifest.json).

## Required layout

The game root selected/imported into GameNative should preserve this relationship:

```text
World of Warcraft/
├── .build.info
├── Data/
├── _classic_era_/
│   ├── WowClassic-arm64.exe
│   ├── Utils/                     # matching Windows ARM64 support files
│   ├── .flavor.info               # preserve the installation's existing file
│   ├── WTF/
│   │   └── Config.wtf
│   └── Interface/
│       └── AddOns/
└── ...                            # preserve the matching installation's other required files
```

Install-manifest paths are relative to the Era product folder: `Utils/BlizzardBrowser.exe` belongs at `_classic_era_/Utils/BlizzardBrowser.exe`. Do not flatten support files next to the EXE or place `Utils` beside the shared root `Data`. The helper merges `UTILS`/`Utils` directory casing into `Utils`, since Windows paths are case-insensitive but an Android transfer folder may not be.

Show hidden files when copying `.build.info` and `.flavor.info`. Keep the existing Era flavor file; do not replace it with a Forever/beta file. `Data` can be shared across installed WoW products. The game executable must match the selected Era build, even when some shared assets are identical.

## Route A: You already have a matching Windows ARM64 installation

1. In Battle.net, install/update **World of Warcraft Classic Era**, not progression Classic, Anniversary, Retail, or Forever.
2. Locate the complete installation and confirm `_classic_era_/WowClassic-arm64.exe` exists.
3. Close Battle.net before making the transfer copy so a patch cannot change files halfway through.
4. Copy the complete required layout to the phone over USB file transfer/MTP, or use your preferred file transfer method. Preserve hidden files.
5. Use GameNative's custom-game picker/import flow and select the ARM64 EXE while retaining the complete game root.

Our original game files came from a Battle.net installation in DroidDeck. That is a valid existing-file migration source, but installing DroidDeck is not a prerequisite for this guide. A Windows x64 EXE with a similar name is not the ARM64 client.

## Route B: Prepare ARM64 binaries from an existing desktop installation

This route uses the matching installation metadata from your Mac or Windows game directory to obtain that build's Windows ARM64 EXE/DLL payloads from Blizzard's CDN. It does not patch the EXE, bypass account access, or download the complete game's `Data` directory.

The helper is adapted from [jaredgei's downloader](https://github.com/jaredgei/wow-forever-android/blob/7e81372b2d1176035572e149a6b18ca6857d40cc/tools/download_wow_arm64.py). Unlike selecting the first active row, it requires exactly one active `wow_classic_era` product. This matters when Forever and Era are both active in `.build.info`.

Install Python 3.9+. Open a terminal at this repository's root. First inspect the matching payloads without writing any output:

```sh
python3 tools/prepare_client.py --install-dir "/Applications/World of Warcraft" --output "/tmp/era-arm64-staging" --dry-run
```

On Windows, an example is:

```powershell
py -3 tools/prepare_client.py --install-dir "C:\Program Files (x86)\World of Warcraft" --output "C:\Temp\era-arm64-staging" --dry-run
```

Choose a staging directory that **does not exist** and lies outside the installation. A dry-run still accesses Blizzard's build/install metadata over the network, but creates no staging directory and downloads no game EXE/DLL payloads.

Verify the reported product is `wow_classic_era` and review the build number and paths. To prepare the files, repeat the command without `--dry-run`:

```sh
python3 tools/prepare_client.py --install-dir "/Applications/World of Warcraft" --output "/tmp/era-arm64-staging"
```

The helper resolves the install/encoding manifests, finds ARM64 Windows payloads, and falls back to indexed archive byte ranges when a payload is not available as a loose CDN object. It checks manifest/content MD5 values and BLTE chunk checksums; these are Blizzard content-addressing checks, not publisher signatures. `preparation.json` records additional SHA-256 values for the staged files.

It verifies all payloads before creating the staging tree. It does not modify your installation. Unsupported/encrypted BLTE modes, ambiguous products, unsafe paths, missing ARM64 payloads and unverifiable content fail explicitly.

Then:

1. Make a separate transfer copy of the same desktop installation, including `.build.info`, `Data`, `_classic_era_` and existing flavor metadata. Keep Battle.net closed during this operation.
2. Overlay the staging directory's `_classic_era_` folder onto the same folder in that **copy**, preserving its nested `Utils` support directory.
3. Keep `preparation.json` privately as a build/hash record; the game does not need it.
4. Transfer the combined copy to the phone and continue with [installation](installation.md).

The downloaded files are the Windows ARM64 EXE/DLL entries in that build's install manifest; they supplement the matching installation, rather than replacing its data, metadata, or platform-neutral files. The helper is not a general Blizzard installer or updater.

## Validation and failure cases

The original in-world test used build **1.15.9.70003**. The desktop installation available while creating this repository is **1.15.9.70576**. The helper's separate preparation validation is recorded in [validation.md](validation.md); do not interpret it as an in-world validation of the newer build.

- **No active Era row:** install/update Era in Battle.net and point at the actual installation root.
- **Several active Era rows:** resolve the installation metadata through Battle.net; the helper does not guess.
- **No ARM64 executable:** the selected build does not expose the expected payload. Do not rename an x64 EXE.
- **CDN unavailable / old payload removed:** update through Battle.net and retry against the new matching installation. Do not edit build keys to force a mixture.
- **Missing data / CAS initialization error:** verify `Data`, `.build.info`, and the Era flavor metadata survived transfer.
- **Game patch lands after preparation:** repeat preparation from the patched installation before transfer.

## Backup boundary

Keep account-specific `WTF/Account`, login details and Wine prefixes private. You may retain them for your own migration, but do not attach them to a public issue. [File inventory](file-inventory.md) identifies the minimal public templates and the private backup locations.
