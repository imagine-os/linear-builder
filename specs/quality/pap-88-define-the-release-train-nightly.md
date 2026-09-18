---
identifier: "PAP-88"
title: "Define the release train: nightly staging deploy, weekly release candidate to Needs Justin with consolidated review report"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Edge-case hunting and release trains"
state: "Backlog"
parent: null
children: ["PAP-252", "PAP-253", "PAP-254"]
blockedBy: ["PAP-26", "PAP-81", "PAP-82", "PAP-94", "PAP-242", "PAP-244", "PAP-245", "PAP-248", "PAP-354", "PAP-505", "PAP-527", "PAP-563", "PAP-677", "PAP-679"]
blocks: ["PAP-89"]
key: "quality/release-train"
url: "https://linear.app/paperos/issue/PAP-88/define-the-release-train-nightly-staging-deploy-weekly-release"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:49:38.023Z"
model: null
effort: null
estimate: null
dueDate: "2026-09-30"
cycle: null
---

# PAP-88: Define the release train: nightly staging deploy, weekly release candidate to Needs Justin with consolidated review report

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Define and automate the cadence that keeps Justin out of pull requests: nightly staging deploys of `main`, a Monday release candidate with consolidated gate evidence, and one Needs Justin issue whose `/approve` promotes to production and tags a release. Re-typed from Spec to Build per the round-2 audit and split into three children; the approval grammar comes from PAP-94, not from here.

**Children**

1. PAP-252 Release train policy document and environments config (S, Spec) - blocks the other two.
2. PAP-253 Nightly staging workflow with full gate run (M).
3. PAP-254 Release candidate cut, certification and Justin approval flow (M).

**Scope**

* In (across children): `docs/quality/release-train.md` and ADR, `ops/release/environments.yaml`, `staging-nightly.yml`, `release-candidate.yml`, `promote.yml`, `certify.ts`, release records, rollback command, queue rule, rehearsal.
* Out: digest content (PAP-89), changelog generation (PAP-133), Tauri packaging (PAP-52), the command grammar (PAP-94), runtime feature flags (app-shell gap issue).

**Spec**

Details live in the children. Cross-child rules:

* `main` is always releasable; `release/<yyyy-ww>` is cut Monday 08:00 UTC only when `main` is green and last week's RC issue is closed.
* Certification is the only path to production: every `GATE_STATUSES` entry green on the RC head, no open S0/S1, no expired waivers, `perf.json` within budget, reversible migrations or an acknowledged checkbox, fresh backup, staging `testMode: false`.
* Promotion is idempotent on the RC head SHA; failure auto-rolls back and reopens the issue.
* Rehearsals use the `rehearsal` label on the PAP team so PAP-94's queue metrics ignore them.

**Interface contract**

* Provides: `environments.yaml` schema, `ReleaseRecord` and `certification.json` (PAP-239 kinds), composite action `deployToEnvironment(name, sha)`, nightly report URLs `/nightly/<date>/`, RC issue template, webhook contract with PAP-97 (`release.approve`, `release.reject`), tags for PAP-52 and PAP-19 updater, `pnpm release:rollback`.
* Requires: PAP-81 and PAP-82 gates (hard), PAP-94 grammar (hard), PAP-26 images and Coolify (hard), PAP-89 digest, PAP-97 webhooks, PAP-86, PAP-85, PAP-87, PAP-242, PAP-30 backups, PAP-52 tags, PAP-133 notes (soft).
* Consumers: PAP-89 (trigger and inputs), PAP-52, PAP-108 handoffs, PAP-29 drill, PAP-94 (RC issues are its largest item class).

**Definition of done**

* All three children Done.
* Integration rehearsal below completed with links and screenshots in the Linear comment.
* Policy linked from CLAUDE.md and the PR template; `docs/quality/release-train.md` and ADR `0008-release-train.md` merged; changelog entry.

**Test plan**

Umbrella rehearsal:

* Three consecutive nightly staging runs with reports.
* RC cut end to end with the `rehearsal` label: branch, PR, gates, digest, Needs Justin issue; `/approve` promotes to a staging-as-production target and tags `v0.1.0-rc.1`; `/reject <reason>` on a second rehearsal reopens fixes and keeps the branch.
* `certify.ts` blocks on a seeded missing status, an expired waiver and `testMode: true`; duplicate approval webhook does not double deploy; rollback command redeploys the previous image.

**Demo**

Open the rehearsal RC issue in Needs Justin: one-line ask, gate table, digest link; comment `/approve`, watch `promote.yml` tag and deploy, and see the issue close with the release record link. Under two minutes after the comment.

**Edge cases**

Cross-child: `main` red on Monday means no cut and a comment on the previous RC; hotfixes branch from the last tag with a short Needs Justin issue; Coolify API down retries 30 minutes then fails loudly; an irreversible migration needs the digest checkbox.

**Dependencies**

PAP-81, PAP-82, PAP-94, PAP-26, PAP-242 (hard). Soft: PAP-89, PAP-97, PAP-86, PAP-85, PAP-87, PAP-30, PAP-52, PAP-133. Downstream, PAP-29 is soft, not blocked: the drill's first run does not need the release train and weekly runs adopt it once it exists; the `blocks` relation to PAP-29 was removed on 2026-09-17 (round-2 FIX-1; this milestone is 09-30, PAP-29's is 09-29).

**Agent**

Sentinel with Atlas (Merger) on promotion and Forge (Ops Runner) on deploys. Reviewed by Atlas and Forge; Justin confirms the mechanics via the rehearsal.

**Size**

L, split into 3 children (S, M, M).
