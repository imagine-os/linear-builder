# Round 4 cross-cutting analysis: platform capability map and new projects

Source: live Linear inventory (2026-09-18, 18 projects, 497 issues), `docs/blueprint.md`, `docs/module-system.md`, Justin's brief. Output data: `plan/round4/gaps/cross-cutting.json`.

**Capability map:** 167 capabilities across 12 areas: 105 covered, 17 partial, 45 gap. Gaps and partials resolve to 5 proposed projects (75 issues) and 12 cross-project suggestions for existing projects.

## What the plan was missing at platform level

1. **Nobody can talk to the product.** The roster builds PaperOS with agents, but no tenant, staff member or customer can ask the app a question, get a cited answer, or have it draft or act. The assistant project adds grounded chat, copilots, actions with confirmation and tenant-configurable business characters.
2. **Processes stop at one table.** Automations (PAP-174) are single-table reactions; five issues each hand-roll an approval step. There is no workflow engine, approvals framework or task inbox, so "expense over $500 needs a manager" has no home.
3. **Forms, documents and signatures are invoices only.** A single-page form view and a Webflow embed cannot run intake, registration or paid forms; document generation exists only for invoices; nothing signs anything.
4. **The customer is won and then forgotten.** Growth acquires; nothing books appointments, texts back, publishes a help center, asks for NPS or reviews, runs memberships or rewards loyalty. Cal.com and Formbricks were spiked and dropped.
5. **Finance has no operations under it.** The ledger, invoices and payroll are there; products, stock, orders, POS, purchasing, projects and time, HR shifts, assets and work orders, customer subscriptions and marketplaces are not, so the five business packs stay shallow and eleven business types in the brief have no pack.
6. **PaperOS has no console for PaperOS.** Tenants get PAP-63; the platform gets nothing: no tenant list, overrides, per-tenant flag rules, DLQ, health scores, status page or incident comms.
7. **Compliance is implemented but unmapped.** Twenty security issues exist and no document says which SOC 2, GDPR or HIPAA control they satisfy, no evidence is collected, no HIPAA mode exists for a clinic tenant, and there is no trust center.
8. **Product analytics, replay and experiments are missing** beyond acquisition attribution and traces, so nobody will know what users do after signup or which variant of a flag worked.
9. **Small shared engines were never owned:** recurrence (five consumers), FX conversion, file scanning and previews, SMS as a notification channel, labels and barcodes, geocoding, scheduled report delivery, settings registry, OAuth apps for third parties, bulk campaigns and bank reconciliation are filed as cross-project suggestions.
10. **Honest phasing:** 13 days remain. Of the 75 new-project issues, 19 are not deferred (contract publishes, keystone model specs, approvals framework and task inbox, retrieval and chat panel, booking engine, catalog and inventory, super-admin console, status page, control mapping); 56 are `deferred: true` for v0.2 at priority 4 but fully specified so the plan is complete.

## Capability map

### Runtime & shell (13 covered, 1 partial, 1 gap)

| Capability | Covered by | Status | Home | Note |
|---|---|---|---|---|
| Web, desktop and mobile shells from one bundle | PAP-13, PAP-19, PAP-20, PAP-255, PAP-256, PAP-257, PAP-258, PAP-259, PAP-260 | covered | `app-shell` | Tauri 2 targets, installers, updater, native shim. |
| Multi-monitor window manager and pop-out | PAP-21, PAP-262, PAP-263 | covered | `app-shell` |  |
| PWA and offline app shell | PAP-18, PAP-11 | covered | `app-shell` | Data offline is realtime (PAP-148). |
| Kiosk, TV and parallel-browser modes | PAP-23, PAP-158 | covered | `app-shell` | POS and check-in kiosks (commerce, engagement) reuse PAP-23. |
| i18n and l10n (catalogs, RTL, Intl helpers, spec copy) | PAP-27, PAP-375, PAP-126 | covered | `app-shell` | Tenant-authored content translation is out of PAP-27; v0.3 with the translate skill. |
| Time zones and recurrence (RRULE) engine | PAP-27, PAP-58, PAP-344 | gap | `data-layer` | Five modules need recurrence; none owns it. Cross suggestion r4/data-layer/recurrence-engine. |
| Feature flags with kill switches and per-tenant rules | PAP-366, PAP-435 | covered | `app-shell` |  |
| Client error handling and crash reporting | PAP-368 | covered | `app-shell` |  |
| Custom domains and white-label branding | PAP-431, PAP-75, PAP-178 | covered | `app-shell` | White-label sending domains per tenant live in PAP-370 DKIM setup (partial, noted). |
| Code signing, notarisation and auto-update | PAP-369, PAP-257 | covered | `app-shell` |  |
| Native mobile capabilities (camera, biometrics, share, push) | PAP-260, PAP-381 | covered | `app-shell` |  |
| Command palette, keyboard and keymaps | PAP-151, PAP-153, PAP-289, PAP-290, PAP-291 | covered | `input` |  |
| Multi-input: touch, pen, gamepad, voice | PAP-150, PAP-154, PAP-157, PAP-158, PAP-159 | covered | `input` |  |
| Settings registry (module-declared settings pages per scope) | PAP-63, PAP-447 | partial | `app-shell` | Slot exists; no registry, storage or generated pages. Cross suggestion r4/app-shell/settings-registry. |
| Template upgrade for generated apps | PAP-430 | covered | `app-shell` |  |

### Data (15 covered, 0 partial, 4 gap)

| Capability | Covered by | Status | Home | Note |
|---|---|---|---|---|
| Postgres, Drizzle schema-as-code, RLS multi-tenancy | PAP-30, PAP-32, PAP-33, PAP-34 | covered | `data-layer` |  |
| Local-first sync and offline write queue | PAP-36, PAP-270, PAP-271, PAP-272, PAP-148 | covered | `data-layer` |  |
| Typed API, OpenAPI and typed client | PAP-35, PAP-267, PAP-268, PAP-269 | covered | `data-layer` |  |
| Background jobs, cron, DLQ and staff jobs view | PAP-43, PAP-295 | covered | `data-layer` |  |
| Full-text and semantic search with a registry | PAP-39, PAP-138, PAP-296 | covered | `data-layer` | Unified search UI in collab (PAP-138). |
| File and media storage with variants | PAP-37 | covered | `data-layer` |  |
| Malware scanning, document previews, video thumbnails, text extraction | PAP-37 | gap | `data-layer` | Explicitly out of PAP-37. Cross suggestion r4/data-layer/file-scanning-previews. |
| CDN and edge caching | PAP-37, PAP-87 | gap | `data-layer` | Cross suggestion r4/data-layer/cdn-edge-cache (deferred). |
| Append-only audit log and record activity timeline | PAP-38, PAP-333 | covered | `data-layer` |  |
| Field encryption and secrets handling | PAP-353, PAP-300, PAP-444, PAP-17 | covered | `data-layer` |  |
| Backups, PITR and platform DR drill | PAP-30, PAP-354, PAP-274, PAP-53 | covered | `data-layer` |  |
| Export, data portability and round-trip import | PAP-205, PAP-420, PAP-421, PAP-422 | covered | `migration` |  |
| Tenant lifecycle, deletion, retention and PII classification | PAP-432, PAP-355 | covered | `data-layer` |  |
| Request idempotency and rate limiting | PAP-304 | covered | `data-layer` |  |
| Domain event bus, outbox and schema registry | PAP-303, PAP-436 | covered | `data-layer` |  |
| Data dictionary and observability (OTel, Grafana) | PAP-41, PAP-40 | covered | `data-layer` |  |
| Custom datasets and schema editor in-app | PAP-332 | covered | `tables` |  |
| Multi-region and data residency | PAP-56 | gap | `platform-ops` | Only mentioned in the auth ADR. New project issue r4/platform-ops/data-residency (deferred). |
| Multi-currency FX rates and revaluation | PAP-302, PAP-179 | gap | `business-core` | `Money` carries a currency; nothing converts. Cross suggestion r4/business-core/fx-rates. |

