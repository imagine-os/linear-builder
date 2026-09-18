---
identifier: "PAP-509"
title: "Developer environment bootstrap: devcontainer, `pnpm setup`, `paperos dev` running compose, api, worker and web together, and `paperos doctor --toolchain` for Rust, Android and Xcode"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Desktop and mobile shells build"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-13", "PAP-42"]
blocks: []
key: "r4/app-shell/dev-environment-bootstrap"
url: "https://linear.app/paperos/issue/PAP-509/developer-environment-bootstrap-devcontainer-pnpm-setup-paperos-dev"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:28:59.363Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-24"
cycle: null
---

# PAP-509: Developer environment bootstrap: devcontainer, `pnpm setup`, `paperos dev` running compose, api, worker and web together, and `paperos doctor --toolchain` for Rust, Android and Xcode

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

A cold Claude session in a worktree needs one command to get Postgres, Electric, Hocuspocus, the API, the worker and the web app running with the right env. PAP-13 gives `pnpm dev` for web only, PAP-42 the compose stack, PAP-22 a `doctor` for tokens; nothing composes them or checks toolchains, and the orchestrator sandbox (PAP-280) needs a reproducible image. This issue is the DX layer that makes "clone and run" true.

**Scope**

In:

* `.devcontainer/devcontainer.json` and `Dockerfile` (Node 22, pnpm 10, Rust toolchain from `rust-toolchain.toml`, `libwebkit2gtk-4.1`, Playwright deps, `sops`, `age`, `restic` CLI) usable by VS Code, Codespaces and the PAP-280 sandbox image.
* `pnpm setup` (`scripts/setup.ts`): checks Node and pnpm versions, copies `.env.example` to `.env.local` if missing, runs `pnpm i --frozen-lockfile`, `pnpm env:check` (PAP-17), starts the PAP-42 stack, runs migrations and the demo seed (PAP-507), prints the URLs.
* `paperos dev [--only web,api,worker] [--no-stack]`: one process supervisor (`concurrently` with prefixed logs) running the compose stack, `apps/api`, `apps/worker`, `apps/web` and Electric; a `/__dev` status page listing services, ports, health and the current worktree database name.
* `paperos doctor --toolchain`: Rust, cargo, `tauri-cli`, Android SDK and `ANDROID_HOME`, Xcode and simulators (macOS only), `adb`, Playwright browsers; prints install commands per OS and never values of secrets (PAP-22 rule).

Out: the compose services themselves (PAP-42), the orchestrator sandbox runtime (PAP-280), the template guide prose (PAP-24; this issue supplies the commands it documents).

**Spec**

* Per-worktree isolation: `paperos dev` derives the database name and ports from the worktree path hash (PAP-42 convention) so twenty sessions run side by side.
* Idempotent: `pnpm setup` on a configured checkout finishes in under 20 s with all `[skip]`.
* `--json` output for the orchestrator (`{ services: [{ name, port, healthy }] }`).
* The devcontainer image is built weekly by CI and pushed to the Forgejo registry (PAP-273) and GHCR; `devcontainer.json` pins the digest (PAP-358 rule).

**Interface contract**

Provides: `pnpm setup`, `paperos dev`, `paperos doctor --toolchain`, `/__dev` page, devcontainer image `git.PAPEROS_DOMAIN/imagine-os/devcontainer`; consumed by PAP-24 (commands), PAP-92 (session playbook), PAP-280 (base image), PAP-96 (worktree launch), every builder session.

Consumes: workspace (PAP-13), compose stack and per-worktree databases (PAP-42), env check (PAP-17), migrations (PAP-32), seed (PAP-507, soft), registry (PAP-273, soft).

**Definition of done**

* Fresh clone in the devcontainer: `pnpm setup && paperos dev` serves web, api and worker with green health in under 4 minutes on a warm image (timed in CI).
* Two worktrees run `paperos dev` concurrently without port or database collision (test).
* `doctor --toolchain` output screenshots on Linux with and without Rust; `docs/template-guide.md` "Run it" section; CHANGELOG; Linear comment.

**Test plan**

* Unit: setup step planner with fakes (skip when configured); port and db derivation from paths; doctor parsers for `rustc --version`, `adb version`, `xcodebuild -version`.
* E2E: CI job builds the devcontainer, runs `pnpm setup` and `paperos dev --json`, asserts all services healthy, then runs the Playwright smoke against `/__dev`.

**Demo**

Reviewer opens the repo in a Codespace, runs `pnpm setup`, then `paperos dev`, opens `/__dev` and sees six green services and the demo accounts, then `paperos doctor --toolchain` listing what is missing for Android. Under 5 minutes wall clock.

**Edge cases**

* Docker unavailable (Codespaces without DinD): `--no-stack` prints instructions for a remote stack URL and `paperos dev` still runs the Node processes.
* Port already in use by another worktree: next free port chosen and printed.
* Rust missing: web and api still run; desktop commands print the install command from `doctor`.
* Corporate proxy: `pnpm setup` honours `HTTPS_PROXY` and prints the CA bundle hint.

**Dependencies**

Hard: PAP-13, PAP-42. Soft: PAP-17, PAP-32, PAP-507, PAP-273, PAP-280. Feeds PAP-24, PAP-92, PAP-96.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/app-shell/starter-kit-demo-seed` = PAP-507.
