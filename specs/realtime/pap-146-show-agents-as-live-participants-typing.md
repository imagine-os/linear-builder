---
identifier: "PAP-146"
title: "Show agents as live participants (typing, editing, reviewing) with distinct visual identity"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Agent", "Staff"]
milestone: "Scale and offline tested"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-60", "PAP-141", "PAP-475"]
blocks: []
key: "realtime/agent-presence"
url: "https://linear.app/paperos/issue/PAP-146/show-agents-as-live-participants-typing-editing-reviewing-with"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:58:05.711Z"
model: "claude-sonnet-5"
effort: "medium"
---

# PAP-146: Show agents as live participants (typing, editing, reviewing) with distinct visual identity

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Make Claude agents visible collaborators wherever a human would be: an agent editing a spec, typing a comment or reviewing a PR appears in presence with a distinct identity, its activity and a link to what it is doing, so machine work is seen while it happens.

**Scope**

In:

* Extend the PAP-141 payload with `agent?: { character, subAgent?, issueKey?, activity: reading|editing|typing|reviewing|waiting, sessionId }`.
* `packages/agents/src/presence-client.ts`: Node client used by PAP-107 hooks to join rooms with the agent's `pos_agent_` key, set activity from tool calls and leave on session end.
* `packages/ui`: `AgentAvatar` (square, character glyph and colour from PAP-103, "AI" mark), dashed cursor and caret, `ActivityChip` ("Forge is editing page.spec.yaml · PAP-42"), `AgentActivityPanel` in the staff console listing active agents with issue and prompt-log links.
* Page spec flag `realtime.agentPresence: staff|all|none` (default `staff`).

Out: agent chat, controlling agents (PAP-113), customer-facing disclosure copy.

**Spec**

* `toolCallToActivity(tool, args)` is pure; unknown tools → `waiting`; resets after 30 s.
* Rooms: `page:<tenant>:<route>` when the tool touches a file mapped by PAP-115's route index, else `issue:<tenant>:<issueKey>` so PAP-102 cards can show agents.
* Customers see only an "Assistant" avatar when `all`; never cursors.
* `aria-label="Forge (agent), editing"`; live region announces once.

**Interface contract**

Exposes: `AgentPresence` Zod extension merged into `PresenceState`; `createAgentPresenceClient({ apiKey, tenantId }) -> { join(room), setActivity(a), leave() }` for PAP-107 and PAP-96; `toolCallToActivity()`; components above; `useAgentsHere()`; flag in the page spec schema (PAP-114). Consumes: awareness transport and schema (PAP-141), `pos_agent_` keys and “Assistant” mapping (PAP-60, PAP-55), `characters.json` glyphs and colours (PAP-103, PAP-104), tool-call hook events (PAP-107), route index (PAP-115), board card slot (PAP-102), `promptlog.read` permission (PAP-129).

**Definition of done**

* An orchestrator session against staging shows the agent avatar on the target page and issue card within 2 s of the first tool call; screenshots at 1024 and 1920.
* Storybook stories for the three components in three themes; axe clean.
* `docs/platform/realtime/agent-presence.md` and handbook note (PAP-112); changelog; Linear comment with a video of an agent editing beside a human.

**Test plan**

* Vitest: `toolCallToActivity` table (Edit → editing, Read → reading, PR review → reviewing, unknown → waiting), payload validation, visibility per audience, 30 s reset with fake timers, `sessionId` keying for the same character twice.
* Integration: presence client joins a local Hocuspocus room with a test agent key and a customer `callAs` context sees only `{ name: 'Assistant' }`.
* Playwright: mocked awareness source injects two agents and one human; panel lists both with links; a customer context on the same page sees no cursors; run at 1024 and 1920.
* Visual: Gate 3 captures of `AgentAvatar` states and the panel in three themes; reduced motion has no pulse.

**Demo**

Start a `pnpm agent:demo-edit PAP-42` session; open the spec page and the PM board as staff; watch the square avatar and activity chip appear and change from reading to editing; click it and open the session in the prompt log. Under two minutes.

**Edge cases**

* 20 sessions on one issue: three avatars plus a count.
* Crash without leave: awareness timeout after 30 s, panel marks "lost".
* File without route mapping: shows on the issue only.
* Renamed character: neutral glyph.

**Dependencies**

PAP-141, PAP-60 (hard, encoded). Soft: PAP-103, PAP-104, PAP-107, PAP-102, PAP-115. Consumed by PAP-113, PAP-96.

**Agent**

Builder: Nova (CRDT Engineer) with Atlas (Dispatcher) wiring hooks. Reviewer: Iris (Component Crafter); Sentinel (Security Auditor) for audience rules.

**Size**

S: payload extension and components over existing presence.
