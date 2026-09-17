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
blockedBy: ["PAP-219", "PAP-239", "PAP-78"]
blocks: []
key: "quality/security-scans"
url: "https://linear.app/paperos/issue/PAP-80/add-dependency-audit-secret-scanning-semgrep-sast-and-container"
source: "plan/specs/bucket-2.json (round-1 canonical spec JSON)"
---

# PAP-80: Add dependency audit, secret scanning, Semgrep SAST and container scanning to CI

**Goal**

Catch leaked secrets, vulnerable dependencies, dangerous code patterns and unsafe container images automatically on every PR and nightly on `main`, so the security reviewer agent starts from a clean baseline and Justin never receives a release with a known critical vulnerability.

**Scope**

In:
- Workflow `.github/workflows/security.yml` with jobs: `secrets` (gitleaks 8.x over the full PR diff and, nightly, full history), `deps` (`osv-scanner` against `pnpm-lock.yaml` and `Cargo.lock` for Tauri, plus `pnpm audit --prod` as a second opinion), `sast` (Semgrep CLI with `p/typescript`, `p/react`, `p/nodejs`, `p/owasp-top-ten`, `p/secrets` and a local ruleset `ops/security/semgrep/`), `containers` (Trivy on every image built from `ops/compose/`), `licenses` hook point for `libraries/license-policy`, and `gate-security` aggregating into commit status `gate/1-security`.
- Local rules in `ops/security/semgrep/`: oRPC procedure without `authorize` middleware, Drizzle query without tenant filter outside `withTenant`, `dangerouslySetInnerHTML` without `dompurify`, `eval`/`new Function`, Tauri `allowlist` widening, hard-coded imagine-os tokens.
- Suppression policy: inline `// nosemgrep: rule-id -- reason (expires 2026-12-01)` with an expiry checked by a script; `gitleaks:allow` requires the same.
- SBOM generation (`cyclonedx` via `@cyclonedx/cyclonedx-npm`) uploaded as artifact per build.
- Dependabot and Renovate off for security here; `libraries/upgrade-bot` owns upgrades and consumes this job's results.

Out: runtime WAF, penetration testing, secret rotation automation, cloud posture management.

**Spec**

- Severity mapping to `quality/review-rubrics`: gitleaks any hit = S0; OSV `CRITICAL`/`HIGH` with fix available = S0, without fix = S1 with waiver flow; Semgrep `ERROR` = S1 (S0 for the authz and tenant rules), `WARNING` = S2; Trivy `CRITICAL` = S0, `HIGH` = S1.
- All tools output SARIF; a merge script `ops/security/merge-sarif.ts` produces `reports/security.json` in the finding schema and a Markdown job summary; SARIF uploaded to GitHub code scanning when available and stored as artifact on Forgejo.
- Nightly job on `main` at 03:00 UTC also runs full-history gitleaks and opens or updates a Linear issue via `pm-linear/webhooks` when new S0/S1 findings appear, deduped by finding ID.
- Waiver file `ops/security/waivers.yaml`: `{ id, tool, reason, approvedBy: 'Justin'|'Sentinel', expires }`; expired waivers fail the job. Sentinel may approve S1 waivers; S0 waivers require Justin via Needs Justin.
- Trivy scans `postgres`, `forgejo`, `hocuspocus`, `minio`, `api` images defined in compose; `--ignore-unfixed` false, results per image.
- Runtime under 4 minutes; Semgrep runs on changed files for PRs and full repo nightly.
- Documentation `docs/quality/security-scans.md`: tools, versions, how to read results, how to suppress.

**Definition of done**

- Workflow green on `main`; seeded test PR with a fake AWS key, a vulnerable `lodash@4.17.15`, a `dangerouslySetInnerHTML` misuse and an oRPC procedure without authorize produces four findings with correct severities and a red status (link).
- Waiver expiry test: an expired waiver fails the job.
- SBOM artifact present on a build; `reports/security.json` validates against the finding schema.
- Nightly run created a Linear issue in a dry-run mode (screenshot).
- Same workflow passes on the Forgejo runner; docs and CHANGELOG entry; Linear comment with run links.

**Edge cases**

- False-positive secrets in test fixtures: place under `**/__fixtures__/**` with a documented allowlist path pattern, never blanket ignores.
- Lockfile with git dependencies or workspace links: OSV skips them; the script lists skipped packages.
- Semgrep timeouts on generated files: exclude `**/generated/**`, `storybook-static`, `dist`.
- Tauri Rust deps without Cargo.lock in the repo yet: job skips with a notice until `app-shell/tauri-desktop` merges.
- Fork PRs without secrets: run everything that needs no token; skip SARIF upload with a comment.
- Vulnerability with no upstream fix for weeks: S1 waiver with expiry and a Linear issue, re-checked nightly.

**Dependencies**

`quality/ci-gate1` (hard: shares setup and status pattern). Soft: `libraries/license-policy` (job slot), `pm-linear/webhooks` (issue creation), `forge/actions-runner`. Consumed by `quality/review-agents` (security reviewer reads `security.json`), `quality/release-train`, `libraries/upgrade-bot`.

**Agent**

Built by Sentinel (Security Auditor sub-agent). Reviewed by Forge (Ops Runner, images) and Atlas for the waiver policy.

**Size**

M: four tools to wire and normalise; the waiver and severity mapping are the design work.
