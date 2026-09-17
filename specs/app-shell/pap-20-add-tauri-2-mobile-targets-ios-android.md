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
children: ["PAP-258", "PAP-259", "PAP-260"]
blockedBy: ["PAP-14", "PAP-17", "PAP-19", "PAP-257"]
blocks: ["PAP-154"]
key: "app-shell/tauri-mobile"
url: "https://linear.app/paperos/issue/PAP-20/add-tauri-2-mobile-targets-ios-android-with-platform-capability-shims"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:40:52.715Z"
model: null
effort: null
---

# PAP-20: Add Tauri 2 mobile targets (iOS, Android) with platform capability shims

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Umbrella: extend the Tauri 2 project to iOS and Android so the same web bundle runs as a native mobile app with camera, haptics, secure storage, share sheet and biometrics through one TypeScript shim that degrades gracefully on web. Three children; this issue closes when the integration test passes on both emulators.

**Scope**

Children:

1. **PAP-258** — Tauri mobile project init and CI builds (Android debug APK, iOS simulator build; needs the non-Linux runner issue in forge for iOS).
2. **PAP-259** — Capabilities shim `packages/core/src/native/capabilities.ts` with `NativeCapabilities` and `WebCapabilities`.
3. **PAP-260** — Mobile plugin wiring and device proofs (camera, haptics, biometric, secure storage, share, geolocation, notification; safe areas; back button).

Out: store submission and signing (signing issue), touch gesture system (PAP-154), push transport.

**Spec**

* Single crate: `tauri android init` and `tauri ios init` inside `apps/desktop/src-tauri`; `apps/mobile` holds platform assets and scripts (ADR records this).
* Android `minSdk 26`, `targetSdk 35`, ABIs arm64-v8a and x86_64; iOS deployment target 15.0 with Info.plist usage strings.
* Capability file `mobile.json` grants mobile plugins to the main window only.
* Viewport `viewport-fit=cover, interactive-widget=resizes-content`; `env(safe-area-inset-*)` mapped to `--safe-*` tokens.
* Dev: `pnpm dev:android`, `pnpm dev:ios` with Vite bound to `0.0.0.0`, printing LAN IP and a QR.
* Test devices per PAP-14: Pixel 8 emulator, iPhone 15 simulator, iPad 11.

**Interface contract**

Provides (from `@paperos/core/native`):

* `Capabilities` interface: `camera`, `haptics`, `biometrics`, `secureStore`, `share`, `geo`, `notify`, each `{ available: boolean; request(): Promise<Status>; status: 'granted'|'denied'|'prompt'|'unavailable' }`; hook `useCapability(name)`.
* `getTarget()` returns `'ios'|'android'` (PAP-17 type extended).
* `--safe-top|right|bottom|left` CSS variables consumed by PAP-70 layout components and PAP-154.
* CI artifacts `app-debug.apk` and `PaperOS.app` (simulator) on every PR touching `apps/`.

Consumes: PAP-19 crate and capabilities; `SecretStore` (PAP-17) for `secureStore`; `BREAKPOINTS` (PAP-14) for target sizes; hosted macOS runner from the forge runner issue for iOS builds.

**Definition of done**

* All three children Done.
* Integration test: on Android emulator and iOS simulator, navigate three routes, scan a QR code, trigger haptics, store and read a secret (recording).
* `docs/shell/mobile.md` covers toolchain, dev loop and the signing hand-off; CHANGELOG; Linear comment with CI artifact links.

**Test plan**

* Unit: Vitest for capability selection by target and every web fallback (Web Share, `navigator.vibrate`, WebAuthn, MediaDevices).
* Rust: mobile feature build under `clippy -D warnings`.
* Integration: CI builds the debug APK on ubuntu and the simulator app on macos-14.
* E2E: Maestro or Appium flow on the emulator covering the four actions above; skipped with a visible note when biometrics are unavailable.
* Visual: screenshots at 375x812, 390x844, 768x1024 portrait and landscape; safe-area check on a notch device.

**Demo**

Reviewer runs `pnpm dev:android` with a Pixel emulator open, scans the printed QR from a second device, taps "Scan" on the demo route to read it back, feels the haptic and stores a secret that survives an app restart. Under 2 minutes with the emulator warm.

**Edge cases**

* Camera denied: `status:'denied'` plus a settings deep link.
* Android back: router `history.back()`; confirm exit at root.
* Keyboard covering inputs: verify `resizes-content` on both WebViews.
* Low-memory WebView kill: route restored from `sessionStorage`.
* Simulator without biometrics: shim returns `available:false`.

**Dependencies**

PAP-19 (hard), PAP-17 (secure store), PAP-14 (target sizes), forge non-Linux runners (iOS CI). Feeds PAP-154, PAP-157, PAP-37 camera uploads.

**Agent**

Built by Forge (Tauri Smith). Reviewed by Sentinel (Security Auditor for plugin permissions).

**Size**

L as an umbrella; children are M, S, M.
