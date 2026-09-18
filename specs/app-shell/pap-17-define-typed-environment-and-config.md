---
identifier: "PAP-17"
title: "Define typed environment and config layer with per-target secret storage (web, desktop keychain, mobile secure storage)"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P0"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Template scaffolds and runs on web"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-13"]
blocks: ["PAP-20", "PAP-259", "PAP-260", "PAP-353", "PAP-366", "PAP-368", "PAP-404", "PAP-444", "PAP-447", "PAP-501", "PAP-502", "PAP-510", "PAP-813"]
key: "app-shell/env-config"
url: "https://linear.app/paperos/issue/PAP-17/define-typed-environment-and-config-layer-with-per-target-secret"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:56:40.693Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-20"
cycle: null
---

# PAP-17: Define typed environment and config layer with per-target secret storage (web, desktop keychain, mobile secure storage)

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

One typed, validated configuration layer shared by web, desktop and mobile, with client-side secrets stored in the right place per target (browser: never persisted; desktop: OS keychain; mobile: Keychain or Keystore) so agent-written code cannot leak a key into a bundle. Server-side encryption of stored secrets is a separate data-layer issue (field encryption gap); runtime feature flags move to the app-shell runtime-flags issue; this issue only provides the env-level bootstrap `VITE_FLAGS`.

**Scope**

In:

* `packages/core/src/config/`: Zod 4 `publicEnvSchema` (`VITE_*`) and `serverEnvSchema`; accessors `publicEnv`, `serverEnv`.
* `.env.example`, `.env.test`, gitignored `.env.local`; `pnpm env:check`.
* `SecretStore` with `WebSecretStore`, `TauriKeychainStore` (`keyring` crate via Tauri command), `MobileSecureStore` (Tauri secure-storage plugin).
* Vite plugin failing the build when any non-`VITE_` variable reaches the bundle.

Out: remote flag service, per-tenant settings, auth token lifecycle (PAP-57), server-side field encryption.

**Spec**

* `publicEnvSchema`: `VITE_API_URL`, `VITE_APP_NAME`, `VITE_GIT_SHA`, `VITE_ELECTRIC_URL`, `VITE_YJS_URL`, `VITE_SENTRY_DSN?`, `VITE_FLAGS?` (comma list, bootstrap only).
* `serverEnvSchema`: `DATABASE_URL`, `DATABASE_URL_MIGRATOR`, `S3_*`, `BETTER_AUTH_SECRET`, `BETTER_AUTH_URL`, `STRIPE_SECRET_KEY?`, `OTEL_EXPORTER_OTLP_ENDPOINT?`, `APP_ENCRYPTION_KEY?` (consumed by the field-encryption issue), `NODE_ENV`.
* Parse once at module load; failure throws a table of missing keys.
* `SecretStore`: `get`, `set`, `delete`, `list`; keys namespaced `paperos.<app>.<key>`.
* `getTarget(): 'web'|'desktop'|'ios'|'android'` via `window.__TAURI_INTERNALS__` then UA fallback.
* Rust commands `secret_get|set|delete` in `apps/desktop/src-tauri/src/commands/secrets.rs`; capability limited to the main window.
* `docs/shell/config.md`: which vars go where, CI and Coolify supply, rotation.

**Interface contract**

Provides (from `@paperos/core/config`):

* `publicEnv: PublicEnv`, `serverEnv: ServerEnv` (Zod-inferred), `publicEnvSchema`, `serverEnvSchema` (other packages extend with `.extend()` and register the extension in `config/registry.ts`).
* `SecretStore` interface and `getSecretStore()`; `getTarget()`, type `Target`.
* Tauri command names `secret_get`, `secret_set`, `secret_delete` (used by PAP-57 for session tokens).
* Env names are the contract for PAP-25 sops files, PAP-26 Coolify injection and PAP-30 role URLs.

Consumes: nothing beyond PAP-13. PAP-19 mounts the Rust commands; until then the desktop backend is compiled but unreachable.

**Definition of done**

* `pnpm env:check` passes on `.env.example` and fails with a table when a key is removed.
* Vitest: schemas, target detection, `WebSecretStore`; Rust keychain round-trip test (skipped without a keychain, noted).
* Bundle guard proven: a test build with a stray `SECRET=` import fails.
* Linux `secret-service` and macOS Keychain round-trips recorded; settings debug page screenshots at 375, 1024, 1920.
* Docs, `.env.example`, CHANGELOG; Linear comment with recording links.

**Test plan**

* Unit: schema parsing (missing, empty string, bad URL), `getTarget()` under four fake globals, `WebSecretStore` session semantics.
* Rust: `cargo test` for `secrets.rs` with the `keyring` mock backend.
* Build: CI step builds `apps/web` with `LEAK_TEST=1` and asserts the plugin fails.
* Tree-shaking: `size-limit` asserts `serverEnvSchema` is absent from the web bundle.
* Visual: `/settings/debug` page at 375, 1024, 1920 showing target and public config.

**Demo**

Reviewer removes `VITE_API_URL` from `.env.local`, runs `pnpm env:check` and reads the table; restores it, runs `pnpm dev:desktop`, opens Settings, stores a test secret, quits, relaunches and sees it read back from the OS keychain. Under 2 minutes on Linux or macOS.

**Edge cases**

* Headless Linux without a secret service: encrypted-file fallback with a loud warning.
* Empty string counts as missing.
* Two windows setting the same key: last write wins; `list()` is immediate.
* Vitest reads `.env.test` only, never `.env.local`.
* Android Keystore values over 4 KB: chunk or reject with a clear error.

**Dependencies**

PAP-13 (hard). PAP-19 for native backends (either merge order). Consumed by PAP-20, PAP-22, PAP-26, PAP-35, PAP-37, PAP-57, the runtime-flags and field-encryption issues.

**Agent**

Built by Forge (Tauri Smith for native stores). Reviewed by Sentinel (Security Auditor).

**Size**

M: small TS surface plus one Rust command set.
