# Troubleshooting

Keep a backup and change one variable at a time. Start by comparing the component names/checksums and settings against the [baseline](../README.md#tested-baseline) and [settings reference](../configs/gamenative-settings.json).

| Symptom | Evidence / next check |
|---|---|
| Process runs but no WoW window | Verify the exact copied-syscall-fixed Proton archive. Stock Proton 10 and the inspected ordinary Proton 11 component did not provide the required implementation. |
| D3D12 appears despite config | Retain **both** `-d3d11` in launch arguments and `gxApi "D3D11"` in the correct Era `Config.wtf`. |
| Missing D3D11 DLL / wrong architecture | Select the official `2.4.1-wowfix-1` ARM64-only DXVK; do not use the default x64/gplasync component. |
| Exits when walking or turning | Confirm the actually selected driver is `Turnip-WoW-scheduler-test`. The captured earlier failure was Mesa shader compilation followed by `vkCreateGraphicsPipelines`, reproduced by keyboard movement with Kishi attached. |
| CAS initialization / missing install info | Check the transferred root, hidden `.build.info`, matching `Data`, and Era `.flavor.info`. Avoid nested or mixed-build installations. |
| No realms / version mismatch | Update Era in Battle.net and prepare/copy a matching installation. The helper does not update all CASC assets. |
| Touch buttons do nothing | Switch the GameNative overlay from mouse to sticks/gamepad mode; confirm `GamePadEnable=1` and Xbox setup. |
| ConsolePort absent | Verify direct `AddOns/<module>/<module>.toc` placement, all nine modules, addon enabled, and supported game interface. |
| ConsolePort setup lost after an exit | Complete setup and `/reload` while stationary to persist SavedVariables before movement testing. Keep account/character backups. |
| B zooms instead of backing out | Apply the final B `ACTIONBUTTON5` world binding and ConsolePort B cancel mapping; remove the accidental zoom binding. |
| Bars on login art | Check in-world rendering before adjusting the already matching 1560×720 desktop/config. |
| UI too small | Adjust UI Scale in the actual Graphics menu; no exact final scale was recorded. |
| Intermittent early exits | Reconfirm esync disabled, exact runtime/driver/DXVK, and inspect a bounded local log. Failures occurred at multiple resolutions; resolution was not isolated as the cause. |

## Distinguish a crash from cleanup

The movement failure had concrete shader/pipeline diagnostics and a WoW exit code **3**. GameNative later logged **137** while cleaning up other guest processes. That later code alone does not establish Android OOM.

The validation session ended with an intentional `/quit`, WoW exit code **0**, and normal cleanup. Its closure was initially described as a crash, then reclassified from the recorded exit evidence. See the [evidence index](../evidence/README.md).

Game-side illegal-instruction exceptions were handled during normal play as well. An isolated exception line, without its outcome, does not establish the fatal event or unsupported phone instructions.

## Capture a bounded local diagnostic

Ordinary play should use **Wine logging off / `WINEDEBUG=-all`**. A historical unbounded exception trace grew to about 1.6 GB and contributed to memory pressure during diagnosis. Do not collect full `+seh` indefinitely.

For an unresolved failure:

1. Note app, game build, selected runtime/DXVK/driver, and the exact reproduction action.
2. Use GameNative's **Get AI help → Start debug run** only if you want its local capture. In stock 1.3.0 the report compose/submission step is separate; cancel it after local collection if you do not intend to upload.
3. Prefer the stock bounded-scope debug channels (`warn+seh,+loaddll,+process,+timestamp,+pid,+tid` in the historical flow), not full `+seh` tracing.
4. End after reproducing the problem or **15 minutes**, whichever comes first. Monitor the active Wine log and stop capture if it reaches **64 MiB**. A size limit is an emergency diagnostic stop, not a normal way to close the game.
5. Save only the relevant excerpts locally. Return to ordinary **Play** and verify logging is off after diagnosis.

Optional ADB monitoring, after connecting to your own current wireless-debugging endpoint:

```sh
adb shell ls -lh /sdcard/Android/data/app.gamenative/files/wine_logs
adb shell du -k /sdcard/Android/data/app.gamenative/files/wine_logs
```

Recheck regularly during the short test; do not leave it unattended. The app may capture active logs privately and then move/compress them under external `debug_reports` after exit. If the active log cannot be monitored through shared storage, stop the test promptly or use a separately verified local size watchdog. Do not assume the external directory includes every active capture byte.

After the run, locally pull the relevant report directory if needed:

```sh
adb pull /sdcard/Android/data/app.gamenative/files/debug_reports /path/to/private-report-backup
```

Reports can include account/character names, device details, network addresses, paths, and other unrelated logcat data. Extract only the small failure signatures needed for an issue; do not attach raw reports by default. This repository's excerpts remove those identifiers.

## Rollback order

1. Restore the previous driver selection if testing another driver; keep the known working driver installed.
2. Restore the pinned Proton and ARM64 DXVK selections if experimenting with updates.
3. Restore the private config and desktop settings for a display regression.
4. Restore bindings and ConsolePort SavedVariables for a control regression, with WoW closed.

Do not replace individual `ntdll` DLLs, discard the matching game metadata, or delete GameNative's private storage as routine fixes. The copied-syscall correction needs coordinated runtime components, and clearing app data can erase the imported game.
