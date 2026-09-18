---
identifier: "PAP-519"
title: "`check-workflow-portability.ts`: GitHub-only action detection, `github.*` context fallbacks, secrets-manifest cross-check and the vendored-action allowlist for both forges"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "CI runs on both forges"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-13", "PAP-45", "PAP-50", "PAP-273"]
blocks: ["PAP-51", "PAP-53", "PAP-522", "PAP-524", "PAP-525", "PAP-526", "PAP-532", "PAP-536"]
key: "r4/forge/portability-checker"
url: "https://linear.app/paperos/issue/PAP-519/check-workflow-portabilityts-github-only-action-detection-github"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:49:49.042Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-24"
cycle: null
---

# PAP-519: `check-workflow-portability.ts`: GitHub-only action detection, `github.*` context fallbacks, secrets-manifest cross-check and the vendored-action allowlist for both forges

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-50 deploys runners and proves Gate 1 on Forgejo; the static checker that keeps every future workflow portable is a separate half-session that PAP-51 (bootstrap) and PAP-78 (Gate 1) both call. Splitting it lets the checker land before the runners are online, so workflows written this week are already portable.

**Scope**

In:

* `scripts/check-workflow-portability.ts` (`pnpm tsx`): parses every `.github/workflows/*.yml`, flags `uses:` actions absent from `code.forgejo.org` (mirror list fetched and cached in `ops/forge/action-mirrors.json`), unguarded `github.*` context reads, `runs-on` labels outside the PAP-50 and PAP-371 sets, secrets not listed in `ops/forge/secrets-manifest.yml`, and unpinned `uses:` (PAP-358 rule, warning here).
* Vendored allowlist `ops/forge/vendored-actions.yml`: actions copied under `.github/actions/<name>` with source, version and digest; the checker accepts `./.github/actions/<name>` and verifies the digest.
* Output: table per workflow with rule id, line and fix hint; `--json` for PAP-51; exit 1 on errors; fixtures under `scripts/__fixtures__/workflows/`.
* Gate 1 step `portability` (PAP-78) and the PAP-51 bootstrap step 8 call.

Out: runner deployment and proofs (PAP-50), non-Linux runners (PAP-371), pinning enforcement (PAP-358).

**Spec**

* Rules: `PORT-1` unmirrored action, `PORT-2` unguarded `github.*` (allowed inside `if: github.server_url == ...` or with `|| forgejo.*` fallback), `PORT-3` unknown label, `PORT-4` secret not in manifest, `PORT-5` vendored digest mismatch.
* Mirror list refreshed weekly by a cron PR; offline runs use the cached file and note its age.
* Runtime under 5 s for 30 workflows.

**Interface contract**

Provides: the script, rule ids, `action-mirrors.json`, `vendored-actions.yml`, Gate 1 step `portability`; consumed by PAP-50 (DoD), PAP-51 (step 8), PAP-78, PAP-371 (label set), PAP-53 (pre-drill check).

Consumes: workflows in the template (PAP-13), secrets manifest (PAP-50 owns the file), label sets (PAP-50, PAP-371).

**Definition of done**

* Fixtures: one passing workflow and one failing per rule with exact messages; the template's workflows pass.
* Step live in Gate 1; PAP-51 `--json` consumption tested; `docs/engineering/ci-portability.md` rules section; CHANGELOG; Linear comment.

**Test plan**

* Unit: each rule on its fixture; mirror cache age warning; vendored digest verification.
* E2E: Gate 1 run on a PR adding `uses: some/unmirrored-action@v1` fails with `PORT-1`.

**Demo**

Reviewer adds `uses: actions/upload-pages-artifact@v3` to a workflow, runs the checker and reads `PORT-1` with the vendoring hint; vendors it and the run passes. Under a minute.

**Edge cases**

* Composite action referencing another unmirrored action: recursed one level with the path shown.
* `workflow_call` reusable workflows from `paperos-infra`: resolved by repo and checked once.
* Forgejo-only action (`forgejo/*`) used on GitHub: symmetric rule `PORT-1` in the other direction.

**Dependencies**

Hard: PAP-13. Soft: PAP-78, PAP-371. Blocks PAP-51 (bootstrap step 8).

**Agent**

Builder: Forge (Ops Runner). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* de-parented from PAP-50 (FIX-R4-1: this issue is an add-on to its former parent's core scope, which is a claimable leaf again). PAP-50 blocks this issue (`blocks` relation).
