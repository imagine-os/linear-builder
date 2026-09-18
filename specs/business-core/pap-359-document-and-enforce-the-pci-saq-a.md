---
identifier: "PAP-359"
title: "Document and enforce the PCI SAQ-A posture: Stripe-hosted card entry only, a Semgrep rule against card-data fields, restricted Stripe keys per service, live-key custody through Needs Justin, and the quarterly SAQ-A checklist"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P1"
type: "Docs"
priority: 2
surfaces: ["Developer"]
milestone: "Stripe billing live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-177"]
blocks: ["PAP-181", "PAP-184", "PAP-896"]
key: "security/pci-posture"
url: "https://linear.app/paperos/issue/PAP-359/document-and-enforce-the-pci-saq-a-posture-stripe-hosted-card-entry"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:19.219Z"
model: "claude-sonnet-5"
effort: "low"
estimate: 2
dueDate: "2026-09-27"
cycle: null
---

# PAP-359: Document and enforce the PCI SAQ-A posture: Stripe-hosted card entry only, a Semgrep rule against card-data fields, restricted Stripe keys per service, live-key custody through Needs Justin, and the quarterly SAQ-A checklist

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Docs S

**Goal**

PaperOS must never be in PCI scope beyond SAQ-A: card numbers are entered only in Stripe Checkout, Elements or the Customer Portal, our servers see tokens and webhook payloads, and payroll bank details live at the payroll provider. This issue writes that posture down as an enforceable set of rules (schema lint, Semgrep, key policy, custody procedure) and the quarterly checklist Justin signs, so PAP-177, PAP-180, PAP-181 and PAP-184 inherit compliance instead of each deciding.

**Scope**

* In: `docs/finance/pci-posture.md` (scope statement, data-flow diagram, SAQ-A eligibility criteria and how each is met), Semgrep rules in `ops/security/semgrep/pci.yaml` (PAP-80), schema lint for card-shaped columns, Stripe key policy (restricted keys per service with the exact permission sets), live-mode custody procedure via a PAP-94 card, webhook and Connect data handling rules, quarterly checklist template and reminder routine, `controls.yaml` entries `SEC-PCI-*` (PAP-219).
* Out: Stripe integration code (PAP-177, PAP-180, PAP-181), tax evidence (PAP-182), payroll provider agreements (PAP-176), SOC 2.

**Spec**

* Scope statement: only Stripe-hosted surfaces collect card data (Checkout, Elements in the portal for saved methods, Customer Portal, payment links from PAP-180); no card fields in any page spec (spec validator PAP-115 rejects components named `cardNumber|cvc|expiry` and any `integrations.stripe` entry with `elements: false`); bank details for payroll are collected on provider-hosted onboarding links (PAP-184) never stored by us; Connect onboarding uses Stripe-hosted flows (PAP-181).
* Semgrep rules (`ERROR`, S0 per PAP-80 mapping): regexes for PAN-shaped literals and fields (`\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\b`, `cvv|cvc|card_number|pan|track2`), `stripe.tokens.create` with raw card, logging of `payment_method` objects, `sk_live_` literals anywhere; schema lint in `pnpm db:scan-secrets` (PAP-353) flags card-shaped columns as forbidden, not merely unencrypted.
* Keys: no secret key with full permissions in any service; restricted keys per service (`api`: customers, checkout sessions, subscriptions, invoices read and write, webhooks read; `worker`: events read, payouts read; `ledger`: balance transactions read) created by Justin in the Dashboard following the doc's table; test-mode keys until live custody; keys stored in sops (PAP-25) and encrypted per tenant for Connect accounts (PAP-353); rotation quarterly per PAP-219 runbook.
* Live-mode custody: switching any environment to `sk_live_` requires a PAP-94 decision card `Enable Stripe live mode for <env>` listing the SAQ-A checklist status, webhook endpoint verification, restricted key scopes and the rollback (revert to test keys); approval recorded in `docs/finance/pci-posture.md` with date; the deny list (PAP-298) blocks agents from using or creating live keys.
* Webhook data: `stripe_event.payload` (PAP-177) retained 90 days then trimmed to `id`, `type`, `created` (PAP-355); payloads never logged in full; PAP-40 span processor drops `payment_method` attributes.
* Quarterly checklist: SAQ-A questions mapped to evidence (Stripe Dashboard screenshots, Semgrep run link, key inventory, TLS scan of `app.` and `api.`), filed as a Docs issue each quarter by a Scout routine (PAP-218 pattern) and closed by Justin.

**Interface contract**

* Provides: `docs/finance/pci-posture.md`, Semgrep `pci.yaml`, spec validator rule `no-card-fields`, key permission table, decision card template, checklist template, controls `SEC-PCI-01..08`.
* Consumers: PAP-177, PAP-180, PAP-181, PAP-184 (inherit rules), PAP-80 (rules), PAP-115 (validator rule), PAP-219 (controls), PAP-298 (live key rules), PAP-94 (custody card).
* Requires: PAP-177 Stripe client conventions; Justin creates restricted keys.

**Definition of done**

* Doc merged with data-flow diagram (Mermaid) and SAQ-A eligibility table, every criterion mapped to a control id.
* Semgrep rules catch five seeded violations (PAN literal, `card_number` column, raw token create, `sk_live_` literal, logged payment method) and pass on the current codebase.
* Spec validator rejects a fixture spec with a `cardNumber` component.
* Restricted keys created per the table; `pnpm security:accounts-check` (PAP-301) reports no full-access Stripe keys.
* First quarterly checklist issue created and linked; changelog under "Security"; Linear comment.

**Test plan**

* Unit: Semgrep rule tests with positive and negative fixtures; validator rule tests.
* Integration: `pnpm db:scan-secrets` on a fixture schema with a card column.
* Manual: Justin reviews the key table and creates keys.
* No UI.

**Demo**

Open the posture doc's diagram, run `semgrep --config ops/security/semgrep/pci.yaml` on the fixtures to see five hits, then show the restricted key table against the Stripe Dashboard. One minute.

**Edge cases**

* Tenant wants to import historic card data from another processor: refused; Stripe's PAN import service is the documented path (PAP-206 notes it).
* Test fixtures containing Stripe's documented test card numbers: allowlisted by exact value in the Semgrep rule.
* Connect connected accounts with their own keys: we never hold connected-account secret keys; OAuth access tokens are encrypted (PAP-353).
* Payroll provider sends bank details in webhooks: adapter contract (PAP-184) masks to last four before persistence.
* Justin unavailable for the custody card: live mode waits; the default-if-no-answer rule of PAP-94 is `hard-block` for this card.

**Dependencies**

Blocked by PAP-177. Blocks PAP-181, PAP-184. Soft: PAP-80, PAP-115, PAP-219, PAP-353, PAP-298.

**Agent**

Written by Ledger (Compliance sub-agent) with Sentinel (Security Auditor) for the rules; Justin creates keys and approves custody.

**Size**

S
