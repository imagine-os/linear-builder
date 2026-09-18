---
identifier: "PAP-740"
title: "Page spec v1.1 sections: `flags`, `modules`, `comments`, `help`, `seo`, `budgets` with codemod stub, JSON Schema and validator rules"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Spec"
priority: 2
surfaces: ["Developer"]
milestone: "Spec schema and validator"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-114"]
blocks: ["PAP-361", "PAP-380", "PAP-744", "PAP-745", "PAP-746", "PAP-752"]
key: "r4/spec-builder/schema-v1-1-extensions"
url: "https://linear.app/paperos/issue/PAP-740/page-spec-v11-sections-flags-modules-comments-help-seo-budgets-with"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:34.636Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-24"
cycle: null
---

# PAP-740: Page spec v1.1 sections: `flags`, `modules`, `comments`, `help`, `seo`, `budgets` with codemod stub, JSON Schema and validator rules

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Spec M

**Goal**

Four live issues write keys PAP-114 v1 rejects: PAP-380 (`help.docs`, `help.tour`), PAP-361 (`comments.anchor`), PAP-366 (`flags:` guard), PAP-467 (`flags`, `modules` in the contract). Add them as one additive schema revision with an ADR, so the unknown-key rule keeps protecting specs and no consumer invents `x-` keys that later diverge.

**Scope**

In: `packages/spec/src/schema/{flags,modules,comments,help,seo,budgets}.ts` merged into `PageSpecSchema` as optional sections; `specVersion` stays 1 (additive; contract patch `0.1.x` per module-system §2.1); `SPEC_VERSIONS` entry `1.1` in the PAP-114 `migrate/` skeleton with an identity codemod and `x-help` to `help` rename codemod; validator rules; `docs/spec/page-spec.md` regenerated; ADR. Out: compiling the sections (three follow-up Build issues), the versioning toolchain (PAP-751).

**Spec**

* `flags: { require?: FlagId[], any?: FlagId[], fallback?: RouteRef | 'denied' }`: page renders only when flags hold (PAP-366); `modules: { require: ModuleId[] }` cross-checked against the PAP-264 registry (`MODULE_UNKNOWN`, `MODULE_DISABLED` reuse PAP-265's rule ids).
* `comments: { anchor: 'entity' | 'element' | 'none', entity?: EntityId, allowCustomers?: boolean }` matching PAP-131's grammar; default `element`.
* `help: { docs: DocPath[], tour: [{ target: specKey, title: MessageRef, body: MessageRef }] (max 7), shortcuts?: CommandId[] }` as PAP-380 needs; `HELP_DOC_MISSING`, `HELP_TOUR_TARGET` (target must be a `components[].key`).
* `seo: { title?, description?, ogImage?, canonical?, noindex?: boolean }` allowed only when `layout.template: public` (`SEO_NON_PUBLIC` warn); `budgets: { lcpMs?, inpMs?, bundleKb?, apiP95Ms? }` with app defaults in PAP-117 `defaults.budgets`.
* `MessageRef` reuses PAP-375's `string | { id, default }`; unknown keys inside the new sections error like top-level ones; `x-help` still passes through but the codemod rewrites it and the validator warns `SPEC_XKEY_PROMOTED`.

**Interface contract**

Provides: six section schemas and types, `PageSpec` v1.1 type, codemods `x-help-to-help`, rule ids above, regenerated JSON Schema. Consumers: PAP-380 (`help`), PAP-361 (`comments`), PAP-366 and PAP-744 (`flags`, `modules`), PAP-745 (`seo`), PAP-746 (`budgets`), PAP-124 form panels, PAP-467 contract (patch bump), PAP-123 (`flags` on nodes). Requires: PAP-114 (hard), PAP-264 module ids, PAP-366 flag ids, PAP-375 `MessageRef` (soft; local alias until merged).

**Definition of done**

* Schema merged; PAP-125 examples gain at least `comments` and `help`; JSON Schema snapshot and drift check green; VS Code completion screenshot for `help.tour`.
* Codemod rewrites an `x-help` fixture; identity for specs without new sections; every rule pass and fail.
* ADR accepted (PAP-130); `@paperos/contract-spec-builder` bumped to `0.1.1` with a comment on PAP-467; comments on PAP-380 and PAP-361; CHANGELOG entry.

**Test plan**

* Unit: section fixtures valid and invalid; rule codes with line and col; codemod output snapshot; `specVersion` unchanged.
* Property: `parseSpec(stringify(spec))` still round-trips with the new sections.
* Integration: PAP-115 CLI on the template with the examples updated; no UI.

**Demo**

Add `help: { docs: ['spec/workflow'], tour: [{ target: invoiceTable, title: 'Your invoices', body: '...' }] }` to the invoices example, validate, then point `target` at a missing key and read `HELP_TOUR_TARGET`. Under one minute.

**Edge cases**

* Flag id removed from `flags.yaml`: `FLAG_UNKNOWN` error names the page and the flag.
* `comments.anchor: entity` on a page without `data.entities`: error.
* `seo` on an `app` template page: warning, ignored by codegen.
* Spec with both `x-help` and `help`: error, codemod refuses.

**Dependencies**

Hard: PAP-114. Soft: PAP-264, PAP-366, PAP-375, PAP-130, PAP-467. Blocks PAP-380 (help fields), PAP-361 (`comments`), the three compile issues.

**Agent**

Builder: Quill (Page Spec Writer). Reviewer: Sentinel (Code Reviewer) with Atlas approving the schema change.

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 4 round-4 file keys in this description to Linear identifiers: `r4/spec-builder/flags-modules-compile` = PAP-744, `r4/spec-builder/page-budgets` = PAP-746, `r4/spec-builder/seo-public-metadata` = PAP-745, `r4/spec-builder/spec-versioning-tooling` = PAP-751.
