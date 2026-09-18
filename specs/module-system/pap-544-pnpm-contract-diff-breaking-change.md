---
identifier: "PAP-544"
title: "`pnpm contract:diff` breaking-change detector: compare Zod schemas, port signatures, topics and slot props between the base branch and the PR, require the matching semver bump and a changeset"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P1"
type: "Infra"
priority: 1
surfaces: ["Developer"]
milestone: "Contracts and conformance wired"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-433", "PAP-440"]
blocks: []
key: "r4/module-system/contract-diff"
url: "https://linear.app/paperos/issue/PAP-544/pnpm-contractdiff-breaking-change-detector-compare-zod-schemas-port"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:51.162Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-27"
cycle: null
---

# PAP-544: `pnpm contract:diff` breaking-change detector: compare Zod schemas, port signatures, topics and slot props between the base branch and the PR, require the matching semver bump and a changeset

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Infra M

**Goal**

The semver table in `docs/module-system.md` §2.1 is a rule agents must apply by judgement; api-extractor, oasdiff and Terraform's schema diff exist because judgement fails under pressure. The compatibility matrix (PAP-440) reacts to version numbers; nothing checks that the version number matches the change. This detector closes the loop: a PR that narrows an output or renames a port cannot merge with a patch bump.

**Scope**

In:

* `tools/contract-diff/`: for every `packages/contracts/<id>` changed in the PR, build both the base and head packages, load exported Zod schemas (via `z.toJSONSchema`), port interfaces (via `ts-morph` signatures), `defineTopic` registrations and slot props, and classify each change with the §2.1 table: `additive-minor`, `breaking-major`, `patch-fix`, `none`.
* Version check: read `package.json` version and `provides.version` at base and head; fail `CONTRACT_BUMP_REQUIRED` when the classification demands a higher bump than applied; pre-1.0 mapping (minor is breaking) applied automatically.
* Changesets: `.changeset/*.md` required for any contract change (`@changesets/cli` in the workspace); the release PR (PAP-52) consumes them for contract packages; `contract:diff --write-changeset` drafts one from the classified changes.
* Report: Markdown table in the PR check summary (change, kind, consumers affected from `compat-matrix.json`, required bump, deprecation window start) and `contract-diff.json` artefact; Gate 1 step `contract-diff` (PAP-78).

Out: deciding the change (contract owners and ADRs), the matrix itself (PAP-440), runtime adapters (PAP-437, PAP-436).

**Spec**

* Classification rules are data in `tools/contract-diff/rules.yaml` with tests per row of §2.1: new optional field minor, widened input major, narrowed output major, new enum value consumed by a switch major, removal major, wrong-schema fix patch (requires `fix:` commit type and a fixture proving the old schema never accepted the documented value).
* Type-only changes count (a renamed exported type is breaking).
* Deprecations: an `@deprecated` tag added is minor; the report lists the removal-eligible date (30 days after the major flip) from `compat-windows.json`.
* Runtime under 60 s for the whole contracts directory; incremental by changed package.

**Interface contract**

Provides: `pnpm contract:diff`, `rules.yaml`, `CONTRACT_BUMP_REQUIRED`, changeset requirement, `contract-diff.json`, Gate 1 step; consumed by every contract issue and every future contract PR, PAP-440 (window start), PAP-442 (step 1 propose evidence), PAP-306 (drift), PAP-52 (changesets), PAP-24.

Consumes: manifest and contract layout (PAP-433), matrix and windows (PAP-440), Gate 1 (PAP-78), JSON Schema generation (PAP-433 `gen:schemas`), release tooling (PAP-52, soft).

**Definition of done**

* Fixture PRs: one per §2.1 row produce the expected classification and bump verdict; a narrowed output with a patch bump fails Gate 1 with the consumer list.
* Template contracts pass at v0.1.0 with `none`; `--write-changeset` drafts a valid file; `docs/platform/contracts.md` versioning section; CHANGELOG; Linear comment.

**Test plan**

* Unit: schema diff classifier over JSON Schema pairs; signature diff over `.d.ts` pairs; topic and slot diffs; bump arithmetic pre and post 1.0.
* E2E: Gate 1 on a fixture PR renaming `ViewQueryPort.query` to `run` fails; bumping to `0.2.0` with a changeset passes and the report lists tables' consumers.

**Demo**

Reviewer removes an optional field from `contract-sample`, opens a PR and reads the check summary: `breaking-major`, consumers `app-shell`, required `0.2.0`; bumps and adds the changeset and the check goes green. Two minutes.

**Edge cases**

* Contract change plus consumer bump in the same PR (allowed by §7 when the owner agrees): the report shows `ok` for updated consumers and `ahead` for the rest.
* Generated JSON Schema stale: the step runs `gen:schemas` first and fails on drift with the fix.
* Two contracts changed with a cycle between them: acyclicity failure comes from PAP-439; this tool reports both.

**Dependencies**

Hard: PAP-433, PAP-440. Soft: PAP-78, PAP-52, PAP-439. Feeds PAP-442, PAP-306.

**Agent**

Builder: Forge (Platform Engineer); Atlas reviews the rules. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.
