"""Append a Contract section to the three project descriptions (content field)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r4
DRY = "--dry" in sys.argv
ch = r4.load_changes(); ch.setdefault("projectsUpdated", [])
cur = json.load(open(os.path.join(r4.HERE, "project_current.json")))
DOCS = {d["project"]: d["url"] for d in ch.get("documents", [])}
PEND = "Linear rejected new issues on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free plan, 275 issues). "

C = {}
C["tables"] = f"""

## Contract

**Provides**

* View model (PAP-161): `ViewSpec`, `FieldDef`, `DatasetRef`, `viewSpecSchema`, `migrateViewSpec`, `registerDataset`, tables `dataset|field|record|view`, `view.schema.json` for page specs.
* Parity tracker (PAP-162): `parity.csv`, `parity:report` Gate 1 check, `formula-functions.csv`.
* Query compiler (PAP-163, children `[tables/compiler/*]`): `compileView`, procedures `views.query|count|groups|distinct`, `useViewQuery`, signed keyset cursors, `ShapeDef`.
* Field types (PAP-164, children `[tables/fields/*]`): `defineFieldType`, `fieldTypes`, `validateRecord`, `convertFieldType`, cells and editors for 17 types plus `geo` (PAP-170) and `button` (PAP-174).
* Views: `GridView` and `RecordPanel` (PAP-165, children `[tables/grid/*]`), toolbar and `FilterBuilder` (PAP-166), `KanbanView` with `onMove` (PAP-167), `CalendarView`, `TimelineView`, `GanttView` (PAP-168, children `[tables/time/*]`), `GalleryView`, `ListView`, `FormView` and `forms.submit` (PAP-169), `ChartView`, `MapView` and the `onFilter` contract (PAP-170).
* Formulas (PAP-171, children `[tables/formula/*]`): `parse`, `checkType`, `evaluate`, `compile`, `FormulaEditor`.
* Sharing (PAP-172): `views.*` CRUD, `view_share`, `view_default`, `resolveDefault`, `/v/:token`, `/embed/v/:token`, `ViewSwitcher`.
* Dashboards (PAP-173, children `[tables/dashboard/*]`): `Dashboard`, `DashboardEditor`, `defineNumberBlock`, `useDashboardFilters`, `/print/d/:id`, `layout.dashboard`.
* Automations (PAP-174, children `[tables/automations/*]`): `defineTrigger`, `defineAction`, `automations.*`, webhook route, starter templates.
* Planned (specs in the pending document): schema editor `[gap/tables/schema-editor]`, record detail and history `[gap/tables/record-detail]`, bulk operations and trash `[gap/tables/bulk-trash]`.

**Requires**

* data-layer: core entities (PAP-33), RLS (PAP-34), oRPC host and client (PAP-35 children), `softDelete` (PAP-32), files (PAP-37), audit and NOTIFY (PAP-38), jobs (PAP-43), Electric shapes (PAP-36 children, soft), the shared `FilterTree` grammar (PAP-279).
* identity: `can()`, `toPredicate`, `useCan` (PAP-59 children), audiences (PAP-62), permission matrix generator (PAP-63).
* design-system: primitives (PAP-67 children), layouts (PAP-70), data display and cell registry (PAP-71), date pickers (PAP-233), theming (PAP-74), tokens (PAP-66).
* input: command registry (PAP-151), focus management (PAP-153), drag-and-drop (PAP-155), touch (PAP-156).
* spec-builder: connector registry (PAP-121), page-spec hooks (PAP-119, PAP-120). collab: comments slot (PAP-131), notifications (PAP-136 core). realtime: record sync and conflict UX (PAP-143, PAP-144, soft).

**Milestone exit criteria**

* Grid with sort, filter, group (2026-09-23): PAP-161 and PAP-162 Done; PAP-163 children Done with the 100k-row bench under 150 ms p95 in CI; PAP-164 children Done with every type round-tripping through the compiler; PAP-165 children Done with the 10k-row Storybook, performance trace and screenshots at 375, 768, 1024, 1440, 1920; PAP-166 Done with a three-level nested filter demo.
* All view types (2026-09-27): PAP-167, PAP-168 children, PAP-169 and PAP-170 Done; one seeded dataset viewable as all ten kinds on the Pages demo; public form submission recorded; chart click emits a filter; schema editor, record detail and bulk-trash gap issues created and Done once the issue cap is lifted.
* View sharing, formulas, dashboards (2026-09-30): PAP-171 children Done with 80+ functions and SQL parity; PAP-172 public view with password and field stripping live; PAP-173 children Done with the six-block demo under 2 s and cross-filter replay; PAP-174 children Done with the "status becomes Done" automation running from a grid edit; parity report above 85 percent for Airtable, Notion and ClickUp rows.

**Pending issues**

{PEND}Twenty-four fully specified issues for this project (three gaps, 21 children of the seven L-sized issues) are stored in [Round 2 pending issues: tables]({DOCS.get("tables", "")}) and are created by `round2/agent4/create_issues.py` once the plan is upgraded. Decision for Justin: upgrade the Linear workspace plan so the queue can grow.
"""

C["business-core"] = f"""

