---
identifier: "PAP-126"
title: "Define the business profile section of app.spec.yaml: industry, audiences, terminology map, locale, currency and tax regime, enabled modules; codegen, templates and the migration agent read it"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P2"
type: "Spec"
priority: 2
surfaces: ["Developer", "Staff", "Customer"]
milestone: "Spec editor UI"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-117", "PAP-266", "PAP-27", "PAP-28"]
blocks: []
key: "spec-builder/business-profile"
url: "https://linear.app/paperos/issue/PAP-126/define-the-business-profile-section-of-appspecyaml-industry-audiences"
source: "plan/specs/gaps.json (round-1 canonical spec JSON)"
---

# PAP-126: Define the business profile section of app.spec.yaml: industry, audiences, terminology map, locale, currency and tax regime, enabled modules; codegen, templates and the migration agent read it

**Goal**

"One-size-fits-all software that then adapts to every single type of business" needs a place where the adaptation is declared. Today that knowledge would be scattered across seed packs (`migration/business-templates`), tenant settings and page copy. This issue adds a `business:` section to `app.spec.yaml`, a vocabulary of industries and their defaults, and a terminology map that renames core concepts (customer becomes patient, guest, client, member, student) consistently across UI strings, navigation, table names in views, notification templates and agent prompts. The migration agent's interview fills it in; codegen and templates read it.

**Scope**

In:
- Schema addition in `packages/spec/src/app-spec.ts`: `business: { industry: <taxonomy id>, subtype?, audiences: [{ id, kind: customer|staff|partner|agent, label, plural }], terminology: { customer: 'Patient', order: 'Appointment', ... }, locale: { default, enabled[], timezone }, currency: { default, enabled[] }, taxRegime: 'us-sales-tax' | 'vat' | 'gst' | 'none', modules: [...] (delegates to app-shell/feature-modules), compliance: ['hipaa'|'pci'|'gdpr'|...] flags for future gates }`.
- Industry taxonomy `packages/spec/src/industries.yaml`: 40 top-level industries with subtypes derived from NAICS sectors and the five business templates, each with default terminology, default modules, default audiences and example entities; ADR explains the choice of a small internal taxonomy over full NAICS.
- Terminology resolution: `t.term('customer', { plural: true })` helper in `packages/i18n` that reads the profile; `spec-builder/layout-codegen` emits `term()` for concept nouns instead of literals; `tables/field-types` relation labels and `collab/notifications` templates use it; the map itself is localised per enabled locale (`app-shell/i18n-l10n` catalogs hold translations of each term).
- Validator rules: audiences in page `access` sections must exist in `business.audiences`; a module referenced in a page must be in `business.modules`; currency codes and timezones validated against Intl support.
- Defaults engine: `pnpm spec business:apply <industry>` fills the profile from the taxonomy and lets the author override; the spec editor UI (`spec-builder/spec-editor-ui`) gains a Business tab.
- Migration agent hook: `migration/migration-agent` interview questions map to the profile fields and write them before choosing a seed pack; `migration/business-templates` packs declare `industry` and are matched from the profile.
- Finance defaults: `business-core/finance-data-model` chart-of-accounts template and `business-core/tax-compliance` regime selected from the profile.
- Docs `docs/spec/business-profile.md` with three worked profiles (clinic, agency, retail).

Out: per-tenant terminology overrides at runtime (a later issue; v1 is per app), automated compliance enforcement (flags only), pricing localisation.

**Spec**

- Terminology keys are a closed set of 30 core concepts (`customer`, `order`, `product`, `service`, `staff`, `location`, `appointment`, `invoice`, `project`, `task`, ...) documented with definitions; unknown keys fail validation.
- Every term has singular and plural in the source locale; translations follow catalogs.
- Changing `terminology` is a spec change that regenerates pages (`spec-builder/layout-codegen`) and is reviewed by the spec-conformance reviewer like any spec change.
- The profile is available at runtime as `useBusinessProfile()` for conditional UI (for example show tax fields only under `vat`).
- Templates and the taxonomy are data, not code; adding an industry is a YAML PR.

**Definition of done**

- Template app switched between the clinic and agency profiles by editing `app.spec.yaml` alone: navigation labels, table headers, empty states and notification templates change accordingly (before and after screenshots at 1280 and 375, both locales `en` and `es`).
- Validator catches an unknown audience, an unknown term, an invalid currency (tests).
- `pnpm spec business:apply clinic` produces a valid profile; the migration agent interview writes an equivalent one in a recorded run.
- The five seed packs declare their industry and are selected automatically.
- Docs, ADR, `CHANGELOG.md`, Linear comment. Justin reviews the industry list and terminology defaults for business realism in the same Needs Justin item that `migration/business-templates` already files (one item, not two).

**Edge cases**

- A business that fits two industries (a gym with a cafe): `industry` plus `secondaryIndustries[]` merging modules and terminology with explicit conflict resolution in the profile.
- Term collisions after renaming (`customer` and `member` both mapped to "Member"): validator warns; codegen disambiguates in labels.
- Plural forms in languages where the term changes by case: the map stores the base term; catalogs carry full forms per message.
- Tax regime `none` for a non-profit: finance module hides tax fields but keeps the ledger.
- Apps generated before this issue: `pnpm spec business:apply generic` fills a neutral profile so validation passes unchanged.

**Dependencies**

`spec-builder/app-level-spec` (the file this extends), `app-shell/feature-modules` (`modules:` semantics), `app-shell/i18n-l10n` (term localisation). Soft: `spec-builder/layout-codegen`, `spec-builder/spec-editor-ui`, `migration/business-templates`, `migration/migration-agent`, `business-core/finance-data-model`, `business-core/tax-compliance`.

**Agent**

Written by Quill (Page Spec Writer) with Scout for the taxonomy research and Ledger for finance defaults. Reviewed by Sentinel (spec-conformance reviewer) and Atlas.

**Size**

M: schema and taxonomy are quick; the value is in threading `term()` through codegen and templates.
