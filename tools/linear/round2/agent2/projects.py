"""Append a Contract section to the three project descriptions (content field), with links to the pending-issue documents."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r2
DRY = "--dry" in sys.argv
ch = r2.load_changes(); ch.setdefault("projectsUpdated", [])
cur = json.load(open(r2.R2 + "/_proj_content_2.json"))
byid = {v["id"]: v for v in cur.values()}
DOCS = {d["project"]: d["url"] for d in ch.get("documents", [])}

CONTRACTS = {
"pm-linear": f"""

## Contract

**Provides**

* Workspace as code (PAP-91): `linear-workspace.json` with every state, label, template and project id; `pnpm linear:configure --check|--apply`; the `Character/*` label group. Decisions record (`[pm-linear/workspace-reconcile]`): `Todo` stays as human parking, surfaces stay ungrouped and one or more are required, Size lives in the description.
* Session playbook (PAP-92): `.claude/rules/session-playbook.md`, `session-footer.schema.json`, comment templates, `playbookVersion`.
* Issue contract (PAP-93): `validateIssue()`, `parseSections()`, `parseFilesGlobs()`, violation codes, the `needs-contract` bounce; every issue in `Ready for Claude` passes it.
* Justin queue (PAP-94): `requestDecision()`, `DecisionCard`, reply grammar `approve | reject | option n | defer nd | ask:`, five-slot governor, daily digest.
* Orchestrator (PAP-96 and children `[pm-linear/orchestrator/*]`): `claimNext()`, `launchSession()`, `linearComment()`, tables `sessions`, `claims`, `events`, `GET /status`, `POST /admin/drain|resume`, typed event bus `issue.claimed`, `session.started`, `session.ended`, `pr.detected`.
* Webhooks (PAP-97): `registerWebhookHandler()`, `postPrStatus()` with `PrStatus` (gates, screenshots, verdicts), verified Linear, GitHub and Forgejo receivers. Metering (PAP-98): `recordUsage()`, `spent()`, `remaining()`, `liveTotal()`, `budgets` table, `pnpm burn`, daily burn report. Scheduler (PAP-99): `buildGraph()`, `eligible()`, `next()`, `Files:` conflict rule, caps per repo and character.
* PM module (PAP-100, PAP-101 and children `[pm-linear/linear-sync/*]`, PAP-102): `@paperos/pm` tables and `pm.*` procedures, `pm_external_ref`, `pm.sync.status()`, `/pm/board|list|timeline`, Linear-wins conflict rule.
* Planned (specs in the pending document): weekly plan re-audit `[pm-linear/weekly-reaudit]`, inbound triage `[pm-linear/inbound-triage]`.

**Requires**

* forge: branch policy and worktree conventions (PAP-46), PR template (PAP-49), bot accounts (PAP-48, soft with a single-bot fallback).
* app-shell: VPS and Coolify (PAP-25), env and secrets conventions (PAP-17).
* agents: `roster.json` and prompts (PAP-104), bundles (PAP-106), `SessionStatus` contract `[agents/session-observability]`, sandbox `[agents/runtime-sandbox]`, handoff schema (PAP-108), budgets (PAP-111).
* quality: gate artifact schemas (PAP-239), screenshot naming (PAP-82), rubrics (PAP-79).
* data-layer: core entities (PAP-33), RLS (PAP-34), oRPC (PAP-35), jobs (PAP-43), Postgres for the orchestrator schema (PAP-30). identity: agent principals (PAP-60). tables: kanban (PAP-167), grid (PAP-165), filters (PAP-166). collab: prompt-log store (PAP-129) for hook sessions.

**Milestone exit criteria**

* Linear configured for the pipeline (2026-09-18): PAP-91 `--check` clean on the live team; PAP-92 dry run produces three valid footers; PAP-93 `contract:audit` reports zero errors on all issues and one live bounce is recorded; PAP-94 doc merged and grammar fixtures green; PAP-95 leaves PAP-5 as the linked scoreboard. `[pm-linear/workspace-reconcile]` created and Done as soon as the issue limit is lifted.
* Orchestrator claims and ships issues (2026-09-22): a real `Ready for Claude` issue becomes a worktree, a session, a PR and `In Review` with a status comment and screenshots (PAP-96 children, PAP-97); restart recovery proven; three daily burn reports posted (PAP-98); scheduler simulation over the live graph conflict-free (PAP-99).
* PM module syncs both ways (2026-09-30): PAP-100 migration and RLS test green; PAP-101 round trip with Linear winning a staged conflict and a clean PAP backfill; PAP-102 board drag changes the Linear issue within 10 s at the seven-width screenshot matrix.

**Pending issues**

Linear rejected new issues on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free plan, 275 issues). Nine fully specified issues for this project (three gaps, six children of PAP-96 and PAP-101) are stored in [Round 2 pending issues: pm-linear]({DOCS.get("pm-linear", "")}) and are created by `round2/agent2/create_new.py` once the plan is upgraded. Decision for Justin: upgrade the Linear workspace plan so the queue can grow past 250 issues.
""",
"agents": f"""

