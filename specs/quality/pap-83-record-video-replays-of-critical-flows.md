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
blockedBy: ["PAP-82", "PAP-239", "PAP-248"]
blocks: ["PAP-137"]
key: "quality/video-replays"
url: "https://linear.app/paperos/issue/PAP-83/record-video-replays-of-critical-flows-per-pr-at-each-responsive-size"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:43:11.078Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-83: Record video replays of critical flows per PR at each responsive size and attach them to the PR

**Goal**

Record short video replays of the critical user flows on every PR at each responsive width, with step captions and a contact sheet, and attach them to the PR and the Linear issue so reviewer agents, the vision inspector and Justin can watch a change instead of reading it.

**Scope**

* In: flow definitions `specs/flows/*.flow.yaml` with a Zod schema, Playwright runner `apps/web/e2e/flows/` recording per flow per width, ffmpeg post-processing (MP4, captions, poster, contact sheet), `reports/videos.json`, MinIO upload with signed URLs, sticky comment section, Linear comment, status `gate/3-video`.
* Out: production session replay, frame diffing, native mobile recordings, audio.

**Spec**

* Flow YAML `{ id, title, audience, critical: true, steps: [{ action: goto | click | fill | press | expect | wait, target, value?, note }], at?: { sm: [extra steps] } }`, max 40 steps; `target` resolves via `getByTestId` or `getByRole(name)`; ambiguous targets fail fast listing candidates. Starter flows: sign-in, create workspace, switch tenant, create and edit a record, open inspector and detach panel (desktop only), theme switch.
* Runner: `recordVideo` at `{ width, height: 900 }`, `slowMo: 150`, caption overlay `data-testid="flow-caption"` via `addInitScript`; default widths `sm-375, md-768, xl-1280, 3xl-1920`, all seven plus dark theme on `main` nightly; seeds and logs in through PAP-240 per `audience`.
* Post-processing `ops/ci/video/`: ffmpeg (pinned in the Playwright image) WebM to MP4 H.264 720p CRF 28, burned step captions with timestamps, poster frame, 3×4 contact sheet PNG; `reports/videos.json` as `GateReport<'videos'>` with `data.videos: [{ flowId, width, theme, mp4, poster, sheet, durationMs, steps: [{ note, atMs }] }]`.
* Storage: run artifacts plus MinIO `qa-videos/<repo>/<pr>/<sha>/` with 30-day lifecycle (180 days for `main` nightly critical flows); signed URLs valid 30 days; comment notes expiry.
* Budget: 6 flows × 4 widths under 6 minutes across 2 shards; per-flow timeout 90 s. `pnpm flows`, `pnpm flows:record <flowId>`.

**Interface contract**

* Provides: `FlowSpec` schema (`packages/spec/src/flows.ts`), `reports/videos.json`, contact sheets, poster URLs, status `gate/3-video`, "Replays" sticky-comment section, Linear comment format, `flow-caption` overlay.
* Requires: PAP-246 projects and fixtures, PAP-240 seed and `loginAs`, PAP-239 schema, PAP-37 or compose MinIO, PAP-97 Linear comments (soft), PAP-78 comment action.
* Consumers: PAP-84 (contact sheets), PAP-89 section 5, PAP-137 annotations, PAP-72 (motion evidence), PAP-29 drill recording.
* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §5 (`packages/contracts` is owned by quality through PAP-239: every `reports/*.json` named above is a `GateReport<kind>` validated by `validateArtifact()`, JSON Schema generated from Zod 4 per §1); §3 (gate results reach the bus as `review.gate_failed` and `review.ready` through PAP-97; artifact `version` bumps keep a reader for 30 days); §6 row "Gate artifacts" (provider PAP-239; consumers PAP-78 to PAP-90, PAP-97, PAP-137, PAP-110). Until PAP-239 merges, write the shape exactly as its Interface contract states and import the schema when it lands. `reports/videos.json` is a `GateReport<'videos'>`; recordings are stored through the §2 "File" contract (PAP-37) and linked, never inlined.

**Definition of done**

* Six flows recorded at four widths on a PR; sticky comment shows posters and links; Linear comment posted (links).
* Nightly `main` covers seven widths and both themes; `videos.json` validates.
* Seeded broken flow (renamed button) fails `gate/3-video` and the MP4 shows the failing step (link).
* Videos play in Chrome, Safari and Firefox; under 4 MB average.
* `docs/quality/flows.md`; changelog entry; Linear comment with a sample video and contact sheet.

**Test plan**

* Unit: flow schema validation (40-step cap, `at` overrides), caption timing math, contact-sheet frame sampling.
* Integration: runner on the example app for two flows at 375 and 1280 in CI; ffmpeg pipeline on a fixture WebM; MinIO unavailable falls back to artifact links.
* Visual: contact sheet snapshot for one flow.
* Cross-browser: MP4 playback smoke in the three engines (Playwright).

**Demo**

Open the PR "Replays" section, click the `switch-tenant` poster at 375 and watch the 20-second MP4 with captions; open its contact sheet. Under one minute.

**Edge cases**

* Step target inside a collapsed drawer at small widths: `at.sm` extra steps open it.
* ffmpeg missing locally: WebM with a warning.
* Flow over 60 s: split into two flows.
* Signed URL expiry in Linear: date noted; PAP-89 re-signs.

**Dependencies**

PAP-82 children (hard: PAP-246 fixtures), PAP-240 (hard). Soft: PAP-37, PAP-97, PAP-239.

**Agent**

Sentinel (Visual Inspector). Reviewed by Forge (storage, ffmpeg in the image) and Nova (flow realism).

**Size**

M.
