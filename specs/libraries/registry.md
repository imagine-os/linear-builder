---
identifier: "PAP-216"
title: "Build the library registry in the docs system: adopted, trialing, rejected with reasons and owners"
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
blockedBy: ["PAP-128", "PAP-209", "PAP-211"]
blocks: ["PAP-218"]
key: "libraries/registry"
url: "https://linear.app/paperos/issue/PAP-216/build-the-library-registry-in-the-docs-system-adopted-trialing"
source: "plan/specs/bucket-8.json (round-1 canonical spec JSON)"
---

# PAP-216: Build the library registry in the docs system: adopted, trialing, rejected with reasons and owners

**Goal**

Give PaperOS one place that says what third-party code we use, why, who owns it and where the decision lives: a file-based registry rendered in-app through the docs engine, with a drift check so a dependency cannot appear in a lockfile without a registry entry and a rejected library cannot creep back in. This is the memory the Scout routine, Renovate summaries and every research ADR write into.

**Scope**

In:
- Registry entries `docs/registry/entries/<id>.yaml`, Zod 4 schema `packages/spec/src/libraries/registry.ts`, generated `docs/.generated/registry.json`.
- CLI `pnpm lib add <npm-name|crate:<name>|image:<ref>> --status trialing --owner scout --adr 0012 --category ui` scaffolding an entry with facts from `scripts/lib-facts.ts` (`libraries/eval-rubric`); `pnpm lib registry build`; `pnpm lib registry check`.
- In-app page `/_app/docs/registry` rendered by `collab/docs-engine` (MDX page plus a small React table component) with filters by status, category and owner, status badges, ADR and scorecard links, and a "review due" indicator.
- Drift check job in Gate 1 (`quality/ci-gate1` `generated-drift` pattern).
- Seed: every current production dependency of paperos-template imported with `status: adopted` and `adr: pending` where no ADR exists, plus one Linear issue listing the pending ADRs for Atlas to triage.

Out: the ADR system itself (`collab/decision-log`), dependency upgrades (`libraries/upgrade-bot`), scanning for new candidates (`libraries/scout-agent`), rendering with the views engine (a plain table is enough; swap to `tables/grid-view` later).

**Spec**

- Entry schema: `{ id, name, source: { kind: npm|crate|image|service, ref }, version (derived from lockfile at build, not hand-edited), status: candidate|trialing|adopted|reference|deprecated|replaced|rejected, category (ui|data|canvas|editor|charts|maps|auth|db|sync|realtime|jobs|email|pdf|storage|search|observability|testing|build|agent-tooling|product), owner (character id), adr (NNNN or `pending`), scorecard (path), license (SPDX, verified by `libraries/license-policy`), context: bundled|server|dev|service, usedBy: [package names], alternativesConsidered: [ids], reasons, addedAt, reviewAt, replacedBy?, notes }`.
- Build: reads `pnpm-lock.yaml` and `Cargo.lock` to fill `version` and `usedBy`; resolves `adr` against `docs/.generated/adr-index.json` from `collab/decision-log` and fails on a dangling id; writes `registry.json` `{ generatedAt, entries[], stats: { byStatus, byCategory } }`.
- Check rules: every production dependency of any non-private package has an entry with status `adopted` or `trialing` (error); entry with status `rejected`, `replaced` or `deprecated` present in a lockfile (error); entry with no `usedBy` and status `adopted` (warning, "unused"); `reviewAt` in the past (warning); trivial helpers allowlisted in `docs/registry/trivial.yaml` (for example `clsx`, `tslib`) need no entry.
- In-app table: sortable columns id, status, category, owner, version, license, ADR; row expands to reasons, alternatives, usedBy; responsive at 375 as stacked cards; axe clean; dark theme via tokens.
- Status transitions documented: `candidate` (Scout scan) -> `trialing` (spike or ADR proposed) -> `adopted` (ADR accepted) or `rejected`; `adopted` -> `deprecated` -> `replaced` with `replacedBy`. The CLI enforces allowed transitions and requires an ADR for `adopted`.
- `docs/registry/README.md`: how to add, review cadence (every entry gets `reviewAt` = addedAt + 180 days), and what each status means.

**Definition of done**

- Schema, CLI, build and check merged; Vitest covers schema, lockfile parsing for pnpm and Cargo, ADR resolution, every check rule with fixtures, and status transitions.
- Seed entries for all current production dependencies committed; check passes on `main`; the pending-ADR Linear issue exists.
- Drift check runs in Gate 1 and a seeded unregistered dependency fails it (screenshot of the red status).
- In-app page screenshots at 375, 1024 and 1920 in light and dark; axe clean; Playwright test filters by status and opens an entry.
- README and `docs/libraries/registry.md` written; CHANGELOG entry; Linear comment with page link and screenshots.
- Research issues' ADR outputs (`libraries/*-landscape`, `libraries/oss-products`) have entries, added by this issue if their drafts exist.

**Edge cases**

- Same library used in `bundled` and `dev` contexts: one entry, `context` becomes an array, strictest license rule applies.
- Dependency renamed or scoped (`radix-ui` unified package replacing `@radix-ui/*`): `aliases[]` on the entry so check passes during migration.
- Lockfile has multiple versions of one package: `version` lists all; warning if more than two.
- Entry references an ADR still `proposed`: allowed for `trialing`, error for `adopted`.
- `adr-index.json` missing because decision-log has not merged: build warns and skips ADR resolution, does not fail.
- Cargo.lock absent before Tauri lands: Rust checks skipped with a notice.

**Dependencies**

`libraries/eval-rubric` (hard: facts collector and scorecard paths), `collab/docs-engine` (hard: in-app rendering). Soft: `collab/decision-log` (ADR index), `quality/ci-gate1` (job slot), `libraries/license-policy` (license field verification). Consumed by `libraries/upgrade-bot`, `libraries/scout-agent`, `quality/review-rubrics` (third-party findings pointer).

**Agent**

Built by Scout (Library Evaluator) with Quill for the docs page conventions. Reviewed by Sentinel (Code Reviewer, Visual Inspector) and Atlas.

**Size**

M: small schema and page, but lockfile parsing, check rules and seeding touch every package.
