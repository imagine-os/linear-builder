---
identifier: "PAP-842"
title: "Build tenant-configurable business characters: persona, knowledge sources, allowed tools, audience and hours, extending the character schema with a tenant scope"
project: "assistant"
projectName: "Tenant AI Assistant & Business Agents"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Business characters, evals and swap"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-103", "PAP-104", "PAP-113", "PAP-134", "PAP-287", "PAP-838", "PAP-841"]
blocks: []
key: "r4/assistant/business-characters"
url: "https://linear.app/paperos/issue/PAP-842/build-tenant-configurable-business-characters-persona-knowledge"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:39.238Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-842: Build tenant-configurable business characters: persona, knowledge sources, allowed tools, audience and hours, extending the character schema with a tenant scope

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Let a tenant shape its own agents the way PaperOS shapes its builders: named characters ("Front Desk", "Bookkeeper", "Onboarding Guide") with a persona, knowledge sources, an allowed tool set, an audience and hours, defined in the same character schema as PAP-103 but stored per tenant, visible on the org chart (PAP-113), and selectable per surface so the portal widget and the staff panel can speak with different characters.

**Scope**

In: Character schema extension (PAP-103): `scope: 'platform'|'tenant'`, `tenantId`, `audience[]`, `surfaces[]`, `knowledge: { docs[], datasets[], helpCenter }`, `tools[]` (subset of the catalogue), `hours`, `handoff: { toCharacter?, toSupport }`, `voice`; stored in `tenant_character` with RLS; platform characters stay in `.claude/agents`. Console page `/console/assistant/characters` (spec) with list, editor (form view generated from the schema via PAP-124 patterns), test chat side panel, publish/unpublish, version history through PAP-134 objects (tenant characters are rules objects too). `CharacterPort.resolve(audience, surface, route)`: picks the published character for the context (portal → customer characters; console route prefix → staff characters), falling back to the default assistant. Org chart (PAP-113): tenant characters appear under a "Business agents" node with usage and spend from the prompt log; PAP-111 budgets per tenant character. Starter characters in business packs (PAP-427 `pack.yaml` gains `characters[]`) so a clinic gets a Front Desk and a Billing Assistant on day one.

Out: Characters running builder sessions (never; tenant characters only use `ActionPort`). Marketplace of characters (v0.3). Voice cloning.

**Spec**

* A tenant character can never hold tools outside the tenant allow-list or the audience's permissions; `tools[]` is intersected at resolve time and the editor shows the effective set
* Persona text passes the PAP-299 lint for instruction-injection patterns before publish ("ignore previous", "you are now") and is capped at 4k tokens
* Hours use the tenant timezone; outside hours the character answers with its handoff text and, for customers, escalates only
* Versioning: publishing creates an immutable version; conversations record the character version so the prompt log can replay the exact persona
* Evals: each starter character ships two golden tasks in `evals/assistant/characters/` graded nightly (PAP-310); a tenant character can run the "test chat" against the same graders on demand

**Interface contract**

Provides: `tenant_character` table and `characters.*` procedures, `CharacterPort` adapter, console page, org chart node, pack `characters[]` schema, starter characters for the five packs. Consumes: character schema and lead prompts (PAP-103, PAP-104), rules objects and history (PAP-134), org chart (PAP-113), budgets (PAP-111), spec editor patterns (PAP-124), pack format (PAP-426), portal and staff surfaces (own issues). Consumed by: commerce packs (starter characters), engagement (Front Desk answers booking questions), platform-ops (character spend in tenant health).

**Definition of done**

* Demo tenant has two published characters with different tool sets; the portal speaks as Front Desk and the console as Ops Assistant; org chart shows both with spend
* Publish blocked for a persona containing an injection pattern; effective tool intersection visible and tested
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: schema validation with tenant scope; resolve() precedence (route > surface > default); tool intersection; hours across DST.
* E2E: edit → test chat → publish → portal picks up the new version within one conversation; version history shows the diff.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Create "Front Desk" for the salon demo, give it booking tools and the help center, set hours, publish; open the portal as a customer and book through it; open the org chart and find its spend.

**Edge cases**

* Character deleted while conversations reference it: conversations keep the version snapshot; new turns fall back to the default assistant with a notice
* Two characters match the same route: the editor refuses to publish overlapping surfaces without an explicit priority
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-838 and PAP-841 (hard), PAP-103, PAP-104 (hard: schema), PAP-134, PAP-113 (soft), PAP-426 (soft: pack integration).

**Agent**

Builder: Nova. Reviewer: Atlas (Decomposer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/assistant/action-catalogue` = PAP-838, `r4/assistant/portal-assistant` = PAP-841.
