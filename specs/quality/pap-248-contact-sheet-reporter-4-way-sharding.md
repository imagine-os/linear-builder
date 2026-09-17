---
identifier: "PAP-248"
title: "Contact-sheet reporter, 4-way sharding and the visual.json artifact"
project: "quality"
projectName: "Quality Pipeline"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Gates 1 and 2 on every PR"
state: "Backlog"
parent: "PAP-82"
children: []
blockedBy: ["PAP-239", "PAP-246", "PAP-247"]
blocks: ["PAP-83", "PAP-84", "PAP-88", "PAP-464"]
key: "quality/playwright-matrix/reporter-sharding"
url: "https://linear.app/paperos/issue/PAP-248/contact-sheet-reporter-4-way-sharding-and-the-visualjson-artifact"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:07.571Z"
model: "claude-sonnet-5"
effort: "medium"
---

# PAP-248: Contact-sheet reporter, 4-way sharding and the visual.json artifact

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Make the suite fast and legible: a custom reporter that composes contact sheets per page across widths, 4-shard CI with merged reports, the `visual.json` artifact in the contracts shape, the sticky PR comment and the Pages report upload.

**Scope**

* In: `ops/ci/visual/contact-sheet-reporter.ts` (`sharp` grid per page, thumbnails of top 6 diffs), `--shard=i/4` matrix in `visual.yml` with `merge-reports`, `reports/visual.json` writer, sticky comment section "Visual", upload to `/pr/<n>/visual/`, `gate/3-visual` status, 8-minute budget check.
* Out: capture (siblings), vision inspection (PAP-84).

**Spec**

* Reporter listens to test results, groups by page ID, renders a grid (columns widths, rows themes) with status badges; output `reports/visual/sheets/<id>.png`.
* `visual.json`: `GateReport<'visual'>` with `data.images: [{ id, project, theme, status: pass|diff|new|missing, diffRatio, paths: { actual, expected?, diff? } }]` validated by `packages/contracts`.
* CI: 4 runners, blob reporter, `npx playwright merge-reports`, HTML report and sheets uploaded to run artifacts and to Pages via PAP-15's branch strategy; comment via the shared sticky-comment action (PAP-78).
* Budget: total wall time under 8 minutes; a count check fails when images exceed 600.

**Interface contract**

* Provides: `visual.json`, contact sheets, Pages URLs `artifactUrl(pr, 'visual/...')`, status `gate/3-visual`.
* Requires: sibling children, `packages/contracts`, PAP-78 comment action, PAP-15 Pages hosting (soft; artifacts otherwise).
* Consumers: PAP-84 (reads `visual.json`), PAP-89, PAP-137.

**Definition of done**

* Suite runs on a PR across 4 shards in under 8 minutes and posts the sticky comment with sheets (link).
* `visual.json` validates; PAP-84 stub consumer lists diff images from it.
* Count check fails on a seeded 601st image.
* Docs section "Reports and sharding".

**Test plan**

* Unit: grid layout math, JSON writer against fixtures.
* Integration: merge of 4 blob reports in CI.
* Visual: a contact sheet snapshot itself.

**Demo**

Open a PR's "Visual" comment, click the contact sheet for `/portal`, see 7 widths × 3 themes with one red badge; open the Pages report link. Under one minute.

**Edge cases**

* Shard failure: merge marks missing results `error`, never pass.
* Pages upload over size: sheets only, full images in run artifacts.
* Zero visual-tagged tests: comment says so, status pass.

**Dependencies**

Both sibling children (hard), `packages/contracts` (hard). Soft: PAP-15.

**Agent**

Built by Sentinel (Visual Inspector). Reviewed by Forge (CI).

**Size**

S.
