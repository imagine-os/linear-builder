---
identifier: "PAP-20"
title: "Add Tauri 2 mobile targets (iOS, Android) with platform capability shims"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer", "Developer"]
milestone: "Desktop and mobile shells build"
state: "Backlog"
parent: null
children: ["PAP-260", "PAP-258", "PAP-259"]
blockedBy: ["PAP-14", "PAP-17", "PAP-19", "PAP-257"]
blocks: ["PAP-154"]
key: "app-shell/tauri-mobile"
url: "https://linear.app/paperos/issue/PAP-20/add-tauri-2-mobile-targets-ios-android-with-platform-capability-shims"
source: "plan/specs/bucket-0.json (round-1 canonical spec JSON)"
---

# PAP-20: Add Tauri 2 mobile targets (iOS, Android) with platform capability shims

**Goal**

Extend the Tauri 2 project to iOS and Android so the same web bundle runs as a native mobile app with access to camera, haptics, secure storage, share sheet and biometrics through a single TypeScript shim layer that degrades gracefully on web.

**Scope**

In:
- `apps/mobile/` sharing `src-tauri` with desktop via Cargo features, or a sibling crate re-using the same commands (decide and record in ADR; default: single crate, `tauri android init` / `tauri ios init` inside `apps/desktop/src-tauri`, with `apps/mobile` holding platform assets and scripts).
- Plugins: `tauri-plugin-barcode-scanner` (camera), `tauri-plugin-haptics`, `tauri-plugin-biometric`, `tauri-plugin-secure-storage` (or stronghold) wired to `SecretStore` from `app-shell/env-config`, `tauri-plugin-share`, `tauri-plugin-geolocation`, `tauri-plugin-notification`.
- `packages/core/src/native/capabilities.ts`: `Capabilities` interface (`camera`, `haptics`, `biometrics`, `secureStore`, `share`, `geo`, `notify`) with `NativeCapabilities` and `WebCapabilities` (Web Share, `navigator.vibrate`, WebAuthn, MediaDevices) implementations selected by `getTarget()`.
- Safe-area CSS variables exported from the shell; status-bar styling; splash screen.
- CI: Android debug APK on every PR to `apps/**`; iOS simulator build on macOS runner; release signing documented (keystore, Apple certs) and executed when secrets exist.

Out: store listings, push-notification server (`collab/notifications`), offline data (`data-layer/local-first-sync`), native UI written in Swift/Kotlin.

**Spec**

- Android: `minSdk 26`, `targetSdk 35`, ABIs arm64-v8a + x86_64; Gradle wrapper pinned; `applicationId` from `identifier`.
- iOS: deployment target 15.0; Info.plist usage strings for camera, location, Face ID.
- Capability files `mobile.json` granting only the mobile plugins to the main window.
- `useCapability('camera')` returns `{ available, request(), status }`; unavailable on web returns `available:false` without throwing.
- Deep links: `paperos://` plus universal links config placeholders.
- Viewport meta `viewport-fit=cover, interactive-widget=resizes-content`; `env(safe-area-inset-*)` mapped to `--safe-*` tokens.
- Dev: `pnpm dev:android`, `pnpm dev:ios` wrapping `tauri android dev`/`tauri ios dev` with the Vite server bound to `0.0.0.0`.
- Test devices: per `app-shell/device-matrix-research` (Pixel 8 emulator, iPhone 15 simulator, iPad 11).

**Definition of done**

- Debug APK and iOS simulator build succeed in CI on the PR.
- App runs on Android emulator and iOS simulator; recording of navigating three routes, scanning a QR code, triggering haptics and storing/reading a secret.
- Vitest for capability selection and web fallbacks; Rust builds with mobile features under `clippy -D warnings`.
- Screenshots at 375x812, 390x844, 768x1024 (portrait and landscape) attached; safe areas verified on notch device.
- `docs/shell/mobile.md` covers toolchain setup (Android Studio, Xcode), signing and release; CHANGELOG entry; Linear comment with CI artifact links.

**Edge cases**

- Camera permission denied: `status:'denied'` with a settings deep-link helper.
- Android back button: map to router `history.back()`; exit on root after confirmation.
- Keyboard covering inputs: verify `resizes-content` works in WebView on both OSes.
- Low-memory WebView kill on Android restores route from `sessionStorage`.
- Simulator has no biometrics: shim returns `available:false`, tests skip.
- Localhost dev URL unreachable from device: script prints LAN IP and QR.

**Dependencies**

`app-shell/tauri-desktop` (hard), `app-shell/env-config` (secure store), `app-shell/device-matrix-research` (target sizes). Feeds `input/touch-gestures`, `input/pen`, `data-layer/file-storage` (camera uploads).

**Agent**

Built by Forge (Tauri Smith). Reviewed by Sentinel (Security Auditor for permissions, Visual Inspector for safe areas).

**Size**

L: two mobile toolchains plus seven plugin shims with web fallbacks.
