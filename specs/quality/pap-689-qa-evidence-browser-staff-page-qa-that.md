---
identifier: "PAP-689"
title: "QA evidence browser: staff page `/qa` that lists PRs and release candidates with their gate reports, screenshots, replays, traces and findings read from `GateReport` artefacts"
project: "quality"
projectName: "Quality Pipeline"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Edge-case hunting and release trains"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-83", "PAP-165", "PAP-239", "PAP-248", "PAP-630"]
blocks: []
key: "r4/quality/qa-evidence-browser"
url: "https://linear.app/paperos/issue/PAP-689/qa-evidence-browser-staff-page-qa-that-lists-prs-and-release"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:26.964Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-689: QA evidence browser: staff page `/qa` that lists PRs and release candidates with their gate reports, screenshots, replays, traces and findings read from `GateReport` artefacts

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Deferred to v0.2 by round 4 (not claimable before 2026-10-01; NJ-14 can reinstate). Justin asked for screenshot checking, workflow logging on screenshots and video replays he can look at; today that evidence is scattered across sticky comments, Pages URLs, MinIO links and Linear status comments. PAP-239 already names "the QA viewer" as a consumer. This page renders every `GateReport` artefact for a PR or release candidate in one place inside the product, using the views engine.

**Scope**

* In: route `/_app/qa` with `specs/qa/evidence.spec.yaml` and `/qa/pr/:number`, `/qa/rc/:version`; data source `qa_gate_runs` (gate metrics issue) plus artefact fetch through `artifactUrl()`; components `GateTimeline`, `ContactSheetViewer` (zoom, before/after slider), `ReplayPlayer` (poster, captions from `videos.json`), `FindingsTable` (grid view with severity filter), `TraceLink` to the Playwright trace viewer; deep links from the Linear status comment (PAP-97) and the digest (PAP-89).
* Out: editing findings, re-running gates, annotation comments (PAP-137 owns annotation to issues), prompt logs (PAP-135).

**Spec**

* Page spec `access.view: staff.*`; list view of recent PRs and RCs with gate badges from `qa_gate_runs`; detail renders sections in `GATE_STATUSES` order, each reading its artefact JSON through the PAP-239 schema and showing `unknown` when missing.
* Contact sheets and diff images from `visual.json` paths via `artifactUrl(pr, path)`; replays from `videos.json` signed URLs (re-signed by the API when expired); Playwright traces linked to `https://trace.playwright.dev/?trace=<url>`.
* Findings grid uses `tables/grid-view` with columns severity, reviewer, rubric, file, title, status (open, resolved, waived) and a filter bar (PAP-166).
* Responsive: under 768 px the gate timeline becomes a vertical list and contact sheets scroll horizontally; screenshots at the seven widths in both themes through Gate 3.

**Interface contract**

* Provides: route `/qa/**`, page specs, components above in `packages/quality-ui`, deep-link format `/qa/pr/<n>#<status>` consumed by PAP-97 and PAP-89.
* Consumes: PAP-239 schemas and `artifactUrl`, PAP-248 `visual.json`, PAP-83 `videos.json`, `qa_gate_runs`, PAP-165 grid, PAP-166 filters, PAP-37 signed URLs.

**Definition of done**

* Page specs validate; conformance tests pass; screenshots at seven widths in both themes.
* A sandbox PR with all gates shows every section populated; a PR with an errored gate shows `unknown` with the re-run link.
* Replay plays with captions; before/after slider works on a seeded visual diff (recording).
* Deep link from a Linear status comment opens the right section; changelog under "Quality".

**Test plan**

* Unit: artefact loaders per kind on fixtures including missing artefacts, URL re-signing, badge derivation.
* E2E: Playwright at 375 and 1280 px: list, open PR, filter findings, play replay.

**Demo**

Open `/qa/pr/42` for the seeded PR: gate timeline, the 375 px contact sheet with one red badge, the replay poster, the findings grid filtered to S1. Ninety seconds.

**Edge cases**

* Artefacts expired (Pages 30 days): section shows the run-artifact link and the expiry date.
* Thousands of images on an RC: contact sheets only, full images lazy-loaded per page.
* Forgejo-hosted PR: `artifactUrl` fallback to run links; trace viewer link requires a reachable URL, else the download link.

**Dependencies**

Hard: PAP-239, PAP-248, PAP-83, PAP-165. Soft: PAP-166, PAP-37, PAP-97, PAP-89, PAP-680.

**Agent**

Builder: Nova (Views Engineer) with Sentinel (Visual Inspector). Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/quality/gate-metrics-and-pipeline-health` = PAP-680.
