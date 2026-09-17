---
identifier: "PAP-135"
title: "Build the prompt log browser: filter by issue or character, replay a session, link to the PR"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff", "Agent"]
milestone: "Comments and canvas"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-129", "PAP-165"]
blocks: []
key: "collab/prompt-log-ui"
url: "https://linear.app/paperos/issue/PAP-135/build-the-prompt-log-browser-filter-by-issue-or-character-replay-a"
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-135: Build the prompt log browser: filter by issue or character, replay a session, link to the PR

**Goal**

Let Justin audit any agent decision in minutes: a browser over the prompt-log store that filters sessions by issue, character, status and cost, replays a session turn by turn with tool calls expanded, and jumps to the PR, Linear issue and worktree. It also feeds evals by letting a reviewer flag a session as a golden or a failure.

**Scope**

In:
- Route `/_app/dev/prompt-log` (platform tenant, `staff.admin` and agent principals read) with a sessions grid built on `tables/grid-view` using a view model from `tables/view-model-spec`: columns character, sub-agent, issue (link), status, model, duration, input and output tokens, cache tokens, cost, PR (link), started; default sort started desc; filters and grouping by character or issue; saved views ("Today", "Failed", "Over $5").
- Session detail `/_app/dev/prompt-log/$sessionId`: header with metadata, cost and token gauges, links (PR, Linear issue via `pm-linear/linear-sync` or direct URL, branch, worktree path, parent session); timeline of events virtualised with `@tanstack/react-virtual` 3, colour by role, tool calls collapsible with input and output (JSON pretty-printed, large outputs loaded from blob on demand), redaction markers shown inline as `[REDACTED:kind]`, `PreCompact` markers, sub-agent sessions nested and expandable.
- Replay mode: step through events with keyboard (`j`, `k`, space to autoplay at 1x to 8x), a progress bar with token accumulation and running cost, "jump to first tool error", "jump to final message".
- Actions: "Flag as golden" and "Flag as failure" call `agents/eval-harness` `evals.flag({ sessionId, verdict, note })`; "Open issue" creates a Linear issue via `collab/comments` escalation path with the session link; "Copy permalink" with event seq (`?seq=142`).
- Stats panel `/_app/dev/prompt-log/stats`: cost and tokens by issue, character and day from `promptLog.stats`, rendered with the chart view from `tables/map-chart-views` or a small Recharts fallback, following the dataviz skill palette.

Out: ingestion and storage (`collab/prompt-log-store`), budget enforcement (`agents/cost-controls`), daily reports (`pm-linear/credit-metering`), editing logs.

**Spec**

- Data via oRPC `promptLog.*` with cursor pagination; grid pages of 100; detail loads events in 500-event chunks by `seq` with prefetch of the next chunk.
- Search within a session: client-side over loaded chunks plus server `events.list({ q })` using `ILIKE` on `content` for the rest.
- Permalinks resolve `seq` and scroll the virtual list to it.
- Responsive: grid becomes a card list under `md`; detail timeline is single-column at every width; gauges stack at 320 and 375.
- All timestamps in the viewer's timezone with UTC on hover.

**Definition of done**

- Playwright with a seeded store of 50 sessions: filter by character, open a session, expand a tool call, replay with keyboard, flag as golden (mocked eval endpoint), open permalink; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark; video of a replay from `quality/video-replays`.
- Vitest: chunk loading, permalink resolution, gauge math, nesting of sub-agent sessions.
- 10k-event session scrolls at 60 fps (measurement in comment).
- axe clean; `docs/collab/prompt-log-ui.md`; CHANGELOG entry; Linear comment with screenshots and video.
- Justin replays one real session and confirms the PR link and cost match Linear's metering comment.

**Edge cases**

- Session still running: header shows live status, timeline tails new events via polling every 5 s (or Electric shape when available).
- Session with gaps (`gaps jsonb`): gap rows rendered with a warning and the missing seq range.
- Redacted content that hides the whole message: show a "fully redacted" row with the kind counts.
- Tool output blob missing (retention): "content expired" placeholder with the size.
- Killed session: red status, final synthetic `session.killed` event with the reason.
- Grid view engine not merged: fall back to a plain TanStack Table with the same columns; documented TODO.

**Dependencies**

`collab/prompt-log-store` (hard), `tables/grid-view` (hard, with fallback). Soft: `agents/eval-harness`, `tables/view-model-spec`, `tables/map-chart-views`, `pm-linear/linear-sync`, `realtime/record-sync`. Consumed by `collab/rules-skills-registry` (usage links), `pm-linear/credit-metering` (deep links).

**Agent**

Built by Nova (Views Engineer) with Quill (Prompt Logger) defining what reviewers need. Reviewed by Sentinel (Visual Inspector, Code Reviewer) and Atlas.

**Size**

M: two screens over an existing API; virtualisation and replay are the work.
