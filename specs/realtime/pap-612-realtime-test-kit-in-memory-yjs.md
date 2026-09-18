---
identifier: "PAP-612"
title: "Realtime test kit: in-memory Yjs provider, awareness simulator, fake shape stream, network chaos helpers and two-context Playwright fixtures published from the realtime contract"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Record sync and conflict UX"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-140", "PAP-326"]
blocks: []
key: "r4/realtime/test-kit"
url: "https://linear.app/paperos/issue/PAP-612/realtime-test-kit-in-memory-yjs-provider-awareness-simulator-fake"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:16.806Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-28"
cycle: null
---

# PAP-612: Realtime test kit: in-memory Yjs provider, awareness simulator, fake shape stream, network chaos helpers and two-context Playwright fixtures published from the realtime contract

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Every project that touches multiplayer writes the same test scaffolding: a fake provider for editor stories, two browser contexts for presence, a way to make the shape stream lag or the socket drop. PAP-478's memory doubles serve conformance, not feature tests; PAP-313, PAP-319, PAP-411 and PAP-342 all need this kit, and a cold builder session should import it instead of inventing one.

**Scope**

In: `packages/contracts/realtime/testing/` exported as `@paperos/contract-realtime/testing`: `createMemoryProvider(room)` implementing `CollabDocPort` with synchronous peer fan-out and optional latency, `AwarenessSimulator` (`join(peer)`, `move`, `select`, `idle`, `leave`, scripted traces from PAP-478 fixtures), `FakeShapeStream(table)` emitting rows, tombstones, 409 handle invalidation and lag, `NetworkChaos` (`offline()`, `dropSocket()`, `slow(ms)`, `flap(n)`) wired into the provider, shape client and outbox; Playwright fixtures `twoContexts`, `asAudience` (on PAP-240 `loginAs`), `collabRoom`, `measurePropagation()`; Storybook decorators `withMockProvider`, `withPeers(n)`; docs `docs/platform/realtime/testing.md`.

Out: Conformance suite and golden fixtures (PAP-478), load generation (PAP-601, which reuses the client pool), test-mode seed endpoints (PAP-240).

**Spec**

* Memory provider passes the `CollabDocPort` conformance cases from PAP-478 except capacity ones (`unsupported`), so features tested against it behave like production for merge semantics.
* `FakeShapeStream` speaks the same handle and offset protocol as PAP-271's client so `useShape`, `useRecord` and the reconciler run unmodified; chaos hooks inject at the transport layer, never by mocking hooks.
* `measurePropagation()` stamps edits with `performance.now()` in context A and reads the DOM in context B, reporting p50 and p95, the same method PAP-328 and PAP-141 use so budgets are comparable.
* Fixtures are deterministic: seeded RNG for peer colours and ids; traces replayable; no real timers unless `realTime: true`.

**Interface contract**

Provides: `createMemoryProvider`, `AwarenessSimulator`, `FakeShapeStream`, `NetworkChaos`, Playwright fixtures, Storybook decorators, docs.

Consumes: Provider interface (PAP-140), shape client and registry (PAP-271, PAP-326), outbox (PAP-272), reconciler events (PAP-327), conformance fixtures (PAP-478, soft), `loginAs` (PAP-240, soft), Playwright projects (PAP-246, soft). Consumed by PAP-313, PAP-319, PAP-342, PAP-411, PAP-603 stories, PAP-608, PAP-610.

**Definition of done**

* Editor core stories and the conflict components run on the memory provider and fake stream with no server; a chaos test drops the socket mid-edit and asserts merge on reconnect (Vitest).
* `twoContexts` and `measurePropagation` used by at least one presence test; docs with three recipes (editor story, offline test, conflict test); changelog; Linear comment.

**Test plan**

* Unit: memory provider fan-out and latency, awareness trace replay determinism, fake stream protocol including 409, chaos state transitions.
* E2E: a Playwright spec using the fixtures against the compose stack passes both with the fake stream and the real Electric container.

**Demo**

Run `pnpm test --filter collab -t chaos` and read the drop-and-merge assertion; open Storybook 'Editor / with peers' showing three simulated carets with no server. Under a minute.

**Edge cases**

* Test forgets to close the provider: fixture teardown closes and warns.
* Fake stream and real Electric disagree: the conformance run against both surfaces it (PAP-478 real-adapter job).
* Storybook in CI without workers: simulator runs on the main thread.

**Dependencies**

Blocked by PAP-140 and PAP-326 (hard). Soft: PAP-271, PAP-272, PAP-327, PAP-478, PAP-240, PAP-246. Consumed by PAP-313, PAP-319, PAP-342, PAP-411 and the round-4 realtime issues.

**Agent**

Builder: Nova (CRDT Engineer) with Sentinel (Edge Case Hunter) on chaos helpers. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 4 round-4 file keys in this description to Linear identifiers: `r4/realtime/conflict-ux-impl` = PAP-608, `r4/realtime/editor-core` = PAP-603, `r4/realtime/headless-client` = PAP-610, `r4/realtime/load-harness` = PAP-601.