## Contract

**Provides**

* Character schema (PAP-103): `@paperos/agents/schema` with `CharacterSchema`, `RosterSchema`, `SCOPES`, `KNOWN_TOOLS`, `validateRoster()`, JSON Schema for YAML authoring.
* Roster (PAP-104 and children `[agents/roster-v1/*]`): 37 character YAML files, nine lead and 28 sub prompts with shared fragments, `.claude/agents/*.md`, `dist/roster.json`, `pnpm agents build --check`, `pnpm agents tree`, smoke results.
* Skills (PAP-105): `.claude/skills/{{page-from-spec,review-pr,screenshot-audit,write-adr,linear-update}}`, `skills.json`, `pnpm skills lint`, the `linear-update` CLI contract.
* Least privilege (PAP-106): per-character bundles (`settings.json`, `.mcp.json`, `hooks.json`), `loadBundle()`, `secretsFor()`, the `enforce-scope` hook, privilege matrix. Sandbox `[agents/runtime-sandbox]`: `runInSandbox()`, egress allowlists, resource limits.
* Prompt logging (PAP-107): `LogEvent` schema, `redact()`, spool and shipper into PAP-129. Handoffs (PAP-108): `HandoffSchema`, `HANDOFF.md`, `pnpm handoff lint`, `kind -> state` mapping. Memory (PAP-109): `loadMemory()`, `applyMemoryBlock()`, the `paperos-memory` block.
* Evals (PAP-110, relabelled Build, children `[agents/eval-harness/*]`): `pnpm evals run|list|report`, `eval_runs` table, judge schema, regression issue template. Cost controls (PAP-111): `preflight()`, `kill()`, `resume()`, `KILL` grammar, `budget-hold` label. Handbook (PAP-112) with `@character` mentions. Org chart (PAP-113): `CharacterNode`, `agents.roster|status|control`.
* Session status `[agents/session-observability]`: `SessionStatus` type, heartbeats, `stuck` detection, OTel `paperos.*` attributes, `/status.sessions`.

**Requires**

* pm-linear: playbook footer (PAP-92), orchestrator launch path and `/status` route (PAP-96), webhooks (PAP-97), metering (PAP-98), decision cards (PAP-94), workspace ids (PAP-91).
* forge: bot accounts (PAP-48, soft), branch protection (PAP-46), runners (PAP-50). app-shell: VPS (PAP-25), secrets conventions (PAP-17).
* collab: prompt-log store (PAP-129), docs engine (PAP-128), decision log (PAP-130), canvas view (PAP-132). quality: rubrics (PAP-79), gate 1 job slots (PAP-78), finding schema (PAP-239). libraries: MCP catalog (PAP-210). data-layer: OTel collector (PAP-40), MinIO (PAP-37). realtime: agent presence (PAP-146, soft).

**Milestone exit criteria**

* Roster defined and installed (2026-09-20): PAP-103 validator green; `pnpm agents tree` matches plan.json; `.claude/agents` committed with `--check` in gate 1 and nine smoke rows green (PAP-104 children); five skills lint and dry-run (PAP-105); probe suite green for 37 characters (PAP-106); a 20-turn session logged end to end (PAP-107, spool-only until PAP-129 lands). `[agents/runtime-sandbox]` probes green as soon as it can be created.
* Sub-agents, skills and evals live (2026-09-25): four-comment handoff dry run switches assignees automatically (PAP-108); second session uses a recorded gotcha (PAP-109); nightly eval baseline posted and one seeded regression detected (PAP-110 children); `KILL ALL` stops three sessions in five seconds (PAP-111); handbook renders with generated tables (PAP-112); `/status.sessions` validates and a stalled session flips to `stuck` `[agents/session-observability]`.
* Agent org visible in app (2026-09-30): PAP-113 node turns `working` within 10 s of a Linear claim, pause works from the drawer, seven-width screenshots in both themes.

**Pending issues**

Linear rejected new issues on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free plan). Nine fully specified issues for this project (two gaps, four children of PAP-104, three of PAP-110) are stored in [Round 2 pending issues: agents]({DOCS.get("agents", "")}) and are created by `round2/agent2/create_new.py` once the plan is upgraded.
""",
"spec-builder": f"""

## Contract

**Provides**

