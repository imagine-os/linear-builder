---
identifier: "PAP-113"
title: "Build the agent org chart UI showing characters, sub-agents, current tasks, tools and access"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Agent", "Staff"]
milestone: "Agent org visible in app"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-98", "PAP-104", "PAP-132", "PAP-287", "PAP-288", "PAP-322"]
blocks: []
key: "agents/org-chart-ui"
url: "https://linear.app/paperos/issue/PAP-113/build-the-agent-org-chart-ui-showing-characters-sub-agents-current"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:16.883Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-113: Build the agent org chart UI showing characters, sub-agents, current tasks, tools and access

**Goal**

Make the agent org a first-class page in the product: an interactive org chart of characters and subs showing who reports to whom, what each is doing right now, what tools and access it holds and how much it has spent, drawn on the canvas engine so it can be rearranged, annotated and commented on like any other PaperOS canvas.

**Scope**

* In: route `/agents` with `specs/agents/org-chart.spec.yaml` and `character.spec.yaml`, `CharacterNode` component, oRPC `agents.roster` and `agents.status`, detail drawer with pause action, tree-list fallback under 768 px.
* Out: the status contract itself (PAP-288), the canvas engine (PAP-132), presence styling (PAP-146, consumed).

**Spec**

* Canvas on PAP-132: nodes for Justin, nine leads, 28 subs from `agents.roster`; ELK layered layout with manual nudges persisted per user in `canvas_layout`; edges for `reportsTo`; badges `idle | working(issueKey) | reviewing | paused | over-budget | killed | stale`.
* Live data: `agents.status` proxies the orchestrator `/status` (`SessionStatus[]` from PAP-288) and PAP-98 (`spentTodayUsd`, `dailyCapUsd`), polled every 10 s until PAP-146 pushes it.
* Drawer: role, prompt excerpt, tools and MCP servers, access scopes (PAP-106 matrix), skills, current session with elapsed time and cost, last five issues, memory link (PAP-109), handbook link (PAP-112), `Pause` and `Resume` calling PAP-111 through `agents.control` (permission `agents.control` from the access section).
* Responsive: under 768 px a collapsible tree list with the same badges and a full-screen sheet for the drawer. Nodes focusable in tree order; arrow keys move between siblings and levels; state in `aria-label`.

**Interface contract**

* Provides: `CharacterNode` in `packages/ui` with stories for seven states, procedures `agents.roster(): Character[]`, `agents.status(): SessionStatus[]`, `agents.control({ character, action: "pause" | "resume" })`, page specs consumed by PAP-122, the graph-loader pattern reused from PAP-123.
* Consumers: Justin (staff audience), PAP-102 (shares the character badge renderer), PAP-146 (pushes status over the realtime layer later).
* Requires: PAP-104 `roster.json`, PAP-288 `SessionStatus`, PAP-98 spend, PAP-111 control, PAP-132 canvas, PAP-106 matrix, PAP-152 focus management.

**Definition of done**

* Page specs validate; conformance tests pass.
* Storybook stories for all states, light and dark; axe passes.
* Screenshots at 320, 375, 768, 1024, 1280, 1920 and 2560 px in both themes.
* Live: start a session via Linear and watch the node switch to `working` within 10 s; pause from the drawer stops it (recording).
* Keyboard and screen-reader labels verified; Pages demo with mocked status; changelog; Linear comment.

**Test plan**

* Unit: badge derivation from `SessionStatus` (fake clock for `stale`), layout persistence, permission-gated pause button.
* Integration: `agents.status` against a mocked orchestrator including unreachable and orphan-character responses.
* e2e (Playwright): open, focus-navigate with arrows, open drawer, pause with a mocked control endpoint; run at 375 (tree list) and 1280 (canvas).
* Visual: seven-width matrix through gate 3; the 768 px switch asserted.

**Demo**

Open `/agents`, watch Forge's node turn `working` as a staging session starts, click it, read its current issue and spend, press `Pause` and see the badge flip and `/status` confirm. Two minutes.

**Edge cases**

* Orchestrator unreachable: "status unknown" with last-known time, no infinite spinner.
* More than six subs under a lead: collapsed by default.
* Character in status but not roster: orphan node with warning.
* Several concurrent sessions for one character: badge shows count; drawer lists all.
* Canvas library not chosen (PAP-132 pending): tree list ships first.

**Dependencies**

Blocked by PAP-104, PAP-132, PAP-288. Uses PAP-98, PAP-111, PAP-106. Soft: PAP-146.

**Agent**

Built by Nova (Canvas Cartographer sub-agent) with Iris (Component Crafter) on `CharacterNode`; reviewed by Sentinel (Visual Inspector).

**Size**

M
