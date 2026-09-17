# Rewritten specs for business-core PAP-175..PAP-180.
SPECS = {}
def add(k, **s): SPECS[k] = s

add("PAP-175",
Goal="""Fix the finance vocabulary every business on PaperOS shares: parties (customer, vendor, employee), chart of accounts, accounting periods, `Money`, dimensions and the `fin_transaction` header that payments, invoices, expenses, payroll and the ledger all reference. Later issues add behaviour; this one stops them drifting.""",
Scope="""In: `packages/finance/src/schema/` Drizzle tables with RLS and seeds; `packages/finance/src/money.ts`; six default charts of accounts (service, retail, SaaS, agency, clinic, restaurant) as seed JSON; oRPC CRUD `finance.parties|accounts|periods.*`; `docs/finance/data-model.md` with a Mermaid ER diagram and a Stripe, QuickBooks and Xero mapping table for PAP-206.

Out: journal posting (PAP-179), Stripe objects (PAP-177), payroll fields beyond identity (PAP-184).""",
Spec="""* `Money = { amountMinor: bigint, currency }` stored as `amount_minor bigint` plus `currency char(3)`; helpers `add`, `subtract`, `allocate(ratios)` (largest remainder), `convert(rate)` with `decimal.js`; ISO exponent table for JPY and KWD; formatting through PAP-27 `formatMoney`.
* `fin_settings`: `functional_currency, fiscal_year_start_month, tax_id, address, invoice_number_format, default_payment_terms_days, expense_approval_threshold_minor`.
* `fin_party`: role flags `is_customer|is_vendor|is_employee`, names, contact fields, addresses jsonb, `tax_id`, `tax_exempt`, `currency`, `payment_terms_days`, `user_id?`, `external_ids jsonb`, `archived_at`; extensions `fin_customer (credit_limit_minor, portal_enabled)`, `fin_vendor (default_expense_account_id, w9_on_file)`, `fin_employee (start_date, end_date, employment_type, pay_schedule, compensation jsonb, payroll_external_id, manager_party_id)`.
* `fin_account`: `code` unique per tenant, `type: asset|liability|equity|revenue|expense`, `subtype` (the stable handle posting rules use: `cash, ar, ap, stripe_balance, sales_tax_payable, payroll_liability, fees, fx_gain_loss, ...`), `parent_id`, `is_system`, `is_active`.
* `fin_period`: monthly, `status: open|closed|locked`, exclusion constraint against overlap.
* `fin_transaction`: `kind: invoice|payment|refund|expense|payroll_run|transfer|adjustment|payout|fee`, `party_id?`, `occurred_at`, `amount_minor`, `currency`, `status`, `source { system, id }` unique per tenant, `memo`, `metadata`, `dimensions jsonb`.
* All tables: `tenant_id` RLS (PAP-34), audit on write (PAP-38), registered as datasets (PAP-161).""",
Contract="""Provides: types `Money`, `Party`, `Account`, `Period`, `FinTransaction`, `AccountSubtype` enum, `moneySchema`, procedures `finance.parties|accounts|periods.list|get|create|update|archive`, datasets `finance.parties`, `finance.accounts`, seed `charts/<businessType>.json`. Consumes: `tenant|user` (PAP-33), RLS (PAP-34), audit (PAP-38), API conventions (PAP-268), `registerDataset` (PAP-161), `Money` formatting (PAP-27). Consumed by PAP-177 to PAP-186, PAP-196, PAP-206, PAP-187 (`billing_customer_id`).""",
DoD="""* Migrations apply on fresh and staging databases; cross-tenant harness green.
* Seeds create six charts; a test asserts every subtype named by any posting rule exists in each.
* Data dictionary regenerated (PAP-41); `docs/finance/data-model.md` published.
* Parties and accounts render as grid views in the demo tenant; screenshots at 375, 1024, 1920.
* ADR `docs/adr/00xx-finance-model.md`; CHANGELOG; Linear comment with doc link.""",
Test="""* Unit: `Money` allocation sums exactly for 10k random splits, currency mismatch throws, JPY and KWD exponents, no float path (`fast-check`).
* Integration (PGlite and Postgres): period overlap rejected; `source` uniqueness rejects a duplicate import; `is_system` account delete blocked; RLS harness on every table; each seed chart passes the subtype test.
* E2E: create a party through the API, open `finance.parties` grid, edit terms inline.
* Visual: grid at 375, 1024, 1920 in light and dark.""",
Demo="""Reviewer runs `pnpm db:seed --profile demo --business clinic`, opens `/finance/accounts` and sees the clinic chart of accounts grouped by type, then runs `pnpm tsx scripts/money-demo.ts` printing a 3-way allocation of 100.00 that sums exactly. Under two minutes.""",
Edge="""* Party that is both customer and vendor: flags allow it; reports treat roles separately.
* Period locked while an import backdates: `CONFLICT` naming the earliest open period.
* Contractor becomes W-2: `employment_type` change audited, history kept.
* Deleting a system account blocked; deactivation only at zero balance (checked by PAP-179).
* Changing functional currency after transactions exist: blocked with explanation.""",
Deps="""PAP-33 (hard), PAP-34 (hard), PAP-161 (dataset registry), PAP-27 (`Money` formatting), PAP-38. Blocks PAP-177, PAP-179, PAP-181, PAP-184, PAP-185.""",
Agent="""Builder: Ledger (Bookkeeper). Reviewer: Forge (Schema Wright) on schema, Sentinel (Code Reviewer) on money helpers.""",
Size="""M: schema and seeds are mechanical; the value is getting subtypes and mappings right.""")

