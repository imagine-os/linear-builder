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
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T05:21:25.145Z"
---

# PAP-216: Build the library registry in the docs system: adopted, trialing, rejected with reasons and owners

**Goal**

Give PaperOS one place that says what third-party code we use, why, who owns it and where the decision lives: a file-based registry rendered in-app through the docs engine, with a drift check so no dependency appears in a lockfile without an entry and no rejected library creeps back. This is the memory PAP-218, PAP-217 and every research ADR write into.

**Scope**

In:

* Entries `docs/registry/entries/<id>.yaml`, Zod 4 schema `packages/spec/src/libraries/registry.ts`, generated `docs/.generated/registry.json`.
* CLI `pnpm lib add <npm|crate:|image:> --status --owner --adr --category` scaffolding with facts from PAP-209's collector; `pnpm lib registry build|check`.
* Page `/_app/docs/registry` via PAP-128 (MDX plus a small React table): filters by status, category, owner; badges; ADR and scorecard links; "review due".
* Drift check job in Gate 1 (`generated-drift` pattern, PAP-78).
* Seed: every current production dependency as `adopted` with `adr: pending`, plus one Linear issue listing pending ADRs for Atlas.

Out: the ADR system (PAP-130), upgrades (PAP-217), scanning (PAP-218), rendering with the views engine (plain table; swap to PAP-165 later).

**Spec**

* Entry `{ id, name, source: { kind: npm|crate|image|service, ref }, version (from lockfile), status: candidate|trialing|adopted|reference|deprecated|replaced|rejected, category, owner, adr, scorecard, license (verified against PAP-211), context: bundled|server|dev|service (array allowed), usedBy[], alternativesConsidered[], reasons, addedAt, reviewAt, replacedBy?, aliases[], notes }`.
* Build reads `pnpm-lock.yaml` and `Cargo.lock` for `version` and `usedBy`; resolves `adr` against PAP-130's `adr-index.json`, failing on a dangling id, warning and skipping when the index is absent.
* Check rules: production dependency without `adopted` or `trialing` entry (error); `rejected|replaced|deprecated` present in a lockfile (error); `adopted` with no `usedBy` (warning); `reviewAt` past (warning); trivial helpers allowlisted in `docs/registry/trivial.yaml`.
* Transitions enforced by the CLI: `candidate` -> `trialing` -> `adopted` (needs accepted ADR) or `rejected`; `adopted` -> `deprecated` -> `replaced` with `replacedBy`.
* `reviewAt` defaults to `addedAt` plus 180 days; README documents statuses and cadence.

**Interface contract**

Provides: `RegistryEntrySchema`, `registry.json` `{ generatedAt, entries[], stats: { byStatus, byCategory } }`, CLI commands above, page route, Gate 1 job `registry-drift`, `trivial.yaml`. Consumes: PAP-209 `lib-facts` and scorecard paths, PAP-128 rendering, PAP-130 `adr-index.json` (soft), PAP-78 job slot, PAP-211 `policy.yaml` for license verification. Consumers: PAP-217 (`registry build` post-merge), PAP-218 (`lib add --status candidate`), PAP-79 third-party findings pointer, PAP-212 to PAP-215 entries.

**Definition of done**

* Schema, CLI, build and check merged; seed entries for all production dependencies committed; check passes on `main`; pending-ADR Linear issue exists.
* Drift check runs in Gate 1; a seeded unregistered dependency fails it (screenshot of the red status).
* Page screenshots at 375, 1024 and 1920 in light and dark; axe clean.
* `docs/registry/README.md` and `docs/libraries/registry.md`; CHANGELOG; Linear comment with page link.
* Entries exist for the ADR outputs of PAP-212 to PAP-215 where drafts exist.

**Test plan**

* Vitest: schema, pnpm and Cargo lockfile parsing fixtures, ADR resolution with and without index, every check rule with fixtures, transition enforcement, alias handling, multiple versions warning.
* CI: seeded violation branch fails `registry-drift`; clean `main` passes.
* Playwright: filter by status, open an entry, stacked cards at 375; visual baselines at 375, 1024, 1920 in both themes; axe.

**Demo**

Reviewer runs `pnpm lib add left-pad --status trialing --owner scout --category ui` and sees the scaffolded entry with facts filled, then `pnpm lib registry check` and opens `/_app/docs/registry` filtered to `trialing`. Under two minutes.

**Edge cases**

* Same library in `bundled` and `dev`: one entry, `context` array, strictest rule.
* Renamed or scoped package (`radix-ui` unifying `@radix-ui/*`): `aliases[]`.
* Multiple versions in lockfile: all listed; warning over two.
* `proposed` ADR: fine for `trialing`, error for `adopted`.
* `Cargo.lock` absent before Tauri: Rust checks skipped with notice.

**Dependencies**

PAP-209 and PAP-128 (hard). PAP-211 (license verification). Soft: PAP-130, PAP-78. Blocks PAP-218.

**Agent**

Built by Scout (Library Evaluator) with Quill for the docs page. Reviewed by Sentinel (Code Reviewer, Visual Inspector) and Atlas.

**Size**

M: small schema and page; lockfile parsing, check rules and seeding touch every package.