### Identity (9 covered, 1 partial, 2 gap)

| Capability | Covered by | Status | Home | Note |
|---|---|---|---|---|
| Authentication: passkeys, magic links, OAuth, Tauri sessions | PAP-57, PAP-223, PAP-224, PAP-225 | covered | `identity` |  |
| Organisations, workspaces, invitations, tenant switching | PAP-58 | covered | `identity` |  |
| Permission engine, audiences, attribute policies, matrix tests | PAP-55, PAP-59, PAP-64, PAP-227, PAP-228, PAP-229 | covered | `identity` |  |
| Agents as first-class principals | PAP-60 | covered | `identity` |  |
| Staff impersonation with audit | PAP-61 | covered | `identity` |  |
| SSO (SAML/OIDC) and SCIM | PAP-65, PAP-230, PAP-231, PAP-232 | covered | `identity` |  |
| Session and device management, MFA, recovery | PAP-220, PAP-301 | covered | `identity` |  |
| Customer API keys, outbound webhooks, SDK | PAP-222 | covered | `identity` | Deferred to v0.2 but fully specified. |
| Tenant-installable OAuth apps (OIDC provider for third parties) | PAP-226, PAP-222 | gap | `identity` | PAP-226 serves Forgejo only. Cross suggestion r4/identity/oauth-provider-apps (deferred). |
| Privacy: DSAR export and erasure, consent, legal pages | PAP-221, PAP-187 | covered | `identity` | Deferred; consent centre folded into PAP-187 WP0. |
| Abuse, signup fraud and sending reputation controls | PAP-304, PAP-193, PAP-405, PAP-408 | partial | `platform-ops` | Rate limits and per-feature spam checks only. New project issue r4/platform-ops/abuse-controls. |
| Sandbox or test-mode tenants for customers | PAP-240, PAP-363 | gap | `identity` | Test seeds exist for QA; no customer-facing sandbox tenant. Note for v0.3; no spec this round. |

### Collaboration (14 covered, 1 partial, 3 gap)

| Capability | Covered by | Status | Home | Note |
|---|---|---|---|---|
| Comments anchored to any entity with mentions and resolve | PAP-131, PAP-317, PAP-318, PAP-319 | covered | `collab` |  |
| Presence, cursors, follow mode, agents as participants | PAP-141, PAP-146, PAP-149 | covered | `realtime` |  |
| Notifications hub: in-app, email, Slack, digests, quiet hours | PAP-136, PAP-323, PAP-324, PAP-325 | covered | `collab` |  |
| SMS and WhatsApp as notification channels | PAP-136, PAP-404 | gap | `collab` | Twilio exists for outreach only. Cross suggestion r4/collab/sms-notification-channel. |
| Push transport (live events, Web Push, mobile push) | PAP-381 | covered | `realtime` |  |
| Docs engine (repo MDX) and tenant-authored docs | PAP-128, PAP-379 | covered | `collab` |  |
| Canvas UX-flow view generated from specs | PAP-132, PAP-123, PAP-320, PAP-321, PAP-322 | covered | `collab` |  |
| Prompt and response logs with browser and replay | PAP-107, PAP-129, PAP-135 | covered | `collab` |  |
| Changelogs per app and per tenant | PAP-133, PAP-52 | covered | `collab` |  |
| Collaborative rich text editor | PAP-142 | covered | `realtime` |  |
| Transactional email package | PAP-370 | covered | `data-layer` |  |
| Screenshot and video annotation to issues | PAP-137 | covered | `collab` |  |
| Rules and skills as browsable objects; ADR log | PAP-134, PAP-130 | covered | `collab` |  |
| Contextual help panel and first-visit tours | PAP-380 | covered | `collab` |  |
| Public help center and knowledge base per tenant | PAP-379, PAP-380 | partial | `engagement` | Tenant docs exist; no public site, categories, search page or feedback. New project issue r4/engagement/help-center. |
| Staff to customer support inbox (email, in-app chat) | PAP-197, PAP-410, PAP-411, PAP-412 | covered | `growth` | Deferred to v0.2 but fully specified. |
| Two-way conversational SMS and WhatsApp messaging | PAP-404, PAP-410 | gap | `engagement` | Outbound sequences only. New project issue r4/engagement/messaging-channels. |
| Video calls and meetings | — | gap | `engagement` | Out of scope for v0.2; link fields to Zoom/Meet only. No spec this round. |

### Product surfaces (11 covered, 6 partial, 7 gap)

