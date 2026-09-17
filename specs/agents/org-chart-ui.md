---
identifier: "PAP-113"
title: "Build the agent org chart UI showing characters, sub-agents, current tasks, tools and access"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff", "Agent"]
milestone: "Agent org visible in app"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-104", "PAP-132", "PAP-98"]
blocks: []
key: "agents/org-chart-ui"
url: "https://linear.app/paperos/issue/PAP-113/build-the-agent-org-chart-ui-showing-characters-sub-agents-current"
source: "plan/specs/bucket-3.json (round-1 canonical spec JSON)"
---

# PAP-113: Build the agent org chart UI showing characters, sub-agents, current tasks, tools and access

**Goal**

Make the agent org a first-class page in the product: an interactive org chart of characters and sub-characters showing who reports to whom, what each is doing right now, what tools and access it holds, and how much it has spent, drawn on the canvas engine so it can be rearranged, annotated and commented on like any other PaperOS canvas.

**Scope**

In:
- Route `/agents` with page spec `specs/agents/org-chart.spec.yaml` (staff and agent audiences; read-only for agents) and `specs/agents/character.spec.yaml` for the detail drawer.
- Canvas built on `collab/canvas-view`: nodes for Justin, nine leads and 28 subs from `roster.json` (fetched via oRPC `agents.roster`), tree layout (dagre or ELK auto-layout with manual nudges persisted per user), edges for `reportsTo`, badge overlays for state: idle, working (with issue key), reviewing, paused, over budget, killed.
- Live data: `agents.status` oRPC procedure proxying the orchestrator `/status` (active sessions, current issue, elapsed time) and `pm-linear/credit-metering` (`spentTodayUsd`, `dailyCapUsd`), polled every 10 seconds or pushed over the realtime layer when `realtime/agent-presence` lands.
- Detail drawer on click: role, prompt excerpt, tools and MCP servers, access scopes (from the privilege matrix), skills, budgets with a progress bar, last five sessions with cost and links to Linear issues and prompt logs, memory file link, handbook link, eval trend sparkline (`agents/eval-harness`).
- Actions for staff with permission: pause/resume character (calls the kill switch scope `character`), open its Linear queue (filtered link), request a mention reply.
- Filters: by lead, by state, by tool (highlight every character holding `stripe:*`); search box.
- Comments anchored to nodes via `collab/comments` when available (falls back to hidden).

Out: editing the roster from the UI (YAML plus PR remains the source of truth), historical time-travel of the org, per-user avatars beyond generated initials.

**Spec**

- Node component in `packages/ui` (`CharacterNode`: name, role line, state badge, budget ring) with stories for every state; distinct visual identity for agents (dashed border, bot glyph) consistent with `realtime/agent-presence`.
- Layout persisted in a `canvas_layout` record per user; "reset layout" action.
- Data contracts: `agents.roster` returns the schema type from `agents/character-schema`; `agents.status` returns `{character, state, issueKey?, sessionId?, startedAt?, spentTodayUsd, dailyCapUsd, lastHeartbeat}`.
- Responsive: under 768 px the canvas becomes a collapsible tree list with the same badges; the drawer becomes a full-screen sheet.
- Accessibility: nodes are focusable in tree order, arrow keys move between siblings and levels (`input/focus-management`), state announced via `aria-label`.

**Definition of done**

- Page spec validates; conformance tests pass.
- Storybook stories for `CharacterNode` in all six states, light and dark; axe passes.
- Playwright screenshots at 320, 375, 768, 1024, 1280, 1920 and 2560 px in both themes attached.
- Live demo on staging: start a session via Linear and watch the node switch to working within 10 seconds; pause from the drawer stops it (recording).
- Keyboard navigation and screen-reader labels verified.
- GitHub Pages demo with mocked status; changelog entry; Linear comment with demo, screenshots and recording.

**Edge cases**

- Orchestrator unreachable: nodes show "status unknown" with the last-known time, no spinner forever.
- 100+ sub-characters in future: collapse subs under a lead by default when more than 6.
- Character present in status but missing from roster (stale build): render as an orphan node with a warning.
- Two sessions for one character concurrently (perCharacter 3): badge shows count; drawer lists all.
- Budget cap zero (paused character): ring shows paused, not 0/0 error.
- User without permission clicks pause: button disabled with tooltip; permission from the page spec access section.
- Canvas library not chosen yet (`collab/collab-research` pending): the tree list mode ships first and the canvas mode follows.

**Dependencies**

- `agents/roster-v1` (roster.json, states).
- `collab/canvas-view` (canvas engine) and through it `spec-builder/schema`; also `pm-linear/credit-metering` and `agents/cost-controls` endpoints, `realtime/agent-presence` optional.

**Agent**

Built by Nova (Canvas Cartographer sub-agent) with Iris (Component Crafter) for `CharacterNode`; reviewed by Sentinel (Visual Inspector, Code Reviewer) and Atlas for data accuracy.

**Size**

M: one canvas page, one drawer and two procedures over existing engines.
