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
blockedBy: ["PAP-129", "PAP-165", "PAP-343", "PAP-474"]
blocks: []
key: "collab/prompt-log-ui"
url: "https://linear.app/paperos/issue/PAP-135/build-the-prompt-log-browser-filter-by-issue-or-character-replay-a"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:58:04.356Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-135: Build the prompt log browser: filter by issue or character, replay a session, link to the PR

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Let Justin audit any agent decision in minutes: a browser over the prompt-log store that filters sessions by issue, character, status and cost, replays a session turn by turn with tool calls expanded, and jumps to the PR, Linear issue and worktree. Reviewers flag sessions as golden or failure for evals.

**Scope**

In:

* Route `/_app/dev/prompt-log` (platform tenant; `staff.admin` and agent principals) with a sessions grid on PAP-165 using a PAP-161 view model: character, sub-agent, issue, status, model, duration, tokens, cache, cost, PR, started; saved views "Today", "Failed", "Over $5".
* Detail `/_app/dev/prompt-log/$sessionId`: metadata header with cost and token gauges, links (PR, issue, branch, worktree, parent), virtualised timeline (`@tanstack/react-virtual` 3) coloured by role, collapsible tool calls with pretty JSON and on-demand blobs, `[REDACTED:kind]` markers, `PreCompact` markers, nested sub-agent sessions.
* Replay: `j`/`k`, space to autoplay 1x to 8x, running cost bar, "jump to first tool error", "jump to final message".
* Actions: Flag as golden or failure → PAP-110 `evals.flag`; Open issue via PAP-131 escalation; Copy permalink `?seq=`.
* Stats `/_app/dev/prompt-log/stats` from `promptLog.stats`, charts per the dataviz palette (PAP-170 or Recharts fallback).

Out: ingestion (PAP-129), budgets (PAP-111), daily reports (PAP-98).

**Spec**

* Cursor pagination; grid pages of 100; events in 500-event chunks by `seq` with prefetch.
* In-session search: client-side over loaded chunks plus `events.list({ q })`.
* Grid becomes a card list under `md`; gauges stack at 320 and 375.
* Timestamps in viewer timezone, UTC on hover.

**Interface contract**

Exposes: routes above; permalink grammar `/_app/dev/prompt-log/<sessionId>?seq=<n>` used by PAP-98 metering comments, PAP-134 usage links and PAP-144 agent attribution; `SessionLink({ sessionId, seq? })` component in `packages/collab`; view model `prompt-sessions.view.json`. Consumes: `promptLog.sessions.list|get`, `promptLog.events.list`, `promptLog.stats` (PAP-129); `GridView` and `ViewModel` (PAP-165, PAP-161) with a plain TanStack Table fallback; `evals.flag({ sessionId, verdict, note })` (PAP-110); `threads.createIssue` (PAP-131); Electric shape on `prompt_session` for live tailing (PAP-143) else 5 s polling.

**Definition of done**

* Seeded store of 50 sessions browsable; a 10k-event session scrolls at 60 fps (measurement in comment).
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark; replay video from PAP-83.
* axe clean; `docs/collab/prompt-log-ui.md`; CHANGELOG entry; Linear comment with screenshots and video.
* Justin replays one real session and confirms PR link and cost match the metering comment.

**Test plan**

* Vitest: chunk loader (boundaries, prefetch), permalink resolution to a virtual index, gauge math, sub-agent nesting from `parent_session_id`, redaction marker rendering.
* Integration: oRPC calls through `callAs(staffAdmin)` succeed and `callAs(customerAdmin)` 403 on both list and events.
* Playwright (seeded 50 sessions): filter by character, open a session, expand a tool call, replay with keyboard to `seq` 42, flag as golden against a mocked eval endpoint, open permalink `?seq=42` and assert the row is in view; run at 375 and 1280.
* Performance: CDP trace scrolling a 10k-event session; assert ≥ 55 fps.
* Visual: Gate 3 baselines for grid, detail and stats at the seven widths, both themes.

**Demo**

Open `/_app/dev/prompt-log`, pick “Over $5”, open the top session, press space to autoplay, hit “jump to first tool error”, expand the call, click the PR link, copy the permalink and paste it in a new tab. Under two minutes.

**Edge cases**

* Running session: live status, timeline tails new events.
* Gaps: warning rows with the missing range.
* Fully redacted message: row shows kind counts.
* Expired blob: "content expired" with size.
* Grid engine unmerged: TanStack Table fallback with a documented TODO.

**Dependencies**

PAP-129, PAP-165 (hard, encoded; fallback for the grid). Soft: PAP-110, PAP-161, PAP-170, PAP-101, PAP-143, PAP-131. Consumed by PAP-134, PAP-98, PAP-144.

**Agent**

Built by Nova (Views Engineer) with Quill (Prompt Logger) defining reviewer needs. Reviewed by Sentinel (Visual Inspector, Code Reviewer) and Atlas.

**Size**

M: two screens over an existing API; virtualisation and replay are the work.
