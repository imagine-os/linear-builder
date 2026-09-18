---
identifier: "PAP-444"
title: "Build the config and secrets port: manifests declare settings and secret names, the kernel validates at boot and hands out secrets through one adapter (env or credential broker)"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Contracts and conformance wired"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-17", "PAP-434", "PAP-537"]
blocks: ["PAP-553"]
key: "module-system/config-secrets-port"
url: "https://linear.app/paperos/issue/PAP-444/build-the-config-and-secrets-port-manifests-declare-settings-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:08.221Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-27"
cycle: null
---

# PAP-444: Build the config and secrets port: manifests declare settings and secret names, the kernel validates at boot and hands out secrets through one adapter (env or credential broker)

**Model / Effort:** Sonnet 5 / medium

**Goal**

Take configuration and secrets out of module code. Each manifest already declares `settingsSchema` (PAP-264); this issue adds `secrets: string[]` (names only), a `ConfigPort` and `SecretsPort` in `contract-app-shell`, kernel boot validation of every module's config with PAP-17's typed layer, and two adapters: `.env` for development and the credential broker (PAP-300) for agent sessions and production. No module reads `process.env` after this (`docs/module-system.md` section 4, config row).

**Scope**

In:

* `ConfigPort` (`get(module)` typed by `settingsSchema`) and `SecretsPort` (`get(name)`, `has(name)`, rotation hook) in `contract-app-shell`; `secrets` field in the manifest schema (minor bump).
* Kernel boot: validate every enabled module's settings; missing required secret fails boot with module and name, never with the value.
* Adapters: `EnvSecrets` (PAP-17 per-target storage: env, keychain, secure storage) and `BrokerSecrets` (PAP-300 egress proxy injection; the port returns opaque handles that the HTTP client resolves).
* Lint rule R12: `process.env` and `import.meta.env` allowed only in `packages/core/config` and adapters.
* `paperos module config <id>` printing effective settings with secrets masked.

Out: the typed env layer itself (PAP-17), the broker (PAP-300), tenant settings stored in Postgres (tenant settings own that).

**Spec**

* Secret names are `SCREAMING_SNAKE`, declared once, unique across modules or explicitly shared (`sharedWith`).
* Boot validation is per enabled module (PAP-266): a disabled module's missing secrets are not errors.
* The broker adapter never exposes raw values to module code; a module that needs the raw value (rare, for example signing) declares `rawSecrets` and the deny list (PAP-298) reviews it.
* Rotation: `SecretsPort.onRotate(name, cb)` so adapters can rotate without a restart (used by PAP-302 cursor secret).

**Interface contract**

Provides: `ConfigPort`, `SecretsPort`, manifest `secrets`, `EnvSecrets` and `BrokerSecrets` adapters, lint R12, `paperos module config`. Consumes: PAP-17 typed env and per-target storage, PAP-300 broker (soft; env adapter until it lands), kernel registry, manifest schema, PAP-298 deny list for `rawSecrets` review. Consumed by: every module with configuration (business-core Stripe keys, growth platform tokens, forge tokens, pm-linear API key, realtime server config), the `Wire <module>` issues, PAP-266 removal matrix.

**Test plan**

* Unit: validation errors name module and key, never the value; `sharedWith` and uniqueness; rotation callback fires.
* Integration: boot with a missing Stripe secret and business-core enabled fails; with business-core disabled boots; broker adapter returns handles and the HTTP client injects (PAP-300 fixture proxy).
* Static: R12 fixtures; `grep` for `process.env` outside allowed paths is empty in Gate 1.

**Definition of done**

* Ports, adapters, lint and CLI merged; every existing `process.env` read moved behind the port (or in the baseline with an expiry); boot validation live.
* `docs/platform/config.md`; Linear comment.

**Edge cases**

* Same secret needed by two modules (Stripe by business-core and growth referrals): declared once with `sharedWith`; the matrix lists both.
* Tauri desktop: secrets from the keychain; the port is the same, the adapter differs by target.
* Secret present but empty string: treated as missing.
* Test mode (`X-PaperOS-Env: test`, PAP-222): the port resolves `<NAME>_TEST` variants automatically.

**Dependencies**

Blocked by PAP-17, module-system/registry-di.

**Agent**

Built by Forge. Reviewed by Sentinel.

**Size**

S

**Demo**

Reviewer runs `paperos module config business-core` and sees settings with `STRIPE_SECRET_KEY` masked; removes it from `.env` and `pnpm dev` fails naming `business-core` and the key; disables business-core for the app and boot succeeds. Under a minute.
