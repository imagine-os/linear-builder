---
identifier: "PAP-505"
title: "Per-PR preview environments: `preview.yml`, Coolify preview application lifecycle, seeded demo tenant, sticky PR comment with URLs and teardown within five minutes of close"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P0"
type: "Infra"
priority: 1
surfaces: ["Developer"]
milestone: "Desktop and mobile shells build"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-13", "PAP-25", "PAP-26", "PAP-30"]
blocks: ["PAP-29", "PAP-83", "PAP-86", "PAP-88", "PAP-253", "PAP-357", "PAP-358", "PAP-365", "PAP-500", "PAP-523", "PAP-524", "PAP-675"]
key: "r4/app-shell/pr-preview-environments"
url: "https://linear.app/paperos/issue/PAP-505/per-pr-preview-environments-previewyml-coolify-preview-application"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:49:40.851Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-24"
cycle: null
---

# PAP-505: Per-PR preview environments: `preview.yml`, Coolify preview application lifecycle, seeded demo tenant, sticky PR comment with URLs and teardown within five minutes of close

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Infra M

**Goal**

Gate 3 (PAP-82), video replays (PAP-83), e2e flows (PAP-86), the vision agent (PAP-84) and the golden path all run against `pr-<n>.preview.PAPEROS_DOMAIN`. PAP-26 lists previews as one bullet among staging, production and rollback; they are the most-consumed part and deserve their own session so the gates are not waiting on production tagging work.

**Scope**

In:

* `.github/workflows/preview.yml`: on `pull_request` opened, synchronize, reopened: build images once (PAP-26 build job reused via `workflow_call`), create or update a Coolify preview application per PR from `ops/coolify/preview.json` (web, api, worker sharing one preview database), set env from `ops/secrets/preview-api.enc.yaml`, deploy, wait for `/healthz` and `/__version == sha`; on `closed`: delete the application and drop the database.
* Preview database: `CREATE DATABASE pr_<n> TEMPLATE app_slot_template` (shared with PAP-500), migrations as pre-deploy, then `POST /__test/seed` (PAP-240) so demo audiences can sign in.
* Sticky PR comment (`marocchino/sticky-pull-request-comment`) with preview URL, Pages URL (PAP-15), API docs URL, demo accounts, SHA and the gate status table placeholder that PAP-89 fills.
* Concurrency group per PR; forks skipped with a comment; `preview-<n>` label for manual redeploy; TTL: previews idle 7 days are removed by a nightly job even if the PR is open.

Out: staging and production deploys and rollback (PAP-26), Pages static previews (PAP-15), the seed content (PAP-240, PAP-363).

**Spec**

* Preview URL contract `https://pr-<n>.preview.PAPEROS_DOMAIN` and `https://api.pr-<n>.preview.PAPEROS_DOMAIN`; wildcard DNS and certificate from PAP-25.
* Preview `PUBLIC_ENV=preview`; test-mode endpoints enabled only here and in dev; production never.
* Budget: preview live within 5 minutes of push on a warm image cache (measured in the job summary); teardown within 5 minutes of close.
* Resource cap: at most 20 concurrent previews; beyond that the oldest idle preview is recycled and the PR comment says so.
* Secrets: previews get the `preview` sops file only (test Stripe keys, sandbox email through PAP-370 allowlist), never staging credentials.

**Interface contract**

Provides: `preview.yml`, the URL contract, `ops/coolify/preview.json`, sticky comment template `ops/ci/templates/preview-comment.md`, TTL job; consumed by PAP-82, PAP-83, PAP-84, PAP-86, PAP-89, PAP-364 (C6), PAP-429.

Consumes: host, wildcard DNS and sops (PAP-25), Postgres host (PAP-30), image build job and `/__version` (PAP-26), seed endpoint (PAP-240, soft), Trivy gate (PAP-80, soft).

**Definition of done**

* Open a test PR: preview live within 5 minutes with seeded demo users; close: gone within 5 minutes and database dropped (job logs with timings).
* Twenty-one concurrent previews recycle the oldest idle one (simulated in staging).
* Playwright smoke against the preview signs in as `staff@demo`; `docs/runbooks/preview.md`; CHANGELOG; Linear comment with a preview URL.

**Test plan**

* Unit: Coolify status polling and version assertion against a mocked API; TTL selection of the oldest idle preview.
* E2E: open, push twice, close a test PR; assert application and database lifecycle via the Coolify and Postgres APIs.

**Demo**

Reviewer opens any PR, clicks the preview URL in the sticky comment, signs in as `staff@demo.<app>.test`, then closes the PR and refreshes the URL after five minutes to see it gone. Under 3 minutes plus wait.

**Edge cases**

* Migration fails on the preview database: the PR comment shows the error and the preview keeps the previous image.
* Two pushes within a minute: the concurrency group cancels the older deploy.
* Coolify API rate limit: retries with backoff; the comment shows `pending` rather than a stale URL.
* PR reopened after teardown: full recreate, new database, comment updated.

**Dependencies**

Hard: PAP-25, PAP-30. Soft: PAP-240 (seed), PAP-80, PAP-370, PAP-500 (shared template database). Unblocks PAP-83, PAP-86; feeds PAP-82, PAP-84, PAP-89, PAP-364, PAP-429.

**Agent**

Builder: Forge (Ops Runner). Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/app-shell/warm-pool-job` = PAP-500.

*Round 4 critique fix (2026-09-18):* de-parented from PAP-26 (FIX-R4-1: this issue is an add-on to its former parent's core scope, which is a claimable leaf again). PAP-26 blocks this issue (`blocks` relation).
