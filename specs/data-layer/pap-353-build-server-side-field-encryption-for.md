---
identifier: "PAP-353"
title: "Build server-side field encryption for stored secrets (OAuth tokens, SCIM and webhook secrets, connector credentials, TOTP seeds) with envelope keys, key rotation and a leak scanner"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer", "Staff"]
milestone: "Tenant-safe and observable"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-17", "PAP-32"]
blocks: ["PAP-190", "PAP-193", "PAP-222", "PAP-230"]
key: "security/field-encryption"
url: "https://linear.app/paperos/issue/PAP-353/build-server-side-field-encryption-for-stored-secrets-oauth-tokens"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:36.624Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-353: Build server-side field encryption for stored secrets (OAuth tokens, SCIM and webhook secrets, connector credentials, TOTP seeds) with envelope keys, key rotation and a leak scanner

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — security-sensitive title keyword: encrypt

**Goal**

Five issues (PAP-190, PAP-65/PAP-230, PAP-174, PAP-199, PAP-193) say their tokens are "encrypted via app-shell/env-config helpers"; PAP-17 only defines client keychains. This issue supplies the server-side primitive: envelope encryption for designated columns with a master key from sops, per-tenant data keys, transparent Drizzle helpers, rotation without downtime, and a scanner that fails CI when a secret-shaped column is stored in the clear.

Merges `gap/data-layer/field-encryption` (round-2 data-layer gap, same deliverable; merged 2026-09-17, FIX-6). From it: encrypted columns are marked `secret` in the PAP-41 data dictionary, and PAP-174 automation connector credentials and PAP-199 import connector PATs are adopters.

**Scope**

* In: `packages/db/src/crypto/` (`encrypted()` column helper, `Keyring`, `rotate`), `data_key` table, master key loading from sops (`FIELD_MASTER_KEY`), migration helpers for existing columns, `pnpm db:rotate-keys`, `pnpm db:scan-secrets`, audit redaction registration (PAP-38 `paperos.audit_redactions`), docs `docs/data/field-encryption.md`.
* Out: client-side storage (PAP-17), full-disk or Postgres TDE, KMS integration (documented as the upgrade path), hashing of API keys (Better Auth plugin already hashes, PAP-60).

**Spec**

* Algorithm: AES-256-GCM via Node `crypto`; ciphertext stored as `bytea` in the form `v1 || key_id(16) || iv(12) || tag(16) || data`; additional authenticated data is `<table>.<column>.<row id>` so ciphertext cannot be moved between rows.
* Keys: `data_key (id uuid, tenant_id uuid null, wrapped_key bytea, master_key_id text, created_at, retired_at)`; one active data key per tenant plus one platform key; wrapped with the master key (`FIELD_MASTER_KEY`, 32 bytes, from sops per PAP-25; env schema entry added to `serverEnvSchema` in PAP-17); master key id in ciphertext header enables multi-master rotation.
* Drizzle helper: `encrypted(name, { tenantColumn: 'tenant_id' })` produces a `customType` with `toDriver`/`fromDriver` that encrypts on write and decrypts on read inside the API process only; the `paperos_readonly` role and Electric never see plaintext because decryption happens in application code, and encrypted columns are excluded from shapes by the PAP-36 registry check.
* Rotation: `pnpm db:rotate-keys --master` re-wraps all data keys (seconds); `--data --tenant <id>` re-encrypts rows in batches of 500 with `SELECT ... FOR UPDATE SKIP LOCKED`, resumable, both keys valid during the run; retired keys kept until no ciphertext references them (`pnpm db:key-usage`).
* Scanner: `pnpm db:scan-secrets` inspects schema for columns named `*token*|*secret*|*credential*|*private_key*|totp*|*api_key*` that are not `encrypted()` and samples 100 rows per encrypted column asserting the `v1` header; runs in Gate 1 and fails on findings; allowlist with expiry in `packages/db/src/crypto/allowlist.yaml`.
* Redaction: every encrypted column is auto-registered in `paperos.audit_redactions` so PAP-38 diffs show `[encrypted]`; OTel span processor (PAP-40) already drops payloads.
* Adoption: connector credentials (PAP-121 registry), OAuth tokens for social and Webflow (PAP-190, PAP-193), SCIM bearer tokens and SAML private keys (PAP-230, PAP-231), webhook endpoint secrets (PAP-222), TOTP secrets and backup codes (PAP-220 stores hashed codes; TOTP seed encrypted), import connector PATs (PAP-199).

**Interface contract**

* Provides: `encrypted()` column type, `encryptValue(tenantId, aad, plaintext)`, `decryptValue(...)`, `Keyring.active(tenantId)`, CLI `db:rotate-keys`, `db:scan-secrets`, `db:key-usage`, event `crypto.key_rotated`.
* Consumers: PAP-190, PAP-193, PAP-199, PAP-222, PAP-230, PAP-231, PAP-220, PAP-121 connector registry; PAP-219 controls `SEC-DATA-*`; PAP-80 Semgrep rule `plaintext-secret-column` references the scanner allowlist.
* Requires: PAP-32 Drizzle workflow, PAP-17 env schema, PAP-25 sops master key, PAP-38 redaction table.

**Definition of done**

* Round-trip tests for every adopting table; ciphertext differs per row for the same plaintext; moving ciphertext between rows fails authentication.
* Master and data key rotation on a seeded tenant with 50k rows completes with zero read failures under concurrent reads (bench recorded).
* `db:scan-secrets` fails on a seeded plaintext `oauth_token` column and passes after adoption.
* `paperos_readonly` psql session shows only ciphertext; audit diff shows `[encrypted]`.
* Docs; changelog under "Security"; Linear comment with bench numbers.

**Test plan**

* Unit: encrypt/decrypt vectors, AAD binding, header parsing, allowlist expiry.
* Integration: PGlite plus Drizzle helpers; rotation with concurrent readers; scanner against a fixture schema.
* Perf: p95 overhead of an encrypted column read under 1 ms per row at 1k rows.
* No UI.

**Demo**

Insert a connector token through the API, `SELECT` the row as `paperos_readonly` and see bytes, read it through the API and see the token, run `pnpm db:rotate-keys --master` and read again. Ninety seconds.

**Edge cases**

* Master key missing at boot: API refuses to start with a clear error (fail closed), never falls back to plaintext.
* Tenant deleted while a data key is active: key retired with the tenant purge (PAP-355).
* Row copied by an import or export: exports (PAP-205) exclude encrypted columns by default; `--include-secrets` requires owner re-authentication.
* Search over encrypted columns is impossible by design; a deterministic `hmac_lookup` column helper is provided for equality lookups (for example webhook secret id).
* PGlite local-first clients: encrypted columns never sync; the shape registry lint blocks them.

**Dependencies**

Blocked by PAP-32, PAP-17. Blocks PAP-222, PAP-190, PAP-193, PAP-230. Soft: PAP-38, PAP-40, PAP-25.

**Agent**

Built by Forge (Schema Wright sub-agent); reviewed by Sentinel (Security Auditor).

**Size**

M
