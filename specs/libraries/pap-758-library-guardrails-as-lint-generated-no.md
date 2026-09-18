---
identifier: "PAP-758"
title: "Library guardrails as lint: generated `no-restricted-imports` from rejected and replaced registry entries plus `ban:` lines in usage notes, wired into Gate 1"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Registry live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-216", "PAP-757"]
blocks: []
key: "r4/libraries/library-guardrails-lint"
url: "https://linear.app/paperos/issue/PAP-758/library-guardrails-as-lint-generated-no-restricted-imports-from"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:39.191Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-758: Library guardrails as lint: generated `no-restricted-imports` from rejected and replaced registry entries plus `ban:` lines in usage notes, wired into Gate 1

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

The registry knows we rejected `moment` and replaced `@radix-ui/*` with the unified package; the lockfile check (PAP-216) catches the dependency, but not the import of a banned API from an allowed library, nor a transitive package imported directly. Turn registry status and the notes' `ban:` lines into lint rules so the guardrail fires in the editor and in Gate 1, with the reason and the replacement in the message.

**Scope**

In: generator `pnpm lib guardrails build` in `tools/libraries/guardrails.ts` writing `biome.generated.jsonc` (Biome `noRestrictedImports` with per-path messages) and, for patterns Biome cannot express (member bans like `lodash/cloneDeep` deep paths or `moment#format`), an ESLint flat-config fragment `eslint.guardrails.generated.js` run only on changed files in Gate 1; sources: registry entries with status `rejected|replaced|deprecated` (message from `reasons` and `replacedBy`), `ban:` lines from usage notes, and the PAP-305 boundary map's cross-module bans re-exported for one message format; drift check `pnpm lib guardrails --check`; `docs/libraries/guardrails.md`. Out: the boundary lint itself (PAP-305, PAP-439), formatting.

**Spec**

* Message format: `<pkg> is <status> in the registry: <reason>. Use <replacedBy> (docs/libraries/notes/<id>.md).`; every message links a note or an ADR.
* Direct import of a transitive dependency not in the package's own `package.json` is banned (`no-extraneous-dependencies` equivalent) with the hint to `pnpm add` it and register it.
* Waivers: `// paperos-allow: <pkg> <PAP-n>` on the import line, counted and listed in the weekly re-audit (PAP-306); expired ADR waivers (PAP-211 style) fail.
* Generation is deterministic and runs in `pnpm lib registry build`; Gate 1 fails when the generated config is stale.
* Performance: Biome part costs nothing extra; the ESLint fragment runs on the PR's changed files only, under 20 s.

**Interface contract**

Provides: generated Biome and ESLint fragments, `pnpm lib guardrails build|--check`, waiver grammar, docs. Consumes: registry statuses and `replacedBy` (PAP-216), `ban:` lines (PAP-757), boundary rules (PAP-305, soft), Gate 1 lint step (PAP-78). Consumed by: Gate 1, PAP-306 re-audit (waiver count), PAP-217 (a replaced package's upgrade PR is closed with the guardrail message), PAP-218 (new rejections become rules on merge).

**Definition of done**

* Seeded import of a `rejected` package fails Gate 1 with the registry message; a `ban:` member import fails; a waiver with an ADR passes; generated config drift is red.
* `docs/libraries/guardrails.md`; CHANGELOG entry; Linear comment with the red run screenshot.

**Test plan**

* Unit: rule generation from fixture registry and notes, message format, waiver parsing and expiry.
* Integration: Biome and ESLint runs on a fixture package with violations; changed-files filter.
* E2E: none.

**Demo**

Mark `moment` as `rejected` with `replacedBy: date-fns` in a fixture registry, run `pnpm lib guardrails build`, import `moment` in a file and read the Biome message pointing at the note. Under one minute.

**Edge cases**

* Library replaced but still used in 40 files: rules generated as warnings for 14 days (registry `deprecated` window), then errors.
* Type-only import of a banned package: still banned (R8 spirit).
* Spikes importing rejected libraries on purpose: `spikes/**` excluded.

**Dependencies**

Hard: PAP-216, PAP-757. Soft: PAP-305, PAP-78, PAP-306, PAP-217.

**Agent**

Builder: Scout (Library Evaluator). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/libraries/library-usage-notes` = PAP-757.
