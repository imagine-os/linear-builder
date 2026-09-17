# Children for business-core L issues and the two business-core gap issues.
P = "business-core"
CHILDREN = {}
GAPS = []
def child(parent, key, title, type_, size, **s):
    CHILDREN.setdefault(parent, []).append(dict(key=key, title=title, type=type_, size=size, sections=dict(s, Size=size + ": " + s.pop("SizeNote", "one session."))))
def gap(key, title, phase, type_, priority, surfaces, milestone, blockedBy, blocks, state="Backlog", **s):
    GAPS.append(dict(key=key, title=title, phase=phase, type=type_, priority=priority, surfaces=surfaces, milestone=milestone,
                     blockedBy=blockedBy, blocks=blocks, state=state, project=P, sections=s))

# ---------------- PAP-179 ledger ----------------
child("PAP-179", "business-core/ledger/journal-constraints", "Journal tables, balance trigger, immutability trigger, gapless numbering and account balances", "Build", "M",
Goal="""Lay the ledger's foundation in Postgres: journal entry and line tables whose constraints make an unbalanced or edited posted entry impossible, with gapless per-tenant numbering and incrementally maintained balances.""",
Scope="""In: `fin_journal_entry`, `fin_journal_line`, `fin_account_balance`; posting SQL function `ledger_post(entry_id)`; triggers `UNBALANCED`, `IMMUTABLE_ENTRY`; `ledger.createDraft` and `ledger.post` procedures. Out: hash chain, reversals, periods workflow, rules and UI (siblings).""",
Spec="""* Tables per the parent; `CHECK ((debit_minor > 0) <> (credit_minor > 0))`; minimum two lines; accounts active and tenant-owned.
* `ledger_post` runs under `pg_advisory_xact_lock(hashtext(tenant_id))`: balance check on `functional_minor`, next `entry_number` from a per-tenant counter row, status to `posted`, balance rows upserted per `(account_id, period_id)`.
* `BEFORE UPDATE OR DELETE` trigger on posted entries and their lines raises `IMMUTABLE_ENTRY` except for the columns the reversal sibling whitelists.
* Drafts editable; `ledger.createDraft` validates with Zod and `Money`.""",
Contract="""Provides: tables, `ledger_post`, `ledger.createDraft|post`, `JournalDraft` type, error codes `UNBALANCED`, `IMMUTABLE_ENTRY`. Consumes: accounts, periods, `Money` (PAP-175), RLS (PAP-34), audit (PAP-38).""",
DoD="""* SQL and Vitest tests: unbalanced rejected, posted update rejected, 50 parallel posts gapless, balances equal brute-force sums after 10k entries.""",
Test="""* Unit: draft validation; `Money` functional conversion.
* Integration (Postgres): the constraint tests above; RLS harness on the three tables.""",
Demo="""Run `pnpm tsx scripts/ledger-post-demo.ts` posting a balanced and an unbalanced draft and printing the results.""",
Edge="""* Multi-currency lines balance in functional currency with an `fx_gain_loss` remainder line; deactivated account named in the failure.""",
Deps="""PAP-175 (hard), PAP-34, PAP-38. Blocks siblings.""",
Agent="""Builder: Ledger (Bookkeeper). Reviewer: Forge (Schema Wright), Sentinel (Security Auditor).""",
SizeNote="invariants must be airtight.")