## Contract

**Provides**

* Finance model (PAP-175): `Money`, `fin_party` with customer, vendor and employee extensions, `fin_account` with stable `subtype`s, `fin_period`, `fin_transaction`, `fin_settings`, six default charts of accounts, procedures `finance.parties|accounts|periods.*`.
* Payroll decision (PAP-176): `PayrollProvider`, `Capabilities`, `PayrollEvent` types and the ADR.
* Platform billing (PAP-177): `plans.ts`, `subscription`, `stripe_event`, `billing.*`, `/api/webhooks/stripe`, event `billing.subscription.changed`. Entitlements (PAP-178): `resolveEntitlements`, `assertWithinLimit`, `useEntitlement`, `EntitlementGate`, `requires: [entitlement.*]`.
* Ledger (PAP-179, children `[business-core/ledger/*]`): `ledger.createDraft|post|reverse|list|trialBalance|verifyChain|rebuildBalances|postEvent`, `definePostingRule`, event `ledger.entry.posted`, errors `UNBALANCED`, `IMMUTABLE_ENTRY`, `PERIOD_LOCKED`.
* Documents (PAP-180, children `[business-core/invoicing/*]`): `documents.*`, `renderDocumentPdf`, `/pay/:token`, `/doc/:token`, events `document.issued|paid|voided`, `bill` kind.
* Connect (PAP-181): `connect.*`, `createConnectedCheckout`, `createTransfer`, connected webhooks, reconciliation dataset. Tax (PAP-182): `tax.calculate`, `TaxEvidence`, `finance.taxSummary`.
* Reports (PAP-183): `defineReport`, datasets `finance.pnl|balanceSheet|cashFlow|arAging|apAging|trialBalance|generalLedger`, number blocks `finance.netIncome|cash|arOutstanding|apOutstanding`, exports.
* Payroll (PAP-184, children `[business-core/payroll/*]`): adapter registry, `payroll.*`, webhook route, contract test suite, `payroll_run` rows. Expenses (PAP-185): `expenses.*`, `ReceiptExtraction`. Cash dashboard (PAP-186): `cash.dashboard.json`, six datasets, alerts.
* Planned (specs in the pending document): usage metering `[gap/business-core/usage-metering]` (`recordUsage`, `usageFor`), recurring invoices and dunning `[gap/business-core/recurring-dunning]`.

**Requires**

* data-layer: core entities (PAP-33), RLS (PAP-34), oRPC (PAP-35 children), files (PAP-37), audit (PAP-38), observability (PAP-40), data dictionary (PAP-41), jobs (PAP-43).
* identity: `can()` and attribute conditions (PAP-59 children), org and membership hooks (PAP-58), agent principals (PAP-60), audiences (PAP-62), portal shell (PAP-64), session payload (PAP-223).
* tables: dataset registry (PAP-161), compiler (PAP-163), grid (PAP-165), sharing (PAP-172), charts (PAP-170), dashboards (PAP-173).
* design-system: `Money` formatting (PAP-27 in app-shell), email and PDF theme (PAP-235), theming (PAP-74). collab: notifications (PAP-136 core). app-shell: env and secrets (PAP-17), mobile camera shim (PAP-259, PAP-260). agents: cost controls and eval harness (PAP-111, PAP-110). spec-builder: access section shorthand (PAP-116).
* External, one Needs Justin item each: Stripe live keys (test mode until then), payroll sandbox agreement, Connect KYC for the demo tenant.

**Milestone exit criteria**

* Stripe billing live (2026-09-27): PAP-175 migrations and six charts seeded with the subtype test green; PAP-176 ADR merged and sandbox requested; PAP-177 test-mode checkout to billing page within 5 s recorded; PAP-178 limit test (5 of 20 parallel creates) green and the upgrade prompt demo; usage metering gap issue created once the cap lifts.
* Ledger and reports (2026-09-29): PAP-179 children Done with 10k-entry chain verification and 50-way gapless concurrency; PAP-180 children Done with the issue-pay-receipt test-mode flow and PDF snapshots; PAP-181 Express onboarding and payout entries recorded; PAP-182 US tax and EU reverse-charge cases; PAP-183 textbook fixture matching to the cent on both bases.
* Payroll adapter and cash dashboard (2026-10-01): PAP-184 children Done with the sandbox run to `paid` and balanced postings; PAP-185 eval set at 90 percent totals; PAP-186 rendering under 2 s with cross-filter replay and PDF export; recurring and dunning gap issue Done once created.

**Pending issues**

{PEND}Eleven fully specified issues for this project (two gaps, nine children of PAP-179, PAP-180 and PAP-184) are stored in [Round 2 pending issues: business-core]({DOCS.get("business-core", "")}) and are created by `round2/agent4/create_issues.py` once the plan is upgraded.
"""

C["growth"] = f"""

## Contract

**Provides**

