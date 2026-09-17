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
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:05:40.395Z"
model: "claude-sonnet-5"
effort: "medium"
---

# PAP-42: Ship the local dev stack: docker compose with Postgres 17, MinIO, Mailpit and Hocuspocus, per-worktree databases and a SessionStart hook so parallel Claude sessions never share state

**Goal**

Give every Claude Code session, CI job and Justin's laptop an identical, disposable backing stack in one command so the dozens of parallel sessions never collide on a shared database. This is why PAP-32 no longer waits for the VPS.

**Scope**

In:

* `ops/compose/dev.yml`: `postgres` (`pgvector/pgvector:pg17`, `wal_level=logical`, init roles), `minio` (bucket `paperos-dev`), `mailpit`, `hocuspocus` placeholder; profiles `core`, `realtime`, `sync`, `full`.
* `pnpm stack up|down|reset|logs|prune` in `packages/config-scripts`, project name and ports derived from the git worktree.
* Per-worktree `DATABASE_URL` written to `.env.local`; `.claude/hooks/session-start.sh` runs `stack up`, migrations and seeds when present.
* Reusable `ci-services.yml` with the same service versions and env names.
* `docs/dev/local-stack.md`.

Out: production services, schema (PAP-32).

**Spec**

* Ports: base 5432, 9000, 9001, 8025, 1234 plus `offset = hash(branch) % 50 * 100`; `main` is offset 0; deterministic across restarts.
* `worktree.ts` slugifies `git rev-parse --abbrev-ref HEAD` to 40 chars; truncation collisions append a 4-char hash.
* Volumes per project name: `down` keeps data, `reset` removes, `prune` removes stacks for deleted branches.
* `stack up` under 60 s warm, waits for `pg_isready`, holds `flock .stack.lock`.
* `PAPEROS_STACK=remote` uses the shared staging database read-only when Docker is missing; database tests skip with a visible warning.
* `ci-services.yml` env names asserted against `dev.yml` by a unit test.

**Interface contract**

Provides:

* Scripts `pnpm stack *`; env written to `.env.local`: `DATABASE_URL`, `DATABASE_URL_MIGRATOR`, `S3_ENDPOINT`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_BUCKET=paperos-dev`, `SMTP_URL`, `YJS_URL`, `ELECTRIC_URL` (names from PAP-17).
* Roles `paperos_owner`, `paperos_app`, `paperos_readonly`, `electric` identical to PAP-30 so PAP-34 tests run locally.
* Reusable workflow `imagine-os/paperos-template/.github/workflows/ci-services.yml` with service containers for PAP-78 and every Vitest job that needs Postgres, MinIO or Mailpit.
* Hook `.claude/hooks/session-start.sh` contract for PAP-93: prints stack status, ports and next steps; exit 0 always.

Consumes: scripts folder and `.claude/` (PAP-13).

**Definition of done**

* Two worktrees on different branches run `stack up` simultaneously and connect to different databases on different ports (transcript).
* Fresh clone plus `pnpm i && pnpm stack up && pnpm test` passes on Linux and macOS with zero manual steps.
* A Claude Code session in a worktree shows the hook output and can run `db:migrate` immediately (screenshot).
* `ci-services.yml` used by at least one Vitest job hitting Postgres; Mailpit shows a smoke-test message (screenshot).
* `docs/dev/local-stack.md`; CHANGELOG; Linear comment.

**Test plan**

* Unit: slug function on slashes, unicode and long names; port offset determinism; env-name parity between `dev.yml` and `ci-services.yml`.
* Integration: CI job starts two stacks with different `--offset` and asserts distinct `pg_isready` ports; `reset` drops data; `prune` removes a stack for a deleted branch.
* Hook: run in a fresh worktree with and without Docker; assert messages and exit 0.
* Smoke: SMTP send to Mailpit, S3 put to `paperos-dev`, `SELECT 1` via `paperos_app`.

**Demo**

Reviewer creates a second worktree with `scripts/worktree.sh new PAP-999`, runs `pnpm stack up` in both, sees two different port sets printed, connects with `psql` to each and then runs `pnpm stack prune` after deleting the branch. Under 2 minutes with warm images.

**Edge cases**

* Docker missing: install instructions and the `remote` option; never silent passes.
* Port collision: `--offset <n>` persisted.
* Apple Silicon: all images multi-arch, verified.
* Disk full of stale volumes: `prune` plus the end-of-session checklist in PAP-93.
* CI has no compose profiles: services listed explicitly.

**Dependencies**

PAP-13 (hard). Soft: PAP-17. Unblocks PAP-32, PAP-57, PAP-37, PAP-140, PAP-78, PAP-93.

**Agent**

Built by Forge (Platform Engineer). Reviewed by Sentinel (Code Reviewer).

**Size**

S: one compose file, one script package, one hook.
