---
identifier: "PAP-83"
title: "Record video replays of critical flows per PR at each responsive size and attach them to the PR"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Visual and video gates"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-239", "PAP-248", "PAP-82"]
blocks: ["PAP-137"]
key: "quality/video-replays"
url: "https://linear.app/paperos/issue/PAP-83/record-video-replays-of-critical-flows-per-pr-at-each-responsive-size"
source: "plan/specs/bucket-2.json (round-1 canonical spec JSON)"
---

# PAP-83: Record video replays of critical flows per PR at each responsive size and attach them to the PR

**Goal**

Record short video replays of the critical user flows on every PR at each responsive width, with a step overlay and a contact sheet, and attach them to the PR and the Linear issue so reviewer agents, the vision inspector and Justin can watch a change instead of reading it.

**Scope**

In:
- Flow definitions in `specs/flows/*.flow.yaml`: `{ id, title, audience, critical: true, steps: [{ action: goto|click|fill|press|expect|wait, target (testid or role), value?, note }] }`; starter flows: sign-in, create workspace, switch tenant, create and edit a record, open inspector and detach panel (desktop only), theme switch.
- Runner `apps/web/e2e/flows/` in Playwright with `recordVideo` per test, one test per flow per width from `breakpoints.json` (default subset `sm-375, md-768, xl-1280, 3xl-1920`; full 7 on `main` nightly), light theme by default and dark on `main`.
- Post-processing `ops/ci/video/`: ffmpeg (pinned in the Playwright Docker image) converts WebM to MP4 (H.264, 720p max height, CRF 28), burns a step caption from step notes with timestamps, generates a poster frame and a 3x4 contact sheet PNG, and writes `reports/videos.json` `[{ flowId, width, theme, mp4, poster, sheet, durationMs, steps: [{ note, atMs }] }]`.
- Storage: artifacts on the run plus upload to MinIO bucket `qa-videos/<repo>/<pr>/<sha>/` (`data-layer/file-storage` or raw S3 client) with 30-day lifecycle; public read via signed URLs valid 30 days.
- PR sticky comment section "Replays" with poster thumbnails linking to MP4s; Linear comment on the linked issue with the same links (`pm-linear/webhooks`).
- Commit status `gate/3-video` (fails only when a flow fails, not on visual difference).

Out: production session replay, visual diffing of frames, mobile native recordings (Tauri mobile), audio.

**Spec**

- Flow YAML validated by Zod schema `packages/spec/src/flows.ts`; `target` resolves via `getByTestId` or `getByRole(name)`; `expect` supports `visible`, `text`, `url`.
- Fixture seeds the same deterministic data as `quality/playwright-matrix` and logs in per `audience`.
- Video size `{ width, height: 900 }` per project; `slowMo: 150` for legibility; a translucent overlay component `data-testid="flow-caption"` injected via `page.addInitScript` shows the current step note bottom-left.
- Contact sheet: 12 frames sampled at step boundaries (or evenly if fewer steps) labelled with step index.
- Total budget: 6 flows x 4 widths under 6 minutes across 2 shards; per-flow timeout 90s.
- `pnpm flows` runs locally with `--headed` option; `pnpm flows:record <flowId>` writes MP4s to `tmp/videos/`.
- Retention: PR videos 30 days; `main` nightly videos of critical flows kept 180 days for the release digest.

**Definition of done**

- Six flows recorded at four widths on a PR; sticky comment shows posters and links; Linear comment posted (links).
- Nightly `main` run covers all seven widths and both themes; report JSON validates.
- A seeded broken flow (button renamed) fails `gate/3-video` and the MP4 shows the failing step (link).
- Videos play in Chrome, Safari and Firefox; MP4 under 4 MB each on average.
- `docs/quality/flows.md` documents writing a flow; CHANGELOG entry; Linear comment with a sample video and contact sheet.

**Edge cases**

- Flow step target ambiguous (multiple matches): fail fast with the candidates listed; never pick the first.
- Width where a step target is inside a collapsed drawer: flows may declare `at: { sm: [extra steps] }` overrides to open the drawer first.
- ffmpeg missing locally: fall back to WebM with a warning; CI always has it.
- MinIO unavailable: keep run artifacts, comment includes artifact link instead of signed URLs.
- Very long flow (over 60s): split into two flows; the schema caps steps at 40.
- Signed URL expiry in Linear comments: comment notes the expiry date; release digest re-signs when built.

**Dependencies**

`quality/playwright-matrix` (hard: fixtures, projects, image). Soft: `data-layer/file-storage` or MinIO from `data-layer/postgres-provision` compose, `pm-linear/webhooks` (Linear comments), `identity/*` for real auth flows (use seeded test users). Consumed by `quality/screenshot-annotation` (contact sheets), `quality/review-report`, `collab/screenshot-annotations`, `design-system/motion` (motion evidence).

**Agent**

Built by Sentinel (Visual Inspector). Reviewed by Forge (storage and ffmpeg in runner image) and Nova for flow realism.

**Size**

M: Playwright records video natively; the work is flow schema, overlay, encoding and publishing.