child("PAP-179", "business-core/ledger/hashchain-reversal-close", "Hash chain with nightly verification, ledger.reverse and the period close and lock workflow", "Build", "M",
Goal="""Make the ledger tamper-evident and auditable: a per-tenant hash chain verified nightly, reversals as the only correction path, and period close and lock with checks.""",
Scope="""In: `prev_hash` and `hash` computation inside `ledger_post`; `ledger.verifyChain`; `ledger.reverse`; `ledger.closePeriod|lockPeriod|reopenPeriod`; nightly job and observability alert. Out: rules and UI (sibling).""",
Spec="""* `hash = sha256(prev_hash || canonical_json(entry, lines))` in `entry_number` order under the tenant lock; `verifyChain(tenantId)` recomputes and returns the first mismatch; nightly PAP-43 job posts a metric and alerts (PAP-40) on failure.
* `ledger.reverse({ id, reason, effectiveDate })` posts mirrored lines, sets `status = reversed`, `reversed_by_id` and `reversal_of_id`; reversal of a reversal allowed.
* Close requires zero drafts and a verified chain, snapshots balances; `closed` needs `ledger.reopen` to post; `locked` rejects all with `PERIOD_LOCKED`.""",
Contract="""Provides: `ledger.reverse|verifyChain|closePeriod|lockPeriod|reopenPeriod`, error `PERIOD_LOCKED`, metric `ledger.chain.valid`. Consumes: journal child, jobs (PAP-43), observability (PAP-40), `can()` (PAP-227).""",
DoD="""* Tamper test (superuser edit) detected; reversal mirror test; period state machine tests; ADR on immutability and chain.""",
Test="""* Integration: chain valid after 10k entries; first mismatch located; backdated post into locked period rejected; close blocked by a draft.""",
Demo="""Run `pnpm ledger verify demo`, tamper a row with `psql`, run again and read the mismatch.""",
Edge="""* Import backdating into a closed period offered a post on period start with memo; reopen audited with reason.""",
Deps="""Journal child (hard), PAP-43, PAP-40.""",
Agent="""Builder: Ledger (Bookkeeper). Reviewer: Sentinel (Security Auditor).""",
SizeNote="one session.")

child("PAP-179", "business-core/ledger/rules-ui-trialbalance", "Posting rule registry with the first five rules, /finance/journal UI, trial balance and rebuildBalances", "Build", "M",
Goal="""Connect business events to the ledger through pure, testable posting rules and give finance staff a journal screen and trial balance.""",
Scope="""In: `definePostingRule`, rules `payment.succeeded`, `refund.created`, `fee.charged`, `adjustment`, `transfer`; `ledger.postEvent`; `ledger.list|trialBalance|rebuildBalances`; `/finance/journal` grid with line panel, manual entry form, period list. Out: invoice, payroll and expense rules (their issues).""",
Spec="""* Rules resolve accounts by `subtype`, never code; `postEvent(tx)` idempotent by `(source_type, source_id)`; registry exported for docs.
* Manual entry form with running balance; Post disabled until balanced; reverse action with reason; period list with close and lock.
* `rebuildBalances(tenantId)` recomputes `fin_account_balance` in one transaction; trial balance sums it per period.""",
Contract="""Provides: `definePostingRule`, `ledger.postEvent|list|trialBalance|rebuildBalances`, dataset `finance.journal`, event `ledger.entry.posted`, route `/finance/journal`. Consumes: both siblings, grid (PAP-165), `fin_transaction` (PAP-175), `can()` (PAP-227).""",
DoD="""* Rule fixtures balance; idempotency test; Playwright draft, post, reverse, close; screenshots at 375, 1024, 1920 in three themes; `docs/finance/ledger.md` rule catalogue.""",
Test="""* Unit: each rule against fixture transactions; duplicate `postEvent` no-op.
* E2E: the manual entry flow above; trial balance matches brute force.""",
Demo="""Create a two-line entry in `/finance/journal`, post it, reverse it, open the trial balance.""",
Edge="""* Rule for an unknown subtype fails loudly at registration; agents draft but cannot post.""",
Deps="""Both siblings (hard), PAP-165, PAP-227.""",
Agent="""Builder: Ledger (Bookkeeper). Reviewer: Sentinel (Code Reviewer).""",
SizeNote="one session.")

