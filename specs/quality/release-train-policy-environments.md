---
identifier: "PAP-252"
title: "Release train policy document and environments config"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Spec"
priority: 1
surfaces: ["Developer", "Agent"]
milestone: "Edge-case hunting and release trains"
state: "Backlog"
parent: "PAP-88"
children: []
blockedBy: ["PAP-94"]
blocks: ["PAP-253", "PAP-254"]
key: "quality/release-train/policy-environments"
url: "https://linear.app/paperos/issue/PAP-252/release-train-policy-document-and-environments-config"
source: "Linear snapshot 2026-09-17T06:03Z (round-2 issue)"
---

# PAP-252: Release train policy document and environments config

**Goal**

Write the rules before the automation: branches, cadence, freeze and hotfix rules, environments, rollback, and who decides what, as a document plus a machine-readable environments file the workflows read.

**Scope**

* In: `docs/quality/release-train.md`, ADR `docs/adr/0008-release-train.md`, `ops/release/environments.yaml` with schema, release record schema `ops/release/records/<version>.json`, RC Linear issue template text, links from CLAUDE.md and the PR template.
* Out: workflows (siblings).

**Spec**

* Policy: `main` always releasable; `release/<yyyy-ww>` cut Monday 08:00 UTC; RC freeze accepts only PRs labelled `rc-fix`; hotfix branches from the last tag with label `hotfix`; rollback procedure with snapshot restore rules; environments preview, staging, production; roles: Atlas merges, Sentinel certifies, Justin approves releases only; feature flags default off for risky work (PAP-17 `Flags`, runtime flags later).
* Queue rule: never more than one open RC issue; skip the cut and comment if last week's is open.
* `environments.yaml`: `[{ name, url, coolifyWebhookSecretName, database, allowedBranches, testMode: false }]` validated by Zod in `packages/contracts`.
* Release record: `{ version, sha, date, gates, digestUrl, approver, deployedAt, rollbackTarget, snapshotId }`.
* Approval grammar: uses PAP-94's `/approve` and `/reject <reason>` comment commands exactly; this document references, not redefines, them.

**Interface contract**

* Provides: `environments.yaml` schema and file, `ReleaseRecord` type, policy rules cited by `certify.ts`, RC issue template.
* Requires: PAP-94 command grammar, PAP-46 branch conventions, PAP-52 tag format.

**Definition of done**

* Policy and ADR merged, linked from CLAUDE.md and PAP-49's template.
* `environments.yaml` validates; staging and production entries filled with secret names (not values).
* Atlas, Forge and Justin each confirm their role in a comment.

**Test plan**

* Unit: schema validation of the YAML and a sample record.
* Review: Quill edits for clarity; Sentinel checks every rule has an enforcing step in a sibling.

**Demo**

Open `docs/quality/release-train.md`, read the one-page calendar table (Monday cut, nightly staging, approval window), then `pnpm release:env --validate`. Under one minute.

**Edge cases**

* Two RCs needed in a week (urgent feature): policy says hotfix path or wait; documented.
* Production and staging share a database by mistake: schema forbids duplicate `database` values.

**Dependencies**

PAP-94 (hard for the grammar). Soft: PAP-46, PAP-52. Blocks the two sibling children.

**Agent**

Written by Sentinel with Atlas. Reviewed by Forge and Justin (roles).

**Size**

S.
