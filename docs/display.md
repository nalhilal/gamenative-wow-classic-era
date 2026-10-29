# Display, Config.wtf, and UI scale

## Back up before editing

Close WoW normally before importing a config. WoW can write its settings at exit, replacing edits made while it is running.

Use the game's **Options → Export Files** action in GameNative. Choose **Game Directory**, browse `_classic_era_/WTF`, select `Config.wtf`, and export. The usual destination is `Download/GameNative/<game name>/`. Check the result notification for the actual filename; repeated exports may receive a numbered name.

Make a distinct private backup such as `Config.before-guide.wtf` on your computer or phone. Our earlier setup used separate pre-ConsolePort and pre-wide-test backups. Do not publish your full config: it may contain account identifiers or realm preferences.

## Option A: New installation with no config to preserve

Use [configs/Config.wtf](../configs/Config.wtf). It is a minimal, sanitized starter file, not the author's full account configuration:

```text
SET gxApi "D3D11"
SET gxWindow "1"
SET gxMaximize "1"
SET gxWindowedResolution "1560x720"
SET GamePadEnable "1"
```

WoW will generate its other settings. Choose the correct region/language interactively.

## Option B: Preserve an existing config

On your computer, merge the five settings into a separate output:

```sh
python3 tools/merge_config.py --input "/path/to/exported/Config.wtf" --output "/path/to/new/Config.wtf"
```

The input/output paths must differ, and the output must not already exist. The helper preserves unrelated lines, matches setting names without case sensitivity, removes duplicate target settings, and never prints the original contents. Keep the output named `Config.wtf` for import.

The identical [fragment](../configs/Config.wtf.fragment) is available for manual merging. Replace existing values for those keys instead of appending contradictory duplicates.

## Import the single file

1. Copy the prepared `Config.wtf` to an accessible phone folder.
2. Open the game's **Options → Import Files** action.
3. Select only the prepared file.
4. Choose **Game Directory** with custom destination `_classic_era_/WTF`.
5. Enable **Replace existing files** when replacing the backed-up config and complete the copy.
6. Keep the container desktop at custom width **1560**, height **720**, and launch arguments at **`-d3d11`**.

If Import Files is not visible immediately, scroll the game's Options menu. Do not import to the prefix's Windows directory, `Data`, or `_classic_era_/WTF/Config.wtf/` as if the filename were a folder.

## Verify display in the world

The tested phone reported **3120×1440 landscape**. `1560×720` is half those dimensions and has the same **13:6** aspect ratio. It renders 21.875% more pixels than 1280×720; it is not a performance-equivalent change.

The login art still showed side bars in one successful launch. After entering the world, the user confirmed that the display filled the screen with the retained 1560×720 configuration. Judge the result in the world rather than changing resolution solely because the login art is letterboxed.

An aligned 1664×768 attempt and some 1280×720 attempts also exited. Those tests did not establish resolution as the cause of intermittent startup failures. Do not repeatedly relaunch at arbitrary resolutions before checking runtime/driver selections.

For another phone, choose dimensions matching its actual landscape aspect ratio. Such a configuration is outside this S24 Ultra validation.

## Increase readability

Open WoW's **Game Menu → Options → Graphics**, use the UI Scale control, and apply a size comfortable for the phone. The user adjusted this manually and reported better readability.

A fresh global config export on 29 October recovered `useUiScale "1"` and stored `uiScale "1.1499999761581"`, approximately **1.15**. The optional [UI-scale fragment](../configs/ui-scale.wtf.fragment) reproduces that preference with `1.15`. To use it, merge its two keys into your backed-up config with WoW closed, replacing existing values, then import the file as above. The five-setting starter and merge helper intentionally leave UI scale to your preference. The observed value is a readability preset for this phone, not a requirement for the runtime/driver fixes.

## Roll back

With WoW closed, import the private pre-edit `Config.wtf` into the same destination. Restore the previous container desktop dimensions if you changed them. Account/character bindings and addon layout have separate backups; see [controls](controls.md).
