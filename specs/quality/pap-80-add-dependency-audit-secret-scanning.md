---
identifier: "PAP-80"
title: "Add dependency audit, secret scanning, Semgrep SAST and container scanning to CI"
project: "quality"
projectName: "Quality Pipeline"
phase: "P0"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Gates 1 and 2 on every PR"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-78", "PAP-219", "PAP-239"]
blocks: ["PAP-357", "PAP-358", "PAP-524", "PAP-675", "PAP-676", "PAP-903"]
key: "quality/security-scans"
url: "https://linear.app/paperos/issue/PAP-80/add-dependency-audit-secret-scanning-semgrep-sast-and-container"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:41.575Z"
model: "claude-opus-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-80: Add dependency audit, secret scanning, Semgrep SAST and container scanning to CI

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Infra M

**Goal**

Catch leaked secrets, vulnerable dependencies, dangerous code patterns and unsafe images automatically on every PR and nightly on `main`, normalised into the shared finding schema, so the security reviewer starts from a clean baseline and no release ships with a known critical vulnerability.

**Scope**

* In: `.github/workflows/security.yml` with jobs `secrets` (gitleaks 8.x), `deps` (`osv-scanner` on `pnpm-lock.yaml` and `Cargo.lock`, `pnpm audit --prod`), `sast` (Semgrep with `p/typescript`, `p/react`, `p/nodejs`, `p/owasp-top-ten`, `p/secrets` plus local rules), `containers` (Trivy on compose images), `licenses` hook for PAP-211, aggregating `gate-security`; SARIF merge into `reports/security.json`; waiver file with expiry; SBOM; nightly full-history run with Linear issues.
* Out: runtime WAF, penetration testing, secret rotation automation (PAP-219 runbook), posture management, upgrades (PAP-217).

**Spec**

* Local Semgrep rules in `ops/security/semgrep/`, each annotated with the PAP-219 control it enforces: oRPC procedure without `authorize` (`SEC-API-01`), Drizzle query outside `withTenant` (`SEC-DB-02`), `dangerouslySetInnerHTML` without `dompurify`, `eval`/`new Function`, Tauri capability widening, hard-coded imagine-os tokens, `/__test` routes reachable without `PAPEROS_TEST_MODE` (PAP-240).
* Severity mapping to PAP-79: gitleaks hit S0; OSV critical/high with fix S0, without fix S1 plus waiver; Semgrep `ERROR` S1 (S0 for authz and tenant rules), `WARNING` S2; Trivy critical S0, high S1.
* `ops/security/merge-sarif.ts` produces `reports/security.json` as `GateReport<'security'>` (PAP-239) with `data.tools: [{ name, version, findings }]`; SARIF to GitHub code scanning when available, artifact on Forgejo.
* Waivers `ops/security/waivers.yaml`: `{ id, tool, reason, approvedBy: 'Justin' | 'Sentinel', expires }`; expired waivers fail; Sentinel may approve S1, S0 needs Justin via Needs Justin. Suppressions `// nosemgrep: rule -- reason (expires YYYY-MM-DD)` and `gitleaks:allow` with the same expiry check.
* Nightly 03:00 UTC on `main`: full-history gitleaks, full-repo Semgrep, opens or updates one Linear issue per new S0/S1 finding via PAP-97 deduped by finding ID.
* SBOM via `@cyclonedx/cyclonedx-npm` per build; Trivy scans `postgres`, `forgejo`, `hocuspocus`, `minio`, `api` images with `--ignore-unfixed=false`. Runtime under 4 minutes; Semgrep on changed files for PRs.

**Interface contract**

* Provides: `reports/security.json`, status `gate/1-security`, waiver file schema, suppression grammar, SBOM artifact `sbom.cdx.json`, the local rule ids and their `SEC-*` mapping, "Security" section in the sticky comment.
* Requires: PAP-78 setup action, sticky comment and status pattern (hard); PAP-239 schema; PAP-219 controls (hard: rule ids reference them); PAP-211 job slot (soft); PAP-97 (soft) for nightly issues; PAP-50 runner.
* Consumers: PAP-245 security reviewer (reads `security.json` and waivers), PAP-88 certification (no open S0/S1, no expired waivers), PAP-217, PAP-89.
* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §5 (`packages/contracts` is owned by quality through PAP-239: every `reports/*.json` named above is a `GateReport<kind>` validated by `validateArtifact()`, JSON Schema generated from Zod 4 per §1); §3 (gate results reach the bus as `review.gate_failed` and `review.ready` through PAP-97; artifact `version` bumps keep a reader for 30 days); §6 row "Gate artifacts" (provider PAP-239; consumers PAP-78 to PAP-90, PAP-97, PAP-137, PAP-110). Until PAP-239 merges, write the shape exactly as its Interface contract states and import the schema when it lands. Also [Security & Threat Model](<https://linear.app/paperos/document/paperos-security-and-threat-model-51fd5fd8929c>) §5 (gitleaks on every diff and nightly over history; suppressions expire) and §8 (Semgrep blocks PAN-shaped fields and `sk_live_` literals; SAST, secret, dependency and container scans per PR gate release candidates), and PAP-219 `controls.yaml` for the `SEC-*` ids.

**Definition of done**

* Workflow green on `main`; seeded PR with a fake AWS key, `lodash@4.17.15`, a `dangerouslySetInnerHTML` misuse and an oRPC procedure without `authorize` yields four findings at the mapped severities and a red status (link).
* Expired waiver fails the job (test); active S1 waiver shows as waived.
* SBOM present; `security.json` validates against `packages/contracts`.
* Nightly dry run shows the Linear issue it would create (screenshot).
* Same workflow green on the Forgejo runner; `docs/quality/security-scans.md`; changelog entry.

**Test plan**

* Rule tests: Semgrep `--test` fixtures (positive and negative) for every local rule.
* Unit: `merge-sarif.ts` on fixture SARIF from each tool; severity mapping table; waiver expiry with a faked date.
* Workflow: seeded PR above; fork PR skips upload with a comment; missing `Cargo.lock` skips with a notice.
* Perf: PR run under 4 minutes on a warm cache.

**Demo**

Open the seeded PR's "Security" comment: four findings with severities and rule ids; click the `SEC-API-01` link to the threat model control; open `waivers.yaml` and the nightly dry-run summary. Under one minute.

**Edge cases**

* Fixture secrets: allowed only under `**/__fixtures__/**` with a documented pattern.
* Git or workspace dependencies: skipped and listed.
* Generated and vendored paths excluded from Semgrep.
* Long-unfixed vulnerability: S1 waiver with expiry plus a Linear issue, re-checked nightly.

**Dependencies**

PAP-78, PAP-219 (hard). Soft: PAP-239, PAP-211, PAP-97, PAP-50.

**Agent**

Sentinel (Security Auditor). Reviewed by Forge (Ops Runner, images) and Atlas (waiver policy).

**Size**

M.
