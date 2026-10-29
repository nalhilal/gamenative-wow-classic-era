# ConsolePort, touch sticks, and Razer Kishi V3

These instructions target **ConsolePort 3.3.12**, whose TOC declares Era interface **11509**. Use the pinned [official release](https://github.com/seblindfors/ConsolePort/releases/tag/3.3.12). WoW updates can require a newer addon; installing a different version changes the baseline and may change the command APIs.

## 1. Install all nine modules

With WoW closed, use GameNative's local mod manager for this custom game:

1. Choose the downloaded `ConsolePort-3.3.12.zip`.
2. Set a **custom destination relative to Game Directory**: `_classic_era_/Interface/AddOns`.
3. Select all archive files, choose **Copy files**, and enable the mod.
4. Verify there are nine direct child module folders:

```text
ConsolePort
ConsolePort_Bar
ConsolePort_Config
ConsolePort_Cursor
ConsolePort_Keyboard
ConsolePort_Menu
ConsolePort_Rings
ConsolePort_Target
ConsolePort_World
```

The correct path is `AddOns/ConsolePort/ConsolePort.toc`, not `AddOns/ConsolePort-3.3.12/ConsolePort/ConsolePort.toc`. Do not accept an automatic placement into `Data`. The historical install copied 608 files; use folder/TOC placement rather than assuming every later ZIP has that count.

Manual extraction into those same paths works if you can access the selected game directory. For a private imported game, use the app's mod/file manager instead of attempting `run-as` access.

## 2. Start with native gamepad input

Launch WoW and enable the addon at character selection if needed. Enter the world, complete ConsolePort's **Xbox** setup, and stay somewhere safe/out of combat.

ConsolePort enables `GamePadEnable` if necessary; the supplied config also requests it. For a local check, enter:

```text
/run print("GamePadEnable:",GetCVar("GamePadEnable"))
/run for _,id in ipairs(C_GamePad.GetAllDeviceIDs()) do print("Gamepad ID:",id) end
```

In the GameNative overlay, a button labeled **Enable Sticks** means you can switch from mouse mode into stick/gamepad mode. After switching, it reads **Enable Mouse**. The label describes the action you can take next. Verify both touch sticks before treating an unresponsive overlay as an addon problem.

Attach the Kishi V3 and verify movement/camera in the world. A Bluetooth keyboard can remain connected; keyboard movement reproduced the old graphics failure too, so attachment alone did not establish an input crash.

## 3. Make private backups

Before applying the layout, use GameNative **Export Files** to back up:

- Global `_classic_era_/WTF/Config.wtf`.
- Your account's `_classic_era_/WTF/Account/<account>/bindings-cache.wtf`, if present.
- Character `bindings-cache.wtf` files when using per-character bindings.
- Account and character `SavedVariables/ConsolePort*.lua` and their `.bak` files.

The easiest complete personal backup is the account's WTF subtree, stored privately. Preserve its relative paths yourself: exported files may be flattened or renamed to avoid collisions. Account names, realms and character names are personal; do not upload this backup to the repository or an issue.

ConsolePort's TOCs declare both account-wide and per-character variables. Copying only the global `Config.wtf` does not back up addon setup or action-bar layout.

## 4. Apply the final layout

Open [controller-commands.txt](../configs/controller-commands.txt). Run each slash-command line **one at a time, in order**, out of combat, after Xbox setup is complete. Lines beginning `#` are instructions, not commands. Do not paste the entire file into a single chat entry. Each command fits the 255-character limit.

The recipe:

1. Captures a session-only snapshot of controller bindings.
2. Sets **LT = Shift, RT = Ctrl, Alt = none**, 350 ms modifier tap window, and stick-click mouse buttons.
3. Generates the active Xbox preset, assigning only controller combinations through `SetBinding` to preserve ordinary keyboard mappings.
4. Explicitly applies the preset's `Generator.Triggers` shoulder mapping.
5. Applies the final world/UI overrides.
6. Saves native bindings through `CPAPI.SaveBindings()` and runs `/reload` to persist addon settings.

Pause two seconds after the modifier verification command before generating the preset, so ConsolePort can update its modifier index. If a command reports a Lua error, stop and check addon version, active Xbox setup, and combat state rather than continuing with a partial layout.

The earlier LB/LT left-hand layout is superseded by this trigger-modifier layout. RT is now a Ctrl modifier, not the earlier unmodified action slot 2.

| Physical control | In-world behavior | UI behavior / qualification |
|---|---|---|
| Left stick | Move | Context-dependent UI movement |
| Right stick | Camera | Context-dependent cursor/navigation |
| A / `PAD1` | Jump | Confirm / cursor left-click |
| B / `PAD2` | Action slot 5 | ConsolePort cancel/back |
| X / `PAD3` | `INTERACTTARGET` | Cursor right-click |
| Y / `PAD4` | Action slot 4 | Preset contextual action |
| LB / `PADLSHOULDER` | Action slot 2 | Supported panel/tab navigation |
| RB / `PADRSHOULDER` | Action slot 1 | Supported panel/tab navigation; custom menu switch |
| LT / `PADLTRIGGER` | Shift layer; preset tap behavior | Modifier |
| RT / `PADRTRIGGER` | Ctrl layer; preset tap behavior | Modifier |
| D-pad up / right / left / down | Action slots 10 / 11 / 9 / 12 | Contextual navigation |
| Back / `PADBACK` | Bags | Bags |
| Start / `PADFORWARD` | Game menu | Game menu |
| Left / right stick click | Mouse left / right emulation | Mouse emulation |

ConsolePort settings explicitly use `UICursorLeftClick=PAD1`, `UICursorCancel=PAD2`, `UICursorRightClick=PAD3`, `SoftTargetInteract=3`, `gameMenuEnable=true`, `gameMenuCustomSet=true`, `gameMenuAccept=PAD1`, `gameMenuReturn=PAD2`, and `gameMenuSwitch=PADRSHOULDER`.

The source mapping and live binding queries confirmed the configured values. User-operated movement and camera were demonstrated. Comprehensive manual menu navigation, every ability combination, and hostile-target attack behavior through X were **not** completed in the retained session. X is an interact binding, not a promise of universal attack behavior.

## 5. Save, verify, and recover

The final commands save native bindings and reload the UI while leaving the character logged in. Wait for the UI to return. Our original setup persisted successfully across `/reload` before reproducing movement. Closing the game during first-time addon setup can lose SavedVariables.

Check the printed bindings: A `JUMP`, B `ACTIONBUTTON5`, X `INTERACTTARGET`, LB `ACTIONBUTTON2`, RB `ACTIONBUTTON1`. Check Shift `PADLTRIGGER`, Ctrl `PADRTRIGGER`. Then manually test A/B, Start, shoulders, trigger layers, bags, interaction, both sticks, and retained keyboard controls.

For a **controller-bindings-only** undo during the same session before `/reload`, use:

```text
/run if GNControllerBackup then for k,v in pairs(GNControllerBackup) do SetBinding(k,v) end; CPAPI.SaveBindings() end
```

This does not undo CVars or addon menu settings and the snapshot disappears on `/reload` or exit. For full rollback, close WoW normally and restore the private config, bindings and SavedVariables backups to their original paths through Import Files. Avoid restoring files while the game is running, since it may write them again at exit.

## Rear paddles: unresolved

Rear-paddle zoom was not completed. Raw Kishi input advertised C/Z and extra buttons, but stock GameNative 1.3.0's normal controller mapper ignores Android BUTTON_C/Z; actual paddle events were still awaiting a user probe when the session stopped.

The [official Kishi V3 manual](https://dl.razerzone.com/master-guides/KishiV3/RazerKishiV3-en.pdf) describes hardware remapping. No rear-paddle mapping is included as verified here. In particular, mapping a paddle to B and assigning B to camera zoom recreates the conflict we repaired.
