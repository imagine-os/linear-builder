---
identifier: "PAP-260"
title: "Mobile plugin wiring, safe areas and device proofs (camera, haptics, biometrics, secure storage, share)"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer", "Developer"]
milestone: "Desktop and mobile shells build"
state: "Backlog"
parent: "PAP-20"
children: []
blockedBy: ["PAP-17", "PAP-259"]
blocks: ["PAP-154"]
key: "child/PAP-20/5"
url: "https://linear.app/paperos/issue/PAP-260/mobile-plugin-wiring-safe-areas-and-device-proofs-camera-haptics"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:22:35.093Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-260: Mobile plugin wiring, safe areas and device proofs (camera, haptics, biometrics, secure storage, share)

**Goal**

Wire the Tauri mobile plugins behind the `NativeCapabilities` implementation, map safe-area insets to tokens, handle the Android back button and keyboard, and record the device proofs the parent's integration test needs.

**Scope**

In: plugins `barcode-scanner`, `haptics`, `biometric`, `secure-storage`, `share`, `geolocation`, `notification`; capability file `mobile.json`; `--safe-*` CSS variables from `env(safe-area-inset-*)`; viewport meta; back-button mapping; route restore from `sessionStorage`; demo route `/_app/native-demo`.

Out: gesture system (PAP-154), push transport.

**Spec**

* Each plugin exposed only through `NativeCapabilities`; no direct plugin imports outside `packages/core/src/native`.
* `mobile.json` grants plugins to the main window only with the minimal permission set per plugin.
* Back button: `history.back()`; at root show a confirm-exit sheet.
* Keyboard: `interactive-widget=resizes-content` verified on both WebViews.
* Demo route exercises every capability with status badges.

**Interface contract**

Provides: `NativeCapabilities` implementation, `--safe-top|right|bottom|left` tokens (PAP-70, PAP-154), demo route. Consumes: crate with mobile targets (child 1), shim (child 2), `SecretStore` (PAP-17).

**Definition of done**

* Recording on Android emulator and iOS simulator: navigate three routes, scan a QR, trigger haptics, store and read a secret, share a link.
* Safe areas verified on a notch device screenshot; back button and keyboard behaviours recorded.
* `clippy -D warnings` with mobile features; Vitest for capability wiring.

**Test plan**

* Rust: mobile feature build in CI.
* E2E: Maestro flow on the emulator for the demo route; biometrics skipped with a note when unavailable.
* Visual: 375x812, 390x844, 768x1024 portrait and landscape, light and dark.
* Permission: camera denied path shows the settings deep link.

**Demo**

Reviewer opens `/_app/native-demo` on the emulator, taps Scan to read a QR from a second screen, taps Buzz for haptics, saves a secret, kills and relaunches the app and reads it back. Under 2 minutes.

**Edge cases**

* Low-memory kill restores the route.
* Camera denied: settings deep link.
* Android 14 notification permission prompt handled.

**Dependencies**

Children 1 and 2 (hard), PAP-17. Feeds PAP-154, PAP-37.

**Agent**

Built by Forge (Tauri Smith). Reviewed by Sentinel (Security Auditor for plugin permissions).

**Size**

M
