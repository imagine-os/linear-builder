---
identifier: "PAP-84"
title: "Have a vision agent inspect screenshots for overflow, misalignment, contrast and truncation and post annotated findings"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Visual and video gates"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-82", "PAP-239", "PAP-248"]
blocks: []
key: "quality/screenshot-annotation"
url: "https://linear.app/paperos/issue/PAP-84/have-a-vision-agent-inspect-screenshots-for-overflow-misalignment"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:43:12.350Z"
---

# PAP-84: Have a vision agent inspect screenshots for overflow, misalignment, contrast and truncation and post annotated findings

**Goal**

Turn Gate 3's pixels into review findings: a vision-capable Claude agent inspects new and changed screenshots and video contact sheets for overflow, clipping, misalignment, truncation, contrast and theme leaks, draws annotated boxes, and posts findings in the shared schema so layout defects block or get fixed without a human looking.

**Scope**

* In: `packages/agents/src/vision/inspectScreenshots()` on the PAP-243 runner with image input, prompt `.claude/agents/reviewers/visual-inspector.md`, Zod-validated per-image output, DOM metrics emitted by the visual suite, computed contrast check, `sharp` annotation renderer and findings sheet, cross-width consistency call, calibration set and `pnpm vision:calibrate`, posting, `reports/vision.json`, cost controls.
* Out: pixel diffing (PAP-82), generating fixes, accessibility tree analysis (PAP-73).

**Spec**

* Input: `reports/visual.json` and `reports/videos.json`; images with status `diff` or `new` (all on `main` nightly), each with story or route id, width, theme, the spec's layout and components sections and `rules.json` items marked `vision` (PAP-76).
* Output per image `{ findings: [{ rubricId, severity, title, body, bbox: { x, y, w, h } normalised 0-1, confidence }], layoutScore: 0-100 }` mapped to `Finding`s with `evidence: [{ kind: 'screenshot', ref }]`; deterministic IDs.
* DOM metrics: the visual suite writes `reports/dom-metrics.json` per screenshot (`scrollWidth > clientWidth`, `text-overflow: ellipsis` hits with `title` presence, elements outside viewport); DOM-confirmed findings get confidence 0.9; intentional truncation with tooltip downgrades to S3.
* Contrast is computed: sample the bbox with `sharp`, compute the ratio; below 3:1 keeps severity, otherwise downgrade to `question`.
* Cross-width: one call receives the same page at all seven widths to spot content missing at one width; identical defects across widths dedupe into one finding listing widths.
* Annotation: boxes and numbered labels in the accent colour, `<id>.annotated.png` beside originals, a composite findings sheet per PR, uploaded with the visual report.
* Cost: downscale to 1 568 px longest side, at most 60 images per PR (diffs, then new, then sample), $4 cap with a sampling notice; runs after PAP-82 via `workflow_run`, under 6 minutes.

**Interface contract**

* Provides: `reports/vision.json` (`GateReport<'vision'>` with `data.images: [{ id, layoutScore, findings }]`), annotated images and findings sheet, status `gate/3-vision`, "Visual inspection" comment section, `dom-metrics.json` shape (produced in PAP-246 fixtures, specified here).
* Requires: PAP-82 children (hard), PAP-243 runner, PAP-79 `visual.md` rubric, PAP-239 schema, PAP-83 contact sheets (soft), PAP-76 `rules.json` (soft), PAP-114 layout sections (soft).
* Consumers: PAP-88 certification, PAP-89 section 3, PAP-137 (annotations become comments), PAP-62 and PAP-63 DoDs, PAP-85 dedupe by bbox overlap.
* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §5 (`packages/contracts` is owned by quality through PAP-239: every `reports/*.json` named above is a `GateReport<kind>` validated by `validateArtifact()`, JSON Schema generated from Zod 4 per §1); §3 (gate results reach the bus as `review.gate_failed` and `review.ready` through PAP-97; artifact `version` bumps keep a reader for 30 days); §6 row "Gate artifacts" (provider PAP-239; consumers PAP-78 to PAP-90, PAP-97, PAP-137, PAP-110). Until PAP-239 merges, write the shape exactly as its Interface contract states and import the schema when it lands. `reports/vision.json` is `GateReport<'vision'>`; findings use the shared finding schema with `findingId()` so PAP-85 can dedupe by id and bbox.

**Definition of done**

* Runs on a PR with visual diffs and posts annotated findings whose boxes land on the real defects (comment screenshot).
* Calibration set `docs/quality/rubrics/calibration/visual/` (10 defective with known bboxes, 10 clean): precision at or above 0.85, recall at or above 0.7, numbers in the PR.
* Seeded overflow at 375 px and a low-contrast badge in dark theme are both caught at S1; a clean PR yields zero blockers.
* Cost under $4 per PR across 10 runs; tokens and image counts in the job summary.
* `docs/quality/vision-inspection.md`; changelog entry; Linear comment with example annotated images.

**Test plan**

* Unit: bbox clamping and remapping for tiled tall screenshots, dedupe across widths, contrast computation on fixture crops, DOM-metric cross-check rules.
* Calibration: `pnpm vision:calibrate` on the 20-image set.
* Integration: full run on the seeded PR; API unavailable yields `status: error`.
* Visual: annotated image snapshot for one calibration case.

**Demo**

Open the "Visual inspection" comment on the seeded PR: two annotated thumbnails with numbered boxes; click one to see the overflow box at 375; open `vision.json` for the same image. Under one minute.

**Edge cases**

* Masked volatile regions: never a finding.
* Very tall screenshots: 1 568 px tiles with overlap, bboxes remapped.
* Hallucinated bbox outside the image: clamped, confidence 0.3, posted as `question`.
* Model unavailable: `error`, listed as missing in the digest.

**Dependencies**

PAP-82 children (hard), PAP-243 (hard). Soft: PAP-83, PAP-76, PAP-79, PAP-239, PAP-114.

**Agent**

Sentinel (Visual Inspector). Reviewed by Iris (design correctness of findings) and Atlas (cost).

**Size**

M.
