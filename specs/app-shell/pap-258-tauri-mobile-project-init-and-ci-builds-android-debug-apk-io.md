---
identifier: "PAP-258"
title: "Tauri mobile project init and CI builds (Android debug APK, iOS simulator app)"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Desktop and mobile shells build"
state: "Backlog"
parent: "PAP-20"
children: []
blockedBy: ["PAP-14", "PAP-255"]
blocks: ["PAP-259"]
key: "child/PAP-20/3"
url: "https://linear.app/paperos/issue/PAP-258/tauri-mobile-project-init-and-ci-builds-android-debug-apk-ios"
source: "Linear snapshot 2026-09-17T06:03Z (round-2 issue)"
---

# PAP-258: Tauri mobile project init and CI builds (Android debug APK, iOS simulator app)

**Goal**

Initialise iOS and Android targets inside the shared `src-tauri` crate, hold platform assets in `apps/mobile`, and build a debug APK and an iOS simulator app in CI so mobile work has an executable baseline.

**Scope**

In: `tauri android init` and `tauri ios init`; Gradle wrapper pinned, `minSdk 26`, `targetSdk 35`, ABIs arm64-v8a and x86_64; iOS deployment target 15.0; Info.plist usage strings; `apps/mobile` with icons, splash and scripts `dev:android`, `dev:ios`; workflow `ops/ci/mobile.yml` (Android on ubuntu, iOS on macos-14, `if`-guarded until the forge non-Linux runner issue lands); ADR recording the single-crate decision.

Out: plugins and shims (children 2 and 3), store signing.

**Spec**

* `applicationId` and bundle id from `identifier`.
* Vite dev server bound to `0.0.0.0`; scripts print LAN IP and a QR.
* CI uploads `app-debug.apk` and `PaperOS.app` as artifacts on PRs touching `apps/` or `packages/core/src/native`.
* `docs/shell/mobile.md` toolchain section (Android Studio, Xcode, simulators).

**Interface contract**

Provides: crate mobile features, artifact names, scripts. Consumes: crate (PAP-19 child 1), macOS runner capacity (forge non-Linux runner issue).

**Definition of done**

* Debug APK and simulator app build in CI; artifacts attached.
* App runs on Pixel 8 emulator and iPhone 15 simulator showing the web bundle (recording).
* ADR merged; docs toolchain section written.

**Test plan**

* CI: both builds green; `apkanalyzer` asserts ABIs and `minSdk`.
* Emulator smoke: `adb install` then `adb shell am start` and a screenshot; `xcrun simctl` install and launch on iOS.
* Visual: 375x812 and 768x1024 portrait screenshots.

**Demo**

Reviewer downloads the APK artifact, installs it on an emulator with `adb install`, launches and sees the PaperOS shell. Under 2 minutes with an emulator running.

**Edge cases**

* Gradle download blocked: wrapper cached in CI.
* No macOS runner yet: iOS job skipped with an explanatory summary line, not a failure.

**Dependencies**

PAP-19 child 1 (hard), forge non-Linux runner issue (iOS CI). Blocks children 2 and 3.

**Agent**

Built by Forge (Tauri Smith). Reviewed by Sentinel.

**Size**

M