add("PAP-176",
Goal="""Choose the first embedded payroll provider by scoring Check, Gusto Embedded, Deel and Rippling on embeddability, API completeness, sandbox access, pricing, geography and compliance ownership, and record it as an ADR that fixes the `PayrollProvider` interface PAP-184 implements.""",
Scope="""In: `docs/finance/payroll-research.md` (scored rubric with evidence links and access dates); ADR `docs/adr/00xx-payroll-provider.md`; draft interface `packages/finance/src/payroll/provider.ts` (types only); one Needs Justin item with exact sandbox signup steps and expected cost.

Out: integration code, contract negotiation, non-US payroll beyond a coverage note.""",
Spec="""* Rubric weights: API embeddability 25 (companies, employees, onboarding, schedules, runs, paystubs, filings, webhooks, embeddable components); sandbox without a sales call 15; pricing model and floor 15; compliance ownership 15 (filings, W-2/1099, state registrations); geography 10; developer experience 10 (TypeScript SDK, idempotency, errors, rate limits); time to first sandbox payroll 10. Score 1 to 5 with URLs.
* Method: official docs, pricing pages, status pages and changelogs via WebFetch; note quote-only pricing; record whether a sandbox key is obtainable within a day.
* Interface draft: `PayrollProvider { id; capabilities(): Capabilities; companies: { create, get, onboardingLink }; employees: { upsert, onboardingLink, list }; contractors?; paySchedules: { list, create }; payrolls: { preview, create, approve, cancel, list, get }; paystubs: { list, pdfUrl }; taxes: { filings }; webhooks: { verify(sig, body), parse(body): PayrollEvent } }` plus the `payroll.approved` event shape (gross, employer taxes, withholdings, net, fees per employee).
* Decision rule: highest score with sandbox access inside the build window; document runner-up and switch conditions (price per employee above X, missing state coverage, no TypeScript SDK).
* List what PaperOS builds regardless of provider: employee sync from `fin_employee`, pay-period calendar, approval flow, ledger posting, paystub portal.""",
Contract="""Provides: `PayrollProvider`, `Capabilities`, `PayrollEvent` types (compiled, no implementation), the ADR decision and reopen criteria, the Needs Justin sandbox request. Consumes: `fin_employee` shape (PAP-175), rubric format (PAP-210), license policy (PAP-211). Consumed by PAP-184 (implements the interface) and PAP-186 (upcoming payroll block reads `payroll_run`, shaped here).""",
DoD="""* Research doc with the scored table and at least four evidence links per provider.
* ADR merged as `accepted` or `proposed` pending Justin's sandbox approval, naming choice, runner-up and reopen criteria.
* `provider.ts` compiles under strict TypeScript and is acknowledged by the PAP-184 builder in a PR comment.
* Needs Justin issue filed with signup steps, cost and the test-mode-only scope.
* Registry entry drafted for PAP-215; CHANGELOG (docs); Linear comment with the score table.""",
Test="""* Unit: `pnpm tsc --noEmit` on `provider.ts`; a Vitest type test asserting a mock adapter satisfies `PayrollProvider` and that `Capabilities` gates optional members.
* Review: rubric arithmetic checked by a 10-line script from `results.json`; every evidence URL returns 200 in a link-check step.
* E2E and visual: none (research deliverable).""",
Demo="""Reviewer opens the ADR, reads the decision paragraph and the score table, then opens `provider.ts` and the Needs Justin issue listing the three signup steps. Under two minutes.""",
Edge="""* Signed agreement required before sandbox: score it, mark "blocked for build window".
* Pricing behind sales: estimate from partner case studies, flag low confidence.
* Mixed EOR and software products (Deel): evaluate the embedded software only.
* Docs contradicting on webhook signing: record both, plan a verification spike in PAP-184.
* International contractors: capability flag, not a blocker.""",
Deps="""None hard; starts now (moved to Ready for Claude per the round-2 audit). Uses PAP-175 for the employee shape and PAP-210 rubric if merged. Blocks PAP-184.""",
Agent="""Builder: Scout (Library Evaluator) with Ledger (Payroll Adapter) co-authoring the interface. Reviewer: Ledger lead and Atlas for the decision.""",
Size="""S: one time-boxed session plus ADR; the interface is the lasting artefact.""")

