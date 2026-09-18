---
identifier: "PAP-51"
title: "Script `forge bootstrap <repo>` to configure imagine-os repos with mirrors, secrets, labels and webhooks"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Agent"]
milestone: "CI runs on both forges"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-47", "PAP-48", "PAP-449", "PAP-519", "PAP-520", "PAP-521"]
blocks: ["PAP-276", "PAP-526", "PAP-531", "PAP-678"]
key: "forge/repo-bootstrap"
url: "https://linear.app/paperos/issue/PAP-51/script-forge-bootstrap-repo-to-configure-imagine-os-repos-with-mirrors"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:49:49.789Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-24"
cycle: null
---

# PAP-51: Script `forge bootstrap <repo>` to configure imagine-os repos with mirrors, secrets, labels and webhooks

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Provide `forge bootstrap <repo>`, one idempotent command that turns a pre-provisioned, empty imagine-os repository into a fully wired PaperOS repo: Forgejo twin and mirrors, secrets, labels, webhooks, branch protection, templates and workflows, Pages. `paperos create` (PAP-22) and the orchestrator call it instead of repeating the steps.

**Scope**

In:

* `packages/forge-cli` (`citty`, `octokit`, generated Forgejo client via `openapi-typescript`, `sops` via child process); config files `labels.yml`, `secrets-manifest.yml`, `webhooks.yml`; `--dry-run` and `--check`; tests against recorded responses; runbook.

Out: cloning template code (PAP-22 does that after bootstrap), creating Linear projects (PAP-91; this accepts `--linear-project <id>` for repo metadata), publishing the package (template-upgrade issue).

**Spec**

* `forge bootstrap <repo> [--dry-run] [--check] [--linear-project <id>] [--visibility private|public] [--rotate-webhook-secret]`; each step logs `[ok]`, `[changed]` or `[skip]`:
   1. verify `imagine-os/<repo>` exists on GitHub (exit 3 otherwise; never create);
   2. create the Forgejo twin if missing;
   3. mirrors both ways via `mirror.ts` (from PAP-47) and register in `repos.yml`;
   4. secrets from `secrets-manifest.yml` on both forges, values from sops, never printed;
   5. labels from `labels.yml` (Type, Surface, Phase mirroring Linear);
   6. webhooks from `webhooks.yml` to the orchestrator (PAP-97) with a generated secret;
   7. rulesets from PAP-46 on both forges;
   8. PR template, CODEOWNERS and `.github/workflows/mirror-to-forgejo.yml` committed if absent;
   9. Pages enabled on the `gh-pages` branch (PAP-15);
  10. `.paperos/repo.json` written with Linear project id, Forgejo id and bootstrap version.
* Exit codes 0, 3 missing repo, 4 rate limited after 5 retries with jitter.

*Round 4 amendment (2026-09-18):*

* Step 8 also commits the community health files when absent: `SECURITY.md` (disclosure address and the PAP-219 policy link), `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/config.yml` with `blank_issues_enabled: false` and a single contact link to the Linear intake (PAP-307), and `.github/dependabot.yml` disabled in favour of Renovate (PAP-217). \* `--ttl <duration>` writes the `paperos-ttl` marker consumed by PAP-531.

**Interface contract**

Provides:

* Bin `forge` with `bootstrap`, later `upgrade-check` (template-upgrade issue); JSON output `--json` `{ repo, steps: [{ name, status, ms }] }` that PAP-22 relays into its own summary.
* Typed Forgejo client `packages/forge-cli/src/forgejo.ts` reused by PAP-54 (`packages/forge-client`) and PAP-53.
* `.paperos/repo.json` schema `{ linearProjectId, forgejoRepoId, githubRepoId, bootstrapVersion, modules?: string[] }` read by PAP-28 and PAP-96.
* Config schemas for `labels.yml`, `secrets-manifest.yml`, `webhooks.yml` (Zod).

Consumes: mirror functions and `repos.yml` (PAP-47), bot tokens and deploy keys (PAP-48), rulesets (PAP-46), PR template (PAP-49), Pages convention (PAP-15), webhook receiver URL and secret format (PAP-97).

**Definition of done**

* `forge bootstrap paperos-bootstrap-fixture` completes all ten steps `[ok]`/`[changed]`; second run all `[ok]`/`[skip]` (transcripts).
* `--dry-run` performs zero writes (asserted by `msw`); `--check` exits 1 after a manual label edit, 0 after re-bootstrap.
* Unit coverage above 80 percent; typecheck clean; secrets never in logs (test greps captured output).
* `docs/runbooks/repo-bootstrap.md` merged; `CLAUDE.md` mentions the command; Linear comment with fixture links; changelog under Tooling.

**Test plan**

* Unit: every step against recorded GitHub and Forgejo responses in fresh, already-configured and drifted states; label recolour path; rate-limit retry with fake timers; log redaction grep.
* Integration nightly: real run on the fixture repo, second run idempotent, `--check` after a manual drift.
* Contract: `--json` output validated against schema; PAP-22 fixture consumes it.
* Security: Sentinel reviews token scopes used per step.

**Demo**

Reviewer runs `pnpm forge bootstrap paperos-bootstrap-fixture --dry-run` to read the ten planned steps, then without `--dry-run`, and opens the fixture repo on both forges to see labels, the mirror and the webhook. Under 2 minutes.

**Edge cases**

* Repo on Forgejo but not GitHub: exit 3; GitHub is the provisioning source of truth.
* Partial failure at step 6: rerun resumes safely; no state file.
* Label with same name, different colour: recolour, `[changed]`.
* Pages unavailable on a private repo: `[skip]` with reason.
* Webhook secret rotated: flag regenerates and updates the orchestrator.

**Dependencies**

PAP-47, PAP-48 (hard). Soft: PAP-46, PAP-49, PAP-15, PAP-97. Consumer: PAP-22, PAP-29, template-upgrade issue.

**Agent**

Built by Forge (lead) with Ops Runner for live verification. Reviewed by Sentinel (Security Auditor).

**Size**

M: ten idempotent steps with recorded-response tests.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/forge/repo-cleanup` = PAP-531.

*Round 4 critique fix (2026-09-18):* PAP-526 was split out as a follow-on issue (FIX-R4-1); this issue is a leaf again with its Model / Effort labels and estimate restored, and it blocks PAP-526.
