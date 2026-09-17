---
identifier: "PAP-302"
title: "Specify shared value types and wire encodings in `packages/core/types`: `Money` (bigint minor units, string on the wire), `ActorRef`, `EntityRef`, UUIDv7 ids, timestamps, signed cursors and the `ApiError` body"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Developer"]
milestone: "Postgres + Drizzle baseline"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-27", "PAP-71", "PAP-131", "PAP-136", "PAP-164", "PAP-175", "PAP-268"]
key: "contracts/shared-value-types"
url: "https://linear.app/paperos/issue/PAP-302/specify-shared-value-types-and-wire-encodings-in-packagescoretypes"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:00:52.035Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-302: Specify shared value types and wire encodings in `packages/core/types`: `Money` (bigint minor units, string on the wire), `ActorRef`, `EntityRef`, UUIDv7 ids, timestamps, signed cursors and the `ApiError` body

**Goal**

Fix the handful of scalar and value types that every package passes across boundaries, so that `Money` is one type instead of three (PAP-71 and PAP-164 use `number`, PAP-175 uses `bigint`, PAP-187 uses `amount_cents`), the actor stored on rows and events is one shape (PAP-33 `user.kind`, PAP-35 context, PAP-55 `Principal`, PAP-60 `principalType`), and ids, timestamps, cursors and error bodies encode the same way in Postgres, TypeScript and JSON. Section 1 of the Interface & Data Contracts document is the prose; this issue is the code.

**Scope**

In:

* `packages/core/src/types/` (owner data-layer inside the app-shell-owned `packages/core` index): `ids.ts` (`Uuid` branded string, `uuidv7()` client generator matching `uuid_generate_v7()` from PAP-32), `time.ts` (`IsoDateTime`, `IsoDate`, `Duration`), `money.ts` (`Money`, arithmetic, JSON codec), `actor.ts` (`ActorRef` as a projection of PAP-55 `Principal`), `entity.ts` (`EntityRef`, `parseEntityKey`, `formatEntityKey`), `cursor.ts` (`signCursor`, `verifyCursor` with HMAC over keyset values), `error.ts` (`ApiErrorBody`, `ApiErrorCode`).
* Drizzle column helpers in `packages/db/src/schema/_shared.ts` for `money('amount')` (emits `amount_minor bigint` + `currency char(3)`), `actorRef('actor')` (emits `actor_id uuid`, `actor_kind text`, `actor_character text`), `entityRef('subject')`.
* Zod schemas with JSON codecs: `moneySchema` accepts `{ amountMinor: string|bigint, currency }` and outputs `bigint`; `z.bigint()` never appears on a wire schema.
* `docs/platform/types.md` with a table: type, TypeScript, Postgres, JSON, example.

Out: formatting for display (PAP-27 `formatMoney`, PAP-71 `Money` cell), currency conversion (PAP-175 `convert`), the `Principal` definition itself (PAP-55), `FilterTree` (PAP-279).

**Spec**

* `Money = { amountMinor: bigint; currency: Iso4217 }`; JSON `{ "amountMinor": "1999", "currency": "USD" }`; `add`, `subtract`, `multiply(ratio: Decimal)`, `allocate(ratios[])` (largest remainder), `compare`, `isZero`; mixed-currency arithmetic throws `CurrencyMismatch`.
* `ActorRef = { id: Uuid; type: 'human'|'agent'|'service'|'anonymous'; character?: string; onBehalfOf?: Uuid }`; `toActorRef(principal)` and `ANONYMOUS_ACTOR`; `type` values are exactly PAP-55 `PrincipalType`.
* `EntityRef = { type: string; id: Uuid }`; key form `entity:<type>:<id>` identical to the PAP-131 anchor grammar; `type` validated against the dataset registry when `packages/views` is present, free-form otherwise.
* Cursors: `signCursor({ sort: [...values], id })` returns base64url of payload plus 16-byte HMAC-SHA256 truncation with `CURSOR_SECRET` from PAP-17; `verifyCursor` throws `VALIDATION` on tamper; both PAP-268 and PAP-163 import these.
* `ApiErrorBody = { code: ApiErrorCode; message: string; requestId: string; details?: { path: (string|number)[]; issue: string }[]; retryAfter?: number }`; `ApiErrorCode` is the closed union from the contracts document (`UNAUTHORIZED | FORBIDDEN | NOT_FOUND | CONFLICT | VALIDATION | RATE_LIMITED | PAYLOAD_TOO_LARGE | INTERNAL`).
* Timestamps: `timestamptz` in Postgres, `Date` in TypeScript, ISO-8601 UTC with milliseconds in JSON; `IsoDate` (`YYYY-MM-DD`) for fiscal dates, never `Date`.
* No runtime dependency on React, Drizzle or the database inside `packages/core/types`; the Drizzle helpers live in `packages/db`.

