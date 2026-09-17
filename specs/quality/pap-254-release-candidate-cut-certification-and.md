---
identifier: "PAP-254"
title: "Release candidate cut, certification and Justin approval flow"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Agent", "Developer"]
milestone: "Edge-case hunting and release trains"
state: "Backlog"
parent: "PAP-88"
children: []
blockedBy: ["PAP-94", "PAP-252", "PAP-253", "PAP-357", "PAP-358"]
blocks: ["PAP-89"]
key: "quality/release-train/rc-certify-approve"
url: "https://linear.app/paperos/issue/PAP-254/release-candidate-cut-certification-and-justin-approval-flow"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:08.152Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-254: Release candidate cut, certification and Justin approval flow

**Goal**

Automate the weekly decision: cut the RC branch and PR, deploy it to staging, run gates, generate the digest, open one Needs Justin issue, and on `/approve` promote to production with a tag while `/reject` reopens fixes, all idempotent and rehearsed.

**Scope**

* In: `.github/workflows/release-candidate.yml` (Monday cut, `release/<yyyy-ww>` branch, PR labelled `release-candidate`, prerelease tag `-rc.N` via PAP-52), `ops/release/certify.ts`, digest call (PAP-89), Needs Justin issue creation with the RC template, `promote.yml` triggered by PAP-97 on `/approve` or Done, production deploy with `deployToEnvironment`, tag `vX.Y.Z`, release notes from PAP-133, `/reject` handling, rollback command, queue rule enforcement, rehearsal with a `rehearsal` label on the PAP team.
* Out: policy (sibling), nightly (sibling), digest content (PAP-89).

**Spec**

* `certify.ts` checks: all `GATE_STATUSES` green on the RC head, no open S0/S1 findings across artifacts, no expired waivers, `perf.json` within budget when present, migrations reversible flag from PAP-32, backup fresher than 24 h, staging `testMode: false`; output `certification.json` and a Markdown table for the issue.
* Needs Justin issue: title `Release candidate <yyyy-ww> (vX.Y.Z-rc.N)`, body with digest link, gate table, one-line ask, `/approve` and `/reject <reason>`; label `rehearsal` marks dry runs so PAP-94's queue metrics ignore them.
* Promotion: idempotency key = RC head SHA in the release record; merge release PR, tag, deploy production, post release notes, close the issue; failure triggers auto-rollback and reopens the issue with logs.
* `pnpm release:rollback <version>` redeploys the previous image and optionally restores the snapshot with confirmation.

**Interface contract**

* Provides: `certification.json` (contracts kind), release records, `promote.yml` webhook contract with PAP-97 (`event: 'release.approve' | 'release.reject'`), tags for PAP-52 and PAP-19 updater.
* Requires: siblings, PAP-89 digest, PAP-94 grammar, PAP-97 webhooks, PAP-52 tags, PAP-133 notes, PAP-26 production target.

**Definition of done**

* Rehearsal RC end to end with the `rehearsal` label: branch, PR, gates, digest, Needs Justin issue, `/approve` promotes to a staging-as-production target and tags `v0.1.0-rc.1` (links, screenshots).
* `/reject` path tested; `certify.ts` blocks on a seeded missing status and on `testMode: true`.
* Duplicate approval webhook does not double deploy (test).
* Docs section "Release candidate and promotion"; changelog under "Quality".

**Test plan**

* Unit: certification rules table, idempotency key, queue rule.
* Integration: promote workflow against the sandbox with a fake Coolify.
* Rehearsal: live once on the PAP team with the label.

**Demo**

Open the rehearsal Needs Justin issue, read the gate table and digest link, comment `/approve`, watch `promote.yml` tag and deploy, and see the issue close. Under two minutes after the comment.

**Edge cases**

* `main` red on Monday: no cut; comment on the previous RC issue.
* Justin approves while a hotfix is deploying: promotion waits for the deploy lock.
* Irreversible migration: certification requires the acknowledgement checkbox from the digest.

**Dependencies**

Both sibling children (hard), PAP-94 (hard). PAP-89 is a consumer, not a dependency: the release train (PAP-88, and this child as its last step) blocks PAP-89; the certification flow links the digest when PAP-89 exists and until then the RC comment carries the gate summary itself. Soft: PAP-97, PAP-52, PAP-133. Relations added 2026-09-17 (FIX-3): PAP-94 blocks this issue; this issue blocks PAP-89.

**Agent**

Built by Sentinel with Atlas (Merger sub-agent) on promotion and Forge (Ops Runner) on deploys. Reviewed by Atlas; Justin confirms via the rehearsal.

**Size**

M.
