---
identifier: "PAP-42"
title: "Ship the local dev stack: docker compose with Postgres 17, MinIO, Mailpit and Hocuspocus, per-worktree databases and a SessionStart hook so parallel Claude sessions never share state"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P0"
type: "Infra"
priority: 1
surfaces: ["Developer"]
milestone: "Postgres + Drizzle baseline"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-13"]
blocks: ["PAP-32"]
key: "data-layer/local-dev-stack"
url: "https://linear.app/paperos/issue/PAP-42/ship-the-local-dev-stack-docker-compose-with-postgres-17-minio-mailpit"
source: "plan/specs/gaps.json (round-1 canonical spec JSON)"
---

# PAP-42: Ship the local dev stack: docker compose with Postgres 17, MinIO, Mailpit and Hocuspocus, per-worktree databases and a SessionStart hook so parallel Claude sessions never share state

**Goal**

Give every Claude Code session, every CI job and Justin's laptop an identical, disposable backing stack in one command, so that the dozens of parallel sessions this plan relies on never collide on a shared database. `data-layer/drizzle-schema` already references `ops/compose/dev.yml` for its CI job and `libraries/backend-landscape` scores libraries on their `docker compose up` story, but no issue creates that file or the isolation rules. This issue does, and it is the reason `data-layer/drizzle-schema` no longer needs the production VPS before it can start.

**Scope**

In:
- `ops/compose/dev.yml`: `postgres` (`pgvector/pgvector:pg17`, `wal_level=logical` for Electric later, init script creating roles `paperos_owner`, `paperos_app`, `electric`), `minio` (S3 API on 9000, console on 9001, bucket `paperos-dev` created by an init job), `mailpit` (SMTP 1025, UI 8025, used by `identity/better-auth` magic links locally), `hocuspocus` placeholder service enabled by profile `--profile realtime` once `realtime/yjs-server` publishes an image; profiles `core`, `realtime`, `sync` (Electric), `full`.
- `pnpm stack up|down|reset|logs` scripts in `packages/config-scripts` wrapping compose with the project name derived from the git worktree: `paperos-<branch-slug>` so two worktrees run two stacks on different host ports (port offset derived from a hash of the branch, printed on `up`).
- Per-worktree database: `DATABASE_URL` written to `.env.local` by `pnpm stack up`; database name `paperos_<branch-slug>`; `pnpm stack reset` drops and recreates it and re-runs `pnpm db:migrate && pnpm db:seed minimal`.
- `.devcontainer/devcontainer.json` (Node 22, pnpm, Docker-in-Docker) so GitHub Codespaces and Claude Code on the web get the same stack; `postCreateCommand: pnpm i && pnpm stack up`.
- `.claude/hooks/session-start.sh` registered in `.claude/settings.json` as a `SessionStart` hook: starts the stack for the current worktree if not running, applies migrations, prints the URLs and `DATABASE_URL`, and exits non-zero with a readable message when Docker is unavailable (the `pm-linear/session-playbook` tells sessions what to do then).
- CI: reusable workflow `ci-services.yml` exposing the same services as GitHub Actions service containers with identical env names, so tests written locally pass in CI unchanged (`quality/ci-gate1` consumes it).
- `docs/dev/local-stack.md`: commands, ports, reset semantics, how to run two worktrees at once, how to point at staging instead.

Out: production or staging Postgres (`data-layer/postgres-provision`), Forgejo locally (`forge/forgejo-deploy` runbook covers a local instance), Kubernetes, Tilt or Nix.

**Spec**

- Host ports: base 5432/9000/9001/8025/1234 plus `offset = hash(branch) % 50 * 100`; the offset is deterministic so a session can reconnect after restart.
- Compose project name and DB name are derived by `packages/config-scripts/src/worktree.ts` (`git rev-parse --abbrev-ref HEAD`, slugified, max 40 chars); `main` maps to offset 0.
- Data volumes are per project name, so `pnpm stack down` keeps data and `pnpm stack reset` removes it; `pnpm stack prune` removes stacks for branches that no longer exist.
- `pnpm stack up` completes in under 60 s on a warm image cache and waits for `pg_isready` before returning.
- Seeds come from `data-layer/drizzle-schema` when present; until then the hook prints "no migrations yet" and succeeds.
- The hook is safe to run concurrently (flock on `.stack.lock`).

**Definition of done**

- Two worktrees on different branches run `pnpm stack up` simultaneously and each connects to its own database on different ports (terminal transcript attached).
- Fresh clone plus `pnpm i && pnpm stack up && pnpm test` passes with zero manual steps on Linux and macOS (GitHub Actions matrix log for Linux; macOS run recorded once).
- Claude Code session started in a worktree shows the hook output and can run `pnpm db:migrate` immediately (screenshot of the session start).
- `ci-services.yml` used by at least one Vitest job hitting Postgres.
- Mailpit shows a message sent by a smoke test through `SMTP_URL` (screenshot).
- `docs/dev/local-stack.md`, `CHANGELOG.md` entry, Linear comment.

**Edge cases**

- Docker not installed or daemon down (common in a fresh Claude Code web session): hook prints install instructions and the option `PAPEROS_STACK=remote` to use the shared staging database read-only; tests requiring a database are skipped with a visible warning, not silently passing.
- Port collision with an unrelated local service: `pnpm stack up --offset <n>` override, persisted in `.env.local`.
- Branch names with slashes and unicode: slug function tested; collisions after truncation append a 4-char hash.
- Apple Silicon: `pgvector/pgvector:pg17` is multi-arch; verify `minio` and `mailpit` tags are too.
- Stale volumes from many branches filling disk: `pnpm stack prune` and a note in the session playbook's end-of-session checklist.
- CI service containers do not support compose profiles: the reusable workflow lists services explicitly and asserts the env names match `dev.yml` via a unit test.

**Dependencies**

`app-shell/monorepo-scaffold` (scripts folder, `.claude/` folder). Unblocks `data-layer/drizzle-schema` (which no longer waits for the VPS), `identity/better-auth` (Mailpit), `data-layer/file-storage` (MinIO), `realtime/yjs-server` (local profile), `quality/ci-gate1` (service containers), `pm-linear/session-playbook` (hook behaviour). Soft: `app-shell/env-config` for env names.

**Agent**

Built by Forge (Platform Engineer). Reviewed by Sentinel (Code Reviewer) and Atlas (who owns the session playbook and must confirm the hook contract).

**Size**

S: compose files and scripts, but it removes a hidden shared-state hazard from every later build session.