| Capability | Covered by | Status | Home | Note |
|---|---|---|---|---|
| Tables and views engine with Airtable, Notion, ClickUp parity | PAP-161, PAP-162, PAP-163, PAP-164, PAP-165, PAP-166, PAP-167, PAP-168, PAP-169, PAP-170, PAP-172 | covered | `tables` |  |
| Dashboards with cross-filters and print route | PAP-173, PAP-385, PAP-386, PAP-387 | covered | `tables` |  |
| Formula engine | PAP-171, PAP-382, PAP-383, PAP-384 | covered | `tables` |  |
| Table automations (triggers, conditions, actions) | PAP-174, PAP-388, PAP-389, PAP-390 | covered | `tables` |  |
| Cross-module workflow engine with human tasks, waits and versions | PAP-174, PAP-388 | partial | `workflows` | Automations are single-table and stateless. New project workflows. |
| Generic approvals framework and task inbox | PAP-94, PAP-401, PAP-408, PAP-185, PAP-400 | partial | `workflows` | Five bespoke approval steps. New project issues r4/workflows/approvals-framework, task-inbox. |
| Forms builder: multi-page, logic, payments, public embeds, anti-spam | PAP-169, PAP-193 | partial | `workflows` | Single-page record-entry view and a Webflow embed. New project issues r4/workflows/forms-schema-runtime, r4/workflows/forms-publishing. |
| Document templates and generation (PDF, DOCX) beyond invoices | PAP-180, PAP-235, PAP-396 | partial | `workflows` | Invoices only. New project issues r4/workflows/document-templates, r4/workflows/document-generation. |
| E-signature with audit certificate | PAP-352 | gap | `workflows` | Only a Documenso mention in the OSS spike. New project issues r4/workflows/esign-core, r4/workflows/esign-audit-compliance. |
| Record detail page, activity, attachments, field history | PAP-333, PAP-334 | covered | `tables` |  |
| Spec builder, codegen, conformance tests, spec editor | PAP-114, PAP-115, PAP-120, PAP-122, PAP-124, PAP-362 | covered | `spec-builder` |  |
| Design system, theming, print and email kit | PAP-66, PAP-67, PAP-75, PAP-235 | covered | `design-system` |  |
| Labels, barcodes, QR codes and scanner input | PAP-235, PAP-260 | gap | `design-system` | Cross suggestion r4/design-system/labels-barcodes-qr. |
| Customer portal and staff console shells | PAP-62, PAP-63, PAP-363 | covered | `identity` |  |
| First-run onboarding wizard and template gallery | PAP-367, PAP-428 | covered | `app-shell` |  |
| In-app AI assistant over tenant data with citations and actions | PAP-291, PAP-39, PAP-380 | gap | `assistant` | Agents build the product; nothing lets tenants or customers talk to it. New project assistant. |
| Natural language to filters, formulas and views | PAP-279, PAP-382 | gap | `assistant` | New project issue r4/assistant/nl-to-views. |
| Customer-facing business characters (tenant-configurable agents) | PAP-103, PAP-113 | gap | `assistant` | Character schema is platform-scoped. New project issue r4/assistant/business-characters. |
| Unified search UI from the command palette | PAP-138, PAP-290 | covered | `collab` |  |
| Maps: geocoding, address field, distance filters | PAP-170, PAP-293, PAP-260 | partial | `tables` | Map view plots existing coordinates only. Cross suggestion r4/tables/address-geo-field. |
| Scheduled delivery of views and dashboards | PAP-387, PAP-421 | gap | `tables` | Cross suggestion r4/tables/scheduled-view-delivery. |
| Offline conflict and stale-data UX | PAP-144, PAP-148, PAP-327 | covered | `realtime` |  |
| In-app announcements and product messaging | PAP-133, PAP-323 | partial | `engagement` | Changelog feed exists; no targeted banners or modals. New project issue r4/engagement/announcements. |
| Feedback and feature request board | — | gap | `engagement` | New project issue r4/engagement/feedback-board. |

### Business operations (7 covered, 4 partial, 15 gap)

| Capability | Covered by | Status | Home | Note |
|---|---|---|---|---|
| Platform billing: Stripe Billing, entitlements, metering | PAP-177, PAP-178, PAP-391 | covered | `business-core` |  |
| Double-entry ledger, period close, finance reports | PAP-179, PAP-392, PAP-393, PAP-394, PAP-183 | covered | `business-core` |  |
| Invoices, quotes, receipts, recurring and dunning | PAP-180, PAP-395, PAP-396, PAP-397 | covered | `business-core` |  |
| Connect payments and payouts, tax, PCI posture | PAP-181, PAP-182, PAP-359 | covered | `business-core` |  |
| Payroll adapter and runs | PAP-184, PAP-398, PAP-399, PAP-400 | covered | `business-core` |  |
| Expenses with receipt OCR; cash-flow dashboard | PAP-185, PAP-186 | covered | `business-core` |  |
| Bank feeds and reconciliation | PAP-186, PAP-424 | gap | `business-core` | Cross suggestion r4/business-core/bank-feeds-reconciliation (deferred). |
| Purchase orders, receiving, vendor bills, AP | PAP-183, PAP-175 | partial | `commerce` | AP aging report without AP documents. New project issue r4/commerce/purchasing-ap. |
| Budgeting and forecasting | PAP-183 | gap | `business-core` | Explicitly out of PAP-183; v0.3 note, no spec this round. |
| Products, variants, price lists and inventory | PAP-177, PAP-207 | gap | `commerce` | New project issue r4/commerce/catalog-inventory. |
| Orders, fulfilment, returns and refunds | — | gap | `commerce` | New project issue r4/commerce/orders-fulfilment. |
| POS mode with Stripe Terminal and offline sales | PAP-23, PAP-148 | gap | `commerce` | New project issue r4/commerce/pos-mode. |
| Tenant-to-customer subscriptions and recurring plans | PAP-177, PAP-181 | partial | `commerce` | PAP-177 bills the tenant; Connect accepts one-off payments. New project issue r4/commerce/customer-subscriptions. |
| Quotes, estimates and contracts | PAP-180, PAP-395 | partial | `workflows` | Quotes exist; contracts need templates and e-sign (workflows). |
| Projects, time tracking, time and materials billing | PAP-100, PAP-427 | gap | `commerce` | Agency pack has no time entries. New project issue r4/commerce/projects-time-billing. |
| HR core: directory, time-off, shifts, timesheets | PAP-399, PAP-400 | partial | `commerce` | Employees exist for payroll only. New project issue r4/commerce/hr-core. |
| Recruiting and ATS | — | gap | `commerce` | v0.3 note; a pack can compose forms and pipelines meanwhile. No spec this round. |
| Assets, maintenance and work orders (field service) | — | gap | `commerce` | New project issue r4/commerce/assets-work-orders. |
| Two-sided marketplace (vendors, split payments, payouts) | PAP-181, PAP-408 | gap | `commerce` | New project issue r4/commerce/marketplace-model. |
| Appointments, resource scheduling and booking pages | PAP-344, PAP-352, PAP-215 | gap | `engagement` | Cal.com spiked, nothing built. New project issues r4/engagement/scheduling-model, booking-engine, booking-pages. |
| Calendar sync (Google, Microsoft, ICS) | — | gap | `engagement` | New project issue r4/engagement/calendar-sync. |
| Memberships, check-in and attendance | PAP-177, PAP-23 | gap | `engagement` | New project issue r4/engagement/memberships-checkin. |
| Loyalty points and gift cards | PAP-179, PAP-407 | gap | `engagement` | New project issue r4/engagement/loyalty-gift-cards. |
| Surveys, NPS, CSAT and review requests | PAP-352 | gap | `engagement` | Formbricks spiked. New project issues r4/engagement/surveys-nps, reviews-requests. |
| LMS, courses and staff training | — | gap | `engagement` | v0.3: compose docs, forms, memberships. No spec this round. |
| Support ticketing | PAP-197, PAP-410, PAP-411, PAP-412 | covered | `growth` | Deferred v0.2. |

### Growth (8 covered, 1 partial, 1 gap)

| Capability | Covered by | Status | Home | Note |
|---|---|---|---|---|
| CRM entities, pipeline and contact views | PAP-187, PAP-189 | covered | `growth` |  |
| Social scheduling with approval queue | PAP-190, PAP-401, PAP-402, PAP-403 | covered | `growth` |  |
| Outreach sequences (email, SMS) with compliance | PAP-191, PAP-404, PAP-405, PAP-406 | covered | `growth` |  |
| Bulk email campaigns and newsletters | PAP-191, PAP-351 | partial | `growth` | Sequences are drip, not broadcast. Cross suggestion r4/growth/bulk-campaigns. |
| Landing pages and form capture (Webflow) | PAP-193 | covered | `growth` | Forms builder (workflows) supersedes the embed. |
| Acquisition attribution analytics | PAP-194 | covered | `growth` |  |
| Segments from CRM and usage | PAP-195 | covered | `growth` |  |
| Referral and affiliate program | PAP-196, PAP-407, PAP-408, PAP-409 | covered | `growth` |  |
| Content agent drafting for approval | PAP-192 | covered | `growth` |  |
| SEO, CMS and blog | PAP-193 | gap | `growth` | Marketing site stays on Webflow by decision; help center and trust center cover SEO for owned pages. No spec this round. |

