---
identifier: "PAP-433"
title: "Specify the module manifest schema and validator: provides, requires, capabilities, slots, events, owner and swap risk on top of PAP-264"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Developer"]
milestone: "Kernel and lint live"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-264", "PAP-265", "PAP-434", "PAP-436", "PAP-438", "PAP-439", "PAP-440", "PAP-441", "PAP-445", "PAP-447", "PAP-448", "PAP-449", "PAP-456", "PAP-459", "PAP-462", "PAP-465", "PAP-466", "PAP-467", "PAP-474", "PAP-475", "PAP-476", "PAP-483", "PAP-484", "PAP-485", "PAP-492", "PAP-493"]
key: "module-system/manifest-schema"
url: "https://linear.app/paperos/issue/PAP-433/specify-the-module-manifest-schema-and-validator-provides-requires"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:49:47.383Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-433: Specify the module manifest schema and validator: provides, requires, capabilities, slots, events, owner and swap risk on top of PAP-264

**Model / Effort:** Opus 5 / high

**Goal**

Fix the one data shape the whole Module System hangs on: the module manifest. PAP-264 defines `ModuleManifest` for routes, entities, jobs and `dependsOn`; this issue specifies the extension that makes a module swappable (`provides`, `requires` with semver ranges and named ports, `capabilities`, `slots.exposes|fills`, `events.publishes|subscribes`, `owner`, `kind`, `swapRisk`) as a Zod schema in `packages/core/src/modules/manifest.ts`, the generated JSON Schema, and a validator that seventeen contract issues run before they can merge. `docs/module-system.md` section 1.2 is the prose; this issue is the code.

**Scope**

In:

* `manifest.ts`: Zod schema (fields per the document), `defineModule()` overload accepting the extension, `validateManifest(manifest, { others })` returning diagnostics with stable codes (`REQUIRES_UNRESOLVED`, `REQUIRES_RANGE_MISMATCH`, `DEPENDS_ON_DISAGREES`, `SLOT_UNKNOWN`, `TOPIC_UNDECLARED`, `OWNER_UNKNOWN`, `CYCLE`).
* `pnpm gen:schemas` emitting `manifest.schema.json` (`$id https://paperos.dev/schema/module-manifest/1`); committed and drift-checked.
* `pnpm modules:validate` CLI over every `module.manifest.json` in the workspace, exit code and a table.
* Golden manifests for the seventeen modules and the kernel under `packages/core/src/modules/fixtures/` (provides and requires per `docs/module-system.md` table 1.1), plus eight invalid ones.
* `docs/platform/manifest.md` field reference.

Out: the registry runtime (registry issue), the compatibility matrix job, generating manifests from code.

**Spec**

* `requires[].range` is a semver range; pre-1.0 `^0.x` semantics; `optional: true` means the consumer boots without the provider and receives `undefined` from `resolve`.
* `dependsOn` (PAP-264) is derived from `requires`; if both are present they must agree or `DEPENDS_ON_DISAGREES`.
* `slots.fills[].slot` must be declared in some module's `slots.exposes`; `events.publishes` must match topics declared in that module's contract package; checked when the contract package exists, warned otherwise.
* `owner.agent` is one of the nine roster names; `owner.project` one of the project keys in `plan.json`.
* `kind` is `runtime|service|tooling|process|kernel`; `swapRisk` is `low|medium|high|critical`; both required.
* The validator is pure and synchronous (usable in Vite config and the server), as PAP-264 requires of `loadModules`.

**Interface contract**

Provides: `ModuleManifest` (extended), `defineModule`, `validateManifest`, `manifest.schema.json`, `pnpm modules:validate`, `pnpm gen:schemas`, the seventeen golden manifests. Consumes: PAP-264 base fields (soft; this issue lands first and PAP-264 adopts it), `plan.json` project keys, the roster names (PAP-103). Consumed by: every `Publish @paperos/contract-<module>` issue, the registry, the compatibility matrix, the dependency map, the docs generator, PAP-264, PAP-265, PAP-266.

**Test plan**

* Unit: each golden manifest validates; each invalid fixture fails with exactly its expected code; `dependsOn` derivation matches `requires`.
* Property (fast-check): random `requires` graphs with and without cycles; `CYCLE` names the cycle path.
* Static: generated JSON Schema committed and identical on regeneration; `ajv` validates the golden manifests against it (schema and Zod agree).
* Type: `defineModule` infers `settingsSchema` and the `provides` contract names as literal types.

**Definition of done**

* Schema, validator, CLI and golden manifests merged; JSON Schema committed; Biome and typecheck clean; 100 percent coverage on `manifest.ts`.
* PAP-264 has a comment pointing to the schema it must adopt; `docs/module-system.md` table 1.1 and `docs/platform/manifest.md` agree with the fixtures.
* ADR `docs/adr/00xx-module-manifest.md`; Linear comment with the docs link.

**Edge cases**

* A module that provides two contracts (realtime provides rooms and push transport as one package): allowed; `provides[]` lists both.
* Two implementations of one contract in one workspace (`impl` differs): allowed; same `impl` twice is `DUPLICATE_PROVIDER`.
* A `process` module with no routes, entities or slots: valid; the schema requires only identity, owner, provides, requires and swap risk.
* Contract version in `provides` does not match the contract package `package.json` version: `PROVIDES_VERSION_MISMATCH` when the package is resolvable.

**Dependencies**

None hard; pure package on the PAP-13 layout (soft: PAP-13 for the workspace, PAP-264 for the base manifest shape, which this issue defines the extension of). Blocks PAP-264, PAP-265.

**Agent**

Built by Atlas. Reviewed by Forge and Sentinel.

**Size**

S

**Demo**

Reviewer runs `pnpm modules:validate` and sees eighteen manifests green in a table with provides and requires counts; edits `tables` to require `@paperos/contract-collab ^0.2` and the run fails with `REQUIRES_RANGE_MISMATCH` naming both modules and versions. Under a minute.
