---
identifier: "PAP-29"
title: "Run the blank-screen-to-running-app drill: time `paperos create` through first spec'd page, deploy and desktop build; record it; answer PAP-5 with numbers"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P2"
type: "Review"
priority: 1
surfaces: ["Developer"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-120", "PAP-22", "PAP-26", "PAP-266", "PAP-28"]
blocks: []
key: "app-shell/new-app-drill"
url: "https://linear.app/paperos/issue/PAP-29/run-the-blank-screen-to-running-app-drill-time-paperos-create-through"
source: "plan/specs/gaps.json (round-1 canonical spec JSON)"
---

# PAP-29: Run the blank-screen-to-running-app drill: time `paperos create` through first spec'd page, deploy and desktop build; record it; answer PAP-5 with numbers

**Goal**

PAP-5 asks a measurable question: how quickly do we get from a blank screen to a running app. Every project in this plan claims to shorten that path; none of them measures it. This drill creates a brand-new app from the template with an agent, using only the documented tools, and records the wall-clock time and credit cost to reach five checkpoints: repo exists, first spec'd page renders locally, staging URL live, desktop binary launches, first release candidate cut. Findings become issues; the drill repeats weekly until the numbers stop improving.

**Scope**

In:
- Drill protocol `docs/drills/new-app.md`: fixed scenario (a two-audience app, e.g. "clinic booking": customer books, staff manages a schedule, one table view, one comment thread), fixed starting state (fresh imagine-os repo, empty Linear project), who runs it (Atlas dispatches, Forge builds, Quill writes the two page specs, Sentinel reviews), and what may not be done by hand.
- Timer harness `pnpm drill:new-app` that stamps checkpoints from CLI events, PR merges and deploy webhooks into `reports/drills/new-app-<date>.json` with token spend from `pm-linear/credit-metering`.
- Video: Playwright records the web flow at 375 and 1280 (`quality/video-replays`) and `asciinema` records the terminal; a 3-minute cut is published to the docs.
- Report: `docs/drills/new-app-<date>.md` with the checkpoint table, cost, the top five frictions ranked by minutes lost, and the issues filed for each (label `drill-finding`).
- PAP-5 closure: after the first drill, comment on PAP-5 with the numbers and the link (extends `pm-linear/pap5-decompose`, which only decomposed the question); reopen the drill weekly through the release train.

Out: building anything the drill reveals (those become issues), marketing demos, performance load testing (`realtime/load-test`).

**Spec**

- Checkpoints and targets for the first run, revised after: C1 repo, mirror, CI, Linear project exist under 10 minutes; C2 two pages from specs render locally under 60 minutes; C3 staging URL live with auth and a seeded tenant under 90 minutes; C4 Linux and macOS desktop builds launch under 150 minutes; C5 release candidate digest in Needs Justin under 240 minutes. Credit target under 150 USD for the full drill.
- Everything through the documented path: `paperos create`, the spec authoring skill, `pm-linear/orchestrator` claiming issues, gates 1 to 4. Any manual intervention is logged as a friction with minutes lost.
- The drill runs in a throwaway imagine-os repo prefixed `drill-` that `forge/repo-bootstrap` deletes afterwards (archive the report first).
- Comparisons across runs are plotted in the docs (`tables/map-chart-views` when available, otherwise a static SVG).

**Definition of done**

- First drill completed end to end with all five checkpoints stamped, report and video published in the docs engine, five or more friction issues filed and linked.
- PAP-5 has a comment with the checkpoint table and the report link; Justin can close it or leave it as the standing scoreboard (no Needs Justin item; informational).
- Second drill scheduled through `quality/release-train` weekly cadence and documented as a recurring Linear issue template.
- `CHANGELOG.md` entry; Linear comment on this issue with the numbers.

**Edge cases**

- The drill stalls on a missing feature: stamp the checkpoint as `blocked`, file the issue, continue with a documented manual step and count the minutes; do not abort the drill.
- Costs blow past the target because of retries: the report separates first-attempt cost from retry cost so the fix targets the right friction.
- Signed macOS build impossible without Justin's Apple developer credentials: record as an external friction, produce an unsigned build for the checkpoint and note the signing status.
- Orchestrator concurrency limits delay claims: the drill runs during a quiet window; scheduling delays are recorded separately from build time.
- The scenario becomes too familiar to the agents (memorised paths): rotate between three scenarios (clinic, agency, retail) after the second run.

**Dependencies**

`app-shell/create-cli`, `app-shell/app-deploy-pipeline`, `quality/release-train`, `spec-builder/layout-codegen`, `app-shell/feature-modules`. Soft: `app-shell/tauri-desktop`, `quality/video-replays`, `pm-linear/credit-metering`, `pm-linear/orchestrator`, `forge/repo-bootstrap`. Feeds `pm-linear/pap5-decompose` (closure comment) and every project through friction issues.

**Agent**

Run by Atlas (Dispatcher) with Forge, Quill and Sentinel in their normal roles; the report is written by Quill and reviewed by Atlas. Justin is not asked to approve anything; he reads the scoreboard on PAP-5.

**Size**

M per run: a half-day of agent time plus the report; the harness itself is S.
