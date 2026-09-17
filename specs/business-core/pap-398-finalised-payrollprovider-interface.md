---
identifier: "PAP-398"
title: "Finalised PayrollProvider interface, first adapter with idempotency keys, webhook route and the adapter contract test suite"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Payroll adapter and cash dashboard"
state: "Backlog"
parent: "PAP-184"
children: []
blockedBy: ["PAP-176"]
blocks: ["PAP-399"]
key: "business-core/payroll/adapter-contract"
url: "https://linear.app/paperos/issue/PAP-398/finalised-payrollprovider-interface-first-adapter-with-idempotency"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:47.457Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-398: Finalised PayrollProvider interface, first adapter with idempotency keys, webhook route and the adapter contract test suite

**Goal**

Turn the PAP-176 interface into a working, tested adapter for the chosen provider, with webhook verification and a contract suite any future adapter must pass.

**Scope**

In: `payroll/provider.ts` (final), `adapters/check.ts` (or `gusto.ts`), `payroll_event`, route `/api/webhooks/payroll/:provider`, `test/payroll-contract.test.ts`, mock adapter. Out: tables beyond `payroll_event`, UI, postings (siblings).

**Spec**

* Methods map to provider REST via the TypeScript SDK if present else `ky` with Zod; idempotency key `paperos:<tenant>:<entity>:<version>` on every mutation; `capabilities()` bitmap.
* Webhooks: signature verification with two accepted secrets during rotation; events deduped by provider id in `payroll_event`; parsed into `PayrollEvent`.
* Contract suite exercises every interface method against the mock adapter and, with sandbox credentials, the real one (`nock` recordings committed).

**Interface contract**

Provides: `PayrollProvider` final, `payrollProviders` registry, `PayrollEvent`, webhook route, contract suite, mock adapter. Consumes: ADR and draft interface (PAP-176), secrets (PAP-17), sandbox credentials (Needs Justin).

**Definition of done**

* Contract suite green on mock and sandbox; signature rotation test; recordings committed; capability matrix in docs.

**Test plan**

* Unit: request mapping; signature verify; dedupe.
* Integration: contract suite against sandbox once, recorded.

**Demo**

Run `pnpm test payroll-contract --adapter mock` and then `--adapter check --record` against the sandbox.

**Edge cases**

* Provider 5xx retried with idempotency; unknown event types logged and acknowledged.

**Dependencies**

PAP-176 (hard), PAP-17, sandbox credentials. Blocks siblings.

**Agent**

Builder: Ledger (Payroll Adapter). Reviewer: Sentinel (Security Auditor).

**Size**

M: plus a webhook-signing spike.
