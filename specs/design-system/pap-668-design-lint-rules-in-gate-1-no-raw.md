---
identifier: "PAP-668"
title: "Design lint rules in Gate 1: no raw colours, no arbitrary spacing, tokens-only utilities, registered icons only, motion and focus rules, with autofix and an allowlist"
project: "design-system"
projectName: "Design System"
phase: "P1"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Component library covers app shell needs"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-66", "PAP-68", "PAP-78"]
blocks: ["PAP-76", "PAP-244"]
key: "r4/design-system/design-lint-rules"
url: "https://linear.app/paperos/issue/PAP-668/design-lint-rules-in-gate-1-no-raw-colours-no-arbitrary-spacing-tokens"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:28.170Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-25"
cycle: null
---

# PAP-668: Design lint rules in Gate 1: no raw colours, no arbitrary spacing, tokens-only utilities, registered icons only, motion and focus rules, with autofix and an allowlist

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

Twenty parallel agent sessions will each pick a slightly different blue unless the build refuses. PAP-66 lints token files and PAP-72 bans `transition: all`, but nothing checks application code. Add the design lint rules that keep generated pages on tokens and registered parts, wired into Gate 1 and readable by the spec-conformance reviewer.

**Scope**

In: `ops/lint/design/` as a Biome plugin (GritQL) or ESLint flat-config package if Biome cannot express a rule; rules `no-raw-color`, `no-arbitrary-spacing`, `no-unregistered-icon`, `no-raw-typography`, `prefer-ui-component` (raw `<button>`, `<input>`, `<table>` in `apps/**` and `packages/**` outside `packages/ui`), `no-inline-style-color`, `no-transition-all` (moves here from PAP-72), `no-raw-control-height` (literal control heights outside `packages/ui`, see density modes); autofix where deterministic; `design-lint.allow.json` with expiry; Gate 1 job.

Out: a11y linting (PAP-73 axe and `eslint-plugin-jsx-a11y` via PAP-78), spec validation (PAP-115), vision checks (PAP-84).

**Spec**

* `no-raw-color`: flags hex, `rgb()`, `hsl()`, `oklch()` literals and Tailwind palette utilities (`bg-red-500`) in TSX, CSS and Tailwind `@apply`; allowed: `var(--pos-*)`, token utilities from PAP-66's `@theme`; autofix maps the nearest token by OKLCH distance when within ΔE 5, else reports.
* `no-arbitrary-spacing`: flags `p-[13px]`, `mt-[7px]`, raw `px` in `style` for spacing properties; allowed values from the 4 px scale; `no-raw-typography`: flags `text-[..]`, `font-[..]` and raw `font-size` outside `packages/ui`, pointing at `Text` and `Heading`.
* `no-unregistered-icon`: any `<Icon name="..." />` or `icon:` in specs must exist in PAP-68's `icon-names.json`; `prefer-ui-component`: raw interactive elements suggest the `ui.*` equivalent with a fixable import when props map one to one.
* Allowlist entries `{ rule, path, reason, expires }` fail the build when expired; the report `design-lint.json` follows the PAP-239 artefact shape so PAP-244 (spec-conformance reviewer) can cite rule ids, which are also listed in PAP-76's `rules.json` as `checkable: 'lint'`.
* Runs on changed files in Gate 1 under 30 s; `pnpm lint:design --fix` locally; rules documented with Do and Don't in `docs/design/lint.md`.

**Interface contract**

Provides: lint package `@paperos/design-lint`, rule ids `DS-LINT-*`, `design-lint.json` artefact, allowlist schema, Gate 1 job `design-lint`. Consumes: token names and `@theme` (PAP-66), `icon-names.json` (PAP-68), Gate 1 job slot and Biome config (PAP-78), artefact schema (PAP-239, soft), `rules.json` ids (PAP-76, soft). Consumed by PAP-244 reviewer prompts, PAP-76 (checkable rules), every builder session.

**Definition of done**

* Eight rules with tests (passing and failing fixtures each); autofix proven on a seeded raw-colour commit; Gate 1 job green on the template and failing on the seed.
* `docs/design/lint.md`; changelog; Linear comment on PAP-244 and PAP-76 with the rule id list.

**Test plan**

* Unit: each rule's positive and negative fixtures; token nearest-match autofix; allowlist expiry; artefact schema validity.
* CI: job runtime under 30 s on a 200-file diff; seeded violation fails the PR (reverted commit as proof).
* E2E: none.

**Demo**

Reviewer adds `className="bg-[#ff0000] p-[13px]"` to a page, runs `pnpm lint:design` and reads two findings with token suggestions, then `--fix` replaces the colour. Under one minute.

**Edge cases**

* Colour inside an SVG illustration file: `illustrations/**` allowlisted by path.
* Third-party component class names: only PaperOS packages and apps are scanned.
* Dynamic class strings (`clsx(cond && 'bg-...')`): scanned as string literals; template expressions reported at low confidence.
* Tokens renamed: rule reads the generated `tokens.ts`, no hard-coded list.

**Dependencies**

PAP-66 (hard), PAP-68 (hard, icon names), PAP-78 (hard, Gate 1). Soft: PAP-239, PAP-76. Blocks PAP-244's rule citations and PAP-76's `checkable: lint` entries.

**Agent**

Builder: Iris (Token Keeper) with Sentinel (Code Reviewer). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.
