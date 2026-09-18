---
identifier: "PAP-572"
title: "Local data protection for PGlite and Tauri caches: sign-out and revocation wipe, `cacheable: false` shapes for sensitive tables, encrypted-column sync lint and the device data policy in page specs"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Local-first sync working"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-271"]
blocks: []
key: "r4/data-layer/local-data-protection"
url: "https://linear.app/paperos/issue/PAP-572/local-data-protection-for-pglite-and-tauri-caches-sign-out-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:09.642Z"
model: "claude-opus-5"
effort: "high"
estimate: 2
dueDate: "2026-09-25"
cycle: null
---

# PAP-572: Local data protection for PGlite and Tauri caches: sign-out and revocation wipe, `cacheable: false` shapes for sensitive tables, encrypted-column sync lint and the device data policy in page specs

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build S

**Goal**

Local-first means tenant data sits in IndexedDB and in the Tauri app data directory on every laptop and phone. PAP-271 persists it, PAP-353 keeps secrets out of shapes, but nothing wipes it on sign-out or session revocation, nothing lets a spec say a dataset must never be cached, and nothing tells a lost-device story. This closes that hole before customers see the sync demo.

**Scope**

In: `packages/sync/src/protection/{wipe,policy}.ts`, `SyncClient.wipe({ keepOutbox })`, sign-out and `session.revoked` handlers, shape option `cacheable: false` (query-through, no PGlite persistence), page-spec key `sync.localData: cached|session|never` (PAP-114), registry lint refusing `encrypted()` columns and `pii kind: credential|financial` columns in shapes unless `cacheable: false`, Tauri data directory permissions and optional OS-level encryption check, `docs/platform/local-data.md`.

Out: Field encryption itself (PAP-353), OS full-disk encryption enforcement, remote device management, session revocation UI (PAP-220).

**Spec**

* Sign-out (PAP-223 client event) and `session.revoked` (PAP-220, via the push transport when present, else on the next 401) call `wipe()`: drop PGlite tables, clear `_sync_meta`, clear `y-indexeddb` databases for the tenant, keep `_outbox` only when the user confirms 'keep unsent changes' and the policy allows.
* `cacheable: false` shapes are served through `useShape` from memory only; a reload refetches; the option is forced for tables flagged by the lint.
* Page spec `sync.localData`: `cached` (default), `session` (wiped when the tab or app closes), `never` (no PGlite rows for the page's datasets); codegen (PAP-120) passes it to the data hooks.
* Tauri: app data directory created with `0700`; on macOS and Windows the app checks FileVault or BitLocker status through a small plugin call and shows a one-time notice when off; Android uses app-private storage (PAP-260).
* Tenant switch (PAP-58 `useTenant` remount) wipes the previous tenant's PGlite tables unless the user has the `multi-tenant cache` preference on.
* Audit: wipe events logged locally and, when online, as `client.wiped` with reason for PAP-356.

**Interface contract**

Provides: `wipe()`, shape option `cacheable`, spec key `sync.localData`, registry lint rule, `LocalDataNotice` component, docs.

Consumes: PGlite client and registry (PAP-271), sign-out event (PAP-223), revocation (PAP-220, soft), push transport (PAP-599, soft), `pii.json` (PAP-559, soft), encrypted columns (PAP-353, soft), spec schema (PAP-114), Tauri shims (PAP-259, PAP-260, soft). Consumed by PAP-148 (outbox keep decision), PAP-62 security page copy, PAP-219 controls `SEC-CLIENT-*`.

**Definition of done**

* Sign out wipes PGlite and `y-indexeddb`; revocation from another device wipes within one request cycle (Playwright with two contexts).
* Registry lint fails for a shape including an `encrypted()` column and passes with `cacheable: false`; spec `never` leaves zero rows in PGlite (test).
* Tauri Linux and macOS runs show the data directory permissions and the notice; docs; CHANGELOG under Security; Linear comment with the recording.

**Test plan**

* Unit: wipe ordering and `keepOutbox` logic, policy resolution from spec and shape options, lint fixtures, tenant-switch wipe decision.
* E2E: two browser contexts: sign in, sync the demo shape, revoke the session from the second context, assert the first context clears its local database and redirects; `sync.localData: never` page leaves no rows.

**Demo**

Reviewer loads the sync demo, inspects IndexedDB in DevTools, signs out and sees the databases disappear; then marks a shape `cacheable: false` and reloads to see it refetch. Under 90 seconds.

**Edge cases**

* Wipe while offline with unsent changes: prompt once; declining keeps `_outbox` encrypted with a session-derived key until the next sign-in of the same user.
* Shared kiosk device (PAP-23): policy `session` forced by the kiosk flag.
* Private browsing (in-memory PGlite): wipe is a no-op with a log line.
* Very large local database: wipe is asynchronous with a blocking overlay under 5 s.

**Dependencies**

Blocked by PAP-271 (hard). Soft: PAP-223, PAP-220, PAP-353, PAP-114, PAP-259, PAP-260, PAP-559, PAP-599. Consumed by PAP-148, PAP-62, PAP-219.

**Agent**

Builder: Forge (Platform Engineer) with Nova (CRDT Engineer). Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/data-layer/pii-registry` = PAP-559, `r4/realtime/live-events-channel` = PAP-599.