### Operations (6 covered, 3 partial, 3 gap)

| Capability | Covered by | Status | Home | Note |
|---|---|---|---|---|
| Hosting, Coolify, deploy pipeline, previews | PAP-25, PAP-26, PAP-15 | covered | `app-shell` |  |
| Public status page and incident communications | PAP-40, PAP-356 | gap | `platform-ops` | Alerts are internal only. New project issue r4/platform-ops/status-page. |
| Security telemetry and alerting | PAP-356 | covered | `quality` |  |
| Performance budgets (web and API) | PAP-87, PAP-242 | covered | `quality` |  |
| Product analytics: events, funnels, retention, adoption | PAP-194, PAP-40, PAP-291 | partial | `platform-ops` | Acquisition and traces only. New project issue r4/platform-ops/product-analytics. |
| Session replay with PII masking | — | gap | `platform-ops` | New project issue r4/platform-ops/session-replay. |
| Experiments and A/B readouts | PAP-366 | partial | `platform-ops` | Variant flags without assignment or metrics. New project issue r4/platform-ops/experiments. |
| Platform super-admin console (tenants, overrides, flags, DLQ) | PAP-63, PAP-43, PAP-366, PAP-61 | partial | `platform-ops` | Pieces exist per module; no platform surface. New project issue r4/platform-ops/superadmin-console. |
| Tenant health scores and ops dashboards | PAP-391, PAP-432 | gap | `platform-ops` | New project issue r4/platform-ops/tenant-health-scores. |
| Usage metering and credit spend reporting | PAP-391, PAP-98 | covered | `business-core` |  |
| Supply-chain and CI security | PAP-358, PAP-80, PAP-357 | covered | `forge` |  |
| Non-Linux CI capacity and flaky-test quarantine | PAP-371, PAP-90 | covered | `forge` |  |

### Developer experience (6 covered, 0 partial, 1 gap)

| Capability | Covered by | Status | Home | Note |
|---|---|---|---|---|
| Spec-first pages, codegen and golden path CLI | PAP-114, PAP-120, PAP-364, PAP-365, PAP-429 | covered | `spec-builder` |  |
| Module system, contracts, conformance, swap tooling | PAP-433, PAP-434, PAP-435, PAP-441, PAP-442, PAP-446 | covered | `module-system` | Every new project ships the module trio. |
| Storybook, docs engine, module docs generator | PAP-69, PAP-128, PAP-445 | covered | `design-system` |  |
| Public API, SDK and webhooks for customers | PAP-222, PAP-269 | covered | `identity` | Deferred v0.2. |
| Plugin and extension marketplace | PAP-28, PAP-433 | gap | `module-system` | Explicit non-goal of the module system for v0.2; tenant-installable extensions via manifests and OAuth apps are the v0.3 path. |
| Test-mode seeds, fixtures and demo tenants | PAP-240, PAP-363 | covered | `quality` |  |
| Library evaluation, registry, license policy, Renovate | PAP-209, PAP-211, PAP-216, PAP-217 | covered | `libraries` |  |

### Agent org (7 covered, 0 partial, 1 gap)

| Capability | Covered by | Status | Home | Note |
|---|---|---|---|---|
| Roster, characters, sub-characters, prompts | PAP-103, PAP-104, PAP-284, PAP-285, PAP-286, PAP-287 | covered | `agents` |  |
| Skills, MCP allowlists, deny list, injection defences | PAP-105, PAP-106, PAP-298, PAP-299, PAP-210 | covered | `agents` |  |
| Budgets, kill switch, observability, sandbox | PAP-111, PAP-288, PAP-280, PAP-300 | covered | `agents` |  |
| Evals harness and golden tasks | PAP-110, PAP-308, PAP-309, PAP-310 | covered | `agents` |  |
| Handoff protocol, inbound triage, weekly re-audit | PAP-108, PAP-307, PAP-306 | covered | `pm-linear` |  |
| Agent org chart and memory | PAP-113, PAP-109 | covered | `agents` |  |
| Agent execution of commands with telemetry | PAP-291 | covered | `input` |  |
| Assistant safety evals and red-team | PAP-299, PAP-308 | gap | `assistant` | New project issue r4/assistant/safety-evals-redteam. |

### Compliance (6 covered, 0 partial, 4 gap)

| Capability | Covered by | Status | Home | Note |
|---|---|---|---|---|
| Threat model and security baseline | PAP-219 | covered | `identity` |  |
| PCI SAQ-A posture | PAP-359 | covered | `business-core` |  |
| SOC 2, GDPR, HIPAA control mapping and evidence | PAP-219, PAP-355, PAP-354, PAP-356, PAP-38 | gap | `platform-ops` | Controls exist, mapping does not. New project issues r4/platform-ops/compliance-controls, evidence-automation. |
| Compliance profiles per tenant (HIPAA mode, student privacy) | PAP-126, PAP-355 | gap | `platform-ops` | PAP-126 hints at a compliance profile; nothing enforces. New project issue r4/platform-ops/compliance-profiles. |
| Accessibility program, statement and VPAT | PAP-73, PAP-156, PAP-160 | covered | `input` |  |
| Trust center, subprocessors, DPA and BAA | PAP-221 | gap | `platform-ops` | New project issue r4/platform-ops/trust-center. |
| Cookie consent and legal pages | PAP-221, PAP-194 | covered | `identity` | Deferred v0.2. |
| Data retention and hard purge | PAP-355, PAP-432 | covered | `data-layer` |  |
| License policy in CI | PAP-211 | covered | `libraries` |  |
| E-signature legal disclosures and certificates | — | gap | `workflows` | New project issue r4/workflows/esign-audit-compliance. |

### Verticals (3 covered, 0 partial, 3 gap)

| Capability | Covered by | Status | Home | Note |
|---|---|---|---|---|
| Business profile and terminology map | PAP-126 | covered | `spec-builder` |  |
| Pack format, applier, gallery and five packs | PAP-207, PAP-426, PAP-427, PAP-428 | covered | `migration` | Deferred v0.2. |
| Packs wave 2: salon, gym, law, real estate | PAP-427 | gap | `commerce` | New project issue r4/commerce/vertical-packs-wave2. |
| Packs wave 3: ecommerce, nonprofit, school, church, construction, property, trades | PAP-427 | gap | `commerce` | New project issue r4/commerce/vertical-packs-wave3. |
| Pack conformance in CI | PAP-429 | gap | `commerce` | New project issue r4/commerce/pack-conformance-tests. |
| Migration agent and importers (Airtable, Notion, ClickUp, Stripe, QuickBooks) | PAP-208, PAP-199, PAP-202, PAP-203, PAP-204, PAP-206 | covered | `migration` | Shopify and Square importers for commerce are a v0.3 note. |

