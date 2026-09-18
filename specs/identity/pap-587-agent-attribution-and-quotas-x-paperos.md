---
identifier: "PAP-587"
title: "Agent attribution and quotas: `X-PaperOS-Actor` header, audit fields for character, session and issue, the `ActorBadge` component and per-character daily quotas emitting `agent.quota.exceeded`"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Agent"]
milestone: "Agent principals and enterprise"
state: "Backlog"
parent: "PAP-60"
children: []
blockedBy: ["PAP-586"]
blocks: ["PAP-146", "PAP-834", "PAP-913"]
key: "r4/identity/agent-attribution-quotas"
url: "https://linear.app/paperos/issue/PAP-587/agent-attribution-and-quotas-x-paperos-actor-header-audit-fields-for"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:12.204Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-587: Agent attribution and quotas: `X-PaperOS-Actor` header, audit fields for character, session and issue, the `ActorBadge` component and per-character daily quotas emitting `agent.quota.exceeded`

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Second half of PAP-60: make machine work visible and bounded. Every mutation by an agent records who, for which issue and session; every response says which actor served it; the badge renders the character everywhere an avatar would; and a per-character daily quota turns runaway spend into a 429 and an event PAP-111 consumes.

**Scope**

In: oRPC middleware writing `actorId`, `actorType`, `character`, `onBehalfOf?`, `sessionId`, `issueKey` into the audit context (PAP-38) and `X-PaperOS-Actor: agent:forge` on responses; `ActorBadge` in `packages/ui` (agent glyph and character colour from PAP-103, tooltip 'Forge (agent) on PAP-123', variants human, agent, agent on behalf of); table `agent_quota_usage (character, day, requests, cost_units)`, `ops/agents/quotas.yml`, event `agent.quota.exceeded`; docs section.

Out: Keys, scopes and CLI (sibling), presence visuals (PAP-146), cost controls and kill switch (PAP-111), delegation rules (PAP-594).

**Spec**

* Attribution middleware runs after auth; agent principals must send `X-PaperOS-Reason` (PAP-38) or receive `VALIDATION`; humans may omit it.
* Quota counted per character per UTC day from the middleware; exceeding returns 429 with `Retry-After` until midnight UTC and publishes `agent.quota.exceeded` once per day per character; overrides per issue via key metadata `quotaOverride` set by the orchestrator.
* `ActorBadge` sizes `sm|md`, colour tokens from PAP-66, `aria-label` 'Forge (agent)', reduced motion; stories for the three variants at 375 and 1280.
* Responses to humans acting via impersonation (PAP-61) show `X-PaperOS-Actor: human:<id> via staff:<id>`; agent on behalf of a human (PAP-594) shows `agent:forge for human:<id>`.

**Interface contract**

Provides: Attribution middleware, header `X-PaperOS-Actor`, `ActorBadge`, table `agent_quota_usage`, config `quotas.yml`, event `agent.quota.exceeded`.

Consumes: Keys and principals (sibling), audit sink (PAP-38, soft: mock), character glyphs and colours (PAP-103, soft), tokens (PAP-66), event bus (PAP-555, soft). Consumed by PAP-111, PAP-146, PAP-144 conflict banners, PAP-142 mentions, PAP-107 prompt log.

**Definition of done**

* Audit rows for agent mutations carry character, session and issue (test against PAP-38 or its mock); header present on every response.
* Daily quota exceeded emits the event and returns 429; midnight UTC rollover tested with a fake clock.
* `ActorBadge` stories at 375 and 1280 light and dark; axe clean; an agent comment in the example app shows the badge and tooltip (Playwright); changelog under Identity.

**Test plan**

* Unit: header rendering for the four actor shapes, quota arithmetic across midnight, reason requirement matrix.
* E2E: agent key from the sibling performs 3 mutations; audit rows and headers asserted; quota set to 2 in a test tenant produces a 429 on the third.

**Demo**

Post a comment with an agent key in the example app, hover the badge, then set `quotas.yml` to 2 for `forge` and watch the third call return 429 with the event in the log. Under 90 seconds.

**Edge cases**

* Quota config missing a character: default from `quotas.yml` `default` entry.
* Clock skew across API replicas: day boundary uses database `now()`.
* Badge for a renamed or unknown character: neutral glyph and the raw name.

**Dependencies**

Blocked by PAP-586 (hard). Soft: PAP-38, PAP-103, PAP-66, PAP-61, PAP-555. Blocks PAP-146.

**Agent**

Builder: Forge (Platform Engineer); Iris reviews the badge. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/data-layer/events-core` = PAP-555, `r4/identity/agent-keys` = PAP-586, `r4/identity/delegated-authority` = PAP-594.