# ---------------- PAP-180 invoicing ----------------
child("PAP-180", "business-core/invoicing/model-statemachine", "Document model, lines, sequences, server-side totals, state machine, quote conversion, void and credit notes", "Build", "M",
Goal="""Model quotes, invoices, receipts, credit notes and bills with exact totals, gapless numbering and a strict state machine, before any rendering or payment is attached.""",
Scope="""In: `fin_document`, `fin_document_line`, `fin_tax_rate`, sequences; `documents.create|update|issue|accept|void|creditNote|list|get`; `computeTotals`. Out: PDFs, pay page, postings, portal, emails (siblings).""",
Spec="""* Schema per the parent; per-kind sequences formatted from `fin_settings.invoice_number_format`, allocated inside `issue` under a tenant lock.
* `computeTotals(lines, currency)` with `Money`: per-line rounding then sum, discounts, multi-rate tax (manual rates or PAP-182 evidence), quantity precision 4.
* Transitions are the only writes to `status`; `issue` freezes lines and number; `accept` from a quote stores signature name and time and creates an invoice draft; `void` only without payments; credit notes apply to paid balances; expiry job for quotes.""",
Contract="""Provides: types `FinDocument`, `DocumentLine`, procedures above, `computeTotals`, `documentStateMachine`, dataset `finance.documents`. Consumes: `Money`, parties, settings (PAP-175), tax evidence (PAP-182, optional), jobs (PAP-43).""",
DoD="""* Totals tests to the cent; state machine table tests; sequence gapless under 20 concurrent issues; dataset renders in a grid.""",
Test="""* Unit: rounding policy, discounts, multi-rate tax, illegal transitions `CONFLICT`.
* Integration: concurrent issue; quote to invoice conversion; credit note application.""",
Demo="""Run `pnpm tsx scripts/invoice-demo.ts` creating a quote, accepting it and printing the invoice totals and number.""",
Edge="""* Number format change mid-year continues from the max; credit note larger than balance rejected.""",
Deps="""PAP-175 (hard), PAP-43, PAP-182 (optional). Blocks siblings.""",
Agent="""Builder: Ledger (Payments Integrator). Reviewer: Sentinel (Code Reviewer).""",
SizeNote="one session.")

child("PAP-180", "business-core/invoicing/pdf-paypage", "Branded PDF rendering, public /pay and /doc pages, Stripe Checkout on platform or connected account, receipts", "Build", "M",
Goal="""Let a customer receive, read and pay a document: branded PDFs and a public pay page backed by Stripe Checkout, producing receipts on payment.""",
Scope="""In: `packages/finance/src/pdf/` templates on the PAP-235 kit, `renderDocumentPdf`, worker rendering and content-addressed storage; routes `/pay/:token`, `/doc/:token`; Checkout session creation; `checkout.session.completed` handler creating receipts. Out: postings, portal, emails (sibling).""",
Spec="""* `@react-pdf/renderer` 4.x with `brandingToInlineCss` and Inter embedded; rendered on issue and on demand; stored via PAP-37 keyed by content hash.
* Pay page shows summary, Pay (Checkout redirect) and Download PDF; uses PAP-181 connected account with application fee when enabled, else platform test mode; voided documents show "Voided".
* Payment handler marks `paid|partial`, issues a receipt document and its PDF; idempotent by `stripe_event.id`.""",
Contract="""Provides: `renderDocumentPdf(id)`, routes, `createDocumentCheckout(documentId)`, receipt issuance. Consumes: model child, Stripe client and events (PAP-177), connected checkout (PAP-181, optional), files (PAP-37), theme kit (PAP-235), rate limiting for public routes (PAP-267).""",
DoD="""* PDF snapshot tests for three kinds at two brands; test-mode pay flow recorded; pay page at 375 and 1024 in Playwright.""",
Test="""* Unit: template props mapping; token validation.
* Integration: `stripe trigger` payment produces receipt and status; duplicate event no-op.
* Visual: PDFs rasterised and diffed; pay page screenshots.""",
Demo="""Open a pay link in a private window, pay with `4242`, download the receipt PDF.""",
Edge="""* Expired or revoked token 410; partial payments recorded manually still render a receipt for the amount.""",
Deps="""Model child (hard), PAP-177, PAP-37, PAP-235 (hard), PAP-181 (optional).""",
Agent="""Builder: Ledger (Payments Integrator). Reviewer: Sentinel (Security Auditor, Visual Inspector).""",
SizeNote="one session.")

