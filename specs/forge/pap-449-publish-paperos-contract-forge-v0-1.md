---
identifier: "PAP-449"
title: "Publish @paperos/contract-forge v0.1 with manifest"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Developer"]
milestone: "CI runs on both forges"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-44", "PAP-46", "PAP-433"]
blocks: ["PAP-51", "PAP-276", "PAP-452", "PAP-455", "PAP-526", "PAP-535"]
key: "module/forge/contract"
url: "https://linear.app/paperos/issue/PAP-449/publish-paperoscontract-forge-v01-with-manifest"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:28:56.600Z"
model: "claude-opus-5"
effort: "high"
estimate: 2
dueDate: "2026-09-24"
cycle: null
---

# PAP-449: Publish @paperos/contract-forge v0.1 with manifest

**Model / Effort:** Opus 5 / high

**Goal**

Publish `@paperos/contract-forge` v0.1 and the `forge` module manifest so every other module codes against a versioned package instead of `ops/forgejo, packages/forge (client), .forgejo/workflows` internals (`docs/module-system.md` sections 1 to 3). The contract holds only types, Zod schemas, event topics, route signatures, slot definitions and port interfaces; the implementation stays where the existing issues put it. Swap risk is declared `medium`, which decides how much of the swap playbook a rewrite must follow.

**Scope**

In:

* `packages/contracts/forge/` published as `@paperos/contract-forge` (workspace-private, `0.1.0`): `src/index.ts`, `ports.ts`, `events.ts`, `routes.ts`, `slots.ts` as applicable, an empty `conformance/` (filled by the conformance issue) and `fixtures/`.
* `module.ts` via `defineModule()` (PAP-264 shape) extended with `provides: [{ contract: '@paperos/contract-forge', version: '0.1.0' }]`, `requires`, `capabilities`, `slots`, `events`, `owner: { agent: 'Forge', project: 'forge' }`, `swapRisk: 'medium'`, `kind: 'service'`, plus the generated `module.manifest.json`.
* `ownership.json` `contracts` entry (PAP-305 file) and the generated `docs/platform/contracts/forge.md` (a `typedoc` stub until the docs generator lands).

Out: runtime behaviour, React, Drizzle tables, network calls; the conformance suite and the kernel binding (own issues). Nothing already fixed by PAP-44, PAP-46 is redesigned; it is packaged.

**Spec**

Ports and schemas exported at v0.1:

* `ForgePort`: `repos.list`, `repos.get`, `tree`, `blob`, `commits`, `pulls.list|get|create|merge`, `mirrorStatus`, `bootstrap(spec)` (PAP-51, PAP-276)
* `RepoRef`, `CommitRef`, `PullRequestRef`, `MirrorState` value types with the Linear trailer grammar (PAP-46)
* `BootstrapSpec` (mirrors, secrets, labels, webhooks, branch protection; PAP-51)
* Webhook envelope normalisation: `forge.push`, `forge.pr.opened|merged|closed`, `forge.ci.finished` into the PAP-303 envelope with `actor.type='service'`
* `CiRunnerContract`: which runner produced which PAP-239 artefact, so gates read results from either forge

Events declared with `defineTopic()` (payload schemas, version 1): `forge.push`, `forge.pr.opened|merged|closed`, `forge.ci.finished`, `forge.mirror.lagging`.

Requires (manifest `requires[]`): \* `@paperos/contract-identity` ^0.1 (OIDC principal for SSO; PAP-226)

* `@paperos/contract-quality` ^0.1 (gate artefact schemas)

Rules: Zod 4 only, JSON Schema generated; no `z.bigint()` on wire schemas (PAP-302 codec); one sentence and one fixture per port method; `size-limit` under 50 KB minified; lint R9 passes; manifest `dependsOn` is derived from `requires`.

*Round 4 amendment (2026-09-18):*

* `ForgePort` also exports `pulls.review(pr, { verdict, findings })` and `checks.set(sha, { name, status, summaryUrl })` so Gate 2 (PAP-81, PAP-243) and the merge automation (PAP-527) post verdicts and required checks through the contract on both forges instead of calling the GitHub and Forgejo APIs directly; the Forgejo adapter maps `checks.set` to commit statuses. `mirrorStatus` reads `mirror-status.json` from PAP-520.

**Interface contract**

Provides: `@paperos/contract-forge@0.1.0` with the exports above; `module.manifest.json` valid against `manifest.schema.json`; `ownership.json` `contracts.forge`. Consumes: the manifest schema and validator (`module-system/manifest-schema`), contract-zero (`@paperos/core/types|filter|events`), the decisions in PAP-44 (Write ADR: keep Git as the format, self-host Forgejo, mirror), PAP-46 (Define branch protection, conventional commits and worktree-). Consumed by: PAP-276 (forge client and oRPC procedures), PAP-51 (bootstrap), PAP-52 (release tags), PAP-97 (PR status back to Linear), PAP-278 (PR pages), and the module's conformance and wire issues.

**Test plan**

* Static: lint rules R7 to R9; generated JSON Schema committed and unchanged; `size-limit`; `tsc --noEmit` with `exactOptionalPropertyTypes`.
* Unit: every schema accepts its valid fixture and rejects its invalid one (four repo trees, three PR lifecycles (open, merge, close), two mirror states (in sync, lagging), five webhook payloads from Forgejo and GitHub normalised to the same envelope); `defineTopic` registrations resolve at import; the manifest validates and its `requires` resolve against the other manifests.
* Review: Sentinel confirms no implementation leaked into the package.

**Definition of done**

* Package merged, `0.1.0` in the workspace changeset; manifest validates; compatibility matrix shows every `requires` as `ok` or a named pending provider.
* `docs/platform/contracts/forge.md` generated; short ADR `docs/adr/00xx-contract-forge.md` recording what was pinned.
* Comments on PAP-276, PAP-51 that their Interface contract sections now import from `@paperos/contract-forge`; Linear comment here with the docs link.

**Edge cases**

* A port the implementation has not built yet: declared `@experimental` with a fixture; conformance marks it `pending`, never `passed`.
* A type two modules want (for example `Money`) belongs to contract-zero; the validator rejects a schema whose `$id` collides with a core one.
* Implementation disagrees with the contract after merge: the contract wins; the implementation issue gets a comment and a fix child.

**Dependencies**

Blocked by `module-system/manifest-schema` and PAP-44, PAP-46. Blocks PAP-276, PAP-51, `module/forge/conformance` and `module/forge/wire`. Soft: docs generator, compatibility matrix job.

**Agent**

Specified by Forge (Version Control & Forge Independence owner). Reviewed by Sentinel and Atlas (contract ownership).

**Size**

S

**Demo**

Reviewer runs `pnpm contract:show forge` and sees `ForgePort`; runs the fixture normaliser on a GitHub and a Forgejo push payload and gets byte-identical envelopes. Under a minute.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/forge/merge-automation` = PAP-527, `r4/forge/mirror-drift-monitor` = PAP-520.
