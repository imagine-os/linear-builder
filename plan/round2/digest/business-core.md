# business-core — Business Core: Payments, Finance & Payroll
PHASE P2 prio 1 dependsOn ['identity', 'tables']
SUMMARY: Stripe Billing, Connect and Tax for money movement, a double-entry ledger we own, invoicing and finance reports, and a payroll provider adapter.
DESC: Goal: every business built on PaperOS can take payments, keep books and run payroll from day one. Stripe Billing handles plans, subscriptions and the customer portal; Connect lets tenants accept payments and receive payouts; Stripe Tax handles sales tax. A double-entry ledger in Postgres is the finance primitive we own, feeding invoices, quotes, receipts, P&L, balance sheet, cash flow and aging reports rendered by the views engine. Payroll sits behind a provider interface with Check or Gusto Embedded as the first adapter. Plan entitlements are enforced by the permission engine. Non-goals: being a payment processor or a payroll provider ourselves.
MILESTONES: ['Stripe billing live 2026-09-27: Finance data model, payroll ADR, Stripe Billing, entitlements', 'Ledger and reports 2026-09-29: Ledger, invoicing, Connect, Tax, finance reports', 'Payroll adapter and cash dashboard 2026-10-01: Payroll adapter, expenses, cash-flow dashboard']