child("PAP-180", "business-core/invoicing/postings-portal-emails", "Posting rules invoice.*, manual payments, reminders job, customer portal invoice list and email templates", "Build", "M",
Goal="""Close the accounting and communication loop: every document event posts to the ledger, customers see and pay invoices in the portal, and reminders and receipts go out automatically.""",
Scope="""In: rules `invoice.issued|paid|voided`, `credit_note.issued`; `documents.recordPayment`; overdue and reminder job (due+3, due+14); portal "Invoices" page; email templates send, reminder, receipt via PAP-136 core and the PAP-235 theme. Out: recurring schedules and dunning ({{gap/business-core/recurring-dunning}}).""",
Spec="""* `invoice.issued` debits `ar`, credits revenue per line account and `sales_tax_payable` per jurisdiction; `invoice.paid` debits `cash` or `stripe_balance`, credits `ar`; FX gain or loss when currencies differ; void posts the reversal.
* Reminders skip when disabled per document or party; `overdue` set daily.
* Portal list for parties with `portal_enabled`, access by `user_id` link; `document.read` own.""",
Contract="""Provides: posting rules, `documents.recordPayment|send`, portal route `_portal/invoices`, notification kinds `document.sent|reminder|receipt`. Consumes: both siblings, posting (PAP-179), portal shell (PAP-64), notifications (PAP-136 core), theme (PAP-235), jobs (PAP-43).""",
DoD="""* Rule fixtures balance; reminder job tests with a fixed clock; portal Playwright; emails snapshot-tested; screenshots at 375, 768, 1024, 1440, 1920.""",
Test="""* Unit: rules, FX handling, reminder eligibility.
* E2E: issue, pay, see journal entries in the activity tab; portal customer pays and sees the receipt.""",
Demo="""Issue an invoice, log in as the customer in the portal, pay it, read the receipt email in the outbox viewer.""",
Edge="""* Manual partial payment sets `partial`; reminder to a party with `do_not_contact` skipped and logged.""",
Deps="""Both siblings (hard), PAP-179, PAP-64, PAP-136 core, PAP-235, PAP-43.""",
Agent="""Builder: Ledger (Bookkeeper and Payments Integrator). Reviewer: Sentinel (Code Reviewer).""",
SizeNote="one session.")

# ---------------- PAP-184 payroll ----------------
child("PAP-184", "business-core/payroll/adapter-contract", "Finalised PayrollProvider interface, first adapter with idempotency keys, webhook route and the adapter contract test suite", "Build", "M",
Goal="""Turn the PAP-176 interface into a working, tested adapter for the chosen provider, with webhook verification and a contract suite any future adapter must pass.""",
Scope="""In: `payroll/provider.ts` (final), `adapters/check.ts` (or `gusto.ts`), `payroll_event`, route `/api/webhooks/payroll/:provider`, `test/payroll-contract.test.ts`, mock adapter. Out: tables beyond `payroll_event`, UI, postings (siblings).""",
Spec="""* Methods map to provider REST via the TypeScript SDK if present else `ky` with Zod; idempotency key `paperos:<tenant>:<entity>:<version>` on every mutation; `capabilities()` bitmap.
* Webhooks: signature verification with two accepted secrets during rotation; events deduped by provider id in `payroll_event`; parsed into `PayrollEvent`.
* Contract suite exercises every interface method against the mock adapter and, with sandbox credentials, the real one (`nock` recordings committed).""",
Contract="""Provides: `PayrollProvider` final, `payrollProviders` registry, `PayrollEvent`, webhook route, contract suite, mock adapter. Consumes: ADR and draft interface (PAP-176), secrets (PAP-17), sandbox credentials (Needs Justin).""",
DoD="""* Contract suite green on mock and sandbox; signature rotation test; recordings committed; capability matrix in docs.""",
Test="""* Unit: request mapping; signature verify; dedupe.
* Integration: contract suite against sandbox once, recorded.""",
Demo="""Run `pnpm test payroll-contract --adapter mock` and then `--adapter check --record` against the sandbox.""",
Edge="""* Provider 5xx retried with idempotency; unknown event types logged and acknowledged.""",
Deps="""PAP-176 (hard), PAP-17, sandbox credentials. Blocks siblings.""",
Agent="""Builder: Ledger (Payroll Adapter). Reviewer: Sentinel (Security Auditor).""",
SizeNote="plus a webhook-signing spike.")

