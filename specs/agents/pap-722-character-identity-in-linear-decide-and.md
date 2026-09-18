---
identifier: "PAP-722"
title: "Character identity in Linear: decide and configure how characters appear as assignees, commenters and project leads (per-character seats versus one OAuth actor with `Character:` attribution), with the Needs Justin cost card"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P0"
type: "Infra"
priority: 2
surfaces: ["Agent"]
milestone: "Roster defined and installed"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-48", "PAP-91", "PAP-521"]
blocks: ["PAP-113"]
key: "r4/agents/character-linear-identity-and-attribution"
url: "https://linear.app/paperos/issue/PAP-722/character-identity-in-linear-decide-and-configure-how-characters"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:20.470Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-24"
cycle: null
---

# PAP-722: Character identity in Linear: decide and configure how characters appear as assignees, commenters and project leads (per-character seats versus one OAuth actor with `Character:` attribution), with the Needs Justin cost card

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

PAP-281 assigns issues to `botUser(character)`, PAP-108 switches assignees between characters, PAP-113 links badges to `assignee_id`, and no issue in the workspace has an assignee because no such users exist: Linear has one human member and two OAuth app users. Per-character seats cost money on the Basic plan and an OAuth actor cannot be assigned. This issue decides the identity model, files the one card Justin must answer, and configures whichever path he picks so every consumer stops assuming bot users that do not exist.

**Scope**

* In: `docs/pm/character-identity.md` (options, costs, decision), the Needs Justin card, configuration for the chosen path: (A) nine Linear member seats named after the leads with avatars, API keys minted for the orchestrator and stored in sops (PAP-25), `linear-workspace.json.characters.<name>.userId`; or (B) a single `PaperOS Orchestrator` OAuth actor (`actor=app` with `createAsUser` display names) plus `Character/<Name>` labels for routing and `Character:` trailers for attribution, assignee left to Justin or unset; adapters in `botUser(character)` (PAP-281) and `agents.roster` (PAP-113) for both paths; the `Character/*` label group creation moved here from PAP-91 if not yet done.
* Out: forge bot accounts (PAP-48), agent principals in PaperOS (PAP-60), the org chart rendering (PAP-113).

**Spec**

* Card `Decision needed: Linear identity for the nine characters`: option A nine seats (cost at the Basic per-seat price, real assignees, native filters by assignee, per-character API keys and audit), option B one OAuth actor with `createAsUser` names (no seat cost, comments show the character name, no assignee, routing by label), option C hybrid (seats for Atlas and Sentinel only); recommendation A if the seat price is acceptable, else B; default after 48 h: B.
* Path A: `linear-workspace.json.characters` maps name to user id; the orchestrator uses per-character API keys through the broker (PAP-300); `assigneeId` set on claim; `Pipeline: <Character>` views filter by assignee.
* Path B: all mutations through the orchestrator key with `createAsUser: '<Character>'` and `displayIconUrl`; `Character/<Name>` label set on claim; `assigneeId` untouched; `Pipeline: <Character>` views filter by label; PAP-108 assignee switching becomes label switching.
* Either path: `botUser(character)` returns `{ userId?, label, displayName, iconUrl }` and consumers branch on presence of `userId`; PAP-113 reads the same map; the handbook (PAP-112) documents how to filter by character.

**Interface contract**

* Provides: `characters` map in `linear-workspace.json`, `botUser()` shape, the decision document, `createAsUser` convention for path B.
* Consumes: PAP-91 script and label group, PAP-48 naming of bots (same names on forges), PAP-94 card, PAP-300 key storage, PAP-281 and PAP-113 as consumers.

**Definition of done**

* Card answered by Justin; the chosen path configured; a rehearsal claim shows the character as assignee (A) or as comment author with label (B) (screenshot).
* `botUser()` adapter tested for both paths; PAP-281, PAP-108 and PAP-113 gain comments naming the path; docs; changelog.

**Test plan**

* Unit: adapter shape per path, label and view filter generation, map validation.
* E2E: rehearsal claim on team PAP after configuration.

**Demo**

Open a rehearsal issue after a claim: either Forge's avatar in the assignee field or a comment authored as `Forge` with the `Character/Forge` label; open `Pipeline: Forge`. Under one minute.

**Edge cases**

* Justin picks A later after starting with B: migration script sets assignees from labels; labels stay.
* Seat removed to save cost: adapter falls back to B for that character with a warning.
* `createAsUser` unsupported for a mutation type: comment prefixed `[Forge]` as a last resort, documented.
* Two characters share a display name with a human (none today): names carry the `(agent)` suffix.

**Dependencies**

Hard: PAP-91, PAP-48. Soft: PAP-94, PAP-300, PAP-281, PAP-108, PAP-113, PAP-112.

* Soft dependency (round 4): PAP-281 is a soft dependency, not a `blocks` relation, because this issue's milestone (2026-09-24) is later than PAP-281's (2026-09-22); build against its interface and reconcile when it lands.
  **Agent**

Builder: Atlas (Dispatcher). Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.