* CRM model (PAP-187): twelve `crm_*` tables, Zod types, routers `crm.*` with `leads.convert` and `deals.move`, datasets, search registrations, events `crm.deal.stage_changed`, `crm.lead.converted`, `crm.contact.created`, three page specs.
* Stack decision (PAP-188): `results.json`, ADR constraints for social, outreach, attribution and support, provider recommendation, data-model mappings for importers.
* CRM views (PAP-189): `/crm/*` routes, reference view JSON, `WonLostDialog`, commands `crm.*`, demo seed.
* Social (PAP-190, children `[growth/social/*]`): `social.posts|accounts.*`, `SocialAdapter`, `validatePost`, events `social.post.published|failed`. Content agent (PAP-192): `campaign-composer` character, `draft-campaign` skill, `CampaignDraft` schema, eval task.
* Outreach (PAP-191, children `[growth/outreach/*]`): `outreach.*`, `outreach.enrol`, `OutreachProvider`, `canSend`, events `outreach.replied|bounced|unsubscribed`.
* Landing and forms (PAP-193): `landing.*`, `form.js` embed, public submit route, event `lead.created`. Attribution (PAP-194): `@paperos/attribution` SDK, collector, `classifyChannel`, datasets `attr.*`. Segments (PAP-195): `segments.*`, `useInSegment`, events `segment.entered|exited`, `SegmentRef`.
* Referrals (PAP-196, deferred, children `[growth/referral/*]`): `referrals.*`, `/r/{{code}}`, `referralTokenFromRequest`. Support (PAP-197, children `[growth/support/*]`): `support.*`, `<SupportChat/>`, `<ConversationList/>`, inbound route.
* Planned (specs in the pending document): consent and compliance centre `[gap/growth/consent-centre]` (`canContact`, `suppression.*`, preference and unsubscribe routes).

**Requires**

* data-layer: core entities (PAP-33), RLS (PAP-34), oRPC and public route pattern (PAP-35 children), files (PAP-37), audit (PAP-38), search (PAP-39), jobs (PAP-43), `FilterTree` (PAP-279).
* tables: dataset registry (PAP-161), compiler (PAP-163), grid (PAP-165), filter builder (PAP-166), kanban (PAP-167), calendar (PAP-168, soft), list view (PAP-169), sharing (PAP-172), dashboards (PAP-173), automations hook (PAP-174, soft).
* business-core: `fin_party` link (PAP-175), Stripe client and webhooks (PAP-177), entitlements (PAP-178), ledger (PAP-179), documents (PAP-180), Connect (PAP-181).
* identity: agent principals (PAP-60), portal shell (PAP-64), OAuth plumbing (PAP-57 children). collab: comments (PAP-131), notifications (PAP-136 core), changelog feed (PAP-133). realtime: record sync and presence (PAP-143, PAP-141, soft). agents: roster, skills, evals, cost controls, memory (PAP-104, PAP-105, PAP-110, PAP-111, PAP-109). design-system: layouts, data display, theming (PAP-70, PAP-71, PAP-74). input: commands and drag (PAP-151, PAP-155). spec-builder: schema, validator, conformance (PAP-117, PAP-123). app-shell: Pages fallback (PAP-15), secrets (PAP-17).
* External, one Needs Justin item covering all: social platform OAuth apps (X, LinkedIn, Instagram, TikTok, YouTube), Resend and Twilio test credentials, a Webflow site and OAuth app, support mailbox DNS, outreach sandbox flip.

**Milestone exit criteria**

* CRM core (2026-09-28): PAP-187 migration and RLS harness green with three validated page specs; PAP-188 ADR approved with six decisions and license review; PAP-189 pipeline, contacts and company detail screenshotted at seven widths with the won dialog flow recorded.
* Campaigns and social (2026-09-30): PAP-190 children Done with X publishing recorded and four adapters in `dryRun` snapshots; PAP-191 children Done with the sandbox email, SMS and STOP round trip; PAP-192 eval at 0.8 or above with drafts filed from a real changelog; PAP-193 live Webflow page submitting a lead; consent centre gap issue Done once created.
* Acquisition analytics (2026-10-01): PAP-194 channel report from a UTM landing with the 1,000 events per second load test; PAP-195 200k-contact bench and a portal banner gated by a segment; PAP-197 children Done with the real email round trip and live chat; PAP-196 scheduled only if every other P2 issue is In Review.

**Pending issues**

{PEND}Thirteen fully specified issues for this project (one gap, twelve children of PAP-190, PAP-191, PAP-196 and PAP-197) are stored in [Round 2 pending issues: growth]({DOCS.get("growth", "")}) and are created by `round2/agent4/create_issues.py` once the plan is upgraded.
"""

for P, extra in C.items():
    pid = r4.PROJECTS[P]
    if pid in ch["projectsUpdated"]: print("skip", P); continue
    content = (cur[P]["content"] or "").rstrip() + extra
    print(P, "words", r4.words(content))
    if DRY: continue
    d = r4.gql("mutation($id: String!, $i: ProjectUpdateInput!) { p: projectUpdate(id: $id, input: $i) { success project { id } } }", {"id": pid, "i": {"content": content}})
    if d["p"]["success"]:
        ch["projectsUpdated"].append(pid); r4.save_changes(ch); print("updated", P)
