---
identifier: "PAP-766"
title: "Exchange rate table and FX service: daily rates job with a fixture provider, rateAt lookup, functional-currency conversion and realised gain or loss helpers"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Ledger and reports"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-43", "PAP-175", "PAP-565"]
blocks: ["PAP-183", "PAP-185", "PAP-423"]
key: "r4/business-core/fx-rates-and-conversion"
url: "https://linear.app/paperos/issue/PAP-766/exchange-rate-table-and-fx-service-daily-rates-job-with-a-fixture"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:40.905Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-29"
cycle: null
---

# PAP-766: Exchange rate table and FX service: daily rates job with a fixture provider, rateAt lookup, functional-currency conversion and realised gain or loss helpers

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Five specs (PAP-175 `convert(rate)`, PAP-179 `fx_gain_loss`, PAP-183 functional amounts, PAP-185 receipt FX, PAP-206 and PAP-423 base equivalents) say 'from the rates table' and none defines it. This issue owns the table, the daily job, the lookup and the gain or loss arithmetic so every multi-currency line converts the same way.

**Scope**

In: `packages/finance/src/fx/` with table `fin_fx_rate (tenant_id nullable for platform rates, base char(3), quote char(3), rate numeric(18,8), as_of date, source: ecb|openexchangerates|manual|fixture, fetched_at)` unique on `(tenant_id, base, quote, as_of)`; job `fx.fetch` daily (PAP-43) behind a `RateProvider` port with `ecb` (free XML feed), `openexchangerates` (key from PAP-17) and `fixture` (committed JSON, the CI default) adapters; `fx.rateAt(date, from, to)` with previous-business-day fallback and triangulation through the base; `convertToFunctional(money, date)`; `realisedGainLoss(bookedFunctional, settledFunctional)`; procedures `fx.rates.list|setManual`; settings section for manual overrides.

Out: hedging, unrealised revaluation at period end (PAP-784 notes it), crypto.

**Spec**

* Rates are stored as decimal strings and multiplied with `decimal.js`; results round half-even to the currency exponent from the PAP-175 ISO table (JPY 0, KWD 3).
* `rateAt` returns `{ rate, asOf, source, stale: boolean }`; `stale` when `as_of` is more than 3 business days before the requested date; consumers surface stale as a footnote, never as an error.
* Manual rates win over provider rates for the same day and tenant; platform rates (`tenant_id null`) are the default for every tenant.
* `fixture` adapter ships 400 days of EUR, USD, GBP, JPY, CAD, AUD, CHF, KWD so tests are deterministic without network; the provider port is registered in the manifest as a swappable adapter (`docs/module-system.md`).
* Realised gain or loss posts to the `fx_gain_loss` subtype through the PAP-394 `adjustment` rule with the source document as `subject`.

**Interface contract**

Provides: `RateProvider` port, `fx.rateAt`, `convertToFunctional`, `realisedGainLoss`, table and dataset `finance.fxRates`, job `fx.fetch`, settings section `shell.settings.sections:fx`. Consumes: `Money` and ISO exponents (PAP-175), jobs (PAP-43), env (PAP-17), posting (PAP-394), settings slot (PAP-264).

**Definition of done**

* Property tests (`fast-check`) show conversion round trips within one minor unit and never produce floats; fixture adapter passes offline in CI; ECB adapter tested against a recorded XML response.
* PAP-183 multi-currency footnote and PAP-397 FX handling read `rateAt` (integration test posts a EUR invoice into a USD tenant and settles at a different rate, asserting the `fx_gain_loss` line).
* `docs/finance/fx.md`; CHANGELOG; Linear comment naming the consumers switched over.

**Test plan**

* Unit: triangulation, half-even rounding per exponent, previous-business-day fallback, manual override precedence, stale flag, gain or loss sign.
* E2E: settings page lists today's rates, an admin sets a manual GBP rate and the next invoice preview uses it with a 'manual' badge.

**Demo**

Reviewer runs `pnpm tsx scripts/fx-demo.ts 2026-09-15 EUR JPY 1999` and reads the converted amount, source and staleness, then sets a manual rate in settings and reruns. Under one minute.

**Edge cases**

* Weekend or holiday: fallback to the last published rate, `stale: false` within 3 business days.
* Currency pair with no path through the base: `VALIDATION` naming both currencies.
* Provider outage: job retries with backoff; yesterday's rates remain; alert after two missed days (PAP-40).
* Functional currency change is blocked by PAP-175; this issue never rewrites history.

**Dependencies**

Hard: PAP-175, PAP-43. Soft: PAP-17, PAP-394, PAP-40. Blocks PAP-183 (footnote), PAP-185, PAP-423 (soft for both).

**Agent**

Builder: Ledger (Bookkeeper). Reviewer: Sentinel (Code Reviewer, Edge Case Hunter for rounding).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/business-core/year-end-close` = PAP-784.
