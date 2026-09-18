---
identifier: "PAP-526"
title: "`forge bootstrap --check` drift detection with per-step diff output and the nightly fixture-repo run publishing `[ok]/[changed]/[skip]` transcripts"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P1"
type: "Build"
priority: 3
surfaces: ["Developer"]
milestone: "CI runs on both forges"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-47", "PAP-48", "PAP-51", "PAP-449", "PAP-519", "PAP-520", "PAP-521"]
blocks: ["PAP-276", "PAP-531", "PAP-678"]
key: "r4/forge/bootstrap-check-mode"
url: "https://linear.app/paperos/issue/PAP-526/forge-bootstrap-check-drift-detection-with-per-step-diff-output-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:49:49.409Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-24"
cycle: null
---

# PAP-526: `forge bootstrap --check` drift detection with per-step diff output and the nightly fixture-repo run publishing `[ok]/[changed]/[skip]` transcripts

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-51 makes bootstrap idempotent; proving that repos stay bootstrapped (labels not hand-edited, webhooks intact, rulesets applied, mirrors present) is a read-only mode plus a nightly job that the weekly re-audit (PAP-306) and the DR drill read. Separating it lets the ten write steps land first.

**Scope**

In:

* `--check` in `packages/forge-cli`: every step gains a `diff()` returning `{ expected, actual }` for labels, secrets (names only), webhooks, rulesets, templates, Pages and `.paperos/repo.json`; exit 1 with a table when any differs; `--json` output for automation.
* Nightly `ops/forge/bootstrap-check.yml` over every repo in `repos.yml` on Forgejo Actions with GitHub fallback; a drifted repo opens a Linear issue (dedupe by repo) or comments on an existing one.
* Fixture run: `forge bootstrap paperos-template-fixture` (PAP-512) then `--check`; a manual label recolour is detected, re-bootstrap restores it; transcripts uploaded.

Out: the write steps (PAP-51), ruleset content (PAP-46), mirror monitoring (PAP-520).

**Spec**

* `--check` performs zero writes (asserted by `msw` recording).
* Secrets compare names and last-updated timestamps only; values never fetched.
* Under 30 s for 50 repos using batched list calls.

**Interface contract**

Provides: `forge bootstrap --check`, `bootstrap-check.yml`, drift JSON `{ repo, steps: [{ name, status, diff? }] }`; consumed by PAP-306 (re-audit), PAP-53 (post-restore check), PAP-22 (`paperos doctor` can call it).

Consumes: mirror functions and `repos.yml` (PAP-47), bot tokens (PAP-48), rulesets (PAP-46), fixture repo.

**Definition of done**

* Fixture drift detected and repaired (transcripts); nightly job green on all repos; `docs/runbooks/repo-bootstrap.md` check section; CHANGELOG; Linear comment.

**Test plan**

* Unit: diff per step against recorded fresh, configured and drifted states; JSON schema.
* E2E: nightly job on the fixture with a seeded drift files one issue.

**Demo**

Reviewer recolours a label on the fixture repo, runs `forge bootstrap paperos-template-fixture --check` and reads the `[changed] labels` row with the diff, then re-bootstraps. Under a minute.

**Edge cases**

* Repo on the list but deleted: `missing` row, issue filed, mirror row removed by PAP-531.
* Forgejo down: GitHub-side checks still run; Forgejo rows `unknown`.

**Dependencies**

Hard: PAP-47, PAP-48. Soft: PAP-46, PAP-512. Parent PAP-51 supplies the steps.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/app-shell/template-fixture-repo` = PAP-512, `r4/forge/mirror-drift-monitor` = PAP-520, `r4/forge/repo-cleanup` = PAP-531.

*Round 4 critique fix (2026-09-18):* de-parented from PAP-51 (FIX-R4-1: this issue is an add-on to its former parent's core scope, which is a claimable leaf again). PAP-51 blocks this issue (`blocks` relation).