child("PAP-184", "business-core/payroll/onboarding-sync", "Payroll tables, company and employee onboarding via provider links, employee sync from fin_employee and status polling", "Build", "M",
Goal="""Get a tenant and its employees onboarded with the provider and kept in sync with `fin_employee`, without storing sensitive data.""",
Scope="""In: `payroll_company`, `payroll_employee_link`; `payroll.company.start|status`, `payroll.employees.sync|list|onboardingLink`; `/finance/payroll/employees` page; 15-minute poll fallback; onboarding emails via PAP-136 core. Out: runs and postings (sibling).""",
Spec="""* Company onboarding via provider-hosted component or link in a sandboxed iframe; employee links emailed; statuses updated by webhooks or poll.
* `syncEmployees` upserts from `fin_employee` (name, email, start date, type, `compensation jsonb`); conflicts shown in a review list before pushing; no SSNs or bank numbers stored, only provider ids and masked last four.""",
Contract="""Provides: the two tables, procedures above, employees page, event `payroll.employee.onboarded`. Consumes: adapter child, `fin_employee` (PAP-175), notifications (PAP-136 core), grid (PAP-165).""",
DoD="""* Sync conflict tests; Playwright onboarding status page; screenshots at 375, 1024, 1920; audit rows for every sync.""",
Test="""* Unit: upsert mapping, conflict detection, masking.
* Integration: sandbox onboarding of a company and two employees recorded; poll fallback marks status when webhooks are disabled.""",
Demo="""Open `/finance/payroll/employees`, sync two seeded employees, resolve one conflict, send an onboarding link.""",
Edge="""* Employee without email cannot be synced and is listed; terminated employee marked and excluded.""",
Deps="""Adapter child (hard), PAP-175, PAP-136 core, PAP-165.""",
Agent="""Builder: Ledger (Payroll Adapter). Reviewer: Sentinel (Security Auditor).""",
SizeNote="one session.")

child("PAP-184", "business-core/payroll/run-approve-post", "Payroll run flow, typed-total approval, webhook status transitions, ledger posting and the paystub portal page", "Build", "M",
Goal="""Run payroll end to end inside PaperOS: hours entry, preview, a deliberate approval, provider processing tracked by webhooks, balanced ledger postings and paystubs for employees.""",
Scope="""In: `payroll_run`, `payroll_run_item`; `payroll.runs.*`, `payroll.paystubs.*`; `/finance/payroll` pages with the hours grid; posting rules `payroll.approved`, `payroll.paid`; portal paystubs page. Out: benefits, time tracking.""",
Spec="""* Flow: create run for next period, edit hours in a PAP-165 grid, `preview`, `approve` with `payroll.approve` and the typed net total, transitions `processing` and `paid` from webhooks, cancel until cutoff from `capabilities`.
* Postings per the parent; `paid` moves `payroll_liability` to `cash`; dimensions from department.
* Paystub PDFs proxied through short-lived signed URLs, visible only to the linked user.""",
Contract="""Provides: run tables, procedures, pages, posting rules, event `payroll.run.approved|paid|failed`, portal route `_portal/paystubs`, `payroll_run` rows for PAP-186. Consumes: both siblings, posting (PAP-179), grid (PAP-165), portal shell (PAP-64), audit (PAP-38).""",
DoD="""* Status machine and posting tests; sandbox run recorded to `paid`; Playwright approve flow with replay; screenshots at 375, 1024, 1920; live checklist in docs and Needs Justin item.""",
Test="""* Unit: transitions, posting totals, typed-total guard.
* Integration: webhook replay and rotation; liabilities net to zero after `paid`.
* E2E: full run flow; employee sees the paystub.""",
Demo="""Create and approve a run, trigger the sandbox `paid` webhook, open the journal and the portal paystub.""",
Edge="""* NSF after approval: `failed`, liabilities remain, owner alerted; off-cycle run when capable.""",
Deps="""Both siblings (hard), PAP-179, PAP-165, PAP-64, PAP-38.""",
Agent="""Builder: Ledger (Payroll Adapter). Reviewer: Sentinel (Security Auditor), Bookkeeper on postings.""",
SizeNote="one session.")

