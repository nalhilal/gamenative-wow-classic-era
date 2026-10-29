# Why this combination works

## Native ARM64 game, Windows compatibility layer

The tested game executable is Blizzard's Windows ARM64 `WowClassic-arm64.exe`. Its game code runs as ARM64; Wine provides Windows compatibility and DXVK translates D3D11 graphics to Vulkan. GameNative can still use x86-oriented helpers in its launch chain. Our stock-app test succeeded through the existing `winhandler.exe` chain; it did not require the standalone Forever launcher's direct-launch changes.

This distinction matters: using the Forever project's runtime components does not make Classic Era the Forever/beta product, require its launcher APK, or justify copying its `_classic_beta_` metadata.

## Startup: a copied syscall stub

The initial DroidDeck experiment used a Linux/glibc Proton Experimental ARM64 runtime. WoW created a D3D12 device, then its main thread faulted, jumped to address zero, and repeated an unwind failure without presenting a WoW window.

Disassembly of the actual runtimes showed a relevant difference in `NtProtectVirtualMemory`:

```asm
; Inspected failing runtime: literal depends on adjacent stub data
mov x8, #0x50
mov x9, x30
ldr x16, literal_after_stub
ldr x16, [x16]
blr x16
ret

; Reference runtime: dispatcher obtained from current thread's TEB
mov x8, #0x50
mov x9, x30
ldr x16, [x18, #0x2f8]
blr x16
ret
```

The reference runtime also initializes the TEB pointer to `__wine_syscall_dispatcher` on the Unix side. In the failed trace, syscall ID `0x50`, a zero dispatcher register, and the return location in the copied code matched the faulty indirect call. This supports the copy-dependent literal as the relevant compatibility fault.

The correction is coordinated across PE and Unix runtime code. Copying only `ntdll.dll` misses thread initialization and can mix incompatible runtimes. The Android/bionic archive must not be assumed interchangeable with DroidDeck's Linux/glibc Proton.

On GameNative, importing the whole checksum-verified patched runtime and selecting ARM64 DXVK reached the language/region dialog, cinematic, login, character selection and world. That is the separate empirical GameNative validation.

The reference archive advertises copied-syscall and NLS fixes. Our runtime comparison directly examined the syscall implementation; we did not independently isolate or benchmark every advertised patch.

## Movement: graphics shader compilation

With stock `Turnip v26.2.0 R4`, walking via a keyboard while Kishi remained attached produced Mesa `compile failed!` and Wine's assertion for `vkCreateGraphicsPipelines`. WoW exited with code 3.

The reference Turnip build includes a Mesa IR3 scheduler correction limiting barycentric waits to the block currently being scheduled. After selecting `Turnip-WoW-scheduler-test`, the same keyboard comparison succeeded, then the user confirmed walking and turning with Kishi. The full validation log did not repeat the fatal shader/pipeline signatures.

The driver was originally described for Adreno 740. Our S24 Ultra evidence extends this particular limited movement test to Adreno 750. It does not validate every GPU, scene, shader, or newer driver.

## Other settings and limits

- D3D11 is requested in both the game config and command line. A config-only attempt through Battle.net had still used D3D12.
- Esync was disabled to match the reference setup. A subsequent launch succeeded, but one success did not isolate esync as the cause of all intermittent startup exits.
- The in-world 1560×720 result was confirmed; login artwork could remain letterboxed.
- The public settings JSON preserves additional inherited values for comparison. They were not each independently proven necessary.
- Local debug metadata labeled the executable as 32-bit in one automatic detection field. That detector is not authoritative: the game's name, inspected runtime path and actual ARM64 executable evidence take precedence. The preparation helper also validates the main PE machine field.

## Source provenance

See [ATTRIBUTION.md](../ATTRIBUTION.md) for runtime source revisions, upstream patch/build references, and the distinction between the official GameNative DXVK archive and the separately packaged reference DXVK archive.

This is a guide for installing verified upstream component packages. It is not a claim that the complete runtime/driver binary set has been rebuilt bit-for-bit from source here, or that this repository contains every upstream build dependency and private diagnostic artifact.
