---
identifier: "PAP-530"
title: "Secret push protection: gitleaks pre-commit through lefthook, Forgejo pre-receive hook, GitHub push protection, and the leaked-secret revocation runbook"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P0"
type: "Infra"
priority: 1
surfaces: ["Developer"]
milestone: "Forgejo live and mirrored"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-46", "PAP-273"]
blocks: []
key: "r4/forge/push-protection"
url: "https://linear.app/paperos/issue/PAP-530/secret-push-protection-gitleaks-pre-commit-through-lefthook-forgejo"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:02.890Z"
model: "claude-opus-5"
effort: "high"
estimate: 2
dueDate: "2026-09-20"
cycle: null
---

# PAP-530: Secret push protection: gitleaks pre-commit through lefthook, Forgejo pre-receive hook, GitHub push protection, and the leaked-secret revocation runbook

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Infra S

**Goal**

PAP-80 runs gitleaks in CI, after the secret is already in history on two forges and in the mirror. Twenty agent sessions with tokens in their environment will eventually paste one into a file; GitHub push protection and a server-side hook stop it at the push, and a local hook stops it at the commit. This is the cheapest security control in the plan and nobody owns it.

**Scope**

In:

* `lefthook.yml` (PAP-46) gains a `pre-commit` `gitleaks protect --staged` step with the shared `.gitleaks.toml` (PaperOS token formats: Forgejo, Linear, Coolify, Stripe test keys, age keys, `FORGEJO_TOKEN_*`).
* Forgejo: `pre-receive` hook installed by `ops/forgejo/hooks/install.sh` on the `imagine-os` org (Forgejo system hooks) running gitleaks over pushed commits; rejects with the rule id and remediation URL; bypass only for `bot-atlas` with a `Needs Justin` reference in the push option `-o secret-bypass=<NJ-n>`.
* GitHub: org-level push protection and secret scanning enabled through the App or org settings (NJ-3 batch); custom patterns mirrored from `.gitleaks.toml`.
* Runbook `docs/runbooks/leaked-secret.md`: identify, rotate (`bots.ts rotate`, PAP-48), purge from prompt logs (PAP-129), rewrite history only with approval, verify both forges and the mirror.

Out: CI scanning and SAST (PAP-80), credential broker (PAP-300), secrets storage (PAP-25, PAP-17).

**Spec**

* Local and server rules are the same file; CI (PAP-80) asserts the GitHub custom patterns match it.
* Hook latency under 2 s for a typical push; large pushes scanned incrementally by commit.
* False positives: `# gitleaks:allow` inline with a reason; the hook logs allowances to the audit channel.
* Server hook failure (gitleaks binary missing) fails closed with a clear message; monitored by PAP-534.

**Interface contract**

Provides: `.gitleaks.toml`, lefthook step, Forgejo pre-receive hook and installer, GitHub pattern set, revocation runbook; consumed by PAP-80 (same config), PAP-46 (hook file), PAP-48 (rotation), PAP-219 (`SEC-SECRETS-*` controls), PAP-129.

Consumes: lefthook and rulesets (PAP-46), Forgejo admin access (PAP-273), GitHub org settings (NJ-3, PAP-301), rotation script (PAP-48, soft).

**Definition of done**

* A commit containing a fixture Forgejo token is rejected locally and, with hooks skipped, by the Forgejo pre-receive hook and by GitHub push protection (three transcripts).
* Bypass path tested once with a fake NJ reference and logged; runbook merged; CHANGELOG under Security; Linear comment.

**Test plan**

* Unit: rule set against fixture strings (true positives for each token format, negatives for UUIDs and SHAs).
* E2E: push fixture secret to the fixture repo on both forges; assert rejection messages.

**Demo**

Reviewer writes `FORGEJO_TOKEN_FORGE=fj_...` into a file, commits and watches lefthook refuse; commits with `--no-verify`, pushes to Forgejo and reads the pre-receive rejection naming the rule. Under a minute.

**Edge cases**

* Secret in a commit already on a feature branch before this landed: CI (PAP-80) catches it; runbook applies.
* Mirror push from GitHub carrying a secret that GitHub allowed by bypass: Forgejo hook rejects; mirror alerts via PAP-520.
* Agent session cannot run lefthook (no node in sandbox): server hook is the guarantee.

**Dependencies**

Hard: PAP-46, PAP-273. Soft: PAP-301 (NJ-3), PAP-48, PAP-80, PAP-129.

**Agent**

Builder: Forge (Ops Runner). Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/forge/forge-observability` = PAP-534, `r4/forge/mirror-drift-monitor` = PAP-520.
