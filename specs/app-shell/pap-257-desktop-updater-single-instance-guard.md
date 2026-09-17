---
identifier: "PAP-257"
title: "Desktop updater, single-instance guard and paperos:// deep links"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Customer", "Developer"]
milestone: "Desktop and mobile shells build"
state: "Backlog"
parent: "PAP-19"
children: []
blockedBy: ["PAP-256"]
blocks: ["PAP-20", "PAP-21", "PAP-24"]
key: "child/PAP-19/2"
url: "https://linear.app/paperos/issue/PAP-257/desktop-updater-single-instance-guard-and-paperos-deep-links"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:12:02.402Z"
---

# PAP-257: Desktop updater, single-instance guard and paperos:// deep links

**Goal**

Make installed desktop apps update themselves from `latest.json`, refuse duplicate instances by focusing the running one, and open `paperos://` links inside the app, proven by a 0.0.1 to 0.0.2 update recording.

**Scope**

In: `tauri-plugin-updater` with pubkey in config, check on launch and every 6 h, UI via `<UpdateToast/>` and the `paperos:sw-updated` event convention from PAP-18; `tauri-plugin-single-instance` forwarding argv to the first instance; `tauri-plugin-deep-link` registering `paperos://` on all three OSes; router integration `paperos://open/<route>`.

Out: OS signing, delta updates.

**Spec**

* Updater endpoint from child 2; failure to reach it logs and retries later, never blocks launch.
* `UpdateToast` shows version and release notes summary (from `feed.json`, PAP-52) with Reload and Later.
* Single instance: second launch sends argv over the plugin channel; first instance focuses and handles any deep link in argv.
* Deep link handler in `packages/core/src/native/desktop.ts`: `onDeepLink(cb)`; router navigates to the path after `open/`; unknown hosts (`paperos://auth/*`) are dispatched to registered handlers (PAP-57 registers `auth`).
* Windows registry and macOS `Info.plist` scheme registration through the plugin; Linux `.desktop` `MimeType=x-scheme-handler/paperos`.

**Interface contract**

Provides: `onDeepLink(cb)` and `registerDeepLinkHost(host, handler)` used by PAP-57 for the auth callback; `checkForUpdate()` for a Settings button; event `paperos:update-available`. Consumes: `latest.json` (child 2), toast (PAP-18), release notes feed (PAP-52, soft).

**Definition of done**

* Install 0.0.1, publish 0.0.2, relaunch: toast appears, Reload installs and restarts on 0.0.2 (recording on Linux and macOS).
* Launching twice yields one process; `xdg-open paperos://open/settings` navigates the running app (recording).
* Vitest and Rust tests green; `docs/shell/desktop.md` release and deep-link sections written.

**Test plan**

* Rust: argv forwarding test; scheme registration presence checks per OS in CI.
* TS: Vitest for deep-link parsing (`open/`, `auth/`, malformed) and update-state reducer.
* E2E: updater proof with two test releases; single-instance test counting processes; deep link via `xdg-open` on Linux and `open` on macOS.
* Negative: updater endpoint blocked by a proxy; app launches and logs the failure.

**Demo**

Reviewer launches the installed 0.0.1 app, sees the update toast for 0.0.2, clicks Reload, and after restart runs `xdg-open paperos://open/settings` to watch the app navigate. Under 2 minutes.

**Edge cases**

* Update downloaded but user picks Later: installs on next quit.
* Deep link while window is minimised: restore and focus.
* Corrupt `latest.json` signature: update refused, logged.

**Dependencies**

Child 1 and child 2 (hard). Feeds PAP-57 auth callback.

**Agent**

Built by Forge (Tauri Smith). Reviewed by Sentinel (Security Auditor for signature verification).

**Size**

M
