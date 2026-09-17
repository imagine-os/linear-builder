---
identifier: "PAP-88"
title: "Define the release train: nightly staging deploy, weekly release candidate to Needs Justin with consolidated review report"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Spec"
priority: 1
surfaces: ["Developer", "Agent"]
milestone: "Edge-case hunting and release trains"
state: "Backlog"
parent: null
children: ["PAP-252", "PAP-253", "PAP-254"]
blockedBy: ["PAP-242", "PAP-244", "PAP-245", "PAP-248", "PAP-26", "PAP-81", "PAP-82", "PAP-94"]
blocks: ["PAP-89"]
key: "quality/release-train"
url: "https://linear.app/paperos/issue/PAP-88/define-the-release-train-nightly-staging-deploy-weekly-release"
source: "plan/specs/bucket-2.json (round-1 canonical spec JSON)"
---

# PAP-88: Define the release train: nightly staging deploy, weekly release candidate to Needs Justin with consolidated review report

**Goal**

Define and automate the cadence that keeps Justin out of pull requests: every merge to `main` deploys to staging nightly, every Monday a release candidate is cut from `main`, all gate evidence is consolidated, and a single Linear issue in Needs Justin asks for one approve or reject decision that promotes the candidate to production and tags a release.

**Scope**

In:
- Written policy `docs/quality/release-train.md`: branches (`main` always releasable, `release/<yyyy-ww>` cut Monday 08:00 UTC), what may be merged when (freeze rules for the RC branch: fixes only, labelled `rc-fix`), hotfix path, rollback procedure, environments (preview per PR, staging, production), and who decides what (Atlas merges, Sentinel certifies, Justin approves releases only).
- Workflow `.github/workflows/staging-nightly.yml`: 02:00 UTC build and deploy `main` to staging through the Coolify deploy webhook, run `@full` e2e (`quality/e2e-flows`), full visual matrix, edge-case library, perf; write `reports/nightly-<date>.json`.
- Workflow `.github/workflows/release-candidate.yml`: Monday cut creates `release/<yyyy-ww>`, opens a release PR labelled `release-candidate` (feeds `forge/release-tags` prerelease `-rc.N`), deploys it to staging, runs all gates, then calls `quality/review-report` to generate the digest and creates the Needs Justin Linear issue with the digest link, approve and reject instructions per `pm-linear/justin-queue`.
- Promotion: a comment `/approve` or state change to Done on that Linear issue (via `pm-linear/webhooks`) triggers `promote.yml`: merge release PR, `forge/release-tags` tags `vX.Y.Z`, deploy production via Coolify, post release notes from `collab/changelog`; `/reject <reason>` reopens fixes with a Linear comment and keeps the RC branch.
- Certification checklist `ops/release/certify.ts` verifying all statuses `gate/*` green on the RC head, no open S0/S1 findings, no expired waivers, migrations reversible flag from `data-layer/drizzle-schema`, backups fresh (`data-layer/postgres-provision`).
- Queue rule enforcement: never more than one open RC issue; if last week's is still open, the new cut is skipped and a comment notes it (keeps Needs Justin under five items).

Out: the digest content itself (`quality/review-report`), changelog generation, Tauri release packaging (`forge/release-tags`).

**Spec**

- Environment config in `ops/release/environments.yaml`: `{ name, url, coolifyWebhookSecretName, database, allowedBranches }`.
- Coolify deploy via `POST /api/v1/deploy?uuid=...` with bearer token secret; wait for deployment status API to report `finished`; smoke `GET /healthz` and `/__version` equals the SHA.
- Migrations run in the deploy job before app rollout, with `drizzle-kit migrate`; a `pre-deploy-backup` step calls the backup script and records the snapshot id in the release record.
- Release record `ops/release/records/<version>.json`: SHA, date, gates summary, digest link, approver, deployed-at, rollback target; committed by the bot.
- Rollback: `pnpm release:rollback <version>` redeploys the previous image tag and, if flagged, restores the pre-deploy snapshot (with confirmation). Documented drill in the policy.
- Linear issue template for the RC: title `Release candidate <yyyy-ww> (vX.Y.Z-rc.N)`, body with digest link, gate table, one-line ask, and the two commands.
- Feature flags for risky work land behind `packages/core/src/flags` defaults off, so RCs are always shippable (policy).

**Definition of done**

- Policy doc merged and linked from CLAUDE.md and the PR template.
- Nightly staging deploy ran three nights in a row with reports (links).
- A rehearsal RC cut end to end: branch, PR, gates, digest, Needs Justin issue created, `/approve` in a test tenant of Linear promotes to a staging-as-production target and tags `v0.1.0-rc.1` (links, screenshots of the Linear issue).
- `/reject` path tested and documented.
- `certify.ts` blocks promotion when a gate status is missing (seeded test).
- CHANGELOG entry; Linear comment with rehearsal links; ADR `docs/adr/0008-release-train.md`.

**Edge cases**

- `main` red on Monday: RC not cut; Linear comment on the previous RC issue explains; Atlas gets a task to fix.
- Hotfix needed mid-week: branch from the last tag, PR labelled `hotfix`, gates run, Justin approval via a short Needs Justin issue, cherry-pick back to `main`.
- Justin approves but production deploy fails: auto-rollback, issue reopened with logs, status stays Needs Justin.
- Two approvals within seconds (duplicate webhook): idempotency key on the release record prevents double deploy.
- Database migration irreversible: certification requires a Justin acknowledgement checkbox in the digest.
- Coolify API down: promotion job retries for 30 minutes then fails loudly with manual steps documented.

**Dependencies**

`quality/review-agents` and `quality/playwright-matrix` (hard: gates to consolidate). Soft: `quality/e2e-flows`, `quality/edge-case-hunter`, `quality/perf-budgets`, `forge/release-tags`, `pm-linear/justin-queue`, `pm-linear/webhooks`, `collab/changelog`, `data-layer/postgres-provision`. Consumed by `quality/review-report`, `forge/release-tags`, `agents/handoffs`.

**Agent**

Written and built by Sentinel with Atlas (Merger sub-agent) owning promotion and Forge (Ops Runner) the Coolify deploys. Reviewed by Atlas and Forge; Justin confirms the approval mechanics via the rehearsal.

**Size**

L: three workflows, deploy integration, certification logic and a rehearsal that touches Linear, Coolify and the forge.