add("PAP-177",
Goal="""Charge tenants for plans: declare plans in code, sync them to Stripe Products and Prices, run Checkout for upgrades, expose the Customer Portal, and ingest webhooks idempotently into a local `subscription` model that PAP-178 reads. Platform billing only; tenant-to-customer payments arrive with PAP-181.""",
Scope="""In: `packages/finance/src/billing/` (`plans.ts`, `stripe.ts`, `sync-catalog.ts`, procedures `billing.*`, webhook route `/api/webhooks/stripe`, tables `billing_customer`, `subscription`, `stripe_event`); `/org/settings/billing` page and the portal billing entry (PAP-64); Stripe CLI scripts for local webhooks; nightly reconciliation job.

Out: usage metering ({{gap/business-core/usage-metering}}), tax (PAP-182), tenant invoices (PAP-180), dunning copy beyond Stripe defaults.""",
Spec="""* `stripe` SDK 17.x, one pinned `apiVersion`; keys `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PUBLISHABLE_KEY` from PAP-17; test keys until Justin approves live.
* `plans.ts`: `{ key: 'free'|'pro'|'business'|'enterprise', name, prices: { monthly, yearly } minor units, trialDays, entitlements: Record<EntitlementKey, boolean | number>, platformFeeBps }`; `pnpm billing:sync` upserts Products (`metadata.paperos_plan_key`) and Prices (lookup keys like `pro_monthly`), archives removed prices, never deletes.
* `billing_customer (tenant_id unique, stripe_customer_id, email, default_payment_method?)` created lazily with `metadata.tenant_id`.
* `subscription (id, tenant_id, stripe_subscription_id, plan_key, price_lookup_key, status, current_period_start|end, cancel_at_period_end, trial_end, seats, latest_invoice_id, updated_from_event_id)`.
* `billing.createCheckoutSession({ planKey, interval, seats })` and `billing.createPortalSession()`; portal configured by `billing:sync` for plan switches, payment methods, cancel at period end.
* Webhooks: `constructEvent`, insert `stripe_event (id pk, type, payload, received_at, processed_at, error)` first (duplicate returns 200), handlers for `checkout.session.completed`, `customer.subscription.*`, `invoice.paid|payment_failed`, `customer.updated`; apply only when `event.created` is newer than the stored one; 500 on failure so Stripe retries; alert after three failures.
* Each billing event creates a `fin_transaction` (`payment|refund`, source `stripe`) for later posting.
* `billing.manage` for owner and admin; agents denied (PAP-60).""",
Contract="""Provides: `plans`, `Plan`, `getPlan(tenantId)`, `subscription` row shape, event `billing.subscription.changed { tenantId, planKey, status }` on the outbox, `stripe_event` table reused by PAP-181 (with `account` column), `stripeClient()`, procedures `billing.*`, Stripe CLI scripts. Consumes: tenant and active org (PAP-58), `fin_transaction` (PAP-175), env (PAP-17), portal shell (PAP-64), notifications for failures (PAP-136 core). Consumed by PAP-178, PAP-180, PAP-181, PAP-182, PAP-196, PAP-194 revenue join, {{gap/business-core/usage-metering}}.""",
DoD="""* Test-mode flow recorded: `4242` checkout, plan visible on the billing page within 5 s of the webhook, portal downgrade updates `subscription`.
* Vitest, integration and Playwright below green.
* `docs/finance/billing.md` with webhook runbook; ADR naming Stripe as processor; CHANGELOG; Linear comment with checkout replay.""",
Test="""* Unit: each handler with fixture events; duplicate delivery; out-of-order `event.created`; bad signature; plan sync diff is idempotent.
* Integration: `stripe trigger checkout.session.completed` against the dev server produces `subscription` and `fin_transaction`; reconciliation job repairs a deliberately mutated row from Stripe.
* E2E: billing page states `trialing`, `active`, `past_due` from seeded rows; upgrade button opens Checkout URL.
* Visual: 375, 1024, 1920 in three themes for the three states.""",
Demo="""Reviewer runs `stripe listen` and `pnpm dev`, upgrades the demo tenant with card `4242`, returns to `/org/settings/billing` showing Pro within seconds, then opens the portal and cancels at period end, seeing the banner update. Under two minutes.""",
Edge="""* Webhook before the session is known: handler creates `billing_customer` from metadata.
* Tenant in deletion grace with an active subscription: cancel at period end, audited.
* Renewal decline: `past_due` banner; entitlements downgrade only at `unpaid` or `canceled`.
* Plan removed from `plans.ts`: price archived, subscribers keep working.
* Two admins upgrade concurrently: second completion detected and refunded with a notice.""",
Deps="""PAP-175 (hard), PAP-58 (hard), PAP-17, PAP-64, PAP-136 (soft). Blocks PAP-178, PAP-180, PAP-181, PAP-182, PAP-196.""",
Agent="""Builder: Ledger (Payments Integrator). Reviewer: Sentinel (Security Auditor for webhooks and secrets, Code Reviewer).""",
Size="""M: Stripe does the heavy lifting; ordering and idempotency are the work.""")