# ---------------- gap issues ----------------
gap("gap/business-core/usage-metering",
"Build usage metering and metered billing: usage events (agent sessions, storage, seats, API calls) aggregated per tenant, Stripe usage records, limit warnings",
"P2", "Build", 2, ["Customer", "Developer"], "Stripe billing live", ["PAP-177", "PAP-178", "PAP-43"], ["PAP-99"],
Goal="""Turn PAP-177's "record hooks only" into real metering: one `recordUsage(kind, quantity)` call that every metered surface emits, per-tenant aggregation, limit warnings that feed PAP-178's `used` values, and Stripe usage records for metered prices, so `agentSessionsPerDay` and `storageGb` stop being unmeasured promises.""",
Scope="""In: tables `usage_event` (partitioned monthly) and `usage_daily`; `recordUsage`, `usageFor(tenantId, kind, window)`; kinds v1 `agent.session`, `agent.tokens`, `storage.bytes` (gauge), `seats.active` (gauge), `api.calls`, `automation.runs`, `outreach.messages`; hourly rollup job; Stripe usage record sync for prices flagged `metered` in `plans.ts`; warnings at 80 and 100 percent via notifications; usage page section on `/org/settings/billing`. Out: pricing decisions, per-user chargeback reports, external analytics.""",
Spec="""* `usage_event (id uuidv7, tenant_id, kind, quantity numeric, unit, actor_id?, source, idempotency_key unique, occurred_at)`; gauges write the current value, counters increment.
* `recordUsage` is fire-and-forget through the PAP-43 queue with idempotency keys so retries never double count; storage gauge computed nightly from PAP-37 `file` rows; active seats from PAP-58 memberships.
* `usage_daily (tenant_id, kind, day, quantity)` rolled up hourly; `usageFor` reads it plus today's live events.
* PAP-178 `assertWithinLimit` uses `usageFor` for `agentSessionsPerDay` and `storageGb`; PAP-99 reads the same value before spawning sessions.
* Stripe: for plans with `metered: true` prices, a nightly job posts `subscriptionItems.createUsageRecord` with `action: 'set'` per kind and stores `stripe_usage_record_id`; failures alert.
* Warnings emitted once per threshold crossing per billing period via `usage.threshold { kind, pct }` and PAP-136 core.""",
Contract="""Provides: `recordUsage(kind, quantity, { idempotencyKey, actorId })`, `usageFor`, `UsageKind` registry `defineUsageKind`, dataset `billing.usage`, event `usage.threshold`, usage bars on the billing page. Consumes: plans and subscriptions (PAP-177), entitlements (PAP-178), jobs (PAP-43), files (PAP-37), memberships (PAP-58), notifications (PAP-136 core), orchestrator sessions (PAP-96, PAP-98 emit `agent.session` and `agent.tokens`). Consumed by PAP-99 concurrency, PAP-178, PAP-174 `cost_units`.""",
DoD="""* Vitest, integration and Playwright below green.
* Usage section screenshots at 375, 1024, 1920 in three themes.
* `docs/finance/usage-metering.md` (kinds, adding a kind, Stripe mapping); CHANGELOG; Linear comment with demo link.""",
Test="""* Unit: counter versus gauge semantics, idempotency, threshold-once logic, rollup arithmetic.
* Integration: 10k events in one hour roll up correctly; duplicate idempotency keys ignored; Stripe usage record posted in test mode and visible on the subscription item; `assertWithinLimit` blocks the sixth agent session when the limit is five.
* E2E: billing page shows storage and agent-session bars; crossing 80 percent produces one notification.
* Visual: matrix above.""",
Demo="""Reviewer runs `pnpm tsx scripts/usage-demo.ts` emitting 50 API calls and a storage gauge, forces a rollup, opens `/org/settings/billing` to see the bars move, then runs the Stripe sync and opens the subscription item in the Stripe test dashboard. Under two minutes.""",
Edge="""* Clock skew between emitters: `occurred_at` from the server on receipt.
* Plan without metered prices: rollups still run, Stripe sync skipped.
* Tenant downgrade mid-period: usage continues to accrue, limits apply from the new plan after the grace period.
* Partition missing for a future month: created ahead by the nightly job.
* Storage gauge stale after a bulk purge: next nightly run corrects it; page shows "as of".""",
Deps="""PAP-177 (hard), PAP-178 (hard), PAP-43 (hard), PAP-37, PAP-58, PAP-136 core, PAP-98 (emitter). Blocks PAP-99's session cap check.""",
Agent="""Builder: Ledger (Payments Integrator). Reviewer: Sentinel (Code Reviewer, Edge Case Hunter for double counting).""",
Size="""M: small tables and one Stripe call; correctness of idempotency and rollups is the work.""")

