---
identifier: "PAP-93"
title: "Define the issue contract (spec link, acceptance criteria, surfaces, definition of done) enforced by a Linear webhook validator"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Agent"]
milestone: "Linear configured for the pipeline"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-91"]
blocks: []
key: "pm-linear/issue-contract"
url: "https://linear.app/paperos/issue/PAP-93/define-the-issue-contract-spec-link-acceptance-criteria-surfaces"
source: "plan/specs/bucket-3.json (round-1 canonical spec JSON)"
---

# PAP-93: Define the issue contract (spec link, acceptance criteria, surfaces, definition of done) enforced by a Linear webhook validator

**Goal**

Define what an issue must contain before a machine is allowed to build it, and enforce it: a Linear webhook validator moves non-conforming issues back out of `Ready for Claude` with a comment listing exactly what is missing. This keeps the orchestrator from spawning expensive sessions on vague issues and gives the Decomposer sub-agent a target format.

**Scope**

In:
- `docs/pm/issue-contract.md` specifying required description sections in order: `**Goal**`, `**Scope**`, `**Spec**`, `**Definition of done**`, `**Edge cases**`, `**Dependencies**`, `**Agent**`, `**Size**` (matching the format used across this plan).
- Required metadata: exactly one label from each of Phase, Type, Surface (one or more), Character; an estimate (S/M/L); a project; at least one link to a spec file (`specs/**/*.spec.yaml` path or a Linear document) for Build issues; dependencies expressed as Linear "blocked by" relations, not prose.
- Validator service module `src/contract/validate.ts` in `imagine-os/paperos-orchestrator`: pure function `validateIssue(issue): ContractResult` returning `{ok, violations: [{code, message, fix}]}`.
- Webhook handler: on `Issue` `update` where state becomes `Ready for Claude`, run the validator; on failure move the issue to `Backlog`, add label `needs-contract` (created in the Type group as a utility label), and post one comment listing violations with a link to the contract doc. On later success remove the label.
- CLI `pnpm contract:check PAP-123` for local use and `pnpm contract:audit` for the whole team, printing a table.
- Codes: `MISSING_SECTION`, `EMPTY_SECTION` (fewer than 20 words), `DOD_NOT_CHECKABLE` (fewer than 5 bullets), `NO_PHASE_LABEL`, `NO_TYPE_LABEL`, `NO_SURFACE_LABEL`, `NO_CHARACTER_LABEL`, `NO_ESTIMATE`, `NO_PROJECT`, `NO_SPEC_LINK` (Build only), `PROSE_DEPENDENCY` (an issue key appears in Dependencies text with no matching relation), `BLOCKED_BY_OPEN` (a blocker is not Done).

Out: the webhook transport itself (`pm-linear/webhooks` provides the Express/Hono receiver and signature check; this issue registers a handler), spec file schema validation (`spec-builder/validator`).

**Spec**

- Parse the description with `remark` (unified) into an mdast; identify sections by bold paragraph headings to match the plan's format; also accept `##` headings.
- Validator is deterministic and has a fixture suite: 12 good issues, 20 bad ones, one per code.
- Comment template lives in `src/contract/templates/violations.md` with the footer JSON block from `pm-linear/session-playbook` (`status: "contract-failed"`).
- `BLOCKED_BY_OPEN` is a warning, not a failure, until `pm-linear/concurrency` takes over dependency scheduling; a `--strict` flag promotes it.
- Store results in the orchestrator's SQLite/Postgres table `contract_checks(issue_id, checked_at, ok, violations_json)` for the burn report.

**Definition of done**

- Fixture suite passes in Vitest; coverage of `validate.ts` above 95 percent.
- Moving a bad issue to `Ready for Claude` in the real PAP team results in a bounce to `Backlog`, label and comment within 10 seconds (screen recording attached).
- Moving a good issue leaves it untouched; `needs-contract` label removed if present.
- `pnpm contract:audit` run on all current PAP issues; results posted as a comment on this issue.
- Contract doc published; issue templates from `pm-linear/configure-workspace` updated to match section names exactly.
- Changelog entry; Linear comment with the recording link.

**Edge cases**

- Description uses `##` headings instead of bold: accept both, normalise.
- Sections present but in a different order: warn, do not fail.
- Issue moved to `Ready for Claude` by the validator's own bot account: ignore to prevent loops (check `actor.id`).
- Webhook delivered twice (Linear retries): idempotent by `webhookId`; no duplicate comments.
- Very long description over 50k characters: validate only the first 50k and flag `DESCRIPTION_TOO_LONG`.
- Sub-issue of a parent with a spec link: inherit `NO_SPEC_LINK` satisfaction from the parent.
- Justin manually forces an issue to `Ready for Claude` after a bounce: a second bounce would be hostile; if the last mover is Justin, post the violations as a comment but do not move it.

**Dependencies**

- `pm-linear/configure-workspace`: label groups, states and templates must exist.
- `pm-linear/webhooks`: shares the receiver; if this lands first, ship a minimal receiver here and let webhooks generalise it.

**Agent**

Built by Atlas (Decomposer sub-agent), reviewed by Sentinel (Code Reviewer) and Quill for the document wording.

**Size**

M: a parser, a fixture suite and a live webhook behaviour.