add("PAP-178",
Goal="""Make paid features gate themselves: map each plan to typed entitlements (booleans and limits), expose them through the permission engine so specs can declare `requires: [entitlement.sso]`, enforce limits inside the creating transaction, and show one consistent upgrade prompt instead of silent failures.""",
Scope="""In: `packages/finance/src/entitlements/` (registry, resolver, oRPC middleware, hooks, `<EntitlementGate />`, `<UpgradePrompt />`); keys v1 `seats, publicViews, dashboards, storageGb, apiRateLimit, whiteLabel, sso, payroll, connectPayments, auditRetentionDays, agentSessionsPerDay`; hook points in PAP-58 `beforeInvite`, PAP-172, PAP-173, PAP-37, PAP-65, PAP-99; usage bars on the billing page.

Out: proration (Stripe), enterprise override UI beyond a JSON field, metering of usage ({{gap/business-core/usage-metering}} supplies `used` for `storageGb` and `agentSessionsPerDay`).""",
Spec="""* `defineEntitlement({ key, type: 'boolean'|'limit', label, description, unit?, upgradeCopy })`; values from `plans.ts`; `tenant.entitlement_overrides jsonb` (platform admins) merge last; free plan is the floor.
* `resolveEntitlements(tenantId)` cached per request, invalidated on `billing.subscription.changed` and override writes; `entitlements.mine` procedure; pushed in the session payload at login and tenant switch.
* Resolver injects `actor.attributes.entitlements` so PAP-227 conditions work; PAP-116 access sections accept `requires: [entitlement.<key>]`.
* `assertWithinLimit(tenantId, key, currentCountFn, increment = 1)` inside the creating transaction with an advisory lock per tenant and key; error `ORPCError('FORBIDDEN', { code: 'ENTITLEMENT_LIMIT', key, limit, current })`.
* `useEntitlement(key) => { allowed, limit, used, remaining, plan, upgradeUrl }`; `<EntitlementGate key fallback="prompt"|"hide"|"disable">`; prompt shows the smallest plan including the feature and links Checkout for admins.
* Downgrade: nothing deleted; over-limit resources read-only with a banner; 14-day grace configurable.
* Applies to agent principals; `agentSessionsPerDay` read by PAP-99.""",
Contract="""Provides: `Entitlements` type, `EntitlementKey`, `resolveEntitlements`, `assertWithinLimit`, `useEntitlement`, `EntitlementGate`, `UpgradePrompt`, procedure `entitlements.mine`, error code `ENTITLEMENT_LIMIT`, `requires: [entitlement.*]` spec shorthand, `docs/finance/entitlements.md` generated matrix. Consumes: `plans` and `billing.subscription.changed` (PAP-177), attribute conditions (PAP-227), spec access adapter (PAP-229, PAP-116), `beforeInvite` (PAP-58), session payload (PAP-223). Consumed by PAP-172, PAP-173, PAP-37, PAP-65, PAP-99, PAP-169, PAP-195 plan clauses.""",
DoD="""* Vitest, permission-matrix, Playwright and Storybook below green.
* `docs/finance/entitlements.md` generated from the registry with the plan matrix.
* CHANGELOG; Linear comment with demo link and matrix.""",
Test="""* Unit: precedence free < plan < override; `limit 0` versus boolean false; `useEntitlement` derived values.
* Integration: 20 parallel creates against limit 5 yield exactly 5 successes; downgrade makes the sixth public view return the read-only page; resolver cache invalidates on the outbox event; PAP-63 matrix includes an entitlement-gated page for each audience.
* E2E: free tenant hits the public-view limit, sees the prompt, seeded upgrade flips access without reload.
* Visual: gate and prompt at 375, 1024, 1920 in three themes.""",
Demo="""Reviewer, on the free demo tenant, creates public views until the fourth attempt shows the upgrade prompt naming Pro, runs `pnpm tsx scripts/set-plan.ts demo pro`, and creates the view without reloading. Under two minutes.""",
Edge="""* Webhook delayed after checkout: client polls `entitlements.mine` for 30 s with "activating".
* Override grants a feature the plan lacks: allowed, labelled "included by agreement".
* Trial ends over the free limit: read-only rules, no deletion.
* Spec references an unknown key: PAP-117 validator fails the PR.
* Platform admin viewing a tenant: the tenant's entitlements apply, never their own.""",
Deps="""PAP-177 (hard), PAP-59 children (hard), PAP-116, PAP-58, PAP-223 (session payload). Blocks (soft) PAP-172, PAP-173, PAP-65, PAP-99.""",
Agent="""Builder: Ledger (Payments Integrator). Reviewer: Sentinel (Security Auditor on bypass attempts, Code Reviewer).""",
Size="""M: small core, many touchpoints.""")

