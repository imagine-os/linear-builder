---
identifier: "PAP-839"
title: "Build the tables copilot: natural language to FilterTree, formula and view spec with a reviewable draft, plus \"explain this view\""
project: "assistant"
projectName: "Tenant AI Assistant & Business Agents"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Actions, copilots and portal assistant"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-161", "PAP-166", "PAP-172", "PAP-279", "PAP-382", "PAP-618", "PAP-624", "PAP-837"]
blocks: []
key: "r4/assistant/nl-to-views"
url: "https://linear.app/paperos/issue/PAP-839/build-the-tables-copilot-natural-language-to-filtertree-formula-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:29.647Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-839: Build the tables copilot: natural language to FilterTree, formula and view spec with a reviewable draft, plus "explain this view"

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Let anyone build a view or formula by describing it: "invoices over 30 days late grouped by customer, biggest first" becomes a validated `ViewSpec` draft shown beside the grid with the generated filter, sort and group visible in the PAP-166 builder, applied only on click; "average order value this quarter" becomes a formula that type-checks in PAP-382 before it is offered.

**Scope**

In: `packages/assistant/src/copilots/tables/`: `toFilterTree(text, datasetId)`, `toFormula(text, datasetId)`, `toViewSpec(text, datasetId, baseView?)`, `explainView(viewId)`; each uses constrained tool-use output (Zod schema of `FilterTree` PAP-279, `ViewSpec` PAP-161, formula AST PAP-382) and validates before returning; invalid output triggers one repair round then a friendly failure. Field resolution: dataset field names, PAP-126 terminology aliases and the PAP-39 registry feed a field lexicon into the prompt; ambiguous references produce a clarifying question card, not a guess. `view.toolbar.ask` slot fill: inline input in the view toolbar (PAP-343) that opens the draft in the filter builder with a diff against the current view; `Apply`, `Save as view` (PAP-172), `Discard`. Formula editor integration: `Ask` button in the CodeMirror editor (PAP-383) inserts the generated formula with an explanation comment; `explainFormula` in reverse.

Out: Creating datasets or fields (PAP-332). SQL generation (the compiler PAP-335 owns SQL; the copilot only emits the typed intermediate). Charts wording beyond the chart view spec.

**Spec**

* The copilot never emits SQL or bypasses the view compiler; output is always the typed intermediate the engine already validates and permission-filters
* Date phrases resolve through `chrono-node` relative to the user timezone (PAP-27) into `FilterTree` date ops; "this quarter" uses the tenant fiscal year from the finance settings (PAP-175) when present
* Drafts are stored as `view_draft` rows for 24 h so a reload keeps them; applying writes through the normal `views.update` with the assistant attribution
* Explain mode renders the current `FilterTree`, sorts and groups as one paragraph in the tenant terminology, cached per view version
* Portal customers get the copilot only on views shared to them (PAP-172) and only `toFilterTree`, never `Save as view`

**Interface contract**

Provides: `CopilotPort.toFilterTree|toFormula|toViewSpec|explain`, `view.toolbar.ask` fill, `view_draft` table, eval tasks `copilot-tables-*` for PAP-310. Consumes: `FilterTree` grammar (PAP-279), formula parser and type checker (PAP-382, PAP-383), view model and builder (PAP-161, PAP-166), sharing (PAP-172), terminology (PAP-126), timezone helpers (PAP-27). Consumed by: tables (toolbar), dashboards (block-level ask, PAP-386), engagement reports, commerce reports.

**Definition of done**

* Golden set of 60 utterances over the demo datasets: ≥85 percent produce a valid draft that matches the expected `FilterTree` or formula on first try; ≥97 percent after one repair; results tracked nightly in the eval report (PAP-310)
* Playwright: ask in the toolbar, see the diff in the filter builder, apply, save as view; formula insertion type-checks
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: schema-constrained output validation and repair loop with mocked model; date phrase resolution across timezones and DST; ambiguity detection when two fields share a synonym.
* E2E: draft survives reload; portal customer cannot save; explain paragraph updates when the view changes.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

On the invoices grid type "late more than 30 days, biggest first, by customer"; the filter builder shows the draft diff; apply, then click Explain on a saved dashboard view to read it back in plain English.

**Edge cases**

* Utterance references a field the user cannot see: the lexicon is built from readable fields only, so the copilot asks which field was meant instead of revealing the name
* Formula that references a relation two hops away: the copilot proposes a lookup or rollup field (PAP-340) as a prerequisite card instead of an invalid formula
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-837 (hard), PAP-279, PAP-382, PAP-161, PAP-166 (hard), PAP-172, PAP-126, PAP-27 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/assistant/staff-chat-panel` = PAP-837.
