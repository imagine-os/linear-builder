---
identifier: "PAP-280"
title: "Build the agent runtime sandbox: per-session container, worktree mount, CPU/RAM/time limits and network isolation with the credential broker's egress proxy as the only route"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P0"
type: "Infra"
priority: 1
surfaces: ["Agent", "Developer"]
milestone: "Roster defined and installed"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-25", "PAP-298", "PAP-300"]
blocks: []
key: "agents/runtime-sandbox"
url: "https://linear.app/paperos/issue/PAP-280/build-the-agent-runtime-sandbox-per-session-container-worktree-mount"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:09.917Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-280: Build the agent runtime sandbox: per-session container, worktree mount, CPU/RAM/time limits and network isolation with the credential broker's egress proxy as the only route

**Goal**

Give every Claude session a wall it cannot talk its way through: each session runs in a per-session container that mounts only its worktree, has bounded CPU, memory, pids and wall clock, and has no network route except the egress proxy owned by PAP-300. This issue owns the container, the worktree mount and the resource limits. The proxy, the per-character allowlist and credential injection belong to PAP-300; the hook policy the image ships belongs to PAP-298. PAP-106 admits its hook is best-effort; this is the isolation it defers to. Split on 2026-09-17 (FIX-6) from a trio that each defined the egress allowlist and the no-secrets rule.

**Scope**

* In: `ops/sandbox/` image and runner (`Dockerfile.session`, `run-session.sh`), `runInSandbox()` in the orchestrator launcher (`launchSession` gains `sandbox: true`), the internal Docker network with the broker proxy as its only route, resource limits by Size, worktree bind mount, orphan sweep, escape probes for filesystem, network route and limits, `docs/agents/sandbox.md`.
* Out: egress proxy container, allowlist generation and credential injection (PAP-300); deny rules and the PreToolUse hook (PAP-298, PAP-106); forge branch protection (PAP-46); VPS provisioning (PAP-25).

**Spec**

* Runtime: rootless Docker (or Podman) on the VPS; image Node 22, git, pnpm, gh, Playwright deps, the PAP-106 hooks and the compiled `agent-deny.json` from PAP-298 (the launcher refuses to start a container whose policy digest is stale); read-only root filesystem except `/work` (the worktree bind mount), `/tmp` and the pnpm store cache; `--cap-drop ALL`, `--security-opt no-new-privileges`, seccomp default profile, `--pids-limit 512`, CPU 2, RAM 4 GB, session wall clock 3 h (configurable per Size).
* Network: containers attach to the internal `sandbox` network that has no default route; the only reachable host is the broker egress proxy (`PAPEROS_PROXY=http://egress:3128`, PAP-300); the sandbox proves the route property (a direct `curl https://example.com` fails at the network layer, not at the proxy). Which hosts the proxy allows per character and which credentials it injects is the broker's concern.
* Environment: the container receives only `broker:*` placeholders and non-secret configuration; the orchestrator's own keys, Postgres superuser, Coolify and sops keys never enter; a probe script asserts on every start that `env` contains no value matching `ghp_|lin_api_|sk-ant-|sk_test_|sk_live_`.
* Worktree: bind-mounted from `/srv/worktrees/<key>`; git pushes go through the proxy, which injects the character's forge token (PAP-48 or default bot, minted by the broker).
* Cleanup: container removed on session end; orphan sweep every 10 minutes; `SandboxHandle.kill` is what PAP-111 `kill` calls.

**Interface contract**

* Provides: `runInSandbox(spec: { worktree, character, env, limits }): SandboxHandle` with `exec`, `kill`, `stats`; image tag `paperos/session:<sha>`; network `sandbox`; events `sandbox.started`, `sandbox.killed`, `sandbox.limit_hit`.
* Consumers: PAP-282 (`launchSession` wraps `query()` execution in the container), PAP-106 (hooks run inside), PAP-110 runner (`sandbox: true`), PAP-111 (`kill`), PAP-288 (`stats`).
* Requires: PAP-25 VPS with Docker; PAP-300 proxy image, network name and placeholder contract; PAP-298 compiled policy; PAP-104 roster (character to Size and limits).

**Definition of done**

* Probe suite inside a running sandbox: cannot read `/srv/repos` of other issues, cannot reach `postgres:5432`, `coolify` or any host except the proxy, can reach Linear and the forge through the proxy; results table attached.
* No production credential present: `env` dump diffed against the placeholder set in CI.
* Limits enforced: a fork bomb and a 6 GB allocation are killed; timing recorded; a stale policy digest refuses to start (test).
* Orchestrator launches a real session in the sandbox and opens a PR (recording).
* Docs; changelog; Linear comment with table and recording.

**Test plan**

* Unit: limit computation by Size; policy digest check; network spec generation.
* Integration: `ops/sandbox/test/probes.sh` run in CI on a self-hosted runner (PAP-50) against a stub proxy; env-diff assertion.
* e2e: staging session through the sandbox and the real broker proxy.
* No UI.

**Demo**

Run `pnpm sandbox probe --character beacon`: watch a direct `curl https://example.com` fail with no route, a `curl` through the proxy to `api.linear.app` succeed, and `env | grep -c -E 'ghp_|lin_api_|sk-ant-'` print 0. One minute.

**Edge cases**

* Playwright needs Chromium: included in the image; `--shm-size 1g`.
* Session needs a host not on the allowlist: the proxy denies and logs `egress-denied`; the fix is the character's `access[]` in the broker rules, never a sandbox change.
* Docker daemon restart: orphan sweep reattaches or kills; claims released by the orchestrator.
* Disk pressure from images: nightly prune keeps two tags.
* Rootless Docker unavailable: fall back to a dedicated `sandbox` user with cgroups v2 limits and nftables rules that allow only the proxy; documented as degraded; the broker's degraded mode (short-lived tokens in env) applies.
* Broker not yet merged when this starts: build against a stub proxy that allows everything and injects nothing (branch-start rule); the DoD probe that needs real injection waits for the broker.

**Dependencies**

Blocked by PAP-25, PAP-300 (proxy, allowlist, injection) and PAP-298 (hook policy shipped in the image). Blocks nothing hard: PAP-106 runs its hooks inside the sandbox once it exists (soft), PAP-96 and PAP-282 enable `sandbox: true` when it merges (soft). Soft: PAP-48, PAP-50, PAP-104.

**Agent**

Built by Forge (Ops Runner sub-agent); reviewed by Sentinel (Security Auditor).

**Size**

M (proxy and allowlist moved to the broker)