add("PAP-179",
Goal="""Build the double-entry ledger PaperOS owns: balanced journal entries against the chart of accounts, period controls, immutability of posted entries with reversals instead of edits, a tamper-evident hash chain, posting rules that translate business events into entries, and balances fast enough for reports. Every money-moving feature posts here. Umbrella for three children.""",
Scope="""Children (M each, same milestone, Backlog):

* {{business-core/ledger/journal-constraints}} Journal tables, balance trigger, immutability trigger, gapless per-tenant numbering, `fin_account_balance` maintenance.
* {{business-core/ledger/hashchain-reversal-close}} Hash chain with nightly `verifyChain`, `ledger.reverse`, period close and lock workflow.
* {{business-core/ledger/rules-ui-trialbalance}} Posting rule registry with the first five rules, `/finance/journal` UI, trial balance and `rebuildBalances`.

Out: report layouts (PAP-183), consolidation, inventory costing.""",
Spec="""Decisions binding all children:

* `fin_journal_entry (id uuidv7, tenant_id, entry_number bigint per tenant, period_id, posted_at, effective_date, memo, status: draft|posted|reversed, source_type, source_id, transaction_id?, reversal_of_id?, reversed_by_id?, created_by, posted_by, prev_hash, hash, dimensions)`; `fin_journal_line (entry_id, line_no, account_id, party_id?, debit_minor, credit_minor, currency, fx_rate numeric(18,8), functional_minor, memo, dimensions)` with `CHECK ((debit_minor > 0) <> (credit_minor > 0))`.
* Posting runs in one SQL function under a per-tenant advisory lock: balance check on `functional_minor` (`UNBALANCED`), minimum two lines, active tenant accounts, next `entry_number`, `hash = sha256(prev_hash || canonical_json(entry, lines))`, incremental balance update.
* `BEFORE UPDATE OR DELETE` on posted rows raises `IMMUTABLE_ENTRY`; the only path is `ledger.reverse`.
* Periods: `closed` needs `ledger.reopen`, `locked` rejects everything; close requires no drafts and a verified chain.
* `definePostingRule({ event, build(tx, ctx) => JournalDraft })` resolving accounts by `subtype`, never code; `ledger.postEvent(tx)` idempotent by `(source_type, source_id)`.
* Writes need `ledger.post`; agents may draft, not post, unless the character carries `ledger:post`.""",
Contract="""Provides: `ledger.createDraft|post|reverse|list|trialBalance|verifyChain|rebuildBalances|postEvent`, `definePostingRule`, `JournalDraft` type, `AccountSubtype` usage rules, dataset `finance.journal`, event `ledger.entry.posted { entryId, sourceType, sourceId }`, error codes `UNBALANCED`, `IMMUTABLE_ENTRY`, `PERIOD_LOCKED`. Consumes: accounts, periods, transactions, `Money` (PAP-175), RLS (PAP-34), audit (PAP-38), grid (PAP-165), `can()` (PAP-227), observability for chain alerts (PAP-40). Consumed by PAP-180, PAP-181, PAP-182, PAP-183, PAP-184, PAP-185, PAP-196, PAP-206.""",
DoD="""* All three children Done.
* Concurrency: 50 parallel posts keep `entry_number` gapless and the chain valid.
* Playwright: draft, post, reverse, close period; screenshots at 375, 1024, 1920 in three themes.
* `docs/finance/ledger.md` with the rule catalogue and invariants; ADR on immutability and hash chain; CHANGELOG; Linear comment with `verifyChain` output.""",
Test="""Umbrella `ledger.e2e.test.ts` on Postgres: post 10k random balanced entries across two currencies from 50 workers; assert gapless numbering, balances equal a brute-force sum per account and period, `verifyChain` passes; tamper one row as superuser and assert the first mismatch is reported; reverse an entry and assert mirrored lines and both statuses; close a period and assert `PERIOD_LOCKED` on a backdated post; run every registered rule against its fixture transaction and assert the draft balances.""",
Demo="""Reviewer opens `/finance/journal`, creates a two-line manual entry (Post disabled until balanced), posts it, tries to edit and sees the immutability error, reverses it with a reason, then runs `pnpm ledger verify demo` printing the chain result. Under two minutes.""",
Edge="""* Multi-currency entry balances in functional currency; rounding remainder posts to `fx_gain_loss`.
* Three-way split uses `Money.allocate`, never off by a cent.
* Reversal of a reversal allowed, both linked.
* Import backdating into a closed period: rejected with an offer to post on period start.
* Tenant hard delete: ledger rows move to an archive schema for the retention period.""",
Deps="""PAP-175 (hard), PAP-34, PAP-38, PAP-165 (journal UI), PAP-59 children. Blocks PAP-180, PAP-181, PAP-183, PAP-184, PAP-185, PAP-196, PAP-206.""",
Agent="""Builder: Ledger (Bookkeeper). Reviewer: Sentinel (Security Auditor for immutability, Code Reviewer), Forge (Schema Wright) for triggers.""",
Size="""L, split into three M children plus a dedicated adversarial review.""")

