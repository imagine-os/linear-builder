---
identifier: "PAP-137"
title: "Allow annotating screenshots and video frames with comments that create Linear issues"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Knowledge surfaced everywhere"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-131", "PAP-83"]
blocks: []
key: "collab/screenshot-annotations"
url: "https://linear.app/paperos/issue/PAP-137/allow-annotating-screenshots-and-video-frames-with-comments-that"
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-137: Allow annotating screenshots and video frames with comments that create Linear issues

**Goal**

Close the loop from picture to ticket: a viewer for the Playwright screenshots and video replays of every PR run where anyone can draw a box or pin on an image or a paused video frame, comment, see the vision agent's findings overlaid, and create a Linear issue with the cropped evidence in one click. Visual bugs stop needing a written reproduction.

**Scope**

In:
- Route `/_app/dev/qa/$runId` (staff, developer) reading the run manifest published by `quality/playwright-matrix` and `quality/video-replays` (`reports/gate3.json` uploaded to MinIO via `data-layer/file-storage` with entries `{ page, width, theme, kind: screenshot|video|contactSheet, fileId, flowId?, durationMs? }`), grouped by page with a width by theme matrix; a runs list `/_app/dev/qa` by PR and date from `pm-linear/webhooks` records.
- Viewer in `packages/collab/annotations/`: image viewer with zoom and pan, video player (`<video>` with frame stepping via `requestVideoFrameCallback`, time code display, flow step captions from the contact sheet data), annotation layer reusing the overlay code from `collab/canvas-view` (`RegionNode`-like rectangles and pins) drawn with pointer events (mouse, touch; pen refinements come from `input/pen`), keyboard alternative (arrow keys to position, `Shift` plus arrows to size).
- Annotations are comment threads with `anchor_type: screenshot` and `anchor { fileId, frame?: ms, rect: { x, y, w, h } in image percent }` via `collab/comments`; existing vision-agent findings from `quality/screenshot-annotation` (its JSON: `{ fileId, severity, kind: overflow|misalignment|contrast|truncation, rect, message }`) are rendered as read-only overlays with a distinct style and a "confirm" or "dismiss" action that posts back to the run comment.
- Create issue: a button on any annotation calls `threads.createIssue` with a title `[visual] <page> @<width> <theme>: <first line>`, description including the crop (canvas crop of the rect with 10 percent padding uploaded through signed upload and embedded as an image), the full image link, the run and PR links, the flow step and time code for videos, labels `Bug` plus the page's Surface label, project inferred from the page spec `meta.owner`; the PR gets a back-link comment via `pm-linear/webhooks`.
- Compare mode: side by side or onion-skin against the `main` baseline of the same page, width and theme when present.

Out: producing screenshots and videos (quality project), pixel-diff gating, freehand drawing tools, customer access.

**Spec**

- Image coordinates stored as percentages so annotations survive resizing; render uses the natural size for crops.
- Video frame anchor uses milliseconds; the viewer seeks and pauses on open; contact sheet thumbnails link to the nearest step.
- Manifest access requires `qa.view` (staff.*); issue creation requires `qa.report`.
- Deep link `?file=<id>&t=<ms>&thread=<id>`.
- Loading budget: first image visible under 1 s on a 1920 grid; thumbnails via MinIO image variants (`data-layer/file-storage`).

**Definition of done**

- Playwright with a seeded run manifest: open run, draw a rectangle on a screenshot, comment, create a Linear issue (mocked) and verify the crop uploaded; pause a video, pin at a frame, permalink reopens at the frame; screenshots at 768, 1024, 1280, 1536 and 1920 in light and dark; 320 and 375 support viewing and pinning, not compare mode.
- Vitest: percent coordinate math, crop generation, title and description builders, vision finding mapping.
- Keyboard-only annotation recorded as a video flow; axe clean.
- `docs/collab/qa-viewer.md`; CHANGELOG entry; Linear comment with screenshots, the test issue created and the video.
- Sentinel's Visual Inspector posts one real finding that a human confirms through the viewer.

**Edge cases**

- Run manifest partially uploaded (shard still running): viewer shows available items and a live "3 of 4 shards" indicator.
- Screenshot regenerated for the same PR (new commit): old annotations stay attached to the old file id and are listed under "previous run".
- Video codec unsupported in Safari or WebKitGTK: fall back to the contact sheet with a notice.
- Very tall full-page screenshot (12k px): tiled rendering, zoom limited to keep memory under 300 MB.
- Rect smaller than 8 px: converted to a pin.
- Linear project inference fails (page without spec): issue lands in the default project with a note.

**Dependencies**

`collab/comments` (hard) and `quality/video-replays` (hard, manifest and MP4s). `quality/playwright-matrix`, `quality/screenshot-annotation` (finding JSON), `data-layer/file-storage`, `pm-linear/webhooks`, `collab/canvas-view` overlay code (soft, can be copied). Consumed by `quality/review-report` (links to the viewer).

**Agent**

Built by Nova (Canvas Cartographer) with Sentinel (Visual Inspector) defining the finding overlay. Reviewed by Sentinel (Code Reviewer) and Iris for viewer UX.

**Size**

M: viewer and overlay build on comments and canvas code; video frame handling is the tricky part.