**Interface contract**

Provides (from `@paperos/core/types`): `Uuid`, `uuidv7`, `IsoDateTime`, `IsoDate`, `Money`, `moneySchema`, `moneyJson`, `ActorRef`, `actorRefSchema`, `toActorRef`, `EntityRef`, `entityRefSchema`, `parseEntityKey`, `formatEntityKey`, `signCursor`, `verifyCursor`, `ApiErrorBody`, `ApiErrorCode`. From `@paperos/db`: `money()`, `actorRef()`, `entityRef()` column helpers. Consumes: PAP-55 `PrincipalType` (soft; a local copy with a type-equality test until it merges), PAP-32 `_shared.ts`, PAP-17 `CURSOR_SECRET`. Consumed by PAP-71, PAP-164, PAP-175, PAP-179, PAP-187, PAP-27, PAP-268, PAP-163, PAP-131, PAP-136, the event contract issue and every business router.

**Test plan**

* Unit: money arithmetic and allocation against fixtures (including negative amounts and JPY zero-decimal); JSON round trip preserves `bigint` exactly past 2^53; `CurrencyMismatch` thrown.
* Property (fast-check): `allocate` sums to the original for random ratios; `signCursor` then `verifyCursor` is identity; one flipped byte fails.
* Type: `expectTypeOf<ActorRef['type']>().toEqualTypeOf<PrincipalType>()`; `moneySchema` output type is `bigint`.
* Integration (PAP-42 stack): the `money()` column helper round-trips `9007199254740993n` through Postgres.

**Definition of done**

* Package merged with the exports above, Biome and typecheck clean, coverage 100 percent on `money.ts` and `cursor.ts`.
* PAP-71, PAP-164 and PAP-175 owners have acknowledged in comments that their specs import these types (comment left by this session on each).
* `docs/platform/types.md` table complete; ADR `docs/adr/00xx-shared-value-types.md`; CHANGELOG under "Platform"; Linear comment with the docs link.

**Edge cases**

* Client without `BigInt` (none in the device matrix, PAP-14) is unsupported; documented.
* Currency with three decimals (BHD, KWD): `minorUnits(currency)` table; allocation uses it.
* `EntityRef` for a global entity (`user`) has no tenant; consumers must not assume tenant scope.
* Cursor secret rotation: `verifyCursor` accepts the previous secret for 24 hours (`CURSOR_SECRET_PREVIOUS`).
* Anonymous actor on audit rows: `actor_id` nullable only when `actor_kind = 'anonymous'` (CHECK constraint emitted by the helper).

**Dependencies**

None hard (pure package on the PAP-13 layout). Soft: PAP-55 for the canonical `PrincipalType`, PAP-32 for `_shared.ts`, PAP-17 for the secret name, PAP-42 for the integration test. Ready now. Blocks PAP-71, PAP-164, PAP-175, PAP-27, PAP-268, PAP-131, PAP-136.

**Agent**

Specified and built by Forge (Platform Engineer). Reviewed by Sentinel (Code Reviewer) and Ledger (finance types).

**Size**

S

**Demo**

Reviewer runs `pnpm --filter core test types` and watches the property tests pass, then `pnpm tsx examples/types.ts`, which prints a `Money` value as JSON, parses it back, allocates $19.99 three ways without losing a cent, signs a cursor and shows the tampered cursor rejected. Under a minute.