## Proposed new projects

### Tenant AI Assistant & Business Agents (`assistant`)

Lead: Nova. Phase: P2. Module: `@paperos/contract-assistant`. Issues: 14 (5 live, 9 deferred v0.2), 41 points.

The in-product AI layer for tenants and their customers: a grounded assistant that chats over tenant data with citations, turns natural language into views and formulas, drafts replies for approval, takes audited actions through the command registry, and lets tenants configure customer-facing business characters, all metered, evaluated and red-teamed.

Milestones: Assistant contract and grounded chat (2026-10-01); Actions, copilots and portal assistant (2026-10-09); Business characters, evals and swap (2026-10-16).

| Key | Title | Type | Model / effort | Size | Pri | Deferred | Milestone |
|---|---|---|---|---|---|---|---|
| `r4/assistant/contract-publish` | Publish @paperos/contract-assistant v0.1 with manifest | Spec | Opus 5 / high | M | P2 | no | Assistant contract and grounded chat |
| `r4/assistant/model-and-provider-port` | Specify the assistant model: conversations, messages, grounding citations, tool calls and the ModelProviderPort (Anthropic first, tenant BYO key) | Spec | Fable 5.1 / max | M | P2 | no | Assistant contract and grounded chat |
| `r4/assistant/retrieval-grounding` | Build permission-filtered retrieval over the search registry: chunking of records, docs, comments and files, hybrid ranking, citations and freshness | Build | Opus 5 / high | M | P2 | no | Assistant contract and grounded chat |
| `r4/assistant/conversation-runtime` | Build the conversation runtime: streaming turns over the push transport, prompt assembly with trust tiers, tool-call loop, prompt-log ingestion and redaction | Build | Opus 5 / high | M | P2 | no | Assistant contract and grounded chat |
| `r4/assistant/staff-chat-panel` | Build the staff assistant panel: inspector slot, command palette "Ask", citations, suggested follow-ups, history and feedback | Build | Sonnet 5 / medium | M | P3 | no | Assistant contract and grounded chat |
| `r4/assistant/action-catalogue` | Build the action catalogue: agentCallable commands and oRPC procedures as tools with scope classes, confirmation cards, preview diffs and undo | Build | Opus 5 / high | M | P4 | yes | Actions, copilots and portal assistant |
| `r4/assistant/nl-to-views` | Build the tables copilot: natural language to FilterTree, formula and view spec with a reviewable draft, plus "explain this view" | Build | Sonnet 5 / high | M | P4 | yes | Actions, copilots and portal assistant |
| `r4/assistant/summaries-and-drafting` | Build summaries and drafting copilots: record and thread summaries, reply drafts for support and outreach into pending approval, notes to tasks | Build | Sonnet 5 / medium | M | P4 | yes | Actions, copilots and portal assistant |
| `r4/assistant/portal-assistant` | Build the customer-facing portal assistant: help-center grounding, account lookups, booking and payment handoffs, guardrails and escalation to the support inbox | Build | Opus 5 / high | M | P4 | yes | Actions, copilots and portal assistant |
| `r4/assistant/business-characters` | Build tenant-configurable business characters: persona, knowledge sources, allowed tools, audience and hours, extending the character schema with a tenant scope | Build | Sonnet 5 / high | M | P4 | yes | Business characters, evals and swap |
| `r4/assistant/safety-evals-redteam` | Build the assistant eval and red-team suite: injection via records and docs, cross-tenant leak probes, action misuse, faithfulness and refusal grading on the nightly harness | Review | Opus 5 / high | M | P4 | yes | Business characters, evals and swap |
| `r4/assistant/metering-limits` | Add assistant metering and limits: usage kinds, per-tenant daily limits and entitlements, cost dashboard section and BYO-key accounting | Build | Sonnet 5 / medium | S | P4 | yes | Business characters, evals and swap |
| `r4/assistant/conformance` | Conformance test suite for assistant contract | Review | Opus 5 / high | M | P4 | yes | Business characters, evals and swap |
| `r4/assistant/wire` | Wire assistant behind the module registry with an adapter and feature flag | Build | Sonnet 5 / high | M | P4 | yes | Business characters, evals and swap |

### Workflows, Approvals, Forms, Documents & E-Signature (`workflows`)

Lead: Nova. Phase: P2. Module: `@paperos/contract-workflows`. Issues: 15 (4 live, 11 deferred v0.2), 48 points.

The cross-module process layer: a durable workflow engine triggered by any domain event with human tasks and approvals, one approvals framework every module reuses, a standalone forms builder with logic, payments and public embeds, document templates that merge tenant data into PDF and DOCX, and e-signature with an audit certificate.

Milestones: Workflow contract and approvals (2026-10-01); Forms builder and document templates (2026-10-09); E-signature, canvas editor and swap (2026-10-16).

| Key | Title | Type | Model / effort | Size | Pri | Deferred | Milestone |
|---|---|---|---|---|---|---|---|
| `r4/workflows/contract-publish` | Publish @paperos/contract-workflows v0.1 with manifest | Spec | Opus 5 / high | M | P2 | no | Workflow contract and approvals |
| `r4/workflows/workflow-model` | Specify the workflow model: definitions, versions, steps, runs, tasks and waits; event-bus triggers; the boundary with table automations | Spec | Fable 5.1 / max | M | P2 | no | Workflow contract and approvals |
| `r4/workflows/approvals-framework` | Build the approvals framework: approval requests, policies (thresholds, roles, quorum), delegation, SLA escalation and adoption by the five existing approval steps | Build | Opus 5 / high | M | P2 | no | Workflow contract and approvals |
| `r4/workflows/task-inbox` | Build the My Tasks inbox: human tasks and approvals across workflows as a saved view with SLAs, bulk actions, live updates and a dashboard block | Build | Sonnet 5 / medium | S | P3 | no | Workflow contract and approvals |
| `r4/workflows/run-engine` | Build the durable workflow run engine on pg-boss: step executor, suspend and resume, timers, retries, compensation, run log and replay | Build | Opus 5 / high | L | P4 | yes | Forms builder and document templates |
| `r4/workflows/step-catalogue` | Build the step catalogue: human task, approval, wait, branch, for-each, sub-workflow, automation action, agent step, webhook, notify, generate document, request signature | Build | Sonnet 5 / high | M | P4 | yes | Forms builder and document templates |
| `r4/workflows/canvas-editor` | Build the workflow canvas editor on React Flow: node palette from the step catalogue, validation, versions and diff, test runs with fixture events, convert from automation | Build | Sonnet 5 / high | M | P4 | yes | E-signature, canvas editor and swap |
| `r4/workflows/forms-schema-runtime` | Build the forms builder schema and runtime: multi-page forms, conditional logic, field types from the tables engine, validation, uploads, submissions to a dataset or a workflow | Build | Sonnet 5 / high | M | P4 | yes | Forms builder and document templates |
| `r4/workflows/forms-publishing` | Build form publishing: public routes, embeds, anti-spam, rate limits, payment step via Stripe Checkout, partial saves, notifications and submission views | Build | Opus 5 / high | M | P4 | yes | Forms builder and document templates |
| `r4/workflows/document-templates` | Build document templates: template model with merge fields, conditional sections and repeating rows over datasets, a Tiptap template editor and versioning | Build | Sonnet 5 / medium | M | P4 | yes | Forms builder and document templates |
| `r4/workflows/document-generation` | Build document generation: render templates to PDF and DOCX, a generated documents library on the file entity, bulk generation jobs, attach to records and share links | Build | Sonnet 5 / medium | M | P4 | yes | Forms builder and document templates |
| `r4/workflows/esign-core` | Build e-signature core: signature requests, signer identity (email OTP, portal login), fields, sequential signing, the signing ceremony UI and the sealed PDF | Build | Opus 5 / high | L | P4 | yes | E-signature, canvas editor and swap |
| `r4/workflows/esign-audit-compliance` | Add the e-signature audit certificate, tamper-evident hash chain, public verification page, legal disclosures (ESIGN, eIDAS simple), reminders and retention | Build | Opus 5 / high | M | P4 | yes | E-signature, canvas editor and swap |
| `r4/workflows/conformance` | Conformance test suite for workflows contract | Review | Opus 5 / high | M | P4 | yes | E-signature, canvas editor and swap |
| `r4/workflows/wire` | Wire workflows behind the module registry with an adapter and feature flag | Build | Sonnet 5 / high | M | P4 | yes | E-signature, canvas editor and swap |

