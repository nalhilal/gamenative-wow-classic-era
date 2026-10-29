# Attribution and provenance

This repository documents how existing compatibility components were integrated and tested on one S24 Ultra. It does not claim authorship of Wine, Proton, DXVK, Turnip, ConsolePort, or the upstream compatibility fixes.

## GameNative

**Utkarsh Dalal and contributors**: [GameNative](https://github.com/utkarshdalal/GameNative), [tested stock release 1.3.0](https://github.com/utkarshdalal/GameNative/releases/tag/v1.3.0). GameNative provides the Android app, custom-game import, Wine container/component management, display/input integration, mod manager and local diagnostics.

Its upstream lineage includes [Pluvia](https://github.com/oxters168/Pluvia), [Winlator](https://github.com/brunodev85/winlator), [Winlator Cmod](https://github.com/coffincolors/winlator), and [leegao's Bionic Vulkan wrapper](https://github.com/leegao/bionic-vulkan-wrapper). These are acknowledged as upstream dependencies rather than code copied into this guide.

The exact official WoW DXVK entry was introduced in [GameNative PR #2132](https://github.com/utkarshdalal/GameNative/pull/2132). We use its ARM64-only `2.4.1-wowfix-1` archive, not an assumed interchangeable x64/default DXVK build.

## Reference compatibility components

**jaredgei and contributors**: [wow-forever-android](https://github.com/jaredgei/wow-forever-android), [components-v1 release](https://github.com/jaredgei/wow-forever-android/releases/tag/components-v1). Its reference documentation, pinned hashes, Proton archive and scheduler-fixed Turnip driver guided this integration.

The upstream project credits the **WoW Forever RP6 community bundle** for the original working component set. Its README at [revision 7e81372b2d1176035572e149a6b18ca6857d40cc](https://github.com/jaredgei/wow-forever-android/tree/7e81372b2d1176035572e149a6b18ca6857d40cc) identifies:

- Proton/Wine source based on [The412Banner/proton-wine at e5fa703ed7f7329e20d7ede481ab185cf8b1a8b2](https://github.com/The412Banner/proton-wine/tree/e5fa703ed7f7329e20d7ede481ab185cf8b1a8b2), with copied-syscall and NLS compatibility work.
- Reference ARM64 DXVK source at [doitsujin/dxvk 0cf05780abd7250c2cd713b7749cf32180157cf5](https://github.com/doitsujin/dxvk/tree/0cf05780abd7250c2cd713b7749cf32180157cf5).
- Mesa base [fe067b17d9](https://github.com/mirror/mesa/tree/fe067b17d9) with a scheduler change limiting barycentric waits to the current block.

Those are upstream source/build references, not a claim that each base revision alone contains every patch or reproduces the published archives. The `90624` runtime label is a local build label. We verified binary hashes and relevant syscall disassembly and tested the imported packages; we did not rebuild those complete runtimes here.

The reference DXVK WCP `dxvk-2.4.1-wow-aarch64-test.wcp` has SHA-256 `f660b5c6422b3f93cec65664f309718942e58581b5b96fa2902d55d63ce1db8a`. It is **not** the exact official GameNative DXVK archive pinned by this guide, whose hash is in our [manifest](components/manifest.json). Credit to DXVK and the community port does not establish those archives as binary-identical.

**AeroNico**: [Thor Forever](https://github.com/AeroNico/thor-forever), inspected at [4d332477b489863c7d5da686403ac92acb1ebad1](https://github.com/AeroNico/thor-forever/tree/4d332477b489863c7d5da686403ac92acb1ebad1). Its scheduler patch and source-distribution notes helped cross-check the patch concept and provenance. No Thor installer or Mesa patch file is copied into this repository. Its runtime kit targets a different integration and is not substituted for the tested GameNative packages.

## Foundational projects

- [Wine](https://www.winehq.org/) and contributors: Windows compatibility runtime.
- [Valve Proton](https://github.com/ValveSoftware/Proton) and contributors: Proton ecosystem and runtime work.
- [DXVK](https://github.com/doitsujin/dxvk), Philip Rebohle and contributors: Direct3D-to-Vulkan translation.
- [Mesa / Turnip](https://www.mesa3d.org/) and contributors: Adreno Vulkan driver and shader compiler.
- [FEX](https://github.com/FEX-Emu/FEX), [box64](https://github.com/ptitSeb/box64), [PulseAudio](https://www.freedesktop.org/wiki/Software/PulseAudio/) and contributors: components of the wider runtime/helper/audio stack. Their presence does not imply the ARM64 game's own code is translated from x86.

## Controller addon and hardware

**seblindfors and ConsolePort contributors**: [ConsolePort](https://github.com/seblindfors/ConsolePort), [release 3.3.12](https://github.com/seblindfors/ConsolePort/releases/tag/3.3.12), release commit `f79057a`. Its Xbox preset, trigger generator, UI handling and native-binding save API underpin the documented controls. The recipe calls those APIs and does not vendor the addon source or preset tables.

**Razer**: Kishi V3 hardware and [official manual](https://dl.razerzone.com/master-guides/KishiV3/RazerKishiV3-en.pdf), consulted for rear-button capabilities. Rear-paddle zoom remains unresolved in this integration.

**Samsung**: Galaxy S24 Ultra hardware. No endorsement or official device support is implied.

## Blizzard and game-file preparation

**Blizzard Entertainment** owns World of Warcraft, Battle.net, the game client/data and associated marks. Readers supply their own installations and accounts. This project distributes none of those game files.

`tools/prepare_client.py` is adapted from [tools/download_wow_arm64.py in jaredgei/wow-forever-android](https://github.com/jaredgei/wow-forever-android/blob/7e81372b2d1176035572e149a6b18ca6857d40cc/tools/download_wow_arm64.py), under that repository's GPL-3.0 license. Adaptations add explicit Era selection, isolated staging, bounded/checked parsing and retrieval, archive fallback, validation, CLI, and synthetic tests. The adapted file and modifications retain GPL-3.0-only; the full license is included.

## Device testing and guide

**[nalhilal](https://github.com/nalhilal)** supplied the device, account/game installation, user-operated login and controller checks, and requested this public guide. This repository consolidates the collaborative diagnosis and configuration work from 26–27 October 2026, with repository/helper verification on 29 October 2026.

The factual account comes from retained conversation notes, compact fault evidence, local validation reports and current artifact inspection. Private transcripts, credentials, raw account configs and full reports are not included.
