---
identifier: "PAP-523"
title: "Install and pin policy: pnpm `minimum-release-age`, `ignore-scripts` allowlist, lockfile integrity lint, action and image digest pinning lint in Gate 1"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P1"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Disaster recovery proven"
state: "Backlog"
parent: "PAP-358"
children: []
blockedBy: ["PAP-78", "PAP-505", "PAP-522"]
blocks: []
key: "r4/forge/supply-chain-install-policy"
url: "https://linear.app/paperos/issue/PAP-523/install-and-pin-policy-pnpm-minimum-release-age-ignore-scripts"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:01.297Z"
model: "claude-opus-5"
effort: "high"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-523: Install and pin policy: pnpm `minimum-release-age`, `ignore-scripts` allowlist, lockfile integrity lint, action and image digest pinning lint in Gate 1

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Infra S

**Goal**

PAP-358 spans install policy, pinning, provenance and signing; the first two are pure repository configuration and lint that can land the day Gate 1 exists and immediately protect twenty agents running `pnpm add`. Splitting them from the cosign work lets the cheap protection ship first.

**Scope**

In:

* `.npmrc` and `pnpm-workspace.yaml`: `minimum-release-age=3d` (with `minimumReleaseAgeExclude` for `@paperos/*`), `ignore-scripts=true` plus `pnpm.onlyBuiltDependencies` (`esbuild`, `sharp`, `@tauri-apps/cli`, `@biomejs/biome`), `verify-store-integrity=true`, registry pinned, `strict-peer-dependencies=false` documented.
* `scripts/check-lockfile.ts`: fails when `pnpm-lock.yaml` changes without a `package.json` change, when any dependency resolves to a git or tarball URL outside `imagine-os`, and when `pnpm audit signatures` reports unverifiable provenance for packages that publish it.
* `scripts/check-pins.ts`: every `uses:` pinned to a full SHA with a version comment; every `image:` in `ops/compose/**`, Dockerfiles and `devcontainer.json` pinned to `@sha256:`; Renovate `pinDigests` config (PAP-217).
* Gate 1 steps `lockfile` and `pins`; override mechanism: `# pin-exempt: <reason> until <date>` comments with expiry enforced.

Out: provenance attestations and signatures (PAP-524), vulnerability scanning (PAP-80), license policy (PAP-211).

**Spec**

* A package needing a postinstall not on the allowlist prints its name and the PR to add it requires Sentinel review (CODEOWNERS on `pnpm-workspace.yaml`).
* `minimum-release-age` override per package uses `pnpm.overrides` with an expiry comment checked by the lint.
* Both lints run under 10 s and print file, line and fix.

**Interface contract**

Provides: `.npmrc` policy, `check-lockfile.ts`, `check-pins.ts`, exemption comment grammar, Gate 1 steps; consumed by PAP-358 parent, PAP-217 (Renovate config), PAP-219 (`SEC-SUPPLY-*` controls), PAP-96 (worktree installs), PAP-254 (RC certification).

Consumes: Gate 1 workflow (PAP-78), Renovate (PAP-217, soft), threat model controls (PAP-219, soft).

**Definition of done**

* Fixtures: lockfile edit without manifest change fails; git URL dependency fails; unpinned `uses:` fails; template passes with all pins applied.
* `pnpm install` with a package published one day ago is refused (recorded); CHANGELOG under Security; Linear comment.

**Test plan**

* Unit: lockfile diff classifier; URL dependency detector; pin regexes for actions and images; exemption expiry parser.
* E2E: Gate 1 on a PR adding `uses: actions/checkout@v4` fails `pins`; after pinning passes.

**Demo**

Reviewer runs `pnpm add left-pad@latest` where the version is two days old and watches pnpm refuse; then adds an unpinned action and `pnpm check` fails naming the line. Under a minute.

**Edge cases**

* Urgent security fix younger than 3 days: override with expiry, flagged in the PAP-80 summary.
* Digest of a base image changes weekly: Renovate PR groups them (PAP-217).
* Tauri CLI postinstall downloads binaries: allowlisted with the checksum verified by the package itself.

**Dependencies**

Hard: PAP-78. Soft: PAP-217, PAP-219. Parent PAP-358; sibling PAP-524.

**Agent**

Builder: Forge (Ops Runner). Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/forge/supply-chain-provenance` = PAP-524.