### Scheduling, Messaging & Customer Engagement (`engagement`)

Lead: Beacon. Phase: P2. Module: `@paperos/contract-engagement`. Issues: 15 (3 live, 12 deferred v0.2), 42 points.

The customer-relationship surfaces every service business needs after acquisition: appointments and resource scheduling with calendar sync, two-way conversational messaging over SMS, WhatsApp, email and in-app, a public help center, surveys and NPS, review requests, memberships with check-in, loyalty and gift cards, in-app announcements and a feedback board.

Milestones: Engagement contract and booking core (2026-10-01); Messaging channels, help center and surveys (2026-10-09); Memberships, loyalty, announcements and swap (2026-10-16).

| Key | Title | Type | Model / effort | Size | Pri | Deferred | Milestone |
|---|---|---|---|---|---|---|---|
| `r4/engagement/contract-publish` | Publish @paperos/contract-engagement v0.1 with manifest | Spec | Opus 5 / high | M | P2 | no | Engagement contract and booking core |
| `r4/engagement/scheduling-model` | Specify the scheduling model: resources, services, availability rules on the recurrence engine, holds, bookings, buffers, time zones and cancellation policies | Spec | Opus 5 / high | M | P2 | no | Engagement contract and booking core |
| `r4/engagement/booking-engine` | Build the booking engine: availability computation, slot search, holds with TTL, exclusion-constraint conflict prevention, reschedule and cancel policies, group capacity and waitlist | Build | Opus 5 / high | M | P2 | no | Engagement contract and booking core |
| `r4/engagement/booking-pages` | Build booking pages and reminders: public /book/:slug flow, portal bookings, staff calendar actions, deposits via Checkout, reminders and no-show follow-ups through notifications | Build | Sonnet 5 / high | M | P4 | yes | Messaging channels, help center and surveys |
| `r4/engagement/calendar-sync` | Build calendar sync: ICS feeds, Google Calendar and Microsoft 365 two-way sync with busy-time import, push into external calendars, webhooks and conflict handling | Build | Opus 5 / high | M | P4 | yes | Messaging channels, help center and surveys |
| `r4/engagement/messaging-channels` | Build two-way conversational messaging: MessagingChannelPort with SMS and WhatsApp (Twilio), threads unified with support conversations, consent and quiet hours, templates and delivery status | Build | Opus 5 / high | M | P4 | yes | Messaging channels, help center and surveys |
| `r4/engagement/help-center` | Build the public help center: articles from tenant docs, categories, search, article feedback, contact and assistant entry points, custom domain and SEO basics | Build | Sonnet 5 / medium | M | P4 | yes | Messaging channels, help center and surveys |
| `r4/engagement/surveys-nps` | Build surveys, NPS and CSAT: templates on the forms runtime, triggers from bookings, tickets and orders through workflows, scoring, response views and Formbricks borrow notes | Build | Sonnet 5 / medium | M | P4 | yes | Messaging channels, help center and surveys |
| `r4/engagement/reviews-requests` | Build review requests and reputation: Google, Facebook and Yelp review links after positive scores, review capture, display widgets for landing pages and a reputation dashboard | Build | Sonnet 5 / medium | S | P4 | yes | Messaging channels, help center and surveys |
| `r4/engagement/memberships-checkin` | Build memberships and check-in: membership plans on Stripe Connect subscriptions for the tenant's customers, member portal card with QR, check-in kiosk and scanner, attendance and lapse handling | Build | Opus 5 / high | M | P4 | yes | Memberships, loyalty, announcements and swap |
| `r4/engagement/loyalty-gift-cards` | Build loyalty and gift cards: points sub-ledger with earn and redeem rules, tiers, rewards at checkout, gift cards as liabilities with codes and balances, fraud limits | Build | Opus 5 / high | M | P4 | yes | Memberships, loyalty, announcements and swap |
| `r4/engagement/announcements` | Build in-app announcements and product messaging: banners, modals and a What's new feed from the changelog, targeting by segment, audience and flag, scheduling, dismissal and metrics | Build | Sonnet 5 / medium | S | P4 | yes | Memberships, loyalty, announcements and swap |
| `r4/engagement/feedback-board` | Build the feedback and feature request board: public and portal board, upvotes, statuses synced to PM entities, duplicates merge, changelog linkage and notifications on status change | Build | Sonnet 5 / medium | S | P4 | yes | Memberships, loyalty, announcements and swap |
| `r4/engagement/conformance` | Conformance test suite for engagement contract | Review | Opus 5 / high | M | P4 | yes | Memberships, loyalty, announcements and swap |
| `r4/engagement/wire` | Wire engagement behind the module registry with an adapter and feature flag | Build | Sonnet 5 / high | M | P4 | yes | Memberships, loyalty, announcements and swap |

### Commerce, Operations & Vertical Packs (`commerce`)

Lead: Ledger. Phase: P2. Module: `@paperos/contract-commerce`. Issues: 16 (3 live, 13 deferred v0.2), 54 points.

The operational core that turns the finance plumbing into runnable businesses: products, variants and inventory; orders, fulfilment and returns; a POS mode with Stripe Terminal; purchasing and accounts payable; projects, time tracking and time-and-materials billing; HR core (directory, time-off, shifts, timesheets to payroll); assets and work orders; tenant-to-customer subscriptions; a two-sided marketplace model; and eleven more vertical packs on the pack format.

Milestones: Commerce contract and catalog (2026-10-01); Orders, POS, purchasing, projects and HR (2026-10-09); Operations packs, marketplace and swap (2026-10-16).

