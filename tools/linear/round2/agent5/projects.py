import os
"""Append a Contract section to the two project descriptions (content field)."""
import sys, json
sys.path.insert(0, os.environ.get("PAPEROS_PLAN_DIR", ".") + "/round2/agent5")
import r5
DRY = "--dry" in sys.argv
ch = r5.load_changes()
cur = json.load(open(r5.R2 + "/_proj_content_5.json"))["data"]
CUR = {cur["a"]["id"]: cur["a"], cur["b"]["id"]: cur["b"]}
DOCS = {d["project"]: d["url"] for d in ch.get("documents", [])}

CONTRACTS = {
"migration": f"""

## Contract

**Provides**

* Research (PAP-198): `docs/migration/sources/<source>.md` sheets, `field-type-matrix.md`, `sources/index.json` (`{{ source, rateLimit, incremental, attachmentExpiry }}`), anonymised fixtures under `packages/import/fixtures/`.
* Framework (PAP-199, work packages WP1-WP3): `SourceConnector`, `SourceSchema`, `SourceRecord`, `MappingDefinition`, `registerConnector()`, `registerWizardStep()`, `runImport()`, `runDry()`, `rollbackRun()`, `inferTypes()`, tables `import_source`, `import_mapping`, `import_run`, `import_run_item`, event `import.run.progress`, components `MappingTable`, `RunReport`, `RunHistory`, CLI `pnpm paperos import`.
* ID mapping (PAP-201): `external_id_map`, `import_cursor`, `recordExternalRef()` (also writes `pm_external_ref` and `crm_external_ref`), oRPC `import.mappings.*`, `runIncremental()`, `ImportedBadge`.
* Connectors: `csv`, `excel`, `gsheets` and `detectSourcePreset()` (PAP-200); `airtable` with `computedFields` pass and `parseFilterByFormula()` (PAP-202); `notion` with `toMdx()`, `toTiptap()` (PAP-203); `clickup`, `linear` with `StateMapping` and `PeopleMatching` steps (PAP-204); `stripe`, `quickbooks`, `xero` with `postingRulesStripe()`, `trialBalance()`, `ledger.reverseRun()`, `JournalPreview` (PAP-206); `template` applier, `PackSchema`, five packs, `TemplateStep` (PAP-207); `paperos` round-trip connector (PAP-205).
* Export (PAP-205): archive format v1.0 with JSON Schemas, job `export.run`, `registerExportDomain()`, oRPC `export.*`, permission `tenant.export`, `verifyRoundTrip()`.
* Migration Guide (PAP-208): character, skill `migrate-tenant`, MCP server `paperos-import`, approval token API, route `_app/settings/migrate`.
* Pending (issue cap): importer test accounts and fixture workspaces; Monday and HubSpot CSV recipes. Specs: {DOCS.get('migration', '')}

**Requires**

* tables: field types and record API (PAP-164), view model (PAP-161), grid (PAP-165, soft), forms (PAP-168, soft), formula grammar (PAP-171, soft).
* data-layer: pg-boss (PAP-43), object storage (PAP-37), audit log (PAP-38), core entities (PAP-33), server-side secret encryption helper.
* collab: docs engine import path (PAP-128), comments (PAP-131), notifications (PAP-136, soft). realtime: record sync (PAP-143, soft), collab text and agent presence (PAP-142, PAP-146, soft).
* pm-linear: PM data model (PAP-100), board views (PAP-102), orchestrator (PAP-96). business-core: ledger (PAP-179), finance model (PAP-175), Stripe catalog (PAP-177), invoicing (PAP-180), reports (PAP-183). growth: CRM model (PAP-187).
* identity: permissions (PAP-59), Google connection (PAP-57). spec-builder: page spec schema (PAP-114), app spec navigation (PAP-117), conformance (PAP-122). agents: roster (PAP-104), skills (PAP-105), handoffs (PAP-108), memory (PAP-109), evals (PAP-110), budgets (PAP-111). app-shell: `paperos create` (PAP-22), env schema (PAP-17). forge: bot secrets (PAP-48).
* External: Airtable, Notion, ClickUp, Stripe test, QuickBooks sandbox, Xero demo, Google OAuth app (pending test-accounts issue, one Needs Justin item).

**Milestone exit criteria**

* Import framework and CSV (2026-09-28): PAP-198 sheets and `index.json` merged; PAP-199 WP1-WP3 merged with the `import-framework.e2e` test green and the 100k-row bench under 5 minutes; PAP-200 imports the 25 fixtures and the 1M-row CSV under 4 minutes; PAP-201 rerun yields zero duplicates; test accounts provisioned or the Needs Justin item open with defaults.
* Airtable, Notion, ClickUp importers (2026-09-30): PAP-202 and PAP-203 demo workspaces import and re-import with counts equal to source; PAP-204 imports team PAP into the PM board; PAP-205 demo tenant round-trips with zero mismatches and a scheduled encrypted export lands in MinIO; Monday and HubSpot recipes merged if the cap lifts, else documented in PAP-198 sheets.
* Business migrations (2026-10-01): PAP-206 Stripe, QuickBooks and Xero imports match source reports within rounding and rollback reverses; PAP-207 five packs pass conformance with zero trial balance and Justin has reviewed content lists; PAP-208 evals score at or above 0.8 with no unapproved commit and Justin approved the character. Anything not merged by 10-01 is reported in the parent issue with the remaining work packages named.
""",
"libraries": f"""

## Contract

**Provides**

* Rubric (PAP-209): `RubricSchema`, `ScorecardSchema`, `pnpm lib score` (with `--facts-only`), `scripts/lib-facts.ts`, `docs/libraries/scorecards/`, ADR Alternatives and Re-open sections.
* MCP catalog (PAP-210): `McpCatalogSchema`, `.claude/mcp-catalog.json`, tool name grammar `mcp__<server>__<tool>`, scope classes `read|write|destructive`, `.mcp.json`, `@paperos/mcp-forgejo`, `pnpm mcp check`.
* License policy (PAP-211): `ops/licenses/policy.yaml` tiers and contexts, status `licenses`, `reports/licenses.json`, waivers schema, `THIRD_PARTY_NOTICES.md`, `deny.toml`.
* Decisions: UI primitives ADR with exact package (PAP-212, due 2026-09-19, else PAP-67 defaults to Base UI); table, chart and map ADRs and canvas/editor shortlist (PAP-213, WP1-WP3; PAP-165 defaults to TanStack Table after 09-21); eleven backend ADRs, `backend-decisions.md`, resource budget table, winner compose files, `@paperos/email` interface sketch (PAP-214, WP1-WP3); OSS products mode matrix, borrow reference docs, embed contracts (PAP-215, WP1-WP3).
* Registry (PAP-216): `RegistryEntrySchema`, `registry.json`, `pnpm lib add|registry build|check`, page `/_app/docs/registry`, Gate 1 job `registry-drift`.
* Upgrades (PAP-217): Renovate preset, `upgrade-summary` workflow and `UpgradeSummary` schema, automerge rules, dashboard mirror. Scout scan (PAP-218): skill `scout-scan`, `ScanReport`, weekly workflow, pinned "Scout scans" issue.
* Pending (issue cap): nine work-package sub-issues for PAP-213, PAP-214, PAP-215. Specs: {DOCS.get('libraries', '')}

**Requires**

* collab: docs engine (PAP-128) for registry and scan pages, ADR index (PAP-130, soft). quality: Gate 1 job slots and sticky comment (PAP-78), security SARIF merge (PAP-80, soft), Gate 3 status (PAP-82), perf report (PAP-87, soft), reviewer pass (PAP-81).
* forge: bot accounts and tokens (PAP-48), runners (PAP-50), VCS decision (PAP-44). app-shell: env names (PAP-17), VPS profile (PAP-25), Tauri shell for WebView tests (PAP-19, soft). design-system: tokens for spikes (PAP-66, soft).
* agents: roster (PAP-104), skills library (PAP-105), character schema (PAP-103), tool scopes (PAP-106), handoffs (PAP-108), evals (PAP-110), budgets (PAP-111). pm-linear: orchestrator headless entry (PAP-96), issue template (PAP-93), Needs Justin routing (PAP-94), concurrency hints (PAP-97).
* tables and collab research inputs by cross-link only: PAP-162, PAP-127, PAP-188, PAP-31, PAP-56, PAP-139.

**Milestone exit criteria**

* Evaluation process (2026-09-19): PAP-209 CLI and worked example merged with Atlas-approved weights; PAP-210 catalog validates with `/mcp` screenshot and Sentinel scope sign-off; PAP-211 fails a seeded SSPL package in CI; PAP-212 ADR accepted and PAP-67 updated with the exact package (or the Base UI default recorded).
* Core adoptions decided (2026-09-24): PAP-213 table ADR by 09-21 and chart and map ADRs by 09-24 with committed traces; PAP-214 eleven decisions in `backend-decisions.md` with the budget under 6 GB and `compose-smoke` green; PAP-215 nine spikes and the mode matrix accepted by Atlas, Nova and Beacon; every winner has a registry draft.
* Registry live (2026-09-30): PAP-216 check passes on `main` and a seeded unregistered dependency fails Gate 1; PAP-217 one patch automerged and one seeded major held with a Linear issue; PAP-218 one real sandbox scan produced a report, an entry and a comment.
""",
}

for key, pid in r5.PROJECTS.items():
    if pid in ch["projectsUpdated"]:
        print("skip", key); continue
    content = (CUR[pid]["content"] or "")
    if "## Contract" in content:
        print("already has contract", key); continue
    new_content = content.rstrip() + CONTRACTS[key]
    print(key, "words", r5.words(new_content))
    if DRY: continue
    d = r5.gql("mutation($id: String!, $i: ProjectUpdateInput!) { p: projectUpdate(id: $id, input: $i) { success } }", {"id": pid, "i": {"content": new_content}})
    if d["p"]["success"]:
        ch["projectsUpdated"].append(pid); r5.save_changes(ch); print("updated project", key)
