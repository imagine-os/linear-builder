---
identifier: "PAP-543"
title: "`paperos module new <id>`: scaffold the contract package, manifest, conformance skeleton, fixtures, memory double, docs stub, ownership entry and `kernel.ts` registration"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Contracts and conformance wired"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-305", "PAP-433", "PAP-441", "PAP-541"]
blocks: []
key: "r4/module-system/module-scaffold"
url: "https://linear.app/paperos/issue/PAP-543/paperos-module-new-id-scaffold-the-contract-package-manifest"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:04.924Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-27"
cycle: null
---

# PAP-543: `paperos module new <id>`: scaffold the contract package, manifest, conformance skeleton, fixtures, memory double, docs stub, ownership entry and `kernel.ts` registration

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Seventeen "Publish `@paperos/contract-<module>` v0.1" issues and every future module repeat the same forty-file layout by hand. Backstage, Nx and Terraform all ship a generator for exactly this reason. A scaffold means a cold session starts from a compiling, validating, conformance-ready skeleton and the layout never drifts between modules.

**Scope**

In:

* `paperos module new <id> --kind runtime|service|tooling|process --owner <agent> --project <key> --risk <level> [--port Name...] [--topic name...] [--slot id...]` in `packages/cli/src/module/new.ts`, templates in `templates/module/` copied from the sample module (PAP-542) with placeholders.
* Generates: `packages/contracts/<id>/` (`package.json` with `size-limit`, `src/{index,ports,events,routes,slots}.ts`, `conformance/{suite,memory}.ts`, `fixtures/.gitkeep`, `fixtures.lock`), `packages/<id>/` (`module.ts` via `defineModule`, `src/adapter.ts` stubs per port, `src/bind.ts`), `docs/platform/contracts/<id>.md` stub, `ownership.json` entries (PAP-305 `packages` and `contracts` sections), `flags.yaml` `module.<id>.impl`, registration lines in the three `kernel.ts` files (R8 exception), `undeclared.baseline.json` untouched.
* `--dry-run` prints the file tree; `--from-manifest <path>` fills ports, topics and slots from an existing manifest; idempotent rerun refuses to overwrite edited files.
* Post-generate checks: `pnpm modules:validate`, `pnpm lint:deps`, `pnpm conformance <id> --strict` (fails as expected until ports have cases, printed as the next step).

Out: writing real ports and fixtures (contract issues), the runner (PAP-441), publishing (PAP-498).

**Spec**

* Generated code compiles and validates immediately (`tsc`, `modules:validate`, R7 to R11) with zero edits.
* Templates are the sample module with `__id__` placeholders; a drift test regenerates the sample from the templates and diffs.
* Owner and project validated against the roster (PAP-103) and `plan.json` keys; unknown values refused.
* The generator writes a `.paperos/module-scaffold.json` record so `paperos upgrade` (PAP-430) can re-apply template fixes to scaffolded files marked `template`.

**Interface contract**

Provides: `paperos module new`, `templates/module/`, scaffold record; consumed by every remaining `Publish @paperos/contract-<module>` issue (PAP-447, PAP-448, PAP-449, PAP-456, PAP-459, PAP-462, PAP-465, PAP-466, PAP-467, PAP-474, PAP-475, PAP-476, PAP-483, PAP-484, PAP-485, PAP-492, PAP-493 can regenerate their skeletons), PAP-24 (guide), PAP-445 (docs stub).

Consumes: manifest schema (PAP-433), suite API (PAP-441), ownership file and rule generator (PAP-305), sample module templates, roster names (PAP-103, soft).

**Definition of done**

* `paperos module new demo --kind runtime --owner Forge --project module-system --risk low --port DemoPort` produces a tree that passes `pnpm check` and `modules:validate` with no edits (CI test); rerun refuses to overwrite.
* Drift test between templates and the sample green; `docs/platform/modules.md` "Create a module" section; CHANGELOG; Linear comment.

**Test plan**

* Unit: placeholder substitution; ownership merge; kernel registration insertion idempotency; owner and project validation.
* E2E: CI generates a module, runs the full check, deletes it; `--from-manifest` over the forge manifest reproduces its port list.

**Demo**

Reviewer runs `paperos module new demo --port DemoPort --dry-run`, reads the 24-file tree, runs it for real and `pnpm check` passes; `pnpm modules:list` shows `demo` bound. Under 2 minutes.

**Edge cases**

* Module id collides with an existing package or contract: refused with the path.
* Kind `process` (no runtime): skips `packages/<id>` runtime stubs and `kernel.ts` registration, keeps the contract and docs.
* Ownership file has a hand-edited entry for the id: merge keeps it and warns.

**Dependencies**

Hard: PAP-433, PAP-441, PAP-305. Soft: PAP-103, PAP-430, PAP-542.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/app-shell/upgrade-package-registry` = PAP-498, `r4/module-system/sample-module` = PAP-542.
