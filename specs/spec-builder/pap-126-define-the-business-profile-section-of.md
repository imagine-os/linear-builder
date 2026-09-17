---
identifier: "PAP-126"
title: "Define the business profile section of app.spec.yaml: industry, audiences, terminology map, locale, currency and tax regime, enabled modules; codegen, templates and the migration agent read it"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P2"
type: "Spec"
priority: 2
surfaces: ["Customer", "Developer", "Staff"]
milestone: "Spec editor UI"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-27", "PAP-28", "PAP-117", "PAP-266"]
blocks: []
key: "spec-builder/business-profile"
url: "https://linear.app/paperos/issue/PAP-126/define-the-business-profile-section-of-appspecyaml-industry-audiences"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:22:44.044Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-126: Define the business profile section of app.spec.yaml: industry, audiences, terminology map, locale, currency and tax regime, enabled modules; codegen, templates and the migration agent read it

**Goal**

"One-size-fits-all software that adapts to every type of business" needs a place where the adaptation is declared. Add a `business:` section to `app.spec.yaml` with an industry taxonomy, a terminology map that renames core concepts (customer becomes patient, guest, client, member, student) across UI strings, navigation, view headers, notification templates and agent prompts, plus locale, currency, tax regime and enabled modules. The migration agent fills it in; codegen and templates read it.

**Scope**

* In: schema extension in `packages/spec/src/schema/app.ts`, `packages/spec/src/industries.yaml` (40 industries with subtypes, defaults), terminology helper in `packages/i18n`, `useBusinessProfile()`, `pnpm spec business:apply <profile>`, validator rules, ADR, `docs/spec/business-profile.md`.
* Out: seed pack contents (PAP-207), the interview (PAP-208), tax calculation (PAP-182), module semantics (PAP-28).

**Spec**

* `business { industry, subtype?, secondaryIndustries[], audiences[] { id, kind, label, plural }, terminology: Record<CoreTerm, { singular, plural }>, locale { default, enabled[], timezone }, currency { default, enabled[] }, taxRegime: us-sales-tax | vat | gst | none, modules[], compliance[] }`.
* `CoreTerm` is a closed set of 30 concepts (`customer`, `order`, `product`, `service`, `staff`, `location`, `appointment`, `invoice`, `project`, `task`, ...); unknown keys fail.
* `t.term('customer', { plural: true })` resolves through PAP-27 catalogs; changing terminology is a spec change that regenerates pages (PAP-120) and is reviewed like any spec change.
* Taxonomy and defaults are data: adding an industry is a YAML PR; secondary industries merge modules and terminology with explicit conflict resolution.
* Rules: `BIZ_UNKNOWN_INDUSTRY`, `BIZ_UNKNOWN_TERM`, `BIZ_INVALID_CURRENCY`, `BIZ_UNKNOWN_AUDIENCE`, `BIZ_TERM_COLLISION` (warn), `BIZ_MODULE_UNKNOWN` (against PAP-264 registry).

**Interface contract**

* Provides: `BusinessProfileSchema`, type `BusinessProfile`, `CoreTerm`, `industries.yaml` with `IndustrySchema`, `useBusinessProfile()`, `t.term()`, `pnpm spec business:apply <industry | generic>`, generated `apps/web/src/generated/app/business.ts`.
* Consumers: PAP-120 labels and empty-state copy, PAP-16 navigation labels, PAP-165 column headers, PAP-136 templates, PAP-104 prompts (terminology fragment), PAP-207 seed packs declare `industry`, PAP-208 interview writes the profile, PAP-175 and PAP-182 read `currency` and `taxRegime`, PAP-124 edits it later.
* Requires: PAP-117 app spec (hard), PAP-28 and PAP-264 module registry, PAP-27 catalogs. Soft: PAP-120, PAP-207, PAP-208.

**Definition of done**

* Switching the template between clinic and agency profiles by editing `app.spec.yaml` alone changes navigation labels, table headers, empty states and notification templates (before and after screenshots at 375 and 1280 px in `en` and `es`).
* Validator catches unknown audience, term and currency.
* `business:apply clinic` produces a valid profile; PAP-208 writes an equivalent one in a recorded run.
* Five seed packs declare their industry; docs, ADR, changelog; Linear comment. Justin reviews industries and defaults in the same `Needs Justin` item PAP-207 files (one item).

**Test plan**

* Unit: schema and rules, term resolution with plural and locale, secondary-industry merge conflicts, `generic` profile validity.
* Integration: `business:apply` then `gen:page` for the examples; snapshot of generated labels.
* e2e: Playwright switches profiles and asserts the nav label text at 375 and 1280 px.
* Visual: before and after screenshots in two locales through gate 3.

**Demo**

Run `pnpm spec business:apply clinic && pnpm spec gen:page --all`, reload the staff console: "Customers" now reads "Patients" in navigation, table headers and the empty state; switch to `agency` and it reads "Clients". Ninety seconds.

**Edge cases**

* Gym with a cafe: `secondaryIndustries` with explicit conflict resolution.
* Two terms mapping to one label: warning; codegen disambiguates.
* Case-inflected plurals: base term in the map; catalogs carry full forms.
* Non-profit `taxRegime: none`: tax fields hidden, ledger kept.
* Pre-existing apps: `business:apply generic` fills a neutral profile.

**Dependencies**

Blocked by PAP-117, PAP-28, PAP-27. Soft: PAP-120, PAP-124, PAP-207, PAP-208, PAP-175, PAP-182.

**Agent**

Written by Quill (Page Spec Writer) with Scout (Library Evaluator) on the taxonomy; reviewed by Atlas and Ledger for finance fields.

**Size**

M