add("PAP-180",
Goal="""Let any tenant bill anyone: quotes that convert to invoices, invoices with lines, taxes and terms, receipts on payment, branded PDFs, a public pay page backed by Stripe, credit notes, and automatic ledger postings for receivables, revenue and cash. Umbrella for three children.""",
Scope="""Children (M each, same milestone, Backlog):

* {{business-core/invoicing/model-statemachine}} `fin_document` and lines, per-kind sequences, server-side totals, state machine, quote acceptance and conversion, void and credit notes.
* {{business-core/invoicing/pdf-paypage}} PDF rendering with the PAP-235 theme, `/pay/:token` and `/doc/:token`, Stripe Checkout on platform or connected account, receipts.
* {{business-core/invoicing/postings-portal-emails}} Posting rules `invoice.*`, `credit_note.issued`, manual payments, reminders job, portal invoice list and email templates.

Out: recurring invoices and dunning ({{gap/business-core/recurring-dunning}}), inventory, multi-language templates beyond locale formatting.""",
Spec="""Decisions binding all children:

* `fin_document (kind: quote|invoice|receipt|credit_note|bill, number formatted by fin_settings.invoice_number_format, party_id, status per kind, issue_date, due_date, currency, subtotal|discount|tax|total|paid|balance _minor, terms, notes, source_document_id, stripe_payment_intent_id?, stripe_checkout_session_id?, public_token, pdf_file_id, sent_at, viewed_at, metadata)`; `fin_document_line (line_no, description, quantity numeric(12,4), unit_price_minor, discount_pct, tax_rate_id?, tax_minor, amount_minor, revenue_account_id?, dimensions)`.
* Invoice statuses `draft|issued|sent|viewed|partial|paid|overdue|void`; transitions are the only writes to `status`.
* `documents.issue` freezes lines and number, posts `invoice.issued` (debit `ar`, credit revenue per line, credit `sales_tax_payable`), creates the Stripe session on the connected account when PAP-181 is enabled else on the platform account in test mode.
* Payment webhook posts `invoice.paid` (debit `cash` or `stripe_balance`, credit `ar`), issues a receipt, emails it; idempotent by `stripe_event.id`.
* PDFs via `@react-pdf/renderer` 4.x using `brandingToInlineCss` and the template kit from PAP-235, content-addressed in PAP-37.
* Reminders at due+3 and due+14 unless disabled; `overdue` set daily.""",
Contract="""Provides: `documents.create|update|issue|send|accept|void|recordPayment|creditNote|list|get`, `renderDocumentPdf(id)`, routes `/pay/:token`, `/doc/:token`, events `document.issued|paid|voided`, dataset `finance.documents` (AR aging for PAP-183), `bill` kind for PAP-185. Consumes: Stripe client and `stripe_event` (PAP-177), posting (PAP-179), connected charges (PAP-181, optional), tax calculation (PAP-182, optional), files (PAP-37), email templates and theme (PAP-235, PAP-136 core), portal shell (PAP-64), `Money` (PAP-175). Consumed by PAP-183, PAP-185, PAP-196 statements, {{gap/business-core/recurring-dunning}}.""",
DoD="""* All three children Done.
* PDF snapshot tests (rasterised with `pdf-to-img`) for invoice, quote, receipt at two brands with visual diff in CI.
* Playwright: editor, public pay page at 375 and 1024, portal list; screenshots at 375, 768, 1024, 1440, 1920 in three themes.
* `docs/finance/invoicing.md`; CHANGELOG; Linear comment with a live test-mode pay link and replay.""",
Test="""Umbrella `invoicing.e2e.test.ts`: create a quote with three lines including 0.3333 quantity and two tax rates, accept it from the public page, issue the invoice and assert the ledger lines to the cent, pay through Stripe test mode via `stripe trigger`, assert `paid`, receipt document, `invoice.paid` posting and the emailed receipt in the outbox; void a fresh invoice and assert the reversal; issue a credit note against a paid invoice; run 20 concurrent issues and assert a gapless sequence.""",
Demo="""Reviewer creates an invoice in the editor, clicks Issue, opens the pay link in a private window, pays with `4242`, and returns to see the invoice paid with a receipt PDF and the journal entries listed in the activity tab. Under two minutes.""",
Edge="""* Partial bank-transfer payment recorded manually sets `partial`.
* Currency differs from functional: FX at issue and payment, gain or loss posted.
* Voided invoice pay link shows "Voided", no Pay button.
* Number format changed mid-year: sequence continues from the max.
* Duplicate webhook after receipt: idempotent.""",
Deps="""PAP-179 (hard), PAP-177 (hard), PAP-37 (hard, PDFs), PAP-235 (hard, theme), PAP-181 and PAP-182 (optional), PAP-136 core, PAP-64. Blocks PAP-182, PAP-183, {{gap/business-core/recurring-dunning}}.""",
Agent="""Builder: Ledger (Payments Integrator with Bookkeeper on rules). Reviewer: Sentinel (Security Auditor for the public route, Visual Inspector for PDFs).""",
Size="""L, split into three M children.""")
