---
identifier: "PAP-695"
title: "Create Linear initiatives for the v0.1.0 release, the v0.2 deferred set and the four brief themes; attach the eighteen projects and let Atlas post initiative updates"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P0"
type: "Infra"
priority: 2
surfaces: ["Staff"]
milestone: "Linear configured for the pipeline"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-91"]
blocks: ["PAP-698"]
key: "r4/pm-linear/linear-initiatives-rollup"
url: "https://linear.app/paperos/issue/PAP-695/create-linear-initiatives-for-the-v010-release-the-v02-deferred-set"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:26.370Z"
model: "claude-sonnet-5"
effort: "low"
estimate: 2
dueDate: "2026-09-20"
cycle: null
---

# PAP-695: Create Linear initiatives for the v0.1.0 release, the v0.2 deferred set and the four brief themes; attach the eighteen projects and let Atlas post initiative updates

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Infra S

**Goal**

The workspace has zero initiatives and no roadmap, so Justin's only rollup above a project is the Blueprint document. Initiatives are the Linear layer where eighteen projects become five lines with progress bars: the Oct 1 release, the deferred v0.2 set, and the brief's themes (developer tooling core, quality and review, agent org, business plumbing). They also give the weekly project update a parent to roll into.

**Scope**

* In: `ops/linear/configure-initiatives.ts` (create-only, idempotent by name) in the PAP-91 script family: initiatives `PaperOS Core Platform v0.1.0 (Oct 1)`, `PaperOS v0.2 (deferred)`, `Theme: developer tooling core`, `Theme: quality and review`, `Theme: agent org`, `Theme: business plumbing`; `initiativeToProjectCreate` links per `plan/plan.json` theme mapping; initiative descriptions from the Blueprint sections; ids in `linear-workspace.json`; docs section "Initiatives".
* Out: sub-initiatives, initiative updates content (the project-updates issue posts them), roadmaps (initiatives replace them), changing project names.

**Spec**

* Theme mapping (a project may sit in several): tooling core = app-shell, data-layer, forge, identity, design-system, spec-builder, module-system, libraries, collab, realtime, input, tables; quality and review = quality; agent org = pm-linear, agents; business plumbing = business-core, growth, migration; release = all eighteen; v0.2 = the projects owning `Deferred` issues, with the deferred issue count in the description.
* Initiative fields: `name`, `description` (one paragraph from the Blueprint plus the milestone exit criteria), `targetDate` (2026-10-01 for the release, 2026-10-31 for v0.2), `status` `Active`, `owner` the Linear admin user (bot users cannot own initiatives on the Basic plan; documented).
* Create-only: the script never updates or deletes an initiative a human made; drift is reported as `manual`; `linear-workspace.json.initiatives` holds ids.
* Blueprint document gains a "Roll-up" line linking the release initiative; PAP-95's PAP-5 table links the release initiative as the top-level scoreboard.

**Interface contract**

* Provides: initiative ids in `linear-workspace.json`, the theme mapping in `plan/plan.json` (`themes[]`), `pnpm linear:configure --initiatives`.
* Consumes: PAP-91 script and ids, `plan/plan.json`, Linear API `initiativeCreate`, `initiativeToProjectCreate`.

**Definition of done**

* Six initiatives exist with the right projects; screenshot of the Initiatives page at 1280 px and on a phone.
* Second run is a no-op; `--check` clean; changelog; Linear comment with the mapping table.

**Test plan**

* Unit: theme mapping completeness (every project in the release initiative), idempotency on names.
* E2E: live create on the workspace; re-run no-op.

**Demo**

Open Initiatives in Linear: `PaperOS Core Platform v0.1.0 (Oct 1)` with eighteen projects and a progress bar fed by the new estimates. Under one minute.

**Edge cases**

* Initiatives unavailable on the plan: script prints the upgrade note and exits 0 without drift (documented on NJ-1's issue).
* A project renamed by Justin: mapping by project id from `linear-workspace.json`, not by name.
* Deferred set changes at NJ-14 or NJ-19: description regenerated on `--apply`; the initiative itself never recreated.

**Dependencies**

Hard: PAP-91. Soft: PAP-95, docs/blueprint.md.

**Agent**

Builder: Atlas (Dispatcher). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.
