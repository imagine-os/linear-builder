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
blocks: ["PAP-20", "PAP-259", "PAP-260"]
key: "app-shell/env-config"
url: "https://linear.app/paperos/issue/PAP-17/define-typed-environment-and-config-layer-with-per-target-secret"
source: "plan/specs/bucket-0.json (round-1 canonical spec JSON)"
---

# PAP-17: Define typed environment and config layer with per-target secret storage (web, desktop keychain, mobile secure storage)

**Goal**

Provide one typed, validated configuration layer shared by web, desktop and mobile, with secrets stored in the right place on each target (browser: never; desktop: OS keychain; mobile: secure enclave/Keystore) so agent-written code cannot accidentally leak a key into a bundle.

**Scope**

In:
- `packages/core/src/config/`: Zod 4 schemas for public config (`VITE_*`, safe to ship) and server config (API, DB, S3, auth), typed accessors `publicEnv`, `serverEnv`.
- `.env.example`, `.env.test`, per-app `.env.local` gitignored; `pnpm env:check` fails on missing/invalid keys.
- Secret storage abstraction `SecretStore` with three backends: `WebSecretStore` (in-memory, session only, warns), `TauriKeychainStore` (via `tauri-plugin-stronghold` or `keyring` crate through a Tauri command), `MobileSecureStore` (Tauri 2 plugin `tauri-plugin-secure-storage`, iOS Keychain and Android EncryptedSharedPreferences).
- Runtime feature flags read from config with a `Flags` type and `useFlag('name')` hook.
- Build-time guard: Vite plugin fails the build if any non-`VITE_` env var appears in output.

Out: remote flag service, per-tenant settings (data layer), auth tokens lifecycle (`identity/better-auth` uses `SecretStore`).

**Spec**

- `publicEnvSchema`: `VITE_API_URL` (url), `VITE_APP_NAME`, `VITE_GIT_SHA`, `VITE_ELECTRIC_URL`, `VITE_YJS_URL`, `VITE_SENTRY_DSN` (optional), `VITE_FLAGS` (comma list).
- `serverEnvSchema`: `DATABASE_URL`, `DATABASE_URL_MIGRATOR`, `S3_ENDPOINT`, `S3_BUCKET`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `BETTER_AUTH_SECRET`, `BETTER_AUTH_URL`, `STRIPE_SECRET_KEY` (optional), `OTEL_EXPORTER_OTLP_ENDPOINT` (optional), `NODE_ENV`.
- Parsing happens once at module load; failure throws with a table of missing keys, never partially loads.
- `SecretStore` interface: `get(key): Promise<string|null>`, `set(key, value)`, `delete(key)`, `list()`; keys namespaced `paperos.<app>.<key>`.
- Target detection: `getTarget(): 'web'|'desktop'|'ios'|'android'` using `window.__TAURI_INTERNALS__` and `navigator.userAgent` fallback.
- Tauri side: Rust command `secret_get/set/delete` in `apps/desktop/src-tauri/src/secrets.rs` using `keyring` 3.x; capability file limits to the main window.
- Documentation `docs/shell/config.md`: which vars go where, how CI supplies them (GitHub/Forgejo secrets, Coolify env), rotation procedure.

**Definition of done**

- `pnpm env:check` passes with `.env.example` and fails with a clear table when a key is removed.
- Vitest: schema parsing, target detection, `WebSecretStore` behaviour; Rust unit test for keychain round-trip (skipped when no keychain available in CI, with a note).
- Build guard proven: a test build with a stray `SECRET=` in a `VITE_`-less import fails.
- Desktop manual check on Linux (`secret-service`) and macOS Keychain recorded as a short screen recording; screenshots of the settings debug page at 375, 1024, 1920.
- Docs and CHANGELOG updated; `.env.example` complete.
- Linear comment with PR and recording links.

**Edge cases**

- Linux without a running secret service (headless kiosk): fall back to an encrypted file with a loud warning; documented.
- Env var present but empty string: treated as missing.
- Same key set from two windows: last write wins; `list()` reflects it immediately.
- Bundle size: schemas must tree-shake so the server schema never reaches the browser.
- Test environment must not read `.env.local`; Vitest uses `.env.test` only.
- Value length above 4 KB on Android Keystore-backed storage: chunk or reject with error.

**Dependencies**

`app-shell/monorepo-scaffold` (hard). `app-shell/tauri-desktop` for native backends (the web backend ships first; native backends land behind the target check). Consumed by `identity/better-auth`, `data-layer/api-layer`, `data-layer/file-storage`.

**Agent**

Built by Forge (Tauri Smith for native stores). Reviewed by Sentinel (Security Auditor primary, Code Reviewer secondary).

**Size**

M: small surface but three platform backends and a build guard that must be airtight.
