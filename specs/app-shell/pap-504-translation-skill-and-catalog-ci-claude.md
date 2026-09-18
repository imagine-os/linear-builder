---
identifier: "PAP-504"
title: "Translation skill and catalog CI: `.claude/skills/translate` producing locale PRs, fuzzy-entry thresholds, missing-string report and the `en-XA` pseudo-locale column in Gate 3"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Desktop and mobile shells build"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-13", "PAP-27", "PAP-66", "PAP-105", "PAP-302"]
blocks: ["PAP-126", "PAP-375", "PAP-688", "PAP-738"]
key: "r4/app-shell/i18n-translate-skill"
url: "https://linear.app/paperos/issue/PAP-504/translation-skill-and-catalog-ci-claudeskillstranslate-producing"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:49:43.526Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-24"
cycle: null
---

# PAP-504: Translation skill and catalog CI: `.claude/skills/translate` producing locale PRs, fuzzy-entry thresholds, missing-string report and the `en-XA` pseudo-locale column in Gate 3

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-27 builds `@paperos/i18n` and the catalogs; the agent workflow that keeps catalogs full is a separate half-session that Quill owns. Without it, every new string ships English-only and the RTL and pseudo-locale promises decay.

**Scope**

In:

* `.claude/skills/translate/SKILL.md` in the PAP-105 format: inputs (locale, catalog path), steps (extract, diff against `en`, translate missing and fuzzy entries with glossary constraints, compile, run the format-helper tests, open a PR with the PAP-49 template), forbidden actions (never edit source strings).
* Glossary `apps/web/src/locales/glossary.yaml` (terms that stay untranslated or have fixed translations: product names, `PAP-n`, currency codes) enforced by a lint on catalog PRs.
* CI `i18n-check` step in Gate 1: `pnpm i18n:extract --check` (no unextracted literals), fuzzy ratio warn above 2 percent and fail above 10 percent for enabled locales, `missing-strings.json` artefact per locale.
* Gate 3 pseudo-locale column: register `en-XA` as a Playwright project variant in `ops/ci/breakpoints.json` consumers (PAP-246) at 375 and 1280.

Out: the i18n package, negotiation and helpers (PAP-27), spec-string extraction (PAP-375), tenant content translation.

**Spec**

* The skill runs as Quill with `repo:write specs/ docs/ apps/web/src/locales` only; PRs carry `Character: Quill` and the `i18n` label.
* Translations of plural forms are validated by compiling the catalog and asserting every CLDR category for the locale is present.
* A catalog PR that changes an `en` msgid is rejected by the lint (source strings live in code).
* Machine-translation is the agent itself; no external MT API in this build (PAP-27 out-of-scope stays).

**Interface contract**

Provides: skill `translate`, glossary schema, Gate 1 step `i18n-check`, `missing-strings.json`, the `en-XA` Gate 3 variant; consumed by PAP-27 (DoD "translation skill produces an `es` PR"), PAP-375 (reuses extraction), PAP-82/PAP-246 (variant), PAP-108 (skills library index).

Consumes: skill format (PAP-105), Gate 1 workflow (PAP-78), catalogs and scripts from PAP-27, PR template (PAP-49), Playwright matrix (PAP-246, soft).

**Definition of done**

* Skill run produces an `es` PR that compiles and passes `i18n-check`; Quill merges it (link).
* Seeded unextracted literal fails Gate 1; fuzzy thresholds tested with fixture catalogs.
* `en-XA` screenshots at 375 and 1280 in the Gate 3 contact sheet; `docs/platform/i18n.md` skill section; CHANGELOG; Linear comment.

**Test plan**

* Unit: glossary lint on a fixture PR that translates a product name; plural completeness for `ar` and `pl`; fuzzy ratio arithmetic.
* E2E: skill dry run against the fixture app produces the expected PR body and file list.

**Demo**

Reviewer adds a new `t\`Export\``call to a page, runs`pnpm i18n:extract`, invokes the skill for `es\` and opens the resulting PR with the translated entry and the glossary check green. Under 2 minutes.

**Edge cases**

* Locale with no catalog yet: skill creates it from `en` with all entries fuzzy and the PR is draft.
* String with ICU select on gender: the skill keeps every branch or the compile fails.
* Concurrent catalog PRs: `.po` merge conflicts resolved by re-running extract, documented in the skill.

**Dependencies**

Hard: PAP-105 (skill format). Sibling: the package half of PAP-27. Soft: PAP-78 (the `i18n-check` step runs inside `pnpm check` until Gate 1 lands), PAP-49, PAP-246, PAP-375.

**Agent**

Builder: Quill (Page Spec Writer) with Forge on the CI step. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* de-parented from PAP-27 (FIX-R4-1: this issue is an add-on to its former parent's core scope, which is a claimable leaf again). PAP-27 blocks this issue (`blocks` relation).
