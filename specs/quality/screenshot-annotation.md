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
blockedBy: ["PAP-239", "PAP-248", "PAP-82"]
blocks: []
key: "quality/screenshot-annotation"
url: "https://linear.app/paperos/issue/PAP-84/have-a-vision-agent-inspect-screenshots-for-overflow-misalignment"
source: "plan/specs/bucket-2.json (round-1 canonical spec JSON)"
---

# PAP-84: Have a vision agent inspect screenshots for overflow, misalignment, contrast and truncation and post annotated findings

**Goal**

Turn Gate 3's pixels into review findings: a vision-capable Claude agent inspects new and changed screenshots and video contact sheets for overflow, clipping, misalignment, truncation, contrast and theme leaks, draws annotated boxes on the images, and posts findings in the shared rubric format so layout defects block or get fixed without a human looking.

**Scope**

In:
- `packages/agents/src/vision/inspectScreenshots({ reportPath })` reading `reports/visual.json` and `reports/videos.json`, selecting images with status `diff` or `new` (all images on `main` nightly), and sending each with its context (page or story id, width, theme, the page spec's layout and components sections, guidelines `rules.json` items marked `vision`) to `claude-fable-5-1` with image input.
- Structured output per image: `{ findings: [{ rubricId, severity, title, body, bbox: { x, y, w, h } (normalised 0-1), confidence }], layoutScore: 0-100 }` validated by Zod; findings mapped into `finding.schema.ts` with `evidence: [{ kind: 'screenshot', ref }]`.
- Annotation renderer using `sharp` 0.33: draws boxes and numbered labels in the accent colour, writes `<id>.annotated.png` next to the original; a composite "findings sheet" per PR.
- Cross-width consistency check: the agent receives the same page at all seven widths in one call to spot content present at one width and missing at another.
- Posting: one review comment "Visual inspection" grouped by page with annotated thumbnails, plus statuses `gate/3-vision`; S0/S1 block per rubric rule.
- Cost controls: images downscaled to max 1568px longest side, at most 60 images per PR (prioritise diffs, then new, then random sample), budget cap $4 per PR with a notice when sampled.

Out: pixel diffing (Playwright does it), generating fixes, a11y tree analysis (`design-system/a11y-audit`).

**Spec**

- Prompt in `.claude/agents/reviewers/visual-inspector.md`: role, rubric `visual.md` checklist with IDs, instructions to report only defects visible in the image, to use bounding boxes in normalised coordinates, to compare against the spec's declared components and states, and to output JSON only.
- Contrast check is computed, not guessed: for each finding of type contrast the tool samples the bbox region with `sharp` and computes the ratio; findings below 3:1 keep severity, otherwise downgraded to `question`.
- Text truncation heuristics assisted by DOM: the visual suite also emits `reports/dom-metrics.json` per screenshot (`elements with scrollWidth > clientWidth`, `text-overflow: ellipsis` hits, elements outside viewport) so the agent can cross-check; DOM-confirmed findings get `confidence 0.9`.
- Deterministic IDs per rubric schema so re-runs update comments.
- Calibration set `docs/quality/rubrics/calibration/visual/` with 20 screenshots (10 defective with known bboxes, 10 clean); `pnpm vision:calibrate` reports precision and recall; target precision 0.85, recall 0.7.
- Output artifacts: `reports/vision.json`, annotated images, findings sheet uploaded alongside visual report to the PR Pages preview.
- Runs after `quality/playwright-matrix` via `workflow_run`; total under 6 minutes.

**Definition of done**

- Runs on a PR with visual diffs and posts annotated findings with boxes landing on the real defects (screenshot of the comment).
- Calibration precision at or above 0.85 and recall at or above 0.7 on the 20-image set, numbers in the PR.
- Seeded overflow at 375px and a low-contrast badge in dark theme are caught at S1 and S1 respectively; a clean PR produces zero blockers.
- Cost per PR under $4 across 10 runs; token and image counts in the job summary.
- `docs/quality/vision-inspection.md`; CHANGELOG entry; Linear comment with example annotated images.

**Edge cases**

- Masked volatile regions: agent told masks are intentional (coloured rectangles), never a finding.
- Intentional truncation with tooltip: DOM metrics include `title` presence so the finding downgrades to S3.
- Extremely tall full-page screenshots: split into 1568px tiles with overlap; bboxes remapped to page coordinates.
- Same defect at all seven widths: dedupe into one finding listing widths.
- Model hallucinated bbox outside the image: clamp and mark `confidence 0.3` (posted as question).
- Vision API unavailable: gate reports `error` and the review report lists inspection as missing; never silently green.

**Dependencies**

`quality/playwright-matrix` (hard). Soft: `quality/video-replays` (contact sheets), `quality/review-rubrics` (`visual.md`, schema), `design-system/guidelines-docs` (`rules.json`), `spec-builder/schema` (layout sections). Consumed by `quality/release-train`, `quality/review-report`, `collab/screenshot-annotations`, `identity/customer-portal-shell` (DoD).

**Agent**

Built by Sentinel (Visual Inspector sub-agent). Reviewed by Iris (design correctness of findings) and Atlas (cost).

**Size**

M: the SDK harness exists from `quality/review-agents`; the work is prompt, calibration, DOM metrics and annotation drawing.