## PAP-175 [P1 Spec M prio1 Backlog] Specify the finance data model: customers, vendors, employees, accounts, transactions and periods across all business types
key=business-core/finance-data-model milestone=Stripe billing live agent=Builder: Ledger (Bookkeeper). Reviewer: Forge (Schema Wright
blockedBy=['PAP-33'] blocks=['PAP-179', 'PAP-177']
GOAL: Specify and migrate the finance entities every business built on PaperOS shares, regardless of type: parties (customers, vendors, employees), the chart of accounts, accounting periods, money as a type, and the transaction header that payments, invoices, expenses, payroll and the ledger all reference. Later business-core issues add behaviour; this issue fixes the vocabulary so they do not drift.
SCOPE: In:

* `packages/finance/src/schema/` Drizzle tables with RLS, seeds and a spec doc `docs/finance/data-model.md` with an ER diagram (Mermaid).
* `Money` value type and helpers in `packages/finance/src/money.ts`.
* Default charts of accounts per business type (service, retail, SaaS, agency, clinic, restaurant) as seed JSON.
* oRPC CRUD for parties, accounts and periods following `data-layer/api-layer` conventions.

Out: journal posting (`business-core/ledger`), Stripe objects (`business-core/stripe-billing`), payroll fields beyond identity (`business-core/payroll-adapter`).
SPEC(first 1200): * `Money = { amountMinor: bigint, currency: ISO4217 }` stored as `amount_minor bigint` plus `currency char(3)`; helpers `add`, `subtract`, `allocate(ratios)` (largest-remainder), `convert(rate)` using `decimal.js` 10.x for rates; formatting reuses `design-system/data-display` `Money`. Tenant `fin_settings`: `functional_currency`, `fiscal_year_start_month`, `tax_id`, `address`, `invoice_number_format`, `default_payment_terms_days`.
* `fin_party`: `id, tenant_id, kind flags is_customer|is_vendor|is_employee, display_name, legal_name, email, phone, billing_address jsonb, shipping_address jsonb, tax_id, tax_exempt, currency, payment_terms_days, user_id? (link to identity user for portal access), external_ids jsonb ({ stripeCustomerId, quickbooksId, ... }), notes, archived_at`. Role extensions: `fin_customer (party_id, credit_limit_minor, portal_enabled)`, `fin_vendor (party_id, default_expense_account_id, w9_on_file)`, `fin_employee (party_id, start_date, end_date, employment_type: 'w2'|'contractor'|'intl', pay_schedule, payroll_external_id, manager_party_id)`.
* `fin_account`: `id, tenant_id, code (unique per tenant, e.g. 1000), name, type: asset|liability|equity|revenue|expense, subt
DOD:
* Migrations apply on a fresh DB and on the staging DB; cross-tenant harness green.
* Seeds create six default charts of accounts; a test asserts every posting-rule subtype exists in each.
* Vitest for `Money` (allocation sums exactly, no float paths, currency mismatch throws).
* Data dictionary regenerated (`data-layer/data-dictionary`) and `docs/finance/data-model.md` with ER diagram published.
* Parties and accounts appear as datasets with grid views in the demo tenant; screenshots at 375, 1024, 1920.
* ADR `docs/adr/00xx-finance-model.md`; CHANGELOG entry; Linear comment with doc link.
EDGE:
* A party who is both customer and vendor (contra settlement): flags allow it; reports treat roles separately.
* Currency with zero minor units (JPY) or three (KWD): `Money` uses ISO exponent table.
* Period locked while an import backdates transactions: reject with `CONFLICT` and suggest the earliest open period.
* Employee converted from contractor to W-2: `fin_employee` keeps history via `employment_type` change audit.
* Deleting a system account: blocked; deactivate only if balance is zero (checked by ledger later).
* Tenant changes functional currency after transactions exist: blocked with explanation.
DEPS: * `data-layer/core-entities` (tenant, user), `data-layer/drizzle-schema`, `data-layer/rls-tenancy`, `tables/view-model-spec` (dataset registry).


## PAP-176 [P1 Research S prio2 Backlog] Research payroll APIs (Check, Gusto Embedded, Deel, Rippling) for embeddability and pricing; write ADR
key=business-core/payroll-research milestone=Stripe billing live agent=Builder: Scout (Library Evaluator) with Ledger (Payroll Adap
blockedBy=[] blocks=['PAP-184']
GOAL: Choose the first embedded payroll provider by evaluating Check, Gusto Embedded, Deel and Rippling against embeddability, API completeness, sandbox access, pricing, geography and compliance ownership, and record the decision as an ADR that defines the provider interface `business-core/payroll-adapter` will implement.
SCOPE: In:

* Research doc `docs/finance/payroll-research.md` with a scored rubric and evidence links.
* ADR `docs/adr/00xx-payroll-provider.md` (context, options, decision, consequences, reopen criteria).
* Draft `PayrollProvider` interface (TypeScript, no implementation) in `packages/finance/src/payroll/provider.ts` derived from the intersection of provider capabilities.
* Sandbox access request written as a Needs Justin item with the exact signup steps.

Out: any integration code, contract negotiation, non-US payroll beyond noting coverage.
SPEC(first 1200): * Rubric (weights): API-first embeddability (25): REST coverage for companies, employees, onboarding, pay schedules, payroll runs, paystubs, tax filings, webhooks; embeddable UI components for onboarding and tax setup. Sandbox availability without sales call (15). Pricing model and floor (15): per-employee-per-month, platform fees, revenue share. Compliance ownership (15): who is employer of record for filings, W-2/1099 generation, state registrations. Geography (10): US states, contractors international. Developer experience (10): docs, SDKs (TypeScript), idempotency, error model, rate limits. Time-to-first-payroll in sandbox (10). Score each 1-5 with evidence URLs and access dates.
* Method: `WebFetch` official docs and pricing pages; note where pricing is quote-only; check status pages and changelogs for cadence; record whether a sandbox key can be obtained in under a day.
* Interface draft: `PayrollProvider { id; capabilities(): Capabilities; companies: { create, get, onboardingLink }; employees: { upsert, onboardingLink, list }; contractors?: {...}; paySchedules: { list, create }; payrolls: { preview, create, approve, cancel, list, get }; paystubs: { list, pdfUrl }; taxes: { f
DOD:
* Research doc with scored table and at least 4 evidence links per provider.
* ADR merged with status `accepted` or `proposed` awaiting Justin's sandbox approval, stating the choice and reopen criteria.
* `provider.ts` interface compiles and is reviewed by the adapter builder.
* Needs Justin issue created with signup steps, expected cost and what he must approve (test-mode only).
* Parity note in `docs/views/parity.md` cross-links nothing; instead link the ADR from `libraries/registry`.
* CHANGELOG entry (docs); Linear comment summarising scores in a table.
EDGE:
* A provider requires a signed agreement before sandbox: score it but mark "blocked for build window".
* Pricing hidden behind sales: estimate from public partner case studies and flag as low-confidence.
* Provider APIs mixing employer-of-record and software models (Deel): evaluate the embedded software product only.
* Docs contradicting each other on webhook signing: record both and plan a verification spike in the adapter issue.
* International contractors needed by a future tenant: capture as a capability flag, not a blocker.
DEPS: * `business-core/finance-data-model` for the employee entity shape; `libraries/eval-rubric` for the shared rubric format; feeds `business-core/payroll-adapter`.


## PAP-177 [P1 Build M prio1 Backlog] Integrate Stripe Billing: products, prices, subscriptions, customer portal and webhooks
key=business-core/stripe-billing milestone=Stripe billing live agent=Builder: Ledger (Payments Integrator). Reviewer: Sentinel (S
blockedBy=['PAP-175', 'PAP-58'] blocks=['PAP-182', 'PAP-181', 'PAP-180', 'PAP-178']
GOAL: Let PaperOS charge tenants for plans: define plans in code, sync them to Stripe Products and Prices, run Checkout for upgrades, expose the Stripe Customer Portal for self-service, and ingest webhooks idempotently into a local `subscription` model that `business-core/entitlements` reads. This is platform billing (PaperOS to tenant); tenant-to-customer payments arrive with Connect.
SCOPE: In:

* `packages/finance/src/billing/`: `plans.ts`, `stripe.ts` client, `sync-catalog.ts`, oRPC `billing.*`, webhook route `/api/webhooks/stripe`, tables `billing_customer`, `subscription`, `stripe_event`.
* Pages `/org/settings/billing` (staff console) and the billing entry in `identity/customer-portal-shell`.
* Stripe test mode end to end with the Stripe CLI for local webhooks; Vitest against `stripe-mock` is optional, real test mode is required.

Out: usage-based metering (record hooks only), tax (`business-core/tax-compliance`), invoices to tenant customers (`business-core/invoicing`), dunning email copy beyond Stripe defaults.
SPEC(first 1200): * Library `stripe` Node SDK 17.x pinned with `apiVersion` fixed in one constant; keys from `app-shell/env-config` (`STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PUBLISHABLE_KEY`), test keys only until Justin approves live.
* Plans declared in `plans.ts`: `{ key: 'free'|'pro'|'business'|'enterprise', name, prices: { monthly, yearly } in minor units, trialDays, entitlements: Record<EntitlementKey, boolean | number> }`; `pnpm billing:sync` upserts Products (metadata `paperos_plan_key`) and Prices (lookup keys `pro_monthly`), never deletes, archives removed prices; idempotent.
* `billing_customer`: `tenant_id unique, stripe_customer_id, email, default_payment_method?`; created lazily on first checkout with `metadata.tenant_id`.
* `subscription`: `id, tenant_id, stripe_subscription_id, plan_key, price_lookup_key, status (Stripe statuses), current_period_start/end, cancel_at_period_end, trial_end, seats, latest_invoice_id, updated_from_event_id`.
* `billing.createCheckoutSession({ planKey, interval, seats })` returns a Checkout URL with `client_reference_id = tenantId`, `success_url` to `/org/settings/billing?session_id=`, `allow_promotion_codes`; `billing.createPortalSession()` 
DOD:
* Test-mode flow recorded: checkout with `4242` card, plan appears in the billing page within 5 s of the webhook, portal downgrade updates `subscription`.
* Vitest for handlers with fixture events, idempotency (duplicate delivery), out-of-order events, signature failure.
* Stripe CLI `stripe trigger` scripts in `packages/finance/scripts/` documented for local development.
* Playwright e2e of the billing page states (trialing, active, past_due) using seeded rows; screenshots at 375, 1024, 1920 in three themes.
* `docs/finance/billing.md` including webhook runbook; ADR noting Stripe as processor; CHANGELOG entry; Linear comment with a video replay of the checkout flow.
EDGE:
* Webhook arrives before the DB knows the checkout session: handler creates `billing_customer` from `metadata.tenant_id`.
* Tenant deleted (grace period) with an active subscription: cancel at period end automatically, audited.
* Card declines at renewal: `past_due` banner with portal link; entitlements downgrade only after Stripe marks `unpaid` or `canceled`.
* Plan removed from `plans.ts` while tenants still subscribe: price archived, existing subscriptions keep working, upgrade path shown.
* Clock skew between Stripe and server: use `event.created`, not receipt time.
* Two admins click Upgrade concurrently: two Checkout sessions, Stripe allows one subscription per customer per our metadata guard; second completion is detected and refunded automatically with a notice.
DEPS: * `identity/org-tenancy` (tenant, active org), `business-core/finance-data-model` (`fin_transaction`), `app-shell/env-config`, `identity/customer-portal-shell` for the customer entry point.


## PAP-178 [P2 Build M prio1 Backlog] Map plans to feature entitlements enforced by the permission engine
key=business-core/entitlements milestone=Stripe billing live agent=Builder: Ledger (Payments Integrator). Reviewer: Sentinel (S
blockedBy=['PAP-59', 'PAP-177'] blocks=[]
GOAL: Make paid features gate themselves: map each plan to typed entitlements (booleans and limits), expose them through the permission engine so page specs and components can declare `requires: entitlement.publicViews`, enforce limits server-side at the point of creation, and show consistent upgrade prompts instead of silent failures.
SCOPE: In:

* `packages/finance/src/entitlements/`: registry, resolver, oRPC middleware, React hooks, `<UpgradePrompt />`, `<EntitlementGate />`.
* Entitlement keys v1: `seats` (number), `publicViews` (number), `dashboards` (number), `storageGb` (number), `apiRateLimit` (number), `whiteLabel` (bool), `sso` (bool), `payroll` (bool), `connectPayments` (bool), `auditRetentionDays` (number), `agentSessionsPerDay` (number).
* Hook points in `identity/org-tenancy` (`beforeInvite`), `tables/view-sharing` (public view count), `tables/dashboard-blocks`, `data-layer/file-storage` (storage), `identity/sso-scim`, `pm-linear/concurrency` (agent sessions).

Out: per-seat proration logic (Stripe handles quantity), custom enterprise overrides UI beyond a JSON field, metering of usage-based prices.
SPEC(first 1200): * Registry `defineEntitlement({ key, type: 'boolean'|'limit', label, description, unit?, upgradeCopy })`; plans in `business-core/stripe-billing` `plans.ts` supply values; `tenant.entitlement_overrides jsonb` (set by platform admins only) merges last. Free plan defaults are the floor when no subscription exists.
* Resolver `resolveEntitlements(tenantId) => Entitlements` cached per request and invalidated on `subscription` change events and override writes; exposed via `orpc.entitlements.mine` to the client and pushed through the session payload at login and tenant switch.
* Permission integration: the resolver injects `actor.attributes.entitlements` so `identity/rbac-abac` conditions like `{ path: 'actor.attributes.entitlements.whiteLabel', op: 'eq', value: true }` work; spec builder access sections accept a shorthand `requires: [entitlement.sso]` that compiles to that condition (`spec-builder/access-section`).
* Limits: `assertWithinLimit(tenantId, key, currentCountFn, increment = 1)` used inside the creating transaction (advisory lock per tenant and key) so concurrent creates cannot exceed the limit; returns `ORPCError('FORBIDDEN', { code: 'ENTITLEMENT_LIMIT', key, limit, current
DOD:
* Vitest for resolver precedence (free < plan < override), limit assertion under concurrency (spawn 20 parallel creates against limit 5, exactly 5 succeed), downgrade read-only behaviour.
* Permission matrix tests (`identity/permission-tests`) include an entitlement-gated page.
* Playwright: free tenant hits the public-view limit, sees the prompt, seeded upgrade flips access without reload (session refresh).
* Storybook for gate and prompt tagged `visual`; screenshots at 375, 1024, 1920 in three themes.
* `docs/finance/entitlements.md` listing keys and plan matrix, generated from the registry.
* CHANGELOG entry; Linear comment with demo link and the plan matrix table.
EDGE:
* Subscription webhook delayed after checkout: client polls `entitlements.mine` for 30 s after return from Stripe and shows "activating".
* Override grants a feature the plan lacks: allowed, shown as "included by agreement" in billing.
* Limit of 0 vs boolean false: registry forbids limits below 0; 0 means "none allowed" and renders as boolean-off in UI.
* Trial ends with usage over the free limit: read-only rules apply, no deletion.
* Entitlement key referenced in a spec but missing from the registry: validator (`spec-builder/validator`) fails the PR.
* Platform admin (PaperOS staff) viewing a tenant: their own entitlements never apply, the tenant's do.
DEPS: * `business-core/stripe-billing` (plans and subscription), `identity/rbac-abac` (attribute conditions), `spec-builder/access-section` (shorthand), `identity/org-tenancy` (`beforeInvite` hook).


## PAP-179 [P2 Build L prio1 Backlog] Build a double-entry ledger (accounts, journal entries, periods) in Postgres with immutability guarantees
key=business-core/ledger milestone=Ledger and reports agent=Builder: Ledger (Bookkeeper). Reviewer: Sentinel (Security A
blockedBy=['PAP-175'] blocks=['PAP-206', 'PAP-185', 'PAP-184', 'PAP-183', 'PAP-180']
GOAL: Build the double-entry ledger PaperOS owns: journal entries with balanced lines against the chart of accounts, period controls, immutability of posted entries with reversals instead of edits, a tamper-evident hash chain, posting rules that translate business events into entries, and balance materialisation fast enough to drive reports. Every money-moving feature posts here.
SCOPE: In:

* Tables `fin_journal_entry`, `fin_journal_line`, `fin_account_balance`; triggers and constraints; oRPC `ledger.*`.
* Posting rule registry and the first rules for `payment`, `refund`, `fee`, `adjustment`, `transfer` (invoice, payroll and expense rules ship with their issues).
* Manual journal entry UI (`/finance/journal`) and entry detail view; trial balance endpoint.
* Period close/lock workflow.

Out: reports layout (`business-core/finance-reports`), multi-entity consolidation, inventory costing.
SPEC(first 1200): * `fin_journal_entry`: `id uuidv7, tenant_id, entry_number bigint (per-tenant sequence), period_id, posted_at timestamptz, effective_date date, memo, status: draft|posted|reversed, source_type, source_id, transaction_id? (fin_transaction), reversal_of_id?, reversed_by_id?, created_by (user or agent), posted_by, prev_hash bytea, hash bytea, dimensions jsonb`. `fin_journal_line`: `id, entry_id, line_no, account_id, party_id?, debit_minor bigint default 0, credit_minor bigint default 0, currency, fx_rate numeric(18,8) (to functional currency), functional_minor bigint, memo, dimensions jsonb`; `CHECK ((debit_minor > 0) <> (credit_minor > 0))`.
* Balance trigger on posting: sum of `functional_minor` debits equals credits per entry or `RAISE EXCEPTION 'UNBALANCED'`; minimum two lines; all accounts active and belonging to the tenant.
* Immutability: `BEFORE UPDATE OR DELETE` trigger on `posted` entries and their lines raises `IMMUTABLE_ENTRY`; the only allowed change is setting `status = reversed` and `reversed_by_id` through the `ledger.reverse` function. Drafts are editable until posted.
* Hash chain: `hash = sha256(prev_hash || canonical_json(entry + lines))` per tenant in `entry_numbe
DOD:
* Vitest and pgTAP-style SQL tests: unbalanced rejected, update of posted rejected, reversal produces mirrored lines, chain verification detects a tampered row (done via superuser in test), balances match a brute-force sum after 10k random entries.
* Concurrency test: 50 parallel posts keep `entry_number` gapless and the chain valid.
* Playwright: create draft, post, reverse, close period; screenshots at 375, 1024, 1920 in three themes.
* `docs/finance/ledger.md` with posting rule catalogue and the invariants; ADR on immutability and hash chain.
* CHANGELOG entry; Linear comment with demo link and the chain verification output.
EDGE:
* Multi-currency entry: lines in USD and EUR balance in functional currency; FX gain/loss line auto-added when rounding leaves a remainder (account subtype `fx_gain_loss`).
* Rounding when allocating a 3-way split: largest-remainder via `Money.allocate`, never off by a cent.
* Reversal of a reversal: allowed, chain links both.
* Backdated entry into a closed period by an import: rejected; import offers to post on period start date with a memo.
* Account deactivated while a draft references it: post fails with the account named.
* Tenant deletion: ledger rows retained for the legal retention period even after tenant hard delete (moved to an archive schema), documented.
DEPS: * `business-core/finance-data-model` (accounts, periods, transactions, Money), `data-layer/rls-tenancy`, `data-layer/audit-log`, `tables/grid-view` for the journal UI, `identity/rbac-abac`.


## PAP-180 [P2 Build L prio2 Backlog] Implement invoices, quotes and receipts with PDF generation and Stripe payment links
key=business-core/invoicing milestone=Ledger and reports agent=Builder: Ledger (Payments Integrator with Bookkeeper on post
blockedBy=['PAP-179', 'PAP-177'] blocks=[]
GOAL: Let any tenant bill anyone for anything: quotes that convert to invoices, invoices with line items, taxes and payment terms, receipts on payment, branded PDFs, a public pay page backed by Stripe, and automatic ledger postings for accounts receivable, revenue and cash.
SCOPE: In:

* Tables `fin_document` (quote, invoice, receipt, credit note) and `fin_document_line`; number sequences; oRPC `documents.*`.
* PDF rendering service and templates; public routes `/pay/:token` and `/doc/:token`.
* Pages: documents grid, editor, detail with activity; customer portal "Invoices" list (`identity/customer-portal-shell`).
* Posting rules `invoice.issued`, `invoice.paid`, `invoice.voided`, `credit_note.issued`.
* Email sending via `collab/notifications` templates (send, reminder, receipt).

Out: recurring invoices (Stripe Billing handles subscriptions), inventory, multi-language templates beyond locale number/date formatting.
SPEC(first 1200): * `fin_document`: `id, tenant_id, kind: quote|invoice|receipt|credit_note, number (per-tenant per-kind sequence formatted by `fin_settings.invoice_number_format`, e.g. `INV-{YYYY}-{0000}`), party_id, status (quote: draft|sent|accepted|declined|expired; invoice: draft|issued|sent|viewed|partial|paid|overdue|void; receipt: issued; credit_note: issued|applied), issue_date, due_date, currency, subtotal_minor, discount_minor, tax_minor, total_minor, paid_minor, balance_minor, terms text, notes text, source_document_id (quote to invoice), stripe_payment_intent_id?, stripe_checkout_session_id?, public_token, pdf_file_id, sent_at, viewed_at, metadata`. `fin_document_line`: `document_id, line_no, description, quantity numeric(12,4), unit_price_minor, discount_pct, tax_rate_id?, tax_minor, amount_minor, revenue_account_id?, dimensions`.
* Totals computed server-side with `Money` in the document's currency; tax lines from `business-core/tax-compliance` when enabled, else manual tax rates table `fin_tax_rate`.
* Lifecycle: `documents.issue` freezes lines and number, posts `invoice.issued` (debit AR, credit revenue per line account, credit tax payable), creates a Stripe Checkout Session (or Pay
DOD:
* Vitest for totals (rounding, discounts, multi-rate tax), state machine transitions, number formatting and sequence gaplessness under concurrency.
* Integration: issue → pay in Stripe test mode → receipt and ledger entries verified against expected lines.
* PDF snapshot tests (rasterised via `pdf-to-img`) for invoice, quote, receipt at two brands; visual diff in CI.
* Playwright: editor flow, public pay page at 375 and 1024, portal list; screenshots at 375, 768, 1024, 1440, 1920 in three themes.
* `docs/finance/invoicing.md`; CHANGELOG entry; Linear comment with a live test-mode pay link and video replay.
EDGE:
* Partial payment via bank transfer recorded manually: `documents.recordPayment` posts cash/AR and sets `partial`.
* Currency differs from functional currency: FX rate captured at issue and at payment; gain/loss posted.
* Customer opens a voided invoice's pay link: page shows "Voided" and no Pay button.
* Line quantity 0.3333 hours: quantity precision 4, amounts rounded per line then summed (documented policy).
* Duplicate webhook after receipt already issued: idempotent by `stripe_event` id.
* Number format changed mid-year: existing numbers untouched; new sequence continues from the max.
DEPS: * `business-core/stripe-billing` (Stripe client, webhook plumbing), `business-core/ledger` (posting), `business-core/stripe-connect` (optional connected-account charges), `business-core/tax-compliance` (optional), `data-layer/file-storage`, `collab/notifications`, `identity/customer-portal-shell`.


## PAP-181 [P2 Build M prio2 Backlog] Add Stripe Connect so tenants can accept payments and receive payouts
key=business-core/stripe-connect milestone=Ledger and reports agent=Builder: Ledger (Payments Integrator). Reviewer: Sentinel (S
blockedBy=['PAP-177'] blocks=['PAP-196']
GOAL: Enable tenants to accept payments from their own customers and receive payouts through Stripe Connect: onboarding a connected account per tenant, charging on that account with a platform application fee, handling connected-account webhooks, and posting fees, payouts and balances to the ledger so a tenant's books stay complete.
SCOPE: In:

* Table `connect_account`; oRPC `connect.*`; connected-account webhook route `/api/webhooks/stripe-connect`.
* Onboarding UI in `/org/settings/payments` with status, requirements and payout schedule.
* Charge helper `createConnectedCheckout` used by `business-core/invoicing` and `growth/referral-program` (payouts to affiliates).
* Posting rules `payout.paid`, `application_fee.created`, `charge.dispute.*`, `balance_transaction` reconciliation.

Out: card-present/Terminal, Issuing, marketplace splits across multiple connected accounts per charge, live-mode activation (Justin approves separately).
SPEC(first 1200): * Account type: Connect Express by default (`controller: { fees: { payer: 'application' }, losses: { payments: 'application' }, stripe_dashboard: { type: 'express' } }`) so Stripe hosts KYC and the dashboard; `Standard` selectable via tenant setting for tenants who already have Stripe. Country from tenant address; capabilities `card_payments`, `transfers`.
* `connect_account`: `tenant_id unique, stripe_account_id, type, country, default_currency, charges_enabled, payouts_enabled, details_submitted, requirements jsonb (currently_due, eventually_due, disabled_reason), payout_schedule jsonb, updated_from_event_id`.
* Onboarding: `connect.start` creates the account and an Account Link (`type: account_onboarding`, refresh and return URLs); `connect.refreshLink` for expired links; `connect.loginLink` opens the Express dashboard; `account.updated` webhook keeps flags current; UI shows a checklist from `requirements.currently_due` with plain-language mapping.
* Charging: direct charges on the connected account (`stripe.checkout.sessions.create({...}, { stripeAccount })`) with `payment_intent_data.application_fee_amount` computed by `platformFee(tenantPlan, amount)` from `plans.ts` (e.g. 1 
DOD:
* Test-mode flow recorded: onboard Express account, charge through an invoice pay link, observe application fee and payout events, ledger entries balanced.
* Vitest for fee calculation, handler idempotency, requirements mapping, reconciliation diff.
* Playwright: settings page states (not started, requirements due, enabled, restricted); screenshots at 375, 1024, 1920 in three themes.
* Reconciliation report shows zero discrepancies on the demo tenant after a seeded day of activity.
* `docs/finance/connect.md` (including live-mode activation checklist for Justin); ADR on Express plus direct charges; CHANGELOG entry; Linear comment with video replay.
EDGE:
* Account restricted mid-month (`disabled_reason`): charges blocked, invoices fall back to "pay by bank transfer" instructions, banner to finance staff.
* Payout failed (bank details invalid): transaction stays in `stripe_balance`, alert raised, no cash posting.
* Refund exceeding available connected balance: Stripe pulls from platform; post a receivable from tenant, flagged.
* Tenant switches from Express to Standard: new account, old account retained for history and reconciliation.
* Currency of connected account differs from tenant functional currency: FX captured at payout.
* Webhook for an unknown `stripe_account_id` (deleted tenant): acknowledged and logged, not processed.
DEPS: * `business-core/stripe-billing` (client, event table, plans), `business-core/ledger` (posting), `business-core/finance-data-model` (transactions, parties), `collab/notifications` for dispute alerts.


## PAP-182 [P2 Build M prio3 Backlog] Handle sales tax and VAT via Stripe Tax and store tax evidence
key=business-core/tax-compliance milestone=Ledger and reports agent=Builder: Ledger (Payments Integrator) with Bookkeeper on pos
blockedBy=['PAP-177'] blocks=[]
GOAL: Handle sales tax and VAT without spreadsheets: use Stripe Tax to calculate tax on invoices, checkout and subscriptions, collect and validate customer tax IDs, store tax evidence per transaction (jurisdiction, rate, amounts, location evidence, calculation id) in our own tables for audits and reports, and post tax liabilities to the ledger.
SCOPE: In:

* Tables `fin_tax_registration`, `fin_tax_evidence`, `fin_tax_rate` (manual fallback); oRPC `tax.*`.
* Stripe Tax integration for Checkout (`automatic_tax`), Billing subscriptions and invoice calculations via the Tax Calculation API for documents charged outside Checkout.
* Settings page `/org/settings/tax` (registrations, nexus, default product tax code, tax-inclusive pricing toggle).
* Tax summary report dataset for `business-core/finance-reports`.

Out: filing returns (link to Stripe Tax filing partners), customs/duties, payroll taxes (`business-core/payroll-adapter`).
SPEC(first 1200): * Enable Stripe Tax on the platform account and on connected accounts (`tax.settings` per account with `head_office` address and default `tax_code`, e.g. `txcd_10000000` general SaaS or product-specific per line). `fin_tax_registration` mirrors `tax.registrations` (`jurisdiction, type, active_from, active_to, stripe_registration_id`) and is the source for the settings UI; creation via `tax.addRegistration` calls Stripe and stores.
* Checkout and subscriptions: pass `automatic_tax: { enabled: true }` and `customer_update: { address: 'auto' }`; collect billing address; for B2B, `tax_id_collection: { enabled: true }` and store validated IDs on `fin_party.tax_id` with `tax_id_type` and validation status from Stripe.
* Documents outside Checkout (bank-transfer invoices): `tax.calculate(document)` calls `stripe.tax.calculations.create` with line items (amount, quantity, tax_code, reference), customer address and tax IDs; results write `fin_document_line.tax_minor` and create `fin_tax_evidence` rows; on payment, `stripe.tax.transactions.createFromCalculation` records the transaction for Stripe's reporting and stores `stripe_tax_transaction_id`; reversals on void/credit note via `createRev
DOD:
* Vitest for calculation mapping, evidence writes, reverse-charge logic, inclusive/exclusive totals.
* Integration in Stripe test mode: US address with nexus registration produces tax; EU B2B with valid VAT ID produces reverse charge; evidence rows verified.
* Playwright: settings page with registrations, invoice showing tax lines, tax summary report grid; screenshots at 375, 1024, 1920 in three themes.
* `docs/finance/tax.md` including "what Stripe Tax does not do" and the manual path.
* ADR on Stripe Tax; CHANGELOG entry; Linear comment with report screenshot and evidence sample (test data).
EDGE:
* Customer address missing: calculation returns `requires address`; invoice cannot be issued until collected, with a request-address email action.
* Tax ID validation pending or invalid: charge tax and flag; re-run when Stripe reports valid.
* Registration added retroactively: past documents untouched; report shows "uncollected" for the gap.
* Rate changes mid-period: evidence stores the rate used at calculation time.
* Refund after tax transaction created: partial reversal with proportional tax.
* Connected account in a country Stripe Tax does not support: fallback to manual rates with a warning banner.
DEPS: * `business-core/stripe-billing` (Stripe client, Checkout), `business-core/invoicing` (documents and posting), `business-core/stripe-connect` (per-account tax settings), `business-core/finance-reports` (report consumer).


## PAP-183 [P2 Build M prio2 Backlog] Generate P&L, balance sheet, cash flow and AR/AP aging as table views
key=business-core/finance-reports milestone=Ledger and reports agent=Builder: Ledger (Bookkeeper). Reviewer: Sentinel (Code Revie
blockedBy=['PAP-165', 'PAP-179'] blocks=['PAP-186']
GOAL: Produce books a founder can read: profit and loss, balance sheet, cash flow (indirect method) and AR/AP aging, generated from the ledger and documents as datasets in the views engine, so they get grouping, filtering, drill-down and export for free and can be dropped into dashboards.
SCOPE: In:

* `packages/finance/src/reports/`: report definitions, SQL builders, dataset registrations `finance.pnl`, `finance.balanceSheet`, `finance.cashFlow`, `finance.arAging`, `finance.apAging`, `finance.trialBalance`, `finance.generalLedger`.
* Report page `/finance/reports/:key` with parameter bar (period, comparison, basis, dimensions) and saved report views.
* Drill-down from any report line to journal entries and documents.
* Exports: CSV, XLSX (`exceljs` 4.x), PDF via the dashboard print route.

Out: budgeting and forecasting, consolidation across tenants, custom report builder UI (saved views over these datasets cover most needs).
SPEC(first 1200): * Parameters (typed, shared): `period` (preset `thisMonth|lastMonth|thisQuarter|ytd|lastYear|custom` resolved with fiscal year from `fin_settings`), `comparison` (`none|previousPeriod|previousYear`), `basis` (`accrual|cash`; cash basis recognises revenue/expenses on payment transactions), `dimensions` (department, location, project), `currency` (functional only in v1).
* P&L: rows are accounts of type revenue and expense grouped by parent account, with subtotals (Gross profit when `cogs` subtype exists, Operating income, Net income); columns per period and comparison with variance amount and percent; built from `fin_account_balance` for closed periods and live lines for the open period.
* Balance sheet: assets, liabilities, equity as of `period.end`; retained earnings computed as cumulative net income of prior periods plus current; must balance or the report shows a red "Out of balance by X" with a link to `ledger.verifyChain`.
* Cash flow (indirect): net income, adjustments (non-cash), changes in working capital derived from AR, AP, tax payable and payroll liability subtypes, investing and financing sections from account subtypes; reconciles to the change in `cash` and `stripe_bal
DOD:
* Vitest against a fixture ledger with known answers (textbook set of 60 entries): P&L, balance sheet, cash flow and aging match to the cent, both bases.
* Property test: for random balanced entries, balance sheet always balances and cash flow reconciles.
* Playwright: open each report, change period, drill down, export CSV; screenshots at 375, 768, 1024, 1440, 1920 in three themes; PDF export snapshot for P&L.
* Performance: P&L for a tenant with 100k journal lines under 1 s (snapshots plus indexed balances).
* `docs/finance/reports.md` explaining each report's derivation; CHANGELOG entry; Linear comment with demo links.
EDGE:
* Fiscal year starting in July: presets and YTD follow `fiscal_year_start_month`.
* Unposted drafts: excluded, with a count badge "n drafts not included".
* Accounts with no activity: hidden by default, toggle "show zero rows".
* Multi-currency lines: functional amounts only; a footnote lists currencies present.
* Comparison period with no data: variance shows "n/a" not division by zero.
* Aging as-of date earlier than some payments: payments after the date are ignored so historical aging is reproducible.
DEPS: * `business-core/ledger` (balances, entries), `business-core/invoicing` (documents for aging), `tables/grid-view` and `tables/query-compiler` (dataset rendering), `tables/dashboard-blocks` (number blocks), `tables/view-sharing` (saved report views).


## PAP-184 [P2 Build L prio2 Backlog] Define the payroll provider interface and implement the first adapter (Check or Gusto Embedded)
key=business-core/payroll-adapter milestone=Payroll adapter and cash dashboard agent=Builder: Ledger (Payroll Adapter). Reviewer: Sentinel (Secur
blockedBy=['PAP-176', 'PAP-179'] blocks=[]
GOAL: Implement the `PayrollProvider` interface chosen in `business-core/payroll-research` and its first adapter (Check by default, Gusto Embedded if the ADR chose it), so a tenant can onboard employees, preview and approve a payroll run, and see paystubs inside PaperOS, with every approved run posted to the ledger. Sandbox mode only until Justin approves live.
SCOPE: In:

* `packages/finance/src/payroll/`: `provider.ts` (interface from the ADR, finalised), `adapters/check.ts` (or `gusto.ts`), `service.ts`, tables `payroll_company`, `payroll_employee_link`, `payroll_run`, `payroll_run_item`, `payroll_event`.
* Pages `/finance/payroll` (runs list, run detail, approve), `/finance/payroll/employees` (sync and onboarding status), employee-facing paystubs in the customer portal shell for users linked to `fin_employee`.
* Posting rule `payroll.approved`.
* Webhook route `/api/webhooks/payroll/:provider`.

Out: benefits administration, time tracking (hours come from a manual entry or a future integration), international payroll, live filings.
SPEC(first 1200): * Adapter contract: `PayrollProvider` from the ADR; each method maps to provider REST calls with the provider SDK if a TypeScript SDK exists, else `ky` 1.x with typed Zod responses; every mutating call carries an idempotency key `paperos:<tenant>:<entity>:<version>`; `capabilities()` drives UI (e.g. hide contractors if unsupported).
* `payroll_company`: `tenant_id unique, provider, external_company_id, onboarding_status, pay_frequency, next_pay_date, bank_verified, updated_from_event_id`. `payroll_employee_link`: `party_id (fin_employee), external_employee_id, onboarding_status, ssn_last4_masked?, w4_complete`. `payroll_run`: `id, tenant_id, external_run_id, period_start, period_end, pay_date, status: draft|previewed|approved|processing|paid|failed|cancelled, totals jsonb (gross, employee_taxes, employer_taxes, deductions, net, provider_fees), approved_by, approved_at, ledger_entry_id`. `payroll_run_item`: per employee amounts (`gross, net, employee_taxes, employer_taxes, deductions, hours, earnings jsonb`).
* Onboarding: company onboarding via provider-hosted component or link (`companies.onboardingLink`) embedded in an iframe with `sandbox` attributes; employee onboarding links e
DOD:
* Sandbox end-to-end recorded: onboard company, two employees, preview, approve, webhook to paid, ledger balanced, paystub visible in portal.
* Vitest for adapter mapping with recorded fixtures (`nock`), idempotency, status machine, posting rule totals.
* Contract test suite runnable against any adapter (`packages/finance/test/payroll-contract.test.ts`).
* Playwright: run flow and employee portal; screenshots at 375, 1024, 1920 in three themes; video replay of approve.
* `docs/finance/payroll.md` with sandbox setup, capability matrix and live activation checklist; CHANGELOG entry; Linear comment with demo link and Needs Justin item for live approval.
EDGE:
* Employee missing tax setup at approve time: provider rejects; UI lists blocked employees with onboarding links.
* Pay date on a bank holiday: use provider's adjusted date and show it.
* Off-cycle bonus run: supported as `kind: off_cycle` if capability present.
* Webhook signature rotation: two secrets accepted during rotation window.
* Run approved then provider fails funding (NSF): `failed` status, liabilities remain, alert to owner.
* Terminated employee mid-period: final pay handled by provider rules; employee shows `terminated` and excluded from future runs.
DEPS: * `business-core/payroll-research` (ADR, interface), `business-core/ledger` (posting), `business-core/finance-data-model` (`fin_employee`), `collab/notifications`, `identity/customer-portal-shell`, `tables/grid-view`.


## PAP-185 [P2 Build M prio3 Backlog] Add expense capture with receipt OCR and ledger posting
key=business-core/expense-capture milestone=Payroll adapter and cash dashboard agent=Builder: Ledger (Bookkeeper) with Forge (Tauri Smith) for mo
blockedBy=['PAP-37', 'PAP-179'] blocks=[]
GOAL: Turn receipts into journal entries: capture a receipt photo or PDF from web or mobile, extract vendor, date, totals, tax and line items with a vision model, let staff review and categorise, create an expense (or vendor bill) and post it to the ledger, with duplicate detection and an approval step for amounts above a threshold.
SCOPE: In:

* Tables `fin_expense`, `fin_expense_line`, `fin_expense_extraction`; oRPC `expenses.*`; extraction worker.
* Pages `/finance/expenses` (inbox grid, review panel), mobile capture flow in the Tauri app using the camera plugin, email-in address per tenant (`receipts+<tenant>@...`) via `collab/notifications` inbound if available, else deferred.
* Posting rules `expense.approved`, `expense.reimbursed`, `bill.created` (vendor bill from an invoice-like receipt).
* Category to account mapping with learning from past choices per vendor.

Out: corporate card feeds (bank sync is a future integration), mileage, per-diem policies, multi-currency reimbursements beyond FX capture.
SPEC(first 1200): * Capture: web drag-drop or file picker (images and PDF up to 20 MB) uploading via `data-layer/file-storage`; Tauri mobile uses `@tauri-apps/plugin-camera` (or `plugin-dialog` fallback) with client-side downscale to 2000 px; each upload creates `fin_expense (status: extracting)` and enqueues extraction.
* Extraction worker (`packages/finance/src/expenses/extract.ts`): calls the Claude API (model per the `claude-api` skill's current recommendation, temperature 0) with the image and a JSON schema tool `receipt_extraction` returning `{ vendorName, vendorTaxId?, date, currency, subtotalMinor, taxMinor, tipMinor?, totalMinor, paymentMethod?, lastFour?, lines: [{ description, quantity, unitMinor, amountMinor }], confidence: 0-1 per field }`; PDFs rasterised first page with `pdf-to-img`; fallback to `tesseract.js` text plus a text-only extraction when the vision call fails; store raw output in `fin_expense_extraction (expense_id, provider, model, raw jsonb, parsed jsonb, cost_usd, duration_ms)` for evaluation; budget alert if daily extraction spend exceeds a configured cap (`agents/cost-controls`).
* Review panel: image viewer (zoom, rotate) beside a form pre-filled from extraction with l
DOD:
* Extraction eval set of 40 receipts (varied layouts, currencies, crumpled, PDF) with labelled truth in `packages/finance/test/receipts/`; totals correct on at least 90 percent, dates on 95 percent; eval runs weekly through `agents/eval-harness`.
* Vitest for duplicate rules, approval routing, posting rule outputs.
* Playwright: upload, review, approve, ledger entry appears; mobile capture verified on Android emulator via `app-shell/tauri-mobile` smoke test; screenshots at 375, 768, 1024, 1440, 1920 in three themes.
* `docs/finance/expenses.md` including privacy note on sending images to the model; CHANGELOG entry; Linear comment with demo link and eval scores.
EDGE:
* Receipt in a currency other than functional: FX rate at receipt date fetched from a rates table (manual entry fallback) and captured on the expense.
* Total does not equal subtotal plus tax (tips, rounding): flag, let reviewer fix, keep raw values.
* Multi-receipt PDF: split pages into separate expenses with a "merge" action.
* Illegible image: extraction returns low confidence everywhere; inbox shows "needs manual entry".
* Vendor name in another script: fuzzy match on normalised transliteration; otherwise create.
* Approver is the submitter: blocked for above-threshold expenses.
DEPS: * `business-core/ledger` (posting), `data-layer/file-storage` (uploads), `business-core/finance-data-model` (parties, accounts), `app-shell/tauri-mobile` (camera), `agents/cost-controls` and `agents/eval-harness`, `collab/notifications`.


## PAP-186 [P2 Build M prio2 Backlog] Build the cash-flow dashboard (in, out, runway, upcoming payroll) as the first dashboard-blocks consumer
key=business-core/cash-dashboard milestone=Payroll adapter and cash dashboard agent=Builder: Ledger (Bookkeeper) with Nova (Views Engineer) on a
blockedBy=['PAP-173', 'PAP-183'] blocks=[]
GOAL: Ship the founder's one screen: a cash-flow dashboard showing cash in and out over time, current cash, runway, upcoming payroll, receivables and payables due, and subscription revenue, assembled from finance report datasets as the first real consumer of `tables/dashboard-blocks`. It proves the dashboard engine end to end and becomes the default landing page of the finance area.
SCOPE: In:

* Seeded dashboard definition `finance.cash` (JSON in `packages/finance/src/dashboards/cash.dashboard.json`) installed per tenant on finance module enablement, editable by finance staff, resettable to default.
* Datasets and number blocks: `finance.cashSeries` (weekly in/out/net), `finance.runway`, `finance.upcomingPayroll`, `finance.arDueSoon`, `finance.apDueSoon`, `finance.mrr`.
* Page spec `specs/pages/finance/cash.spec.yaml` and route `/finance` using `layout.dashboard`.
* Alerts: runway below 3 months and payroll uncovered by cash produce notifications.

Out: forecasting scenarios, bank account sync (cash comes from ledger `cash` and `stripe_balance` subtypes), budgets.
SPEC(first 1200): * Layout (12-col, `lg`): row 1 four number blocks (Cash now, Runway, Net burn 30d, MRR); row 2 chart block "Cash in vs out" (stacked bar weekly, 13 weeks, net line) spanning 8 cols and number block "Upcoming payroll" with date (4 cols); row 3 grid block "Receivables due next 30 days" (AR aging dataset filtered) and grid block "Payables due next 30 days" (6 cols each); row 4 chart "Cash balance trend" (line, daily, 90 days) 12 cols. `md` collapses to 8 cols two per row; `sm` stacks. A global date-range filter block at top controls the charts; the number blocks pin to "now".
* `finance.cashSeries` builds from ledger lines on `cash` and `stripe_balance` accounts bucketed by `date_trunc('week')` with columns `inflow, outflow, net, balance_end`; `finance.runway` = cash now divided by average net burn over the trailing 3 months (only when burn is negative, else "profitable"); `finance.upcomingPayroll` reads the next `payroll_run` in `draft|previewed|approved` or estimates from the last paid run when none exists (labelled "estimate"); `finance.mrr` derives from active Stripe subscriptions on the connected account normalised to monthly (yearly divided by 12), excluding trials; AR/AP due so
DOD:
* Vitest for series bucketing, runway maths (including profitable and zero-history cases), MRR normalisation, alert thresholds.
* Playwright: dashboard renders with seeded data, cross-filter from chart to AR grid, date range change, empty state for a fresh tenant; screenshots at 375, 768, 1024, 1440, 1920 in three themes; video replay of cross-filtering; PDF export via the print route.
* Performance: dashboard settles under 2 s on the seeded tenant (trace attached).
* Accessibility: every block has a text summary; number blocks readable by screen reader.
* `docs/finance/cash-dashboard.md` explaining each metric's derivation; CHANGELOG entry; Linear comment with demo link and a screenshot for Justin's release digest (`quality/review-report`).
EDGE:
* No payroll module enabled: payroll block hidden, layout reflows.
* Cash negative (overdraft): runway shows "0 months" with a red banner.
* Multi-currency cash accounts: functional currency totals with a footnote of currencies; no blind summation.
* Tenant with revenue but no Stripe: MRR block shows "n/a" with a link to enable billing.
* Week boundary across fiscal year change: buckets by calendar week, labels include year.
* Dashboard edited by staff then reset: reset restores the seeded JSON but keeps their saved copy as "Cash (custom)".
DEPS: * `business-core/finance-reports` (datasets, number blocks), `tables/dashboard-blocks` (engine), `tables/map-chart-views` (charts), `business-core/payroll-adapter` (upcoming payroll, optional), `business-core/stripe-connect` (MRR), `collab/notifications`.
