# Third-party notices

This is a documentation/configuration repository with small helper scripts. Referenced APKs, WCPs, drivers, addons and Blizzard files are downloaded separately and retain their own terms. Our root [LICENSE](LICENSE) covers only the material identified there.

| Material | Source / notice |
|---|---|
| Adapted `tools/prepare_client.py` | jaredgei/wow-forever-android; GPL-3.0-only. [Source provenance](ATTRIBUTION.md#blizzard-and-game-file-preparation), [full license](LICENSES/GPL-3.0.txt). |
| GameNative app | [GameNative LICENSE](https://github.com/utkarshdalal/GameNative/blob/v1.3.0/LICENSE) and its own third-party notices. No APK/helper binaries are committed here. |
| Reference runtime packages | [WoW Forever Android notices](https://github.com/jaredgei/wow-forever-android/blob/7e81372b2d1176035572e149a6b18ca6857d40cc/THIRD_PARTY_NOTICES), component release and source references in attribution. |
| Wine | [Wine licensing](https://gitlab.winehq.org/wine/wine/-/blob/master/LICENSE); retain per-file notices when adapting source. |
| Proton | [Proton license](https://github.com/ValveSoftware/Proton/blob/proton_11.0/LICENSE) and component-specific licenses; consult the selected runtime's source distribution. |
| DXVK | [Upstream license](https://github.com/doitsujin/dxvk/blob/master/LICENSE), zlib-style; inspect the particular archive/source version for its notices. |
| Mesa/Turnip | [Mesa license documentation](https://docs.mesa3d.org/license.html); individual files may carry specific notices. No Mesa patch/source file is vendored here. |
| ConsolePort | [ConsolePort repository](https://github.com/seblindfors/ConsolePort/tree/3.3.12); its own license and bundled library notices govern the addon. The guide only downloads its official ZIP. |
| Blizzard client/data | Proprietary Blizzard material, supplied by the reader from their installation/CDN metadata; no redistribution here. |

Upstream download links and checksums are provenance/integrity information. They do not grant a new license or, on their own, supply corresponding source for a redistributed binary. This repository does not mirror those binaries. If you later choose to mirror them, assess the exact component's notices and source requirements rather than treating this guide's MIT/CC licenses as permission for every referenced artifact.

No upstream logos, splash art, or unredacted gameplay screenshots are included. Product and project names identify the tested software/hardware and remain their owners' marks.
