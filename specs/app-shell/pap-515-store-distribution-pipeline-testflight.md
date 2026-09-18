---
identifier: "PAP-515"
title: "Store distribution pipeline: TestFlight and Google Play internal testing lanes with fastlane, store metadata generated from `app.spec.yaml` and screenshots reused from Gate 3"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P2"
type: "Infra"
priority: 4
surfaces: ["Customer"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-258", "PAP-369", "PAP-371"]
blocks: []
key: "r4/app-shell/store-distribution"
url: "https://linear.app/paperos/issue/PAP-515/store-distribution-pipeline-testflight-and-google-play-internal"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:00.597Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-515: Store distribution pipeline: TestFlight and Google Play internal testing lanes with fastlane, store metadata generated from `app.spec.yaml` and screenshots reused from Gate 3

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra M

**Goal**

Deferred to v0.2 (past 2026-10-01). PAP-369 signs builds and PAP-258 produces a debug APK and simulator app; nothing uploads a build where a customer can install it. This issue adds the internal-testing lanes so a generated app reaches testers without a laptop.

**Scope**

In:

* `fastlane/` in `apps/mobile` with lanes `ios_testflight` (`match` for profiles, `gym`, `pilot`) and `android_internal` (`gradle bundleRelease`, `supply` to the internal track); workflow `ops/ci/mobile-release.yml` on `mobile-v*` tags (PAP-52) using the PAP-371 macOS runner.
* Metadata generator `scripts/store/metadata.ts`: name, subtitle, description from `app.spec.yaml` and the idea sentence; screenshots picked from the Gate 3 contact sheet (PAP-248) at store sizes; privacy labels from `telemetry-events.yaml` (PAP-510) and PAP-221 categories.
* Secrets: App Store Connect API key and Play service account JSON in sops (PAP-369 layout); `verify.sh` extended with `pilot` and `supply` dry runs.

Out: public store review submission, store listing copywriting beyond generation, in-app purchases.

**Spec**

* Lanes are idempotent: an existing build number is skipped; build numbers derive from the release-please version plus CI run number.
* Internal tracks only; promotion to production is a manual Needs Justin step documented in the runbook.
* Metadata regenerated on every tag and diffed in the PR so copy changes are reviewed.

**Interface contract**

Provides: lanes, `mobile-release.yml`, metadata generator, privacy label mapping; consumed by PAP-88 (release train mobile step), PAP-369, PAP-29 (C4 mobile).

Consumes: signing keys and profiles (PAP-369), mobile project (PAP-258), macOS runner (PAP-371), tags (PAP-52), Gate 3 screenshots (PAP-248, soft), telemetry catalogue (soft).

**Definition of done**

* One TestFlight build and one Play internal build installed on a tester device from a tag run (recording); metadata diff in the PR.
* Runbook `docs/shell/store-release.md`; CHANGELOG; Linear comment.

**Test plan**

* Unit: metadata generation snapshot for the clinic fixture; build-number derivation.
* E2E: dispatch the workflow with `--dry-run` lanes on the macOS runner and assert artefacts.

**Demo**

Reviewer opens TestFlight on an iPhone, installs the latest build of the clinic app and signs in as a demo user. Under 2 minutes after processing.

**Edge cases**

* Apple processing delays: lane returns after upload, a follow-up job polls `pilot` status.
* Play first upload must be manual: runbook step with the one-time console action.
* macOS minutes cap (PAP-371): lane skipped with a summary line when within 10 percent of the cap.

**Dependencies**

Hard: PAP-369, PAP-258, PAP-371. Soft: PAP-52, PAP-248, PAP-221, PAP-510.

**Agent**

Builder: Forge (Ops Runner). Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/app-shell/client-telemetry` = PAP-510.
