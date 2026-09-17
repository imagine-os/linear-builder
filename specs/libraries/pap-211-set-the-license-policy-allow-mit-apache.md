---
identifier: "PAP-211"
title: "Set the license policy (allow MIT/Apache/BSD, review AGPL, block SSPL) enforced by a CI license check"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P0"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Evaluation process"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-209"]
blocks: ["PAP-216"]
key: "libraries/license-policy"
url: "https://linear.app/paperos/issue/PAP-211/set-the-license-policy-allow-mitapachebsd-review-agpl-block-sspl"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T05:19:20.893Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-211: Set the license policy (allow MIT/Apache/BSD, review AGPL, block SSPL) enforced by a CI license check

**Goal**

Make license surprises impossible: a written policy (allow permissive, review copyleft and source-available, block SSPL and unlicensed) and a CI job that scans every JavaScript and Rust dependency on every PR, fails on violations and honours a waiver file with expiry. PAP-80 reserved the job slot; PAP-127 (tldraw) and PAP-188 (AGPL products) depend on the tiers.

**Scope**

In:

* `docs/libraries/license-policy.md` and `ops/licenses/policy.yaml` (tiers per context).
* CI job `licenses` in `security.yml` (or `licenses.yml` if PAP-80 is unmerged) producing `reports/licenses.json`, SARIF and a summary; runs on Forgejo Actions.
* `ops/licenses/waivers.yaml` with expiry; fixtures for allow, review, block, waived, expired.
* `THIRD_PARTY_NOTICES.md` generated at build for web and Tauri bundles.
* `deny.toml` for `cargo-deny` mirroring the tiers, skipping cleanly until `Cargo.lock` exists.
* One Needs Justin question: the license of PaperOS's own template code.

Out: scoring (PAP-209), vulnerability scanning (PAP-80), legal advice.

**Spec**

* Contexts derived automatically: `bundled` (deps of `apps/*` and packages they import), `server` (`apps/api`, `ops/`), `dev` (devDependencies), `service` (declared by hand for PAP-215 products).
* Allow everywhere: MIT, Apache-2.0, BSD-2/3-Clause, ISC, 0BSD, Unlicense, CC0-1.0, Zlib, BlueOak-1.0.0, Python-2.0, MPL-2.0 unmodified, OFL-1.1 and CC-BY-4.0 for assets. Review (ADR plus waiver): LGPL and GPL in `dev` and `service` only, AGPL-3.0 `service` only, BUSL-1.1, ELv2, WTFPL, `SEE LICENSE IN` texts such as tldraw's. Block: SSPL-1.0, Commons Clause, JSON, `UNLICENSED` or missing, any copyleft in `bundled`.
* Scanner `ops/licenses/check.ts`: `pnpm licenses list --json --prod` plus `pnpm ls --json` for contexts; SPDX via `spdx-expression-parse` and `spdx-satisfies` (OR passes if any branch allowed, AND needs all); LICENSE file text wins over a disagreeing `license` field and flags `mismatch`. Rust via `cargo deny check licenses`.
* Waiver `{ package, versionRange, license, context, reason, adr, approvedBy: Justin|Atlas, expires }`; Atlas may approve `review`, `block` needs Justin; expired fails.
* Private workspace packages and uninstalled optional peers skipped; budget under 90 s.

**Interface contract**

Provides: `policy.yaml` tiers consumed as data by PAP-209's license gate and PAP-216's `license` field verification, `reports/licenses.json` `{ status, scanned, violations: [{ package, version, license, context, tier, waiver?, reason }], warnings, notices }`, status `licenses`, waivers schema, `pnpm licenses:check` and `pnpm licenses:notices`, `deny.toml`. Consumes: PAP-78 setup action and job slot, PAP-80 SARIF merge (soft), PAP-130 ADR links (soft). Consumers: PAP-217 (report delta on Renovate PRs, required status), PAP-216, PAP-212 to PAP-215 (spike lockfiles), PAP-218 (`block` tier filter).

**Definition of done**

* Policy doc, `policy.yaml`, waivers schema, scanner, `deny.toml`, notices generator merged.
* Real CI run on a seeded fake SSPL package fails with an inline annotation; screenshot attached.
* `THIRD_PARTY_NOTICES.md` produced by `pnpm build` and bundled in Tauri resources.
* Sentinel Security Auditor approves; own-code license question filed to Needs Justin with a default.
* CHANGELOG; Linear comment linking policy and a sample report.

**Test plan**

* Vitest fixtures: allowed, review without waiver (fail), waived (pass), expired waiver (fail), `(MIT OR Apache-2.0)`, `(GPL-3.0 AND MIT)`, field and file mismatch, missing license, GPL dev tool moved to `dependencies` (fail), lockfile out of sync (fast fail).
* CI: seeded violation branch red; clean `main` green under 90 s.
* Notices: snapshot of the generated file for the template.

**Demo**

Reviewer adds a fake SSPL package to a branch, pushes, and watches the `licenses` check fail with the package, tier and context annotated inline; reverts and sees green plus `THIRD_PARTY_NOTICES.md` in the build output. Under two minutes.

**Edge cases**

* tldraw `SEE LICENSE IN LICENSE.md` with watermark clause: review, waiver referencing the PAP-127 ADR.
* Dual license passes; `AND` with copyleft is review.
* GPL CLI in `dev`: allowed with note, blocked if it moves to `dependencies`.
* Fonts and icons (OFL, ISC, MIT): allowed as assets, notices generated.
* Lockfile stale: fail fast rather than scan stale data.

**Dependencies**

PAP-209 (hard: gate references tiers; draft acceptable). Soft: PAP-80, PAP-78, PAP-130. Blocks PAP-216 (license verification) and informs PAP-217.

**Agent**

Built by Scout (Library Evaluator) with Forge (Ops Runner) for CI. Reviewed by Sentinel (Security Auditor) and Atlas.

**Size**

M: two ecosystems, SPDX parsing and context derivation need care; the policy text is a day.
