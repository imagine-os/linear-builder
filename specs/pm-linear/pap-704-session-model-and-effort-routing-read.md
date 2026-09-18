---
identifier: "PAP-704"
title: "Session model and effort routing: read the issue's Model and Effort labels, map to SDK options with a documented fallback chain on overload or refusal, record the served model in the footer and `usage_events`"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Orchestrator claims and ships issues"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-281", "PAP-282"]
blocks: ["PAP-98", "PAP-243"]
key: "r4/pm-linear/session-model-and-effort-routing"
url: "https://linear.app/paperos/issue/PAP-704/session-model-and-effort-routing-read-the-issues-model-and-effort"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:25.514Z"
model: "claude-opus-5"
effort: "high"
estimate: 2
dueDate: "2026-09-22"
cycle: null
---

# PAP-704: Session model and effort routing: read the issue's Model and Effort labels, map to SDK options with a documented fallback chain on overload or refusal, record the served model in the footer and `usage_events`

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build S

**Goal**

CLAUDE.md says a session runs on the model named by the issue's `Model` label at the `Effort` label, falling back to Sonnet 5 / medium; PAP-282 says `model` comes from `roster.json`; PAP-243 hard-codes Fable 5.1 for reviewers. Justin asked to switch models per job and to see cost per chunk, which is impossible until one place resolves the model, applies the effort, handles overloads and writes what actually ran.

**Scope**

* In: `src/session/model-routing.ts`: `resolveModel(issue, character, role: 'builder'|'reviewer'|'qa'): { model, effort, source }`, label parsing (`Model: Fable 5.1|Opus 5|Sonnet 5|Haiku 4.5`, `Effort: low|medium|high|max`), map to model ids and to SDK options (`model`, `effort` or thinking budget per the `claude-api` skill table), fallback chain on HTTP 529 or 429 and on refusal stops, served-model capture from SDK messages into `sessions.model_served` and PAP-98 `usage_events.model`, footer field `model`, `docs/pm/model-routing.md`.
* Out: choosing the labels (planning rounds and Atlas), pricing (PAP-98), the reviewer definitions (PAP-243 consumes `resolveModel`), character prompts naming models (forbidden by PAP-285).

**Spec**

* Precedence: issue labels; else the character's `model` and `effort` from `roster.json` (PAP-103); else Sonnet 5 / medium; the chosen `source` is logged and shown in the `Session started` comment.
* Reviewer role (cost doc section 4b): Opus 5 / high after an Opus or Fable builder, Sonnet 5 / high after a Sonnet builder; QA gate Haiku 4.5 / low; release-candidate reviews Fable 5.1 / high; `xhigh` in character files maps to `high` until the label set grows.
* Fallback chain on overload (529) or rate limit (429) after three backoff attempts within five minutes: Fable 5.1 to Opus 5 to Sonnet 5; Haiku stays Haiku; a fallback never goes up; the session prompt is unchanged and the footer records `modelServed` and `fallbackReason`; a refusal stop never triggers a fallback (PAP-282 rule: record and escalate).
* Cost: `usage_events.model` is the served model, so PAP-98 prices correctly and the burn report shows planned versus served model counts; the chunk progress report (round-4 issue) uses the same field.
* Validation: `pnpm linear:configure --check` warns when an issue has one of the two labels but not the other; PAP-93 gains `MODEL_LABELS_INCOMPLETE` (warn).

**Interface contract**

* Provides: `resolveModel()`, SDK option mapping table, fallback chain constant, footer field `model` and `modelServed`, `sessions.model_served`, validator code `MODEL_LABELS_INCOMPLETE`.
* Consumes: PAP-281 labels and ids, PAP-282 `launchSession` options, PAP-103 roster fields, PAP-98 `recordUsage`, PAP-92 footer schema, the `claude-api` skill's model table for ids and effort semantics.

**Definition of done**

* Twenty fixture issues (all label combinations, missing labels, umbrella) resolve to the expected model and effort with the right `source` (table).
* Mocked 529 storm triggers the fallback after three attempts and the footer shows `modelServed: claude-opus-5, fallbackReason: overloaded`; a refusal does not fall back (tests).
* Live: one rehearsal issue per label pair runs and `usage_events.model` matches (recording of the burn report line); docs; changelog; Linear comment.

**Test plan**

* Unit: label parser, precedence, 4b reviewer table, fallback state machine with fake timers, footer serialisation.
* E2E: mocked SDK stream with overload responses; live rehearsal sessions.

**Demo**

Move a rehearsal issue labelled `Model: Opus 5`, `Effort: high` to Ready; read the `Session started` comment naming the model and source; flip the mock to return 529 and watch the footer show the fallback. Under two minutes.

**Edge cases**

* Label names a model the price table lacks: resolve fails closed to Sonnet 5 / medium with a `PRICE_UNKNOWN` warning (PAP-98 flag).
* Character file says Fable 5.1 for a Sonnet-labelled issue: labels win; the comment says so.
* Sub-agent spawned by the session: inherits the served model unless its own character sets a cheaper one (never dearer).
* Anthropic deprecates a model id: the table carries `deprecatedAfter`; the router warns thirty days ahead.

**Dependencies**

Hard: PAP-281, PAP-282. Soft: PAP-103, PAP-98, PAP-92, PAP-93, PAP-243.

**Agent**

Builder: Atlas (Dispatcher). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.