| Key | Title | Type | Model / effort | Size | Pri | Deferred | Milestone |
|---|---|---|---|---|---|---|---|
| `r4/commerce/contract-publish` | Publish @paperos/contract-commerce v0.1 with manifest | Spec | Opus 5 / high | M | P2 | no | Commerce contract and catalog |
| `r4/commerce/domain-model` | Specify the commerce and operations domain model: product, variant, price list, stock location and movement, order and fulfilment, purchase order and bill, project and time entry, shift, asset and work order, mapped to fin_* and Stripe | Spec | Fable 5.1 / max | M | P2 | no | Commerce contract and catalog |
| `r4/commerce/catalog-inventory` | Build catalog and inventory: products, variants, price lists, stock per location with the append-only movement ledger, reservations, counts, low-stock alerts, barcodes and Stripe price sync | Build | Opus 5 / high | M | P2 | no | Commerce contract and catalog |
| `r4/commerce/orders-fulfilment` | Build orders and fulfilment: cart to order state machine, payment via Checkout on platform or connected account, pickup, delivery and shipping label port, returns and refunds with ledger postings, portal order history | Build | Opus 5 / high | L | P4 | yes | Orders, POS, purchasing, projects and HR |
| `r4/commerce/pos-mode` | Build POS mode: kiosk and tablet layout, cart and tenders (Terminal, cash, gift card, points, manual), Stripe Terminal adapter, offline sales queue, receipts and shift close with Z-report | Build | Opus 5 / high | M | P4 | yes | Orders, POS, purchasing, projects and HR |
| `r4/commerce/purchasing-ap` | Build purchasing and accounts payable: purchase orders, receiving into stock, vendor bills with OCR capture, three-way match, approval policies, bill payment scheduling and AP postings | Build | Opus 5 / high | M | P4 | yes | Orders, POS, purchasing, projects and HR |
| `r4/commerce/projects-time-billing` | Build projects, time tracking and time-and-materials billing: projects over PM tasks, time entries and timers, billable rates and budgets, retainers, expenses to projects, time to invoice, utilisation reports | Build | Sonnet 5 / high | M | P4 | yes | Orders, POS, purchasing, projects and HR |
| `r4/commerce/hr-core` | Build HR core: employee directory and profiles on fin_employee, time-off policies and requests with approvals, shift scheduling on the availability shape, clock-in, timesheets and export to payroll runs | Build | Sonnet 5 / high | M | P4 | yes | Orders, POS, purchasing, projects and HR |
| `r4/commerce/assets-work-orders` | Build assets and work orders: asset registry with locations and warranties, maintenance schedules on the recurrence engine, work orders with checklists, parts and labour, mobile technician flow with photos, signatures and invoicing | Build | Sonnet 5 / medium | M | P4 | yes | Orders, POS, purchasing, projects and HR |
| `r4/commerce/customer-subscriptions` | Build tenant-to-customer subscriptions: plans and recurring billing on the connected account, trials, proration, usage add-ons, dunning, portal self-service and MRR datasets, distinct from platform billing | Build | Opus 5 / high | M | P4 | yes | Operations packs, marketplace and swap |
| `r4/commerce/marketplace-model` | Build the two-sided marketplace model: vendor accounts on Connect, vendor audience and portal, listings, split payments with platform fees, vendor payouts and statements, disputes routing | Build | Opus 5 / high | M | P4 | yes | Operations packs, marketplace and swap |
| `r4/commerce/vertical-packs-wave2` | Author vertical packs wave 2 on the pack format: salon and spa, gym and studio, law firm, real estate brokerage, with pages, views, pipelines, services, chart of accounts, terminology, workflows, documents and sample data | Build | Sonnet 5 / medium | L | P4 | yes | Operations packs, marketplace and swap |
| `r4/commerce/vertical-packs-wave3` | Author vertical packs wave 3: ecommerce, nonprofit, school, church, construction, property management, trades and field service | Build | Sonnet 5 / medium | L | P4 | yes | Operations packs, marketplace and swap |
| `r4/commerce/pack-conformance-tests` | Build pack conformance in CI: every pack applies to a blank tenant, home dashboard screenshots at seven widths, terminology and audience policy checks, posting traces, and golden-path acceptance extension | Review | Sonnet 5 / medium | M | P4 | yes | Operations packs, marketplace and swap |
| `r4/commerce/conformance` | Conformance test suite for commerce contract | Review | Opus 5 / high | M | P4 | yes | Operations packs, marketplace and swap |
| `r4/commerce/wire` | Wire commerce behind the module registry with an adapter and feature flag | Build | Sonnet 5 / high | M | P4 | yes | Operations packs, marketplace and swap |

### Platform Operations, Analytics & Compliance (`platform-ops`)

Lead: Sentinel. Phase: P2. Module: `@paperos/contract-platform-ops`. Issues: 15 (4 live, 11 deferred v0.2), 43 points.

What PaperOS itself needs to run as a product for many tenants: a platform super-admin console, a public status page with incident comms, product analytics and session replay with privacy controls, experiments on flags, abuse and signup-fraud controls, tenant health, a control framework mapping SOC 2, GDPR and HIPAA to the evidence the platform already produces, compliance profiles per tenant, a trust center, and the multi-region and data-residency design.

Milestones: Ops contract, super-admin console and status page (2026-10-01); Product analytics, experiments and abuse controls (2026-10-09); Compliance evidence, residency and swap (2026-10-16).

