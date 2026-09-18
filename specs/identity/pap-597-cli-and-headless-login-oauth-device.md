---
identifier: "PAP-597"
title: "CLI and headless login: OAuth device authorization flow for `paperos login`, keychain token storage, `paperos whoami`, `--as-agent` key exchange and the approval page"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Agent principals and enterprise"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-223", "PAP-224"]
blocks: []
key: "r4/identity/device-flow-login"
url: "https://linear.app/paperos/issue/PAP-597/cli-and-headless-login-oauth-device-authorization-flow-for-paperos"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:13.944Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-597: CLI and headless login: OAuth device authorization flow for `paperos login`, keychain token storage, `paperos whoami`, `--as-agent` key exchange and the approval page

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

`paperos create`, `paperos upgrade`, the golden-path driver and any script a Claude session runs need to call the PaperOS API as a person, and today there is no way to sign a CLI in except copying a browser cookie. The device authorization grant (RFC 8628) is the standard answer (gh, az, flyctl); Better Auth ships a `deviceAuthorization` plugin. Add it, store the token in the OS keychain and let agents exchange a session key the same way.

**Scope**

In: `deviceAuthorization()` plugin in `packages/auth` with endpoints `/api/auth/device/code`, `/api/auth/device/token`, approval page `/auth/device` with spec (shows user code, client name, scopes, approve or deny; requires a recent authentication), CLI commands in `packages/cli` (PAP-22 host, soft: standalone bin until it lands) `paperos login [--tenant]`, `paperos logout`, `paperos whoami`, token storage through the OS keychain (`keytar`-compatible) with a file fallback under `0600`, `--as-agent <key>` mode that exchanges a `pos_agent_` key for a scoped session (PAP-586), docs `docs/platform/cli-auth.md`.

Out: The CLI's other commands (PAP-22, PAP-364), customer OAuth apps (PAP-222), Tauri deep-link flow (PAP-225).

**Spec**

* Device code valid 10 minutes, polling interval 5 s with `slow_down`; user code 8 characters without ambiguous glyphs; approval bound to the signed-in user and audited `auth.device.approved|denied`.
* Tokens are bearer sessions (PAP-223) labelled `cli:<hostname>` so they appear on the sessions page (PAP-581) and can be revoked there; default absolute lifetime 30 days, idle 7.
* `paperos login --tenant acme` sets the active tenant; `whoami` prints principal, tenant, role and expiry as JSON with `--json`.
* Headless environments (CI, agent sessions) use `--as-agent` or `PAPEROS_TOKEN`; the device flow refuses to print a token to stdout unless `--print-token` is passed explicitly.
* Rate limits on `/device/code` per IP (PAP-558, soft) and the challenge from PAP-592 when abused.

**Interface contract**

Provides: Plugin config and endpoints, approval page and spec, CLI commands, keychain adapter, `getCliSession()` for other CLI commands, audit events.

Consumes: Better Auth server and pages (PAP-223, PAP-224), sessions listing (PAP-581, soft), agent keys (PAP-586, soft), CLI host (PAP-22, soft), rate limits and abuse controls (soft). Consumed by PAP-22, PAP-364, PAP-430, PAP-96 tooling, PAP-92 session playbook.

**Definition of done**

* `paperos login` prints a URL and code, approval in the browser signs the CLI in, `whoami` shows the principal; the session appears on the sessions page and revoking it makes the CLI fail with a clear message (Playwright plus a CLI harness).
* Expired code, `slow_down`, denied approval and `--as-agent` paths tested; keychain and file fallback both proven on Linux and macOS.
* Docs; changelog under Developer.

**Test plan**

* Unit: user code alphabet, polling backoff, token storage adapter selection, JSON output shape.
* E2E: CLI harness on the ephemeral stack: login, whoami, logout; agent key exchange used by an example script.

**Demo**

Run `paperos login`, approve in the browser with a passkey, run `paperos whoami --json`, then revoke the CLI session from `/portal/security` and rerun to see the message. Under two minutes.

**Edge cases**

* Two CLIs on one machine: separate keychain entries per profile (`--profile`).
* Approval page opened by a different user than intended: the code binds to whoever approves; the CLI prints who it is signed in as.
* No keychain (container): file fallback with a warning; `PAPEROS_TOKEN` preferred in CI.

**Dependencies**

Blocked by PAP-223 and PAP-224 (hard). Soft: PAP-22, PAP-581, PAP-586, PAP-558, PAP-592. Consumed by PAP-22, PAP-364, PAP-430.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 4 round-4 file keys in this description to Linear identifiers: `r4/data-layer/rate-limits` = PAP-558, `r4/identity/agent-keys` = PAP-586, `r4/identity/auth-abuse-controls` = PAP-592, `r4/identity/sessions-stepup` = PAP-581.
