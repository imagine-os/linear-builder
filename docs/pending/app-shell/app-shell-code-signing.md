---
key: "gap/app-shell/code-signing"
title: "Set up desktop and mobile code signing and notarisation (Apple Developer, Windows certificate, Android keystore) with one Needs Justin credential ask"
project: "app-shell"
parent: null
phase: "P1"
type: "Infra"
priority: 2
size: null
surfaces: []
milestone: null
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/gaps-pending-0.json (agent0/gaps.py)"
linearDocument: null
status: "pending"
---

# Set up desktop and mobile code signing and notarisation (Apple Developer, Windows certificate, Android keystore) with one Needs Justin credential ask

**Goal**

Make desktop and mobile builds installable without security warnings: Apple Developer ID signing and notarisation, a Windows code-signing certificate, and an Android upload keystore, with keys in sops and signing steps in the PAP-19 and PAP-20 CI workflows. Files the single Needs Justin item for the accounts and payments so PAP-29 stops recording unsigned builds as friction.

**Scope**

In:

* Needs Justin issue listing exactly what to buy and share: Apple Developer Program membership, App Store Connect API key, Windows OV or EV certificate (or Azure Trusted Signing), Google Play upload keystore; costs and links.
* sops entries `ops/secrets/signing.enc.yaml`; CI secrets set by PAP-51.
* `desktop.yml` steps: macOS `codesign` plus `notarytool` via tauri-action env; Windows `signtool` or Trusted Signing action; Linux unchanged.
* Android release signing config; iOS provisioning profiles for TestFlight.
* Verification scripts `ops/signing/verify.sh` (`spctl`, `codesign -dv`, `signtool verify`, `apksigner verify`).

Out: store listings and review submissions, Linux package signing (deferred to `gp/app-shell/upgrade`).

**Spec**

* Signing keys never on developer laptops; CI-only; rotation runbook.
* Notarisation waits with a 20-minute timeout and staples the ticket.
* Windows builds produce a SmartScreen-clean installer after reputation warm-up; documented.
* Unsigned fallback remains available with `SIGN=0` for PRs.

**Interface contract**

Provides: secret names `APPLE_ID`, `APPLE_TEAM_ID`, `APPLE_API_KEY_*`, `WINDOWS_CERT_*`, `ANDROID_KEYSTORE_*` in the PAP-50 secrets manifest; workflow steps consumed by PAP-19 child 2 and PAP-20 child 1; `verify.sh`. Consumes: installers (PAP-19), mobile builds (PAP-20), sops (PAP-25), non-Linux runners (forge runner issue) for macOS and Windows jobs.

**Definition of done**

* Needs Justin item filed with costs and links on day one; credentials received and stored.
* macOS `.dmg` passes Gatekeeper with no warning; `spctl --assess` output attached; Windows installer shows the publisher name; Android release APK verified.
* `verify.sh` runs in CI after signing; `docs/shell/signing.md` and rotation runbook; CHANGELOG; Linear comment.

**Test plan**

* CI: signing steps run on a tag; `verify.sh` asserts signatures on all artifacts.
* Manual recorded: fresh macOS VM opens the `.dmg` without warning; Windows VM installs with publisher shown; Android device installs the release APK.
* Negative: `SIGN=0` still builds for PRs; missing secret fails with a clear message.

**Demo**

Reviewer downloads the signed `.dmg` from the release on a Mac, double-clicks it and the app opens with no Gatekeeper dialog; `codesign -dv --verbose=2 PaperOS.app` prints the team id. Under a minute.

**Edge cases**

* Apple account approval takes days: file first, proceed with unsigned builds meanwhile.
* Notarisation rejected for a hardened-runtime entitlement: documented entitlements list.
* Certificate expiry: calendar reminder in the runbook 30 days before.
* EV certificate on a hardware token: prefer Azure Trusted Signing to keep signing in CI.

**Dependencies**

PAP-19, PAP-25 (hard). Soft: PAP-20, forge non-Linux runner issue. Consumed by PAP-29, PAP-88.

**Agent**

Built by Forge (Ops Runner); Justin supplies credentials once. Reviewed by Sentinel (Security Auditor).

**Size**

M
