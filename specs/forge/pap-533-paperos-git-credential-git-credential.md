---
identifier: "PAP-533"
title: "`paperos-git-credential`: git credential helper and SSH configuration that fetch short-lived per-session tokens from the credential broker for both forges, with host-key pinning"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Agent"]
milestone: "Disaster recovery proven"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-48", "PAP-300", "PAP-521"]
blocks: []
key: "r4/forge/git-credential-helper"
url: "https://linear.app/paperos/issue/PAP-533/paperos-git-credential-git-credential-helper-and-ssh-configuration"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:03.308Z"
model: "claude-opus-5"
effort: "high"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-533: `paperos-git-credential`: git credential helper and SSH configuration that fetch short-lived per-session tokens from the credential broker for both forges, with host-key pinning

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build S

**Goal**

PAP-300 says sessions hold no raw secrets and PAP-48 mints tokens per character; git itself still needs credentials for `push` and `fetch` on two hosts. Without a helper, sessions fall back to tokens in `.git/config` or the environment, which is exactly what the threat model forbids. This issue is the missing adapter between git and the broker.

**Scope**

In:

* `packages/forge-cli/src/credential-helper.ts` built as `paperos-git-credential` (`bin`): implements the git credential protocol (`get`, `store`, `erase`) and answers `get` for `git.PAPEROS_DOMAIN` and `github.com` by asking the broker (PAP-300 local socket) for a token scoped to the session character and repo; caches in memory for the token lifetime; `store` and `erase` are no-ops.
* Session git config applied by `worktree.sh` (PAP-46) and the sandbox (PAP-280): `credential.helper=paperos-git-credential`, `credential.useHttpPath=true`, `url.https://.insteadOf=ssh://` so HTTPS is the only path; `core.sshCommand` with a pinned `known_hosts` for the rare SSH case (Forgejo 2222).
* Host-key and CA pinning: `ops/forge/known_hosts` and the Caddy CA chain checked into the template; the helper refuses hosts not on the allowlist.
* Audit: every `get` logged to the PAP-300 audit stream with character, repo and operation; denied repos return an empty answer and git fails with a clear message.

Out: the broker itself (PAP-300), token minting (PAP-48, PAP-521), human developer credentials (personal tokens remain their own).

**Spec**

* Helper answers within 200 ms from cache, under 2 s on a broker round trip.
* Broker unavailable: helper fails closed; git prints the broker status URL; no environment fallback.
* Tokens are never written to disk; `git credential-cache` is disabled in the session config.
* Works with `git lfs` (uses the same helper) and with `pnpm` registry auth via a matching `.npmrc` `_authToken` shim for the Forgejo npm registry.

**Interface contract**

Provides: `paperos-git-credential`, session git config fragment, `known_hosts` allowlist; consumed by PAP-96 (session launch), PAP-280 (sandbox image), PAP-46 (`worktree.sh`), PAP-498 (npm auth shim), PAP-219 controls.

Consumes: broker protocol and audit (PAP-300), token scopes (PAP-48), branch tooling (PAP-46), sandbox (PAP-280, soft).

**Definition of done**

* Session in the sandbox clones, pushes and runs `git lfs push` to both forges with no token in the environment or on disk (`grep` and `env` proof in the transcript).
* Denied repo yields a clear failure; broker down fails closed; `docs/engineering/agent-identities.md` git section; CHANGELOG under Security; Linear comment.

**Test plan**

* Unit: credential protocol parsing; host allowlist; cache expiry; broker error mapping.
* E2E: sandbox job: clone and push to the fixture repo on both forges through the helper; negative denied repo.

**Demo**

Reviewer opens a shell in the session sandbox, runs `env | grep -i token` (empty), `cat .git/config` (helper only), then `git push` succeeds and the broker audit shows the `get`. Under a minute.

**Edge cases**

* Token expires mid-push of a large repo: helper refreshes on the next `get`; git retries once by config.
* Repo renamed: `useHttpPath` scopes by path; the broker maps by id and answers for the new path.
* Developer laptop without a broker: helper detects no socket and exits 0 with no answer so the personal helper takes over.

**Dependencies**

Hard: PAP-300, PAP-48. Soft: PAP-46, PAP-280, PAP-521.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/app-shell/upgrade-package-registry` = PAP-498, `r4/forge/github-app-identities` = PAP-521.