| Key | Title | Type | Model / effort | Size | Pri | Deferred | Milestone |
|---|---|---|---|---|---|---|---|
| `r4/platform-ops/contract-publish` | Publish @paperos/contract-platform-ops v0.1 with manifest | Spec | Opus 5 / high | M | P2 | no | Ops contract, super-admin console and status page |
| `r4/platform-ops/superadmin-console` | Build the platform super-admin console at /admin: tenant list and detail, entitlement overrides, flag rules, module toggles, jobs and dead-letter queue, usage and health, every action audited and MFA-gated | Build | Opus 5 / high | M | P2 | no | Ops contract, super-admin console and status page |
| `r4/platform-ops/status-page` | Build the public status page and incident comms: components, incidents with updates, scheduled maintenance, subscribers by email, SMS and RSS, fed by observability alerts and security S0 events, with per-tenant embedding | Build | Sonnet 5 / medium | M | P3 | no | Ops contract, super-admin console and status page |
| `r4/platform-ops/compliance-controls` | Specify the control framework: controls.yaml mapping SOC 2 trust criteria, GDPR articles and HIPAA safeguards to the issues, artefacts and evidence the platform already produces, with the gap list | Spec | Opus 5 / high | M | P2 | no | Ops contract, super-admin console and status page |
| `r4/platform-ops/product-analytics` | Build product analytics: track() SDK with an event schema registry, consent-aware first-party pipeline reusing the attribution collector, funnels, retention and feature adoption datasets, tenant-facing analytics for their own customers | Build | Sonnet 5 / high | M | P4 | yes | Product analytics, experiments and abuse controls |
| `r4/platform-ops/session-replay` | Build session replay: rrweb capture with PII masking driven by schema annotations, consent and sampling, storage budget, replay viewer linked to errors and support conversations, decision ADR | Build | Opus 5 / high | M | P4 | yes | Product analytics, experiments and abuse controls |
| `r4/platform-ops/experiments` | Build experiments on feature flags: experiment definitions over PAP-366 variants, deterministic assignment, exposure events, metrics from product analytics, sequential readouts with guardrails and a results page | Build | Sonnet 5 / high | M | P4 | yes | Product analytics, experiments and abuse controls |
| `r4/platform-ops/abuse-controls` | Build abuse and signup-fraud controls: CaptchaPort, disposable-email and velocity checks, verification gates, tenant quarantine, outbound sending reputation guard, report-abuse endpoint and review queue | Build | Opus 5 / high | M | P4 | yes | Product analytics, experiments and abuse controls |
| `r4/platform-ops/tenant-health-scores` | Build tenant health scores and ops dashboards: activation, usage, errors, sync lag, storage, billing state and NPS per tenant, alerts to platform staff, churn-risk segment feeding growth | Build | Sonnet 5 / medium | S | P4 | yes | Product analytics, experiments and abuse controls |
| `r4/platform-ops/compliance-profiles` | Build compliance profiles per tenant: standard, gdpr, hipaa and student-privacy profiles from the business profile enforcing MFA, session timeouts, PHI access logging, encryption of phi columns, export restrictions and BAA acknowledgement | Build | Opus 5 / high | M | P4 | yes | Compliance evidence, residency and swap |
| `r4/platform-ops/evidence-automation` | Build automated compliance evidence collection: nightly snapshots of access reviews, backup verification, vulnerability scans, change management gates, incident records and agent policy checks into compliance_evidence with retention and an auditor export | Build | Sonnet 5 / medium | M | P4 | yes | Compliance evidence, residency and swap |
| `r4/platform-ops/trust-center` | Build the trust center: security overview, live control status, subprocessor register, policy documents from the docs engine, DPA and BAA template downloads, uptime from the status page, accessibility report link and change subscriptions | Build | Sonnet 5 / medium | S | P4 | yes | Compliance evidence, residency and swap |
| `r4/platform-ops/data-residency` | Design multi-region and data residency: region per tenant, EU region stack, host and API routing, per-region backups, residency in the business profile and provisioning plan, as an ADR with a runbook | Spec | Opus 5 / high | M | P4 | yes | Compliance evidence, residency and swap |
| `r4/platform-ops/conformance` | Conformance test suite for platform-ops contract | Review | Opus 5 / high | M | P3 | yes | Compliance evidence, residency and swap |
| `r4/platform-ops/wire` | Wire platform-ops behind the module registry with an adapter and feature flag | Build | Sonnet 5 / high | M | P3 | yes | Compliance evidence, residency and swap |

## Cross-project suggestions (gaps that belong in existing projects)

| Key | Target | Title | Model / effort | Size | Pri | Deferred | Milestone |
|---|---|---|---|---|---|---|---|
| `r4/data-layer/file-scanning-previews` | `data-layer` | Add file scanning and previews: ClamAV malware scan with quarantine states on the file entity, document previews (PDF first page, office via Gotenberg), video thumbnails and text extraction for search | Sonnet 5 / medium | M | P3 | no | Tenant-safe and observable |
| `r4/data-layer/recurrence-engine` | `data-layer` | Build the shared recurrence engine: RRULE (RFC 5545) parsing and expansion with time zones, exceptions and bounds, used by jobs schedules, recurring invoices, calendar views, bookings and maintenance | Sonnet 5 / medium | S | P2 | no | Tenant-safe and observable |
| `r4/data-layer/cdn-edge-cache` | `data-layer` | Add CDN and edge caching for public assets, public views and embeds, and signed file downloads, with cache keys, purge on change and a provider decision (Caddy cache versus Bunny or Cloudflare) | Sonnet 5 / medium | S | P4 | yes | Tenant-safe and observable |
| `r4/collab/sms-notification-channel` | `collab` | Add SMS and WhatsApp as notification channels on the notification core: Twilio provider shared with outreach, per-kind opt-in, consent and quiet hours, STOP handling and cost metering | Sonnet 5 / medium | S | P4 | yes | Knowledge surfaced everywhere |
| `r4/business-core/fx-rates` | `business-core` | Build the multi-currency FX rate service: daily rates from ECB and Open Exchange Rates adapters, convert(Money, currency, date), reporting currency, realised and unrealised gain posting rules and revaluation job | Opus 5 / high | M | P4 | yes | Ledger and reports |
| `r4/business-core/bank-feeds-reconciliation` | `business-core` | Build bank feeds and reconciliation: BankFeedPort with Plaid and GoCardless adapters, statement import, matching rules to documents and ledger entries, reconciliation UI and Stripe payout reconciliation | Opus 5 / high | L | P4 | yes | Payroll adapter and cash dashboard |
| `r4/tables/scheduled-view-delivery` | `tables` | Add scheduled delivery of views and dashboards: PDF and CSV snapshots on a recurrence to email, Slack or a share link, rendered per recipient permissions, with run history | Sonnet 5 / medium | S | P4 | yes | View sharing, formulas, dashboards |
| `r4/tables/address-geo-field` | `tables` | Add an address and location field type with a geocoding provider port, autocomplete, map view binding and distance and within-area filter operators in the FilterTree | Sonnet 5 / medium | M | P4 | yes | All view types |
| `r4/design-system/labels-barcodes-qr` | `design-system` | Add labels, barcodes and QR codes to the print kit: Barcode and QRCode components, label templates for Avery and thermal sizes, a barcode field type helper and scanner input handling | Sonnet 5 / medium | S | P4 | yes | Themable per tenant with docs |
| `r4/app-shell/settings-registry` | `app-shell` | Build the settings registry: modules declare settings sections and schemas in their manifests, the shell generates tenant, workspace and user settings pages with permissions, audit and search | Sonnet 5 / high | M | P2 | no | Multi-monitor and PWA polish |
| `r4/identity/oauth-provider-apps` | `identity` | Add tenant-installable OAuth apps: OIDC provider for third-party apps with consent screens, client registration, scopes mapped to API key scopes, token introspection and revocation | Opus 5 / high | M | P4 | yes | Agent principals and enterprise |
| `r4/growth/bulk-campaigns` | `growth` | Build bulk email campaigns and newsletters: campaign builder on the email template editor, list segments, send-time throttling and warmup, per-campaign analytics, Listmonk borrow notes | Sonnet 5 / medium | M | P4 | yes | Campaigns and social |

## Method

Every capability was checked against issue titles and full descriptions in the live inventory (keyword search plus reading the Goal and Scope of the partially covering issues). `covered` means an existing issue owns the capability end to end (deferred issues count as covered because they are fully specified); `partial` means a piece exists but the capability as a business would recognise it does not; `gap` means nothing owns it. Every new issue follows the canonical spec format (PAP-342), cites only identifiers that exist in the inventory, includes the module trio required by `docs/module-system.md`, and uses the model rule: Sonnet 5 / medium by default, Opus 5 / high for security-sensitive, money-moving or widely consumed pieces, Fable 5.1 / max for the three keystone model specs, Haiku 4.5 unused this round (no mechanical docs). Estimates S=2, M=3, L=5. Milestones after 2026-10-01 are marked deferred (v0.2) in their descriptions.
