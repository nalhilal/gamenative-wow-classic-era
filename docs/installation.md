# Installation from scratch

These instructions target **stock GameNative 1.3.0 on the S24 Ultra / Adreno 750**. Later app, game, and driver releases can change behavior. Use the pinned baseline before experimenting with upgrades.

## 1. Prepare the phone and game files

You need a Snapdragon/Adreno S24 Ultra, an internet connection, your own Battle.net account and applicable WoW access, and enough free space for a complete Era installation plus GameNative's runtime and temporary transfer files. A Bluetooth keyboard makes initial login and slash commands easier. Kishi is optional until the control setup.

Measure your own `Data` and `_classic_era_` folders before transfer. `Data` may be shared with other WoW products; copying the whole desktop directory can include substantial unrelated data. Allow space for both the transfer source and GameNative's imported copy if the app copies rather than uses the source. No Era-specific storage minimum was measured in the original test.

Follow [game-file preparation](game-files.md) first. Your phone transfer must include the matching `.build.info`, `Data`, `_classic_era_` and Windows ARM64 support files. Do not transfer only the EXE. Keep an untouched desktop/source copy for rollback.

ADB is optional; ordinary USB file transfer works. On a release GameNative APK, `adb shell run-as app.gamenative` cannot read the app's private storage. Use the app's Import/Export Files UI for subsequent changes.

## 2. Download and verify the five packages

Clone/download this guide to a computer, open its folder in a terminal, and install Python 3.9+ if necessary. On Windows, substitute `py -3` for `python3`.

```sh
python3 tools/fetch_components.py --dest downloads
python3 tools/fetch_components.py --dest downloads --verify-only
```

Transfer the verified downloads to the phone's Downloads folder. For manual downloads, open each URL in [manifest.json](../components/manifest.json) and compare against [SHA256SUMS](../components/SHA256SUMS). On macOS use `shasum -a 256 FILE`; on Linux use `sha256sum FILE`; on PowerShell use `Get-FileHash FILE -Algorithm SHA256`.

A mismatch is a failed verification. Do not import the file, edit the expected hash, or replace it with an unrelated "latest" build. The helper refuses stale `.part` files; move/remove an interrupted partial and retry.

## 3. Install stock GameNative and add the game

1. Install `gamenative-v1.3.0.apk` using Android's installer. Allow installation from the file manager/browser when Android asks. This is the ordinary APK, not the legacy-XR variant.
2. Open GameNative and finish its initial setup and required runtime downloads. Store account linking is not required for adding this custom game.
3. Use **Add Game** from the library and choose the prepared local game files. Give it a recognizable name such as World of Warcraft Classic Era.
4. Select `_classic_era_/WowClassic-arm64.exe` as the executable. Preserve the full game directory and its parent relationship to `Data` and `.build.info`. If the picker copies a directory, verify the imported root still contains all three.
5. Open the game's **Options → Edit container**. Generated IDs, private paths, and drive letters differ across installations; do not reproduce this guide author's old container ID or assume a fixed `A:` drive.

## 4. Import the patched runtime and graphics components

In GameNative's main **Settings → Contents Manager**, choose **Import .wcp from device** and import:

- `proton-11.0-90624-arm64ec.wcp`
- `dxvk-2.4.1-wowfix.wcp`

The corresponding selections should be `proton-11.0-90624-arm64ec-1` and `2.4.1-wowfix-1`. DXVK may also be offered through the official online component list as **DXVK 2.4.1 wowfix (ARM64 only)**. The downloaded archive is the pinned source if online catalog offerings change.

In **Settings → Driver Manager**, choose **Import ZIP from device** and import `turnip-wow-scheduler-test.zip`. Verify it appears as **Turnip-WoW-scheduler-test**. This ZIP is a Vulkan driver; it does not belong in Contents Manager or the game's addon manager.

The Proton `90624` label is an upstream local build label, not an official Valve Proton release. Archive metadata predates our S24 Ultra validation and may still say GameNative validation pending; [our evidence](validation.md) records the subsequent result.

## 5. Configure the container

Reopen **Options → Edit container**, select the imported components, and set:

| Group | Setting | Value |
|---|---|---|
| General | Container variant | Bionic |
| General | Wine version | `proton-11.0-90624-arm64ec-1` |
| General | Screen Size → Custom | Width `1560`, height `720` |
| Launch/game | Executable | `_classic_era_/WowClassic-arm64.exe` |
| Launch/game | Exec arguments | `-d3d11` |
| Graphics | Graphics driver | Wrapper |
| Graphics | Graphics Driver Version | `Turnip-WoW-scheduler-test` |
| Graphics | Display renderer | Vulkan |
| Graphics | DX wrapper | DXVK |
| Graphics | DXVK version | `2.4.1-wowfix-1` |
| Environment | WINEESYNC | Off / `0` |
| Environment | TU_DEBUG | Retain `noconform` |
| Debug settings | Wine file logging | Off for normal play |

Save, then reopen the settings to confirm the values persisted. Set esync through the container toggle rather than leaving duplicate environment values with conflicting settings.

Additional inherited settings were present in the successful run, including all eight native CPU cores, PulseAudio, mailbox wrapper presentation, FIFO display-renderer presentation, and a 512 MB Mesa shader cache. The complete safe reference is [gamenative-settings.json](../configs/gamenative-settings.json). Different presentation fields refer to different layers; do not force them all to the same value. Raw legacy fields such as `renderer=gl` inside the DX wrapper configuration do not mean the selected display renderer was OpenGL.

No experiments established that every inherited option is necessary. Begin with the explicit table and use the reference when comparing a failure; avoid changing unrelated settings together.

## 6. Install the WoW config

With WoW closed, follow [display/config instructions](display.md) to import the supplied starter `Config.wtf` or merge the five settings into your existing file. The destination is:

```text
Game Directory/_classic_era_/WTF/Config.wtf
```

The game config requests D3D11 **and** the launch arguments contain `-d3d11`. Keep both. An earlier config-only test through Battle.net still selected D3D12.

## 7. Launch and sign in

1. Use ordinary **Play**, with diagnostic capture off.
2. Allow first-launch runtime initialization and loading. One successful run took approximately a minute to reach login; that is an observation, not a fixed timeout.
3. Select the language and region for your own account. Our test used **English (EU)** and explicitly confirmed **Europe**.
4. Enter credentials and any authenticator code on the phone. No login file or account automation is supplied.
5. Confirm character selection, then enter the world.
6. Check full-width rendering **in the game world**. Login artwork can retain side bars.

If it exits, use [troubleshooting](troubleshooting.md) before changing multiple settings. A successful D3D device initialization line alone does not establish successful rendering.

## 8. Configure and persist controls

Follow [ConsolePort and Kishi setup](controls.md). Install all nine addon modules, select Xbox, switch the touch overlay to gamepad mode, and apply the final trigger-modifier layout. Save bindings and `/reload` while stationary to persist addon setup before movement testing.

For the user's recovered readability preference, see the optional **1.15 UI-scale** preset in [display settings](display.md#increase-readability).

Confirm touch movement/camera first, then Kishi movement/camera. The patched Turnip driver matters even if the symptom appears to begin with a controller movement.

## 9. Updates and rollback

Update the game through Battle.net, then prepare/copy a matching set of game files again. Do not combine an old ARM64 executable with a new build's metadata/data. This guide's helper stages matching binaries; it is not a complete CASC updater.

Keep the working component versions available when trying upgrades. Back up the config and account WTF directory first. Change one component at a time, verify login and movement, and revert to the recorded selection if necessary. Uninstalling GameNative can remove its privately imported game data, so it is not a routine troubleshooting step.
