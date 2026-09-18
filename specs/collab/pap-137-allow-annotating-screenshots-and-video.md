---
identifier: "PAP-137"
title: "Allow annotating screenshots and video frames with comments that create Linear issues"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Knowledge surfaced everywhere"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-83", "PAP-131", "PAP-319", "PAP-462", "PAP-474", "PAP-671"]
blocks: []
key: "collab/screenshot-annotations"
url: "https://linear.app/paperos/issue/PAP-137/allow-annotating-screenshots-and-video-frames-with-comments-that"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:39.259Z"
model: "claude-sonnet-5"
effort: "low"
estimate: 3
dueDate: null
cycle: null
---

# PAP-137: Allow annotating screenshots and video frames with comments that create Linear issues

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Close the loop from picture to ticket: a viewer for every PR run's screenshots and video replays where anyone draws a box or pin on an image or paused frame, comments, sees the vision agent's findings overlaid and creates a Linear issue with cropped evidence in one click.

**Scope**

In:

* Routes `/_app/dev/qa` (runs by PR and date from PAP-97 records) and `/_app/dev/qa/$runId` reading the manifest `visual.json` and `videos.json` (PAP-239 contract) from MinIO (PAP-37), grouped by page with a width by theme matrix.
* Viewer in `packages/collab/annotations/`: image zoom and pan, video with frame stepping (`requestVideoFrameCallback`), flow captions from the contact sheet, annotation layer reusing the PAP-132 `RegionNode` overlay for rectangles and pins with mouse, touch and keyboard (arrows position, `Shift` plus arrows size).
* Annotations are PAP-131 threads with `anchor_type: screenshot`; PAP-84 findings rendered read-only with confirm and dismiss posting back to the run comment.
* Create issue: `threads.createIssue` with title `[visual] <page> @<width> <theme>: <first line>`, description with the padded crop uploaded via signed URL, image, run and PR links, flow step and time code; labels `Bug` plus the page's Surface; project from spec `meta.owner`; PR back-link via PAP-97.
* Compare mode: side by side or onion-skin against the `main` baseline.

Out: producing media (quality), pixel-diff gating, freehand tools (PAP-157), customer access.

**Spec**

* Rects stored as image percentages; crops use natural size.
* Video anchors in milliseconds; open seeks and pauses.
* `qa.view` for manifests, `qa.report` for issue creation.
* Deep link `?file=<id>&t=<ms>&thread=<id>`; first image under 1 s on a 1920 grid via MinIO variants.

**Interface contract**

Exposes: `AnnotationViewer`, `useRunManifest(runId)`, screenshot anchor `{ fileId, frame?: ms, rect: { x, y, w, h } }` (percent) registered in PAP-131's `CommentAnchor` union, finding overlay adapter `VisionFinding -> Overlay`, issue builder `buildVisualIssue(annotation)`, `InkAnnotationLayer` slot for PAP-157. Consumes: `visual.json` `{ screenshots: [{ id, page, width, theme, path }] }` and `videos.json` `{ videos: [{ id, flowId, width, path, steps: [{ t, label }] }] }` from PAP-239; `vision.json` findings `{ fileId, severity, kind, rect, message }` from PAP-84; `threads.createIssue` from PAP-131; run records and PR comment API from PAP-97; signed uploads and variants from PAP-37.

**Definition of done**

* Seeded run browsable; screenshots at 768, 1024, 1280, 1536 and 1920 in light and dark; 320 and 375 support viewing and pinning, not compare.
* Keyboard-only annotation recorded as a PAP-83 flow; axe clean.
* `docs/collab/qa-viewer.md`; CHANGELOG entry; Linear comment with screenshots, the test issue and the video.
* Sentinel's Visual Inspector posts one real finding a human confirms in the viewer.

**Test plan**

* Vitest: percent to pixel math at three image sizes, crop generation with padding and clamping, title and description builders, finding mapping, rect under 8 px becomes a pin.
* Integration: manifest loader against a fixture MinIO bucket with a partial shard; `callAs(customer)` denied on `qa.view`.
* Playwright (seeded run): draw a rectangle, comment, create issue against mocked PAP-101 and assert the crop upload; pause a video at 3200 ms, pin, copy permalink, reopen at the frame; compare mode toggles onion-skin; run at 1280 and 1920, plus pin-only at 375.
* Visual: Gate 3 baselines for viewer and compare at five widths, both themes.

**Demo**

Open the latest run, click the 1280 dark screenshot of Inbox, drag a box over the misaligned button, type “off by 4 px”, click Create issue and open the Linear link with the crop embedded; scrub the sign-in video, pin a frame and copy the permalink. Under two minutes.

**Edge cases**

* Shard still running: "3 of 4 shards" live indicator.
* New commit regenerates screenshots: old annotations under "previous run".
* Unsupported video codec: contact sheet fallback.
* 12k-pixel screenshot: tiled rendering, memory under 300 MB.
* No spec owner: default project with a note.

**Dependencies**

PAP-131, PAP-83 (hard, encoded). Soft: PAP-82, PAP-84, PAP-239, PAP-37, PAP-97, PAP-132. Consumed by PAP-89.

**Agent**

Built by Nova (Canvas Cartographer) with Sentinel (Visual Inspector) defining the finding overlay. Reviewed by Sentinel (Code Reviewer) and Iris.

**Size**

M: viewer and overlay build on comments and canvas code; video frames are the tricky part.
