---
identifier: "PAP-375"
title: "Add spec-level internationalisation: message IDs for spec copy fields, extraction into catalogs, pseudo-locale validation rule"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Developer"]
milestone: "Spec editor UI"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-27", "PAP-120"]
blocks: []
key: "spec-builder/spec-i18n"
url: "https://linear.app/paperos/issue/PAP-375/add-spec-level-internationalisation-message-ids-for-spec-copy-fields"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:12.501Z"
---

# PAP-375: Add spec-level internationalisation: message IDs for spec copy fields, extraction into catalogs, pseudo-locale validation rule

**Goal**

Stop codegen from baking English into every generated app: copy fields in specs (`states.*.copy`, `purpose.summary` shown to users, navigation labels, component `props` marked as text, terminology from PAP-126) get message ids, an extractor writes them into the PAP-27 catalogs, generated pages render through `t()`, and a pseudo-locale validation rule catches hard-coded strings.

**Scope**

* In: `x-i18n` conventions in `PageSpecSchema` and `AppSpecSchema` (`copy` accepts a string or `{ id, default }`), `pnpm spec gen:messages`, catalog writer for `packages/i18n`, codegen changes in PAP-120 templates to emit `t('<id>')`, validator rules, pseudo-locale test in gate 3.
* Out: translation itself, runtime locale switching (PAP-27), terminology semantics (PAP-126).

**Spec**

* Message id derivation: `<specId>.<path>` (for example `customer-invoices.states.empty.copy`), overridable with `{ id }`; ids stable across regenerations; `default` is the source-locale text.
* Text-bearing props: the PAP-74 registry marks props `i18n: true` (`label`, `placeholder`, `title`, `description`); codegen wraps only those.
* Extractor writes `packages/i18n/messages/<locale>/spec.json` for the default locale, merges without dropping human edits, marks removed ids `obsolete`.
* Rules: `I18N_HARDCODED` (string copy without id when `app.i18n.strict` is true; warning otherwise), `I18N_DUP_ID`, `I18N_OBSOLETE` (warn).
* Pseudo-locale `en-XA` (accented, 30 percent longer) generated automatically; gate 3 screenshots one example page in `en-XA` at 375 and 1280 px to expose truncation.

**Interface contract**

* Provides: `MessageRef = string | { id: string; default: string }` type, `extractMessages(specs, app): Catalog`, `pnpm spec gen:messages`, rule ids above, `pseudoLocale()` helper, `spec.json` catalog namespace.
* Consumers: PAP-120 templates (`t()` emission), PAP-27 loader (namespace `spec`), PAP-126 terminology (`t.term` ids), PAP-124 form shows id and default side by side, PAP-82 pseudo-locale screenshots, PAP-136 templates reuse ids for notification copy.
* Requires: PAP-27 catalogs and `t()`, PAP-120 templates, PAP-74 `i18n` prop flags (soft; defaults to the four known props).

**Definition of done**

* Three example pages emit zero literal user-facing strings (grep test on generated views).
* `gen:messages` produces a catalog; a second run is a no-op; removing a state marks its id `obsolete`.
* Pseudo-locale screenshots of `customer-invoices` at 375 and 1280 px show no truncation after fixes.
* `docs/spec/i18n.md`; changelog; Linear comment with screenshots.

**Test plan**

* Unit: id derivation stability, merge preserving edits, rule fixtures, pseudo-locale transform.
* Integration: codegen snapshot with `t()` calls; catalog round trip through PAP-27 loader.
* e2e (Playwright): example page rendered in `en-XA` at 375 and 1280 px.
* Visual: two widths through gate 3 in the pseudo-locale.

**Demo**

Set `app.i18n.strict: true`, run `pnpm spec:validate` to see `I18N_HARDCODED` on a literal, replace it with `{ id, default }`, run `gen:messages`, switch the app to `en-XA` and see the accented copy. Ninety seconds.

**Edge cases**

* Copy with interpolation (`{count} invoices`): ICU placeholders preserved and validated.
* Same default text in two places: two ids; the extractor suggests sharing.
* Terminology term inside copy: nested `{term:customer}` resolved by PAP-126.
* Spec id renamed: ids change; migration note via PAP-114 codemod.
* Right-to-left locale: no layout work here; documented as PAP-27 scope.

**Dependencies**

Blocked by PAP-27, PAP-120. Soft: PAP-74, PAP-126, PAP-114.

**Agent**

Built by Quill (Page Spec Writer) with Nova on codegen; reviewed by Iris for truncation review.

**Size**

M
