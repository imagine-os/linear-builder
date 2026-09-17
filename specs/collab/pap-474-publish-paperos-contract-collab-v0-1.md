---
identifier: "PAP-474"
title: "Publish @paperos/contract-collab v0.1 with manifest"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P1"
type: "Spec"
priority: 2
surfaces: ["Developer"]
milestone: "Docs and prompt log stores"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-127", "PAP-128", "PAP-433"]
blocks: ["PAP-135", "PAP-137", "PAP-138", "PAP-410", "PAP-477", "PAP-480"]
key: "module/collab/contract"
url: "https://linear.app/paperos/issue/PAP-474/publish-paperoscontract-collab-v01-with-manifest"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:58:04.356Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-474: Publish @paperos/contract-collab v0.1 with manifest

**Model / Effort:** Sonnet 5 / high

**Goal**

Publish `@paperos/contract-collab` v0.1 and the `collab` module manifest so every other module codes against a versioned package instead of `packages/collab (docs, comments, notifications, prompt log), docs/` internals (`docs/module-system.md` sections 1 to 3). The contract holds only types, Zod schemas, event topics, route signatures, slot definitions and port interfaces; the implementation stays where the existing issues put it. Swap risk is declared `medium`, which decides how much of the swap playbook a rewrite must follow.

**Scope**

In:

* `packages/contracts/collab/` published as `@paperos/contract-collab` (workspace-private, `0.1.0`): `src/index.ts`, `ports.ts`, `events.ts`, `routes.ts`, `slots.ts` as applicable, an empty `conformance/` (filled by the conformance issue) and `fixtures/`.
* `module.ts` via `defineModule()` (PAP-264 shape) extended with `provides: [{ contract: '@paperos/contract-collab', version: '0.1.0' }]`, `requires`, `capabilities`, `slots`, `events`, `owner: { agent: 'Nova', project: 'collab' }`, `swapRisk: 'medium'`, `kind: 'runtime'`, plus the generated `module.manifest.json`.
* `ownership.json` `contracts` entry (PAP-305 file) and the generated `docs/platform/contracts/collab.md` (a `typedoc` stub until the docs generator lands).

Out: runtime behaviour, React, Drizzle tables, network calls; the conformance suite and the kernel binding (own issues). Nothing already fixed by PAP-127, PAP-128 is redesigned; it is packaged.

**Spec**

Ports and schemas exported at v0.1:

* `CommentAnchor` grammar (`entity:`, `element:`, `doc:`, `canvas:`, `shot:`; PAP-131) and `CommentPort` (`threads`, `create`, `resolve`, `escalate`)
* `DocsPort`: `list`, `render(path)`, `search`, `publish` for repo MDX and runtime docs (PAP-128, PAP-379)
* `PromptLogPort`: `writeSession`, `readSession`, `redact` (PAP-129), implementing agents' `PromptLogSink`
* `ChangelogPort` (PAP-133), `AdrRecord` schema (PAP-130), `NotificationPort` with the kinds registry and preferences (PAP-136)
* Slot fills: `shell.inspector:comments`, `record.panel.tabs:comments`, `shell.header.actions:notifications`

Events declared with `defineTopic()` (payload schemas, version 1): `comment.created|mentioned|resolved`, `doc.published`, `changelog.published`, `notification.sent`.

Requires (manifest `requires[]`): \* `@paperos/contract-data-layer` ^0.1

* `@paperos/contract-identity` ^0.1
* `@paperos/contract-realtime` ^0.1 (rooms for live docs and comments)
* `@paperos/contract-design-system` ^0.1

Rules: Zod 4 only, JSON Schema generated; no `z.bigint()` on wire schemas (PAP-302 codec); one sentence and one fixture per port method; `size-limit` under 50 KB minified; lint R9 passes; manifest `dependsOn` is derived from `requires`.

**Interface contract**

Provides: `@paperos/contract-collab@0.1.0` with the exports above; `module.manifest.json` valid against `manifest.schema.json`; `ownership.json` `contracts.collab`. Consumes: the manifest schema and validator (`module-system/manifest-schema`), contract-zero (`@paperos/core/types|filter|events`), the decisions in PAP-127 (Evaluate tldraw vs React Flow for the canvas and Tiptap vs B), PAP-128 (Build the docs engine: MDX docs stored in the repo, rendered). Consumed by: PAP-135 (prompt log browser), PAP-137 (screenshot annotations), PAP-138 (unified search), PAP-410 (support inbox), PAP-100 PM comments, PAP-216 library registry, and the module's conformance and wire issues.

**Test plan**

* Static: lint rules R7 to R9; generated JSON Schema committed and unchanged; `size-limit`; `tsc --noEmit` with `exactOptionalPropertyTypes`.
* Unit: every schema accepts its valid fixture and rejects its invalid one (fifteen anchors (three per grammar form, valid and malformed), four comment threads with resolution, two MDX docs with block ids, one redacted prompt log session, six notification kinds); `defineTopic` registrations resolve at import; the manifest validates and its `requires` resolve against the other manifests.
* Review: Quill confirms no implementation leaked into the package.

**Definition of done**

* Package merged, `0.1.0` in the workspace changeset; manifest validates; compatibility matrix shows every `requires` as `ok` or a named pending provider.
* `docs/platform/contracts/collab.md` generated; short ADR `docs/adr/00xx-contract-collab.md` recording what was pinned.
* Comments on PAP-135, PAP-137, PAP-138, PAP-410 that their Interface contract sections now import from `@paperos/contract-collab`; Linear comment here with the docs link.

**Edge cases**

* A port the implementation has not built yet: declared `@experimental` with a fixture; conformance marks it `pending`, never `passed`.
* A type two modules want (for example `Money`) belongs to contract-zero; the validator rejects a schema whose `$id` collides with a core one.
* Implementation disagrees with the contract after merge: the contract wins; the implementation issue gets a comment and a fix child.

**Dependencies**

Blocked by `module-system/manifest-schema` and PAP-127, PAP-128. Blocks PAP-135, PAP-137, PAP-138, PAP-410, `module/collab/conformance` and `module/collab/wire`. Soft: docs generator, compatibility matrix job.

**Agent**

Specified by Nova (In-App Collaboration & Knowledge owner). Reviewed by Quill and Atlas (contract ownership).

**Size**

M

**Demo**

Reviewer runs `pnpm contract:show collab`, parses the fifteen anchor fixtures and sees the malformed ones rejected with the grammar position. Under a minute.
