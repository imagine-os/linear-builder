---
identifier: "PAP-521"
title: "GitHub App `paperos-agents`: installation on imagine-os, `mintGithubToken(character)`, per-character commit identities, SSH signing keys, `.mailmap` and `allowed_signers`"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P0"
type: "Infra"
priority: 1
surfaces: ["Agent"]
milestone: "Forgejo live and mirrored"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-45", "PAP-48", "PAP-273"]
blocks: ["PAP-51", "PAP-106", "PAP-217", "PAP-300", "PAP-498", "PAP-526", "PAP-527", "PAP-533", "PAP-709", "PAP-722", "PAP-813"]
key: "r4/forge/github-app-identities"
url: "https://linear.app/paperos/issue/PAP-521/github-app-paperos-agents-installation-on-imagine-os"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:49:42.830Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-20"
cycle: null
---

# PAP-521: GitHub App `paperos-agents`: installation on imagine-os, `mintGithubToken(character)`, per-character commit identities, SSH signing keys, `.mailmap` and `allowed_signers`

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Infra M

**Goal**

PAP-48 covers both forges; the GitHub side is a distinct piece of work with its own credentials (NJ-3), its own token model (installation tokens minted per session) and the commit attribution and signing rules every agent PR carries. Splitting it puts the Forgejo bots (which block PAP-51) and the GitHub App (which blocks PAP-106) on parallel tracks.

**Scope**

In:

* GitHub App `paperos-agents` on org `imagine-os` with permissions contents, pull requests, checks, metadata, workflows; private key, app id and installation id in `ops/secrets/bots.enc.yaml` (PAP-48 layout) and mirrored to Coolify for PAP-96.
* `packages/forge-cli/src/github-app.ts`: `mintGithubToken(character, { repos? })` returning a one-hour installation token scoped to the repositories the character's `access-matrix.yml` entry allows; cached per session; refresh at 50 minutes.
* Commit identity: `"<Character> (PaperOS agent) <bot-<name>@agents.<domain>>"`; SSH signing key per character (`SIGNING_KEY_<CHARACTER>`), `allowed_signers` and `.mailmap` committed to the template; `git config` snippet applied by `worktree.sh` (PAP-46).
* Verification: a fixture PR opened with a minted token, authored by "Forge (PaperOS agent)", shows the verified signature badge; `git log --show-signature` prints Good signature.

Out: Forgejo bot accounts and teams (PAP-48 sibling work), MCP scope enforcement (PAP-106), rotation of Forgejo tokens.

**Spec**

* Tokens never written to disk; the orchestrator (PAP-96) passes them through the credential broker (PAP-300) when it exists, environment otherwise.
* Sub-agents commit under their lead's identity with a `Sub-Agent:` trailer (PAP-48 rule).
* Degraded mode when the org blocks Apps: fine-grained PAT per character on a machine user, documented and flagged in `bots.ts audit`.
* Rate limits: installation tokens share the App limit (15k/h); per-character budgets documented for PAP-99.

**Interface contract**

Provides: `mintGithubToken`, secret names `GITHUB_APP_ID`, `GITHUB_APP_PRIVATE_KEY`, `GITHUB_APP_INSTALLATION_ID`, `SIGNING_KEY_<CHARACTER>`, `.mailmap`, `allowed_signers`, the commit identity convention; consumed by PAP-96 (session env), PAP-106 (scopes), PAP-47 (mirror PAT alternative), PAP-51, PAP-133 (attribution), PAP-114.

Consumes: founder root of trust and NJ-3 approval (PAP-301), Forgejo org for the matching bot names (PAP-273), access matrix (PAP-48), sops recipients (PAP-25).

**Definition of done**

* App installed; a CI job mints a token and lists installation repositories; fixture PR with verified character signature (screenshot).
* `bots.ts audit` covers the App permissions row; `gitleaks` clean; `docs/engineering/agent-identities.md`; CHANGELOG; Linear comment.

**Test plan**

* Unit: JWT and installation token minting against recorded responses; repo scoping from the matrix; refresh timing with fake timers.
* E2E: open and close a fixture PR with a minted token; assert author, signature and App attribution.

**Demo**

Reviewer runs `pnpm tsx ops/forge/bots.ts mint bot-forge --repos paperos-template`, uses the token to push a branch and open a PR, and sees "Forge (PaperOS agent)" with a Verified badge. Under 2 minutes.

**Edge cases**

* App private key rotated: old tokens keep working until expiry; new mints use the new key; runbook step.
* Character not in the matrix: `mint` refuses with the roster file path.
* Token appears in a prompt log: PAP-129 redaction plus immediate revocation through the App API.

**Dependencies**

Hard: PAP-273 and the NJ-3 credential batch (GitHub App on imagine-os). Soft: PAP-301 (founder root of trust hardens the same org accounts in parallel), PAP-300, PAP-96. Blocks PAP-106; feeds PAP-47, PAP-51.

**Agent**

Builder: Forge (Ops Runner). Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* de-parented from PAP-48 (FIX-R4-1: this issue is an add-on to its former parent's core scope, which is a claimable leaf again). PAP-48 blocks this issue (`blocks` relation).
