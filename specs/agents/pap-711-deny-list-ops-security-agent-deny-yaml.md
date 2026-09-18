---
identifier: "PAP-711"
title: "Deny list: `ops/security/agent-deny.yaml` with 45+ rules across eleven areas, the `packages/agent-policy` matcher and explain CLI, and the PreToolUse hook extension"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Roster defined and installed"
state: "Backlog"
parent: "PAP-298"
children: []
blockedBy: ["PAP-210", "PAP-709", "PAP-710"]
blocks: ["PAP-280", "PAP-712"]
key: "r4/agents/deny-list-policy-file-and-hook"
url: "https://linear.app/paperos/issue/PAP-711/deny-list-opssecurityagent-denyyaml-with-45-rules-across-eleven-areas"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:30.587Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-24"
cycle: null
---

# PAP-711: Deny list: `ops/security/agent-deny.yaml` with 45+ rules across eleven areas, the `packages/agent-policy` matcher and explain CLI, and the PreToolUse hook extension

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

First half of PAP-298: the policy and the matcher. One machine-readable file lists what no agent may do, a library evaluates a tool call against it with shell-aware parsing, the PAP-106 hook consults it after the allowlist, and `pnpm policy:explain` tells a session why. Approval path, MCP interception and backstops are the sibling child.

**Scope**

* In: `ops/security/agent-deny.yaml` and its Zod schema, `packages/agent-policy` (`loadPolicy()`, `evaluate()`, `compile` to `dist/agent-deny.json`, `explain`), the `enforce-scope.ts` extension that evaluates compiled rules after the allowlist, `deny-list-hit` log event, the launcher staleness check (PAP-96 refuses a stale digest), generated `docs/security/agent-deny-list.md` table, adversarial fixture corpus.
* Out: `/request-approval` skill, MCP destructive-scope interception, backstop matrix and `pnpm policy:backstops` (sibling), sandboxing (PAP-280), token minting (PAP-300).

**Spec**

* Rule shape `{ id: DENY-<area>-<nn>, area, match: { tool, input: { <field>: regex } }, action: deny|approve, reason, backstop: [{ control, issue }], severity: S0|S1 }`; areas `git`, `fs`, `db`, `linear`, `forge`, `stripe`, `payroll`, `infra`, `secrets`, `comms`, `agents`; the initial 45 rules are the PAP-298 Spec list verbatim, covering all eleven areas.
* Matcher: tokenises Bash with `shell-quote` and evaluates every sub-command across `&&`, `;`, `|`, `sh -c`, heredocs, `xargs` and `eval`; unparseable commands deny with `DENY-SHELL-00`; path rules resolve relative to the worktree; SQL bodies (Drizzle raw, `psql -c`) and Linear GraphQL documents are parsed for the db and linear rules.
* Hook order: allowlist (PAP-106) first, then policy; `deny` returns `permissionDecision: deny` with `DENY-<id>: <reason>. Use /request-approval if this is required.`; `approve` adds the approval hint; every hit logs `deny-list-hit { rule, character, issue, commandHash }` through PAP-107; three S0 hits in one session emit `agent.policy.strike3` for PAP-111.
* `pnpm policy:build` compiles YAML to JSON with a digest; the PAP-282 launcher and the PAP-280 image compare digests and refuse stale policy; `pnpm policy:explain "<command>"` prints matched rules.
* Profiles: the `justin` operator profile denies only the secrets area; Atlas keeps `approve` on destructive Linear and forge operations.

**Interface contract**

* Provides: `agent-deny.yaml` schema and file, `loadPolicy()`, `evaluate(toolName, toolInput, ctx)`, compiled JSON with digest, events `deny-list-hit` and `agent.policy.strike3`, `pnpm policy:build|explain`, generated docs table.
* Consumes: the PAP-106 hook and bundles (sibling issue in this round), PAP-210 scope classes, PAP-107 logging, PAP-282 launcher, PAP-280 image, PAP-219 `controls.yaml` ids `SEC-AGENT-*`.

**Definition of done**

* 45+ rules across eleven areas validate; every S0 rule names at least one backstop (the sibling fills the matrix; here the field is required).
* Matcher fixtures: 200 commands, 40 paraphrases (`git push -f`, `--force-with-lease`, `rm -r -f`, `psql -c "delete from users"`) denied and 40 benign near-misses (`git push origin feat/PAP-42`, `rm -rf node_modules` in the worktree) allowed; zero false positives on the benign set.
* Recorded Forge session denied `git push --force origin main` with `DENY-GIT-01`; stale digest refused (test).
* Docs table generated; changelog under "Security"; Linear comment with the fixture results.

**Test plan**

* Unit: tokeniser and sub-command walk, regex per rule, path containment, SQL and GraphQL parsing, digest staleness, strike counter.
* E2E: `claude -p` sessions at low effort with `maxTurns: 3` against the hook using the PAP-106 harness.

**Demo**

Ask a Forge session to `cd /tmp && git push --force origin main`; the hook denies with `DENY-GIT-01` and the reason. Run `pnpm policy:explain 'psql -c "truncate users"'` and read the matched db rule. Under one minute.

**Edge cases**

* Legitimate migration file containing `DROP TABLE`: writing the file is allowed; executing it is `approve` unless the target database matches `paperos_dev_*` (PAP-42).
* Rule too broad blocks an issue: session posts the rule id, returns the issue to Backlog with `policy-blocked`; Sentinel reviews weekly.
* Command with secrets in arguments: only a hash is logged.
* Policy file edited by a non-Sentinel character: itself a `DENY-AGENTS-*` hit and a CODEOWNERS block (PAP-305).

**Dependencies**

Hard: PAP-709, PAP-210. Soft: PAP-107, PAP-282, PAP-280, PAP-219, PAP-305, PAP-42.

**Agent**

Builder: Sentinel (Security Auditor). Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/agents/character-bundles-and-enforce-scope-hook` = PAP-709.