* Schema (PAP-114): `@paperos/spec` with `PageSpecSchema`, `ComponentRef`, `RouteRef`, `SpecIssue`, `parseSpec()`, `migrateSpec()`, JSON Schema, `specVersion`.
* Validator (PAP-115): `paperos-spec validate|routes`, `validateSpecs()` library API, `defineRule()`, rule codes `SPEC_*`, baseline file, GitHub annotations for gate 1.
* Sections: access (PAP-116) `toPolicies()`, `accessMatrix()`, `spec-policies.json`; app spec (PAP-117) `AppSpecSchema`, `resolvePage()`, generated navigation and entities; data (PAP-119 and children `[spec-builder/data-section/*]`) `DataSectionSchema`, `gen:data`, hooks `use<Query>()` and `dataStates`; integrations (PAP-121) `ConnectorSchema`, registry, `requiredEnvVars()`.
* Codegen (PAP-120 and children `[spec-builder/layout-codegen/*]`): `gen:page`, `Printer`, two-file ownership, `data-spec-key` and `data-action` attributes, state switch. Conformance (PAP-122): `gen:tests`, `reports/spec-conformance.json`. Flow graph (PAP-123): `FlowGraphSchema`, `buildFlowGraph()`, `diffGraphs()`, `flow-graph.json`.
* Authoring skill (PAP-118): `author-spec` scripts `context | commit | open-issue`. Editor (PAP-124 and children `[spec-builder/spec-editor-ui/*]`): `specs.list|get|save|validate`, `SpecForm`, `SpecPreview`. Docs and examples (PAP-125): three executable example specs, `docs/spec/workflow.mdx`. Business profile (PAP-126): `BusinessProfileSchema`, `industries.yaml`, `t.term()`, `useBusinessProfile()`.
* Planned (pending document): spec i18n `[spec-builder/spec-i18n]` (`MessageRef`, `gen:messages`, pseudo-locale rule) and versioning tooling `[spec-builder/spec-versioning]` (`Codemod` API, `paperos-spec migrate`, `x-deprecated`).

**Requires**

* design-system: component registry and resolver (PAP-74), state components (PAP-234), layout (PAP-70), data display (PAP-71), Storybook (PAP-69), tokens (PAP-66).
* data-layer: shared filter grammar (PAP-279), oRPC contract and client (PAP-35), Electric and PGlite (PAP-36), audit log (PAP-38), Drizzle schema (PAP-32).
* identity: `Policy` and `can()` (PAP-59), audience model (PAP-55), permission matrix report (PAP-64 consumes). quality: gate 1 (PAP-78), test-mode login and seeds (PAP-240), screenshot matrix (PAP-82), video flows (PAP-83), artifact schemas (PAP-239).
* app-shell: router and layout slots (PAP-16), i18n catalogs (PAP-27), feature modules (PAP-28, PAP-264), kiosk template (PAP-23). collab: canvas (PAP-132), docs engine (PAP-128), decision log (PAP-130). libraries: MCP catalogue (PAP-210). agents: skills format and `linear-update` (PAP-105). forge: trailers (PAP-46), PR template (PAP-49), Forgejo client (PAP-276). input: command registry (PAP-151), focus (PAP-152), drag-drop (PAP-155).

**Milestone exit criteria**

* Spec schema and validator (2026-09-22): PAP-114 fixtures and JSON Schema committed with drift in gate 1; PAP-115 green on the template and red on a seeded PR on both forges under 2 s for 300 specs; PAP-116 property test agrees with `can()`; PAP-117 navigation renders from the generated file for two audiences; PAP-118 dry run yields a valid spec, PR and contract-valid issue.
* Codegen and conformance tests (2026-09-26): PAP-119 children deliver hooks with the two-context live update and offline replay; PAP-120 children generate the three examples byte-identically with the seven-width screenshot matrix; PAP-121 eleven connectors and the env boot check; PAP-122 mutated spec turns gate 1 red; PAP-123 graph renders and diffs.
* Spec editor UI (2026-09-30): PAP-124 children pass the edit-validate-save-PR flow with a keyboard-only recording; PAP-125 three examples executable and a fresh session writes a fourth spec from `workflow.mdx`; PAP-126 profile switch changes labels in two locales. Pending i18n and versioning issues may land after 2026-10-01 without blocking anything.

**Pending issues**

Linear rejected new issues on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free plan). Eleven fully specified issues for this project (two gaps, nine children of PAP-119, PAP-120 and PAP-124) are stored in [Round 2 pending issues: spec-builder]({DOCS.get("spec-builder", "")}) and are created by `round2/agent2/create_new.py` once the plan is upgraded.
""",
}

for key, pid in r2.PROJECTS.items():
    if pid in ch["projectsUpdated"]: print("skip", key); continue
    content = byid[pid]["content"] or ""
    if "## Contract" in content: print("already has contract", key); continue
    new_content = content.rstrip() + CONTRACTS[key]
    print(key, "words", r2.words(new_content))
    if DRY: continue
    d = r2.gql("mutation($id: String!, $i: ProjectUpdateInput!) { p: projectUpdate(id: $id, input: $i) { success } }", {"id": pid, "i": {"content": new_content}})
    if d["p"]["success"]:
        ch["projectsUpdated"].append(pid); r2.save_changes(ch); print("updated project", key)
