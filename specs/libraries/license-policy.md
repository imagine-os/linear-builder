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
source: "plan/specs/bucket-8.json (round-1 canonical spec JSON)"
---

# PAP-211: Set the license policy (allow MIT/Apache/BSD, review AGPL, block SSPL) enforced by a CI license check

**Goal**

Make license surprises impossible: a written policy (allow permissive, review copyleft and source-available, block SSPL and unlicensed) and a CI job that scans every JavaScript and Rust dependency on every PR, fails on violations, and honours a waiver file for approved exceptions. `quality/security-scans` reserved a job slot for this; `collab/collab-research` (tldraw) and `growth/growth-research` (AGPL products) already depend on the tiers.

**Scope**

In:
- Policy doc `docs/libraries/license-policy.md` and machine config `ops/licenses/policy.yaml` (tiers per usage context).
- CI job `licenses` in `.github/workflows/security.yml` (or `licenses.yml` if that file is not merged) producing `reports/licenses.json`, SARIF and a job summary, runnable on Forgejo Actions.
- Waivers `ops/licenses/waivers.yaml` with expiry, plus Vitest fixtures for allow, review, block, waived and expired cases.
- `THIRD_PARTY_NOTICES.md` generation for shipped bundles (Tauri and web) at build time.
- `deny.toml` for `cargo-deny` mirroring the tiers, skipping cleanly until `Cargo.lock` exists (`app-shell/tauri-desktop`).
- One Needs Justin question: the license of PaperOS's own template code (currently the placeholder from `app-shell/monorepo-scaffold`).

Out: scoring libraries (`libraries/eval-rubric`), vulnerability scanning (`quality/security-scans`), legal advice.

**Spec**

- Contexts: `bundled` (shipped in web or native bundles, strictest), `server` (runs in our containers), `dev` (build and test tooling only), `service` (separately deployed OSS product). Derived automatically: `dependencies` of `apps/*` and `packages/*` imported by apps are `bundled`; `apps/api` and `ops/` are `server`; `devDependencies` are `dev`; `service` entries are declared by hand for products from `libraries/oss-products`.
- Tiers (SPDX ids). Allow in all contexts: MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, 0BSD, Unlicense, CC0-1.0, Zlib, BlueOak-1.0.0, Python-2.0, MPL-2.0 (unmodified), OFL-1.1 and CC-BY-4.0 (assets only). Review (requires ADR plus waiver): LGPL-2.1/3.0 and GPL-2.0/3.0 (allowed in `dev` and `service` only, never `bundled`), AGPL-3.0 (`service` only, unmodified or with published fork), BUSL-1.1, ELv2, WTFPL, `SEE LICENSE IN` custom texts such as tldraw's. Block: SSPL-1.0, Commons Clause, JSON, `UNLICENSED` or missing license from third parties, any license in `bundled` that is copyleft.
- Scanner `ops/licenses/check.ts`: reads `pnpm licenses list --json --prod` plus `pnpm ls --json` for context derivation; parses SPDX expressions with `spdx-expression-parse` and `spdx-satisfies` (OR passes if any branch is allowed, AND requires all); falls back to LICENSE file text detection when the `license` field is missing or disagrees with the file, preferring the file and flagging the mismatch. Rust via `cargo deny check licenses`.
- Output `reports/licenses.json`: `{ status, scanned, violations: [{ package, version, license, context, tier, waiver? , reason }], warnings, notices }`; SARIF uploaded like the other security jobs; Markdown summary lists violations first.
- Waiver record: `{ package, versionRange, license, context, reason, adr, approvedBy: Justin|Atlas, expires }`; expired waivers fail; Atlas may approve `review`-tier waivers, `block`-tier requires Justin.
- Private workspace packages and `pnpm` overrides are skipped; optional peers not installed are ignored.
- Job budget under 90 seconds on the template; results consumed by `libraries/upgrade-bot` on Renovate PRs.

**Definition of done**

- Policy doc, `policy.yaml`, waivers schema, scanner, `deny.toml` and notices generator merged.
- Vitest fixtures: allowed, review without waiver (fails), waived (passes), expired waiver (fails), SPDX OR and AND expressions, field/file mismatch, missing license.
- One real CI run on a seeded fake SSPL package fails with an inline annotation; screenshot in the PR.
- `THIRD_PARTY_NOTICES.md` produced by `pnpm build` and included in the Tauri bundle resources.
- Sentinel Security Auditor approves; Justin answered (or was asked, with a default) the own-code license question via Needs Justin.
- CHANGELOG entry; Linear comment linking the policy and a sample report.

**Edge cases**

- tldraw `SEE LICENSE IN LICENSE.md` with watermark clause: review tier, waiver referencing the `collab/collab-research` ADR.
- Dual license `(MIT OR Apache-2.0)`: passes; `(GPL-3.0 AND MIT)`: review.
- GPL-licensed dev tool (for example a CLI) in `dev` context: allowed with a note, blocked if it ever moves to `dependencies`.
- License field says MIT, LICENSE file is proprietary: violation with `mismatch` reason.
- Fonts and icon sets (OFL, ISC, MIT): allowed as assets, notices generated.
- Lockfile out of sync with `package.json`: job fails fast with a clear message rather than scanning stale data.

**Dependencies**

`libraries/eval-rubric` (hard: license gate references these tiers). Soft: `quality/security-scans` (job slot and SARIF merge), `quality/ci-gate1` (setup job), `collab/decision-log` (waiver ADR links). Consumed by `libraries/upgrade-bot`, `libraries/registry`, every research issue.

**Agent**

Built by Scout (Library Evaluator) with Forge (Ops Runner) for the CI wiring. Reviewed by Sentinel (Security Auditor) and Atlas.

**Size**

M: two ecosystems, SPDX parsing and context derivation need care; the policy text itself is a day.
