---
identifier: "PAP-514"
title: "Mobile universal links and Android app links: `apple-app-site-association`, `assetlinks.json`, route handoff into the app, and a web smart banner for installed apps"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-257", "PAP-260"]
blocks: []
key: "r4/app-shell/mobile-universal-links"
url: "https://linear.app/paperos/issue/PAP-514/mobile-universal-links-and-android-app-links-apple-app-site"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:00.432Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-514: Mobile universal links and Android app links: `apple-app-site-association`, `assetlinks.json`, route handoff into the app, and a web smart banner for installed apps

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 (past 2026-10-01). PAP-257 registers `paperos://` on desktop; on phones the equivalent is `https://app.<domain>/...` opening the installed app. Magic-link emails (PAP-224) and shared record links must land in the app, not the browser. This issue completes the deep-link story for iOS and Android.

**Scope**

In:

* `apps/api` serves `/.well-known/apple-app-site-association` and `/.well-known/assetlinks.json` generated from `app.spec.yaml` identifier and the signing fingerprints (PAP-369), per custom domain (PAP-431).
* Tauri mobile config: associated domains entitlement (iOS) and intent filters with `autoVerify` (Android) in the PAP-258 project; `onDeepLink` (PAP-257 API) handles `https://` URLs on mobile.
* Route handoff: `/_link/<token>` for magic links opens the app when installed, else the web sign-in; the web page shows the PAP-18 install sheet or a smart banner when the app exists.

Out: store distribution (PAP-515), push (PAP-516).

**Spec**

* Association files are cached 24 h and validated in CI against Apple and Google schemas.
* A link that opens the app while signed out lands on sign-in and then the target route (PAP-225 flow).
* Unknown path in the app: falls back to the web URL in the system browser.

**Interface contract**

Provides: well-known endpoints, mobile link handling, `/_link` route; consumed by PAP-224 (magic links), PAP-225, PAP-431 (per-domain files), growth links (PAP-407 `/r/{code}`).

Consumes: mobile plugins and back handling (PAP-260), deep-link API (PAP-257), signing fingerprints (PAP-369), custom domains (PAP-431, soft).

**Definition of done**

* Recording on Android emulator and iOS simulator: tapping a magic link in Mail opens the app on the target route.
* Association files validate; smart banner shown on iOS Safari; `docs/shell/mobile.md` links section; CHANGELOG; Linear comment.

**Test plan**

* Unit: association file generation from spec and fingerprints; handoff state machine.
* E2E: Maestro: open link via `adb shell am start` and `xcrun simctl openurl`, assert route.

**Demo**

Reviewer sends themselves a magic link on the emulator, taps it in Gmail and the PaperOS app opens signed in on the portal home. Under 2 minutes.

**Edge cases**

* Custom domain not yet verified: files served only for `active` hosts.
* Debug builds with a different fingerprint: `assetlinks.json` lists both debug and release fingerprints in preview only.

**Dependencies**

Hard: PAP-260, PAP-257. Soft: PAP-369, PAP-431, PAP-224, PAP-225.

**Agent**

Builder: Forge (Tauri Smith). Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/app-shell/native-push-registration` = PAP-516, `r4/app-shell/store-distribution` = PAP-515.
