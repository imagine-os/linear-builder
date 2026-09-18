---
identifier: "PAP-48"
title: "Create scoped bot accounts and deploy keys for each agent character on both forges"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P0"
type: "Infra"
priority: 2
surfaces: ["Agent"]
milestone: "Forgejo live and mirrored"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-45", "PAP-273"]
blocks: ["PAP-51", "PAP-106", "PAP-217", "PAP-300", "PAP-498", "PAP-521", "PAP-526", "PAP-527", "PAP-533", "PAP-709", "PAP-722", "PAP-813"]
key: "forge/bot-accounts"
url: "https://linear.app/paperos/issue/PAP-48/create-scoped-bot-accounts-and-deploy-keys-for-each-agent-character-on"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:49:43.103Z"
model: "claude-opus-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-20"
cycle: null
---

# PAP-48: Create scoped bot accounts and deploy keys for each agent character on both forges

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Infra M

**Goal**

Give every agent character a least-privilege identity on both forges so commits, PRs and API calls are attributable to Atlas, Forge, Iris and the rest rather than to Justin or a shared token. Access matches each character's `access` list exactly and rotation is one command. This sits on the P0 critical path to PAP-106.

**Scope**

In:

* Forgejo bot accounts per lead character; one GitHub App with per-character commit identities; deploy keys for CI; scoped tokens; sops layout; rotation script; access matrix document; `.mailmap` and `allowed_signers`.

Out: MCP tool enforcement (PAP-106 consumes the tokens), human accounts, sub-character identities (sub-agents act under their lead with a `Sub-Agent:` trailer).

**Spec**

* `ops/forge/bots.ts` creates `bot-atlas`, `bot-forge`, `bot-iris`, `bot-quill`, `bot-sentinel`, `bot-nova`, `bot-ledger`, `bot-beacon`, `bot-scout` with emails `<name>@agents.<domain>`, reading the roster file so new characters are added, never deleted without `--prune`.
* Teams: `agents` (write) for builders; `reviewers` (read plus PR review) for `bot-sentinel`; `owners` adds `bot-atlas` for merges; `bot-scout` read plus `docs/registry` via CODEOWNERS.
* Token scopes: builders `write:repository`, `write:issue`; Sentinel `read:repository`, `write:issue`; Atlas adds `write:organization`. Stored in `ops/secrets/bots.enc.yaml` (recipients Justin and orchestrator) and mirrored into Coolify for PAP-96.
* GitHub App `paperos-agents` on imagine-os: contents, pull requests, checks, metadata; installation token minted per session; commit author `"<Character> (PaperOS agent) <bot-<name>@agents.<domain>>"`; SSH signing keys per character with `allowed_signers`.
* `bots.ts audit` compares live state with `ops/forge/access-matrix.yml`; `bots.ts rotate <name>` completes in under 5 minutes.

**Interface contract**

Provides:

* Secret keys in `bots.enc.yaml`: `FORGEJO_TOKEN_<CHARACTER>`, `GITHUB_APP_ID`, `GITHUB_APP_PRIVATE_KEY`, `GITHUB_APP_INSTALLATION_ID`, `SIGNING_KEY_<CHARACTER>` consumed by PAP-96 (session env), PAP-106 (tool scopes), PAP-47 (mirror token `FORGEJO_TOKEN_MIRROR`), PAP-51 (bootstrap).
* `ops/forge/access-matrix.yml` schema `{ characters: [{ name, forgejoUser, teams[], scopes[], paths[] }] }` consumed by PAP-104 and PAP-106.
* Helper `mintGithubToken(character)` in `packages/forge-cli/src/github-app.ts`.
* Commit identity convention and `.mailmap` consumed by PAP-133, PAP-114.

Consumes: Forgejo org and admin token (PAP-45), roster (PAP-104; plan.json roster until then), sops recipients (PAP-25).

**Definition of done**

* Nine bots exist; `bots.ts audit` prints the matrix and exits non-zero on deviation (test).
* GitHub App installed; a session mints a token and opens a PR attributed to the App with a character author.
* `bot-sentinel` push to `main` rejected; its review accepted (transcripts).
* Rotation run once end to end; old token verified revoked.
* `gitleaks` clean; `.mailmap` and `allowed_signers` committed; `git log --show-signature` prints Good signature; matrix doc merged; Linear comment; changelog under Infra.

**Test plan**

* Unit: `bots.ts` plan against recorded Forgejo responses (create, skip, prune-guard); matrix diff detection with a mutated fixture.
* Integration: mint an installation token in CI and call `GET /installation/repositories`; open and close a PR on a fixture repo with the character author.
* Permission: `bot-sentinel` push rejected, review accepted; `bot-scout` write outside `docs/registry` rejected by CODEOWNERS review requirement.
* Rotation: `rotate bot-forge` then old token returns 401 (log, timed).
* Security: `gitleaks` in Gate 1 for the infra repo.

**Demo**

Reviewer runs `pnpm tsx ops/forge/bots.ts audit` and reads the nine-row matrix, opens the fixture PR on GitHub authored by "Forge (PaperOS agent)" with a verified signature badge, then checks Forgejo's `agents` team membership page. Under 90 seconds.

**Edge cases**

* Org blocks Apps: fine-grained PAT per character on a machine user, documented degraded mode.
* New character later: `bots.ts` creates it from the roster.
* Token in a prompt log: rotate under 5 minutes; purge via PAP-129 redaction.
* Bot rate-limited: per-bot limits documented; orchestrator backoff.
* Two sessions share a character: attribution stays per character; sessions distinguished by the `Linear:` trailer.

**Dependencies**

PAP-45 (hard). Soft: PAP-104. Unblocks PAP-51, PAP-106, PAP-96; feeds PAP-47.

*Round 4 (2026-09-18): PAP-301 soft: the founder root-of-trust hardening (09-23) lands after the forge milestone (09-20); until it lands, create the bot accounts and deploy keys with the current admin credentials; PAP-301 rotates and re-parents them when it lands. The* `blocks` *relation PAP-301 -> PAP-48 was removed.*

**Agent**

Built by Forge (Ops Runner). Reviewed by Sentinel (Security Auditor).

**Size**

M: one script, one App, a matrix and a rotation proof.

*Round 4 critique fix (2026-09-18):* PAP-521 was split out as a follow-on issue (FIX-R4-1); this issue is a leaf again with its Model / Effort labels and estimate restored, and it blocks PAP-521.
