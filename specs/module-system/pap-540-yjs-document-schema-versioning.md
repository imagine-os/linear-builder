---
identifier: "PAP-540"
title: "Yjs document schema versioning: `ydocVersion` in the document meta, converter run on open through `CollabDocPort`, snapshot retention and the 20 MB guard"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Shell swap drill passes"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-32", "PAP-43", "PAP-140", "PAP-436", "PAP-443", "PAP-475", "PAP-564", "PAP-565"]
blocks: []
key: "r4/module-system/ydoc-converter"
url: "https://linear.app/paperos/issue/PAP-540/yjs-document-schema-versioning-ydocversion-in-the-document-meta"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:49:48.174Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-10-01"
cycle: null
---

# PAP-540: Yjs document schema versioning: `ydocVersion` in the document meta, converter run on open through `CollabDocPort`, snapshot retention and the 20 MB guard

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-443 covers four data shapes; the Yjs one needs Nova and the realtime contract rather than Drizzle. A swapped docs or canvas implementation must open documents written by the old one; this child gives collaborative documents the same expand-contract discipline as tables.

**Scope**

In:

* `ydocVersion` (integer) in the Yjs `meta` map, written by the collab doc port on first save; `defineMigrationAdapter({ kind: "ydoc", from, to, upcast })` registration in `packages/kernel/migrate` where `upcast(doc: Y.Doc): Y.Doc` is pure over a fresh doc built from the old update set.
* Open hook in `CollabDocPort` (PAP-475): if stored version < current, run the converter chain, write the new snapshot as a new Hocuspocus document version (PAP-140 persistence), keep the old snapshot until the swap CLI `remove` step; clients on the old implementation keep reading the old snapshot.
* Guard: converted document over the 20 MB cap fails the open with `YDOC_TOO_LARGE`, old snapshot stays, a Needs Justin card is created (PAP-443 rule).
* Fixtures: a v1 docs document and a v1 canvas overlay (PAP-321 shapes) with converters to v2 and tests that `upcast(v1) == v2` structurally.

Out: tables, events and API shapes (PAP-443 sibling), the Hocuspocus server (PAP-140), the editors (PAP-142, PAP-132).

**Spec**

* Converters never mutate stored updates; they produce a new document and snapshot.
* Chain application is ordered and idempotent; converting a current-version doc is a no-op.
* Conversion runs server-side on open, under 2 s for a 5 MB document; larger documents convert in a PAP-43 job with the client shown a `converting` state (PAP-234).
* Awareness and presence (PAP-141) are not versioned; only persisted content is.

**Interface contract**

Provides: `ydocVersion` convention, ydoc adapter kind, open hook, `YDOC_TOO_LARGE`; consumed by PAP-443 (kit completeness), PAP-442 (destructive detection reads ydoc adapters), PAP-379 (runtime docs store), PAP-132 (canvas overlay), PAP-142.

Consumes: Hocuspocus persistence (PAP-140), `CollabDocPort` (PAP-475), jobs (PAP-43, soft), state components (PAP-234, soft).

**Definition of done**

* Fixture v1 documents open as v2 through the hook; the v1 snapshot still loads with the old implementation bound (test with two impls in the kernel).
* Oversized conversion fails safely; `docs/platform/migrations.md` Yjs section; Linear comment.

**Test plan**

* Unit: chain ordering; no-op on current version; structural equality of converted fixtures; size guard.
* E2E: compose stack: open a v1 doc through the API, assert new snapshot version and old snapshot retained in Postgres.

**Demo**

Reviewer opens a seeded v1 document in the docs editor and sees it render under the v2 schema; `SELECT version FROM ydoc_snapshot WHERE doc_id = ...` shows both versions. Under a minute.

**Edge cases**

* Two clients open the same old doc simultaneously: conversion is serialised per document with an advisory lock; the second waits.
* Converter throws on a malformed v1 doc: open fails with the error, old snapshot untouched, finding filed.
* Document created by a newer implementation opened by an older one during canary: refused with `YDOC_VERSION_AHEAD`, never downgraded silently.

**Dependencies**

Hard: PAP-140, PAP-475. Sibling: PAP-443. Soft: PAP-43, PAP-234, PAP-379, PAP-321.

**Agent**

Builder: Nova (CRDT Engineer). Reviewer: Sentinel (Edge Case Hunter).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* de-parented from PAP-443 (FIX-R4-1: this issue is an add-on to its former parent's core scope, which is a claimable leaf again). PAP-443 blocks this issue (`blocks` relation).