gap("gap/business-core/recurring-dunning",
"Build recurring tenant invoices and dunning: schedules, automatic reminders, late fees, payment retry for tenant-to-customer billing",
"P2", "Build", 3, ["Staff", "Customer"], "Payroll adapter and cash dashboard", ["PAP-180", "PAP-43"], [],
Goal="""Give a clinic, agency or landlord billing its own customers monthly a recurring path in PAP-180's document model: schedules that generate and send invoices, a dunning ladder with reminders and optional late fees, and payment retry for saved cards on the connected account. This is tenant-to-customer billing, distinct from platform subscriptions (PAP-177).""",
Scope="""In: tables `fin_recurring_schedule`, `fin_dunning_policy`; procedures `recurring.*`, `dunning.*`; generation job; dunning job; saved payment method capture on the pay page; `/finance/recurring` page and per-party schedule editor; portal "Upcoming" list. Out: usage-based tenant billing, proration, contracts and e-signature.""",
Spec="""* `fin_recurring_schedule (party_id, template_document_id, cadence: weekly|monthly|quarterly|yearly, day_of_period, next_run_at, timezone, auto_send, auto_charge, status: active|paused|ended, ends_at?, occurrences?)`; the template is a draft document whose lines are copied with `{{period.start}}` and `{{period.end}}` substitutions in descriptions.
* Generation job (PAP-43, hourly) creates the invoice from the template, issues it, sends it when `auto_send`, and charges the saved method when `auto_charge` through a PaymentIntent on the connected account (PAP-181) or platform test mode; idempotent per `(schedule_id, period_start)`.
* `fin_dunning_policy (name, steps jsonb [{ offset_days, action: remind|late_fee|retry|escalate, template_id?, fee: { pct | fixed_minor, cap_minor } }], default)`; per-party override; the daily job walks steps for overdue documents and records each action as `crm_activity` and `document.event`.
* Late fees create a `fee` line on a new document or the original (setting), posting through the PAP-180 rules; retries follow Stripe smart retry windows, capped at four.
* Saved cards: pay page offers "save for future invoices" (Stripe SetupIntent), stored as `stripe_payment_method_id` on `fin_customer`; never stored raw.
* Automations (PAP-174) may call `recurring.pause|resume`; escalations notify finance via PAP-136 core.""",
Contract="""Provides: `recurring.create|update|pause|resume|preview`, `dunning.policies.*`, `dunning.run(documentId)`, events `recurring.generated`, `dunning.step_applied`, dataset `finance.recurring`, portal upcoming list. Consumes: documents and rules (PAP-180), Stripe client (PAP-177), connected charges (PAP-181, optional), jobs (PAP-43), notifications (PAP-136 core), automations hook (PAP-174, soft), consent for reminders ({{gap/growth/consent-centre}}, soft).""",
DoD="""* Vitest, integration and Playwright below green.
* Screenshots at 375, 1024, 1920 in three themes for schedule editor, dunning policy and portal list.
* `docs/finance/recurring-dunning.md`; CHANGELOG; Linear comment with demo link.""",
Test="""* Unit: next-run computation across month ends and DST, substitution, idempotency key, late fee maths with caps, retry windows.
* Integration (test clock): a monthly schedule generates three invoices over three simulated months; the second is left unpaid and receives remind, late fee and retry steps on the right days; a paused schedule skips a period; saved-card charge succeeds and fails (`4000000000000341`).
* E2E: create a schedule from an invoice, preview the next three dates, open the portal upcoming list; edit the dunning policy.
* Visual: matrix above.""",
Demo="""Reviewer turns a seeded invoice into a monthly schedule, previews the next three dates, advances the test clock a month, sees the generated invoice, advances past due and watches the reminder and late fee appear in the activity. Under two minutes.""",
Edge="""* 31st of the month cadence: last day of shorter months.
* Party opted out of reminders: dunning still applies fees but sends nothing, flagged for manual contact.
* Template edited: applies to future occurrences only.
* Customer pays during the retry window: pending retries cancelled.
* Connected account restricted: charges skipped, invoices still generated with bank instructions.""",
Deps="""PAP-180 (hard), PAP-43 (hard), PAP-177, PAP-181 (optional), PAP-136 core, PAP-174 (soft). Blocks nothing.""",
Agent="""Builder: Ledger (Payments Integrator with Bookkeeper on fees). Reviewer: Sentinel (Edge Case Hunter for calendars and retries, Code Reviewer).""",
Size="""M: schedules and a step ladder over the existing document model.""")


# FIX-5 (2026-09-17): folded into live issues as work packages; never create. See round2/folded-into-live-issues.json.
import json as _json, os as _os
_FOLDED = {f["key"] for f in _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "folded-into-live-issues.json")))["folded"]}
GAPS = [g for g in GAPS if g["key"] not in _FOLDED]
