"""Shared renderer for round-4 cross-cutting specs (canonical PAP spec format)."""

MODELS = {
    'fable': ('Fable 5.1', 'claude-fable-5-1', 'max'),
    'opus': ('Opus 5', 'claude-opus-5', 'high'),
    'sonnet': ('Sonnet 5', 'claude-sonnet-5', 'medium'),
    'haiku': ('Haiku 4.5', 'claude-haiku-4-5', 'low'),
}
ESTIMATE = {'S': 2, 'M': 3, 'L': 5}
SIZE_LINE = {'S': 'S: half a session.', 'M': 'M: one session.', 'L': 'L: two sessions; split at the first natural seam if the first session does not reach the integration test.'}


def bullets(items):
    return '\n'.join('* ' + i for i in items)


def render(issue, project_key):
    """issue: dict with structured fields; returns (description, meta dict)."""
    tier = issue.get('tier', 'sonnet')
    name, mid, default_effort = MODELS[tier]
    effort = issue.get('effort', default_effort)
    size = issue['size']
    surfaces = issue.get('surfaces', ['Staff'])
    typ = issue.get('type', 'Build')
    head = f"**Model / Effort:** {name} (`{mid}`) / {effort} — {typ} {size}"

    scope_in = issue['scope_in']
    scope_out = issue.get('scope_out', [])
    scope = 'In: ' + ' '.join(s.rstrip('.') + '.' for s in scope_in)
    if scope_out:
        scope += '\n\nOut: ' + ' '.join(s.rstrip('.') + '.' for s in scope_out)

    ic = f"Provides: {issue['provides'].rstrip('.')}. Consumes: {issue['consumes'].rstrip('.')}."
    if issue.get('consumed_by'):
        ic += f" Consumed by: {issue['consumed_by'].rstrip('.')}."

    dod = list(issue['dod'])
    # standard closing evidence lines every issue carries
    if 'Customer' in surfaces or 'Staff' in surfaces:
        if typ in ('Build',):
            dod.append('Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.')
    dod.append('Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.')

    tests = issue['tests']
    if isinstance(tests, dict):
        tlines = [f"{k}: {v.rstrip('.')}." for k, v in tests.items()]
    else:
        tlines = list(tests)
    if typ == 'Build' and issue.get('tenant_data', True):
        tlines.append('Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.')

    edge = list(issue['edge'])
    if typ == 'Build' and issue.get('module_edge', True):
        edge.append(f'Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.')

    builder = issue.get('builder', 'Nova')
    reviewer = issue.get('reviewer', 'Sentinel (Code Reviewer)')
    parts = [
        head, '',
        '**Goal**', '', issue['goal'], '',
        '**Scope**', '', scope, '',
        '**Spec**', '', bullets(issue['spec']), '',
        '**Interface contract**', '', ic, '',
        '**Definition of done**', '', bullets(dod), '',
        '**Test plan**', '', bullets(tlines), '',
        '**Demo**', '', issue['demo'], '',
        '**Edge cases**', '', bullets(edge), '',
        '**Dependencies**', '', issue['deps'], '',
        '**Agent**', '', f'Builder: {builder}. Reviewer: {reviewer}.', '',
        '**Size**', '', SIZE_LINE[size],
    ]
    desc = '\n'.join(parts)
    meta = {
        'key': issue['key'], 'title': issue['title'], 'type': typ, 'phase': issue.get('phase', 'P2'),
        'priority': issue['priority'], 'surfaces': surfaces, 'milestone': issue['milestone'],
        'parent': issue.get('parent'), 'size': size, 'estimate': ESTIMATE[size], 'model': name, 'modelId': mid,
        'effort': effort, 'deferred': issue.get('deferred', False), 'blockedBy': issue.get('blockedBy', []),
        'blocks': issue.get('blocks', []), 'description': desc,
    }
    if issue.get('targetProject'):
        meta = {'targetProject': issue['targetProject'], **meta}
    return meta


def trio(p):
    """Module trio for a new project. p: dict with key, name, contract ports, events, requires, impl, fixtures,
    consumers, kind, swapRisk, owner, milestones (list of 3 names), impl_keys (r4 keys of implementation issues), lead."""
    k = p['key']
    c = f"@paperos/contract-{k}"
    ports = p['ports']
    fixtures = p['fixtures']
    pub = {
        'key': f'r4/{k}/contract-publish', 'title': f'Publish {c} v0.1 with manifest', 'type': 'Spec', 'tier': 'opus',
        'size': 'M', 'priority': 2, 'surfaces': ['Developer'], 'milestone': p['milestones'][0], 'deferred': False,
        'blockedBy': ['PAP-433', 'PAP-302', 'PAP-279', 'PAP-303', 'PAP-264', 'PAP-305'] + p.get('publish_blockedBy', []), 'blocks': [f'r4/{k}/conformance', f'r4/{k}/wire'] + p.get('impl_keys', []),
        'goal': f"Publish `{c}` v0.1 and the `{k}` module manifest so every other module codes against a versioned package instead of `{p['impl']}` internals (`docs/module-system.md` sections 1 to 3). The contract holds only types, Zod schemas, event topics, route signatures, slot definitions and port interfaces; the implementation stays in the project's Build issues. Swap risk is declared `{p['swapRisk']}` and kind `{p['kind']}`, which decides how much of the swap playbook a rewrite must follow. This is a new module: the contract is written before the implementation, so the Build issues in this project consume it from day one rather than being retrofitted.",
        'scope_in': [
            f"`packages/contracts/{k}/` published as `{c}` (workspace-private, `0.1.0`): `src/index.ts`, `ports.ts`, `events.ts`, `routes.ts`, `slots.ts` as applicable, an empty `conformance/` (filled by the conformance issue) and `fixtures/`",
            f"`module.ts` via `defineModule()` (PAP-264 shape) extended with `provides: [{{ contract: '{c}', version: '0.1.0' }}]`, `requires`, `capabilities`, `slots`, `events`, `owner: {{ agent: '{p['owner']}', project: '{k}' }}`, `swapRisk: '{p['swapRisk']}'`, `kind: '{p['kind']}'`, plus the generated `module.manifest.json`",
            f"`ownership.json` `contracts` entry (PAP-305 file) and the generated `docs/platform/contracts/{k}.md` (a `typedoc` stub until the docs generator PAP-445 lands)",
            f"A `## Module boundary` paragraph on this project's model or umbrella issue naming the contract version each Build issue implements",
        ],
        'scope_out': ['Runtime behaviour, React, Drizzle tables, network calls', 'The conformance suite and the kernel binding (own issues)', 'Changing contract-zero types; anything missing there is filed against PAP-302, PAP-279 or PAP-303'],
        'spec': [
            'Ports and schemas exported at v0.1: ' + '; '.join(ports),
            'Events declared with `defineTopic()` (payload schemas, version 1): ' + ', '.join('`' + e + '`' for e in p['events']),
            'Requires (manifest `requires[]`): ' + '; '.join(p['requires']),
            'Rules: Zod 4 only, JSON Schema generated and committed; no `z.bigint()` on wire schemas (PAP-302 `Money` codec); one sentence of doc and one fixture per port method; `size-limit` under 50 KB minified; lint R9 passes; manifest `dependsOn` is derived from `requires`, never hand-written',
            f"Every port method that mutates money, sends a message or signs a document carries `Idempotency-Key` semantics from PAP-304 in its signature (`{{ idempotencyKey }}` option) so adapters cannot forget it",
            'Error codes reuse the contracts document catalogue (`NOT_FOUND`, `FORBIDDEN`, `CONFLICT`, `MODULE_DISABLED`, `RATE_LIMITED`); module-specific codes are listed in `errors.ts` with user-facing copy keys (PAP-368)',
        ],
        'provides': f"`{c}@0.1.0` with the exports above; `module.manifest.json` valid against `manifest.schema.json`; `ownership.json` `contracts.{k}`",
        'consumes': "the manifest schema and validator (PAP-433), contract-zero (`@paperos/core/types|filter|events`, PAP-302, PAP-279, PAP-303), the base manifest shape (PAP-264) and the ownership map (PAP-305)",
        'consumed_by': p['consumers'] + f", and this module's conformance and wire issues",
        'dod': [
            'Package merged, `0.1.0` in the workspace changeset; manifest validates; `pnpm modules:validate` and `pnpm gen:dep-map` green with the new module present',
            'Generated JSON Schema, `typedoc` stub and ownership entry committed; `compat-matrix.json` (PAP-440) shows every `requires` resolving',
            'Sentinel confirms no implementation leaked into the package (no React, no Drizzle, no fetch)',
        ],
        'tests': {
            'Static': 'lint rules R7 to R9; generated JSON Schema committed and unchanged; `size-limit`; `tsc --noEmit` with `exactOptionalPropertyTypes`',
            'Unit': f'every schema accepts its valid fixture and rejects its invalid one ({fixtures}); `defineTopic` registrations resolve at import; the manifest validates and its `requires` resolve against the other manifests',
            'Review': 'Sentinel reads the package top to bottom against `docs/module-system.md` section 2 and the contracts document; every port method has a fixture',
        },
        'demo': f"`pnpm modules:validate` prints the `{k}` manifest with its provides and requires, `pnpm gen:dep-map` shows the new node with only declared edges, and `docs/platform/contracts/{k}.md` renders the port list.",
        'edge': [
            'A port needed by a Build issue but missing at v0.1 is added as a minor bump (`0.2.0`) with a fixture, never as a direct import of the implementation',
            'A type that two contracts both want (for example a scheduling `TimeRange`) goes to contract-zero via PAP-302, not into this package, to avoid a dependency between contracts',
        ],
        'deps': 'PAP-433 manifest schema (hard), contract-zero PAP-302, PAP-279, PAP-303 (hard), PAP-264 and PAP-305 (soft, shape only). Unblocks every other issue in this project.',
        'builder': p['lead'], 'reviewer': 'Sentinel (Code Reviewer)', 'tenant_data': False, 'module_edge': False,
    }
    conf = {
        'key': f'r4/{k}/conformance', 'title': f'Conformance test suite for {k} contract', 'type': 'Review', 'tier': 'opus',
        'size': 'M', 'priority': p.get('trio_priority', 4), 'surfaces': ['Developer'], 'milestone': p['milestones'][2], 'deferred': p.get('trio_deferred', True),
        'blockedBy': [f'r4/{k}/contract-publish', 'PAP-441', 'PAP-239', 'PAP-42'], 'blocks': [f'r4/{k}/wire'],
        'goal': f"Give `{c}` an executable meaning: a Vitest suite that any implementation of the {k} ports must pass, plus the golden fixtures both old and new implementations are diffed against during a swap (`docs/module-system.md` section 5). Without this, \"plug and play\" is a promise; with it, `paperos module conformance {k} --impl a,b` is a fact the gates can check.",
        'scope_in': [
            f"`packages/contracts/{k}/conformance/`: `defineConformanceSuite('{k}', factory)` covering every port exported at v0.1, one `describe` per port, one `it` per fixture; `unsupported` capability handling so partial adapters report honestly",
            f"`fixtures/`: {fixtures}; every fixture validated against the contract schemas in CI",
            "In-memory reference doubles (`memory/` inside `conformance/`) for the data-bearing ports so the suite runs without Postgres, Stripe, Twilio, Hocuspocus or network",
            "Registration with the conformance runner (PAP-441): suite id, ports, fixture manifest, expected duration; `conformance.json` output per run in the PAP-239 artefact shape (pass, fail, pending, unsupported, per-case diff)",
        ],
        'scope_out': ['The implementation itself', 'Performance budgets (PAP-242)', 'Visual checks (Gate 3)'],
        'spec': [
            'The suite is parametrised by `factory: () => Promise<Impl>` and a `capabilities` set; a case whose capability is absent is `unsupported`, a case for an `@experimental` port is `pending`; both are visible in the report and neither fails the run unless `--strict`',
            'Cases assert behaviour, not shape: idempotency (same key twice yields one row or one send), ordering guarantees, permission filtering (a principal without the audience sees nothing), error codes from the contracts document, event emission with the right topic and version',
            'Golden fixtures are immutable within a contract version: adding is a minor bump, changing is a major bump; the runner refuses fixtures whose hash changed without a version bump',
            'Runtime under 60 s against the memory doubles, under 5 min against the real adapter on the compose stack',
            f"Every case id is stable (`{k}.<port>.<n>`) so shadow-run diffs and Linear comments can cite it",
        ],
        'provides': f"`{c}/conformance` (`defineConformanceSuite`, `memory` doubles, `fixtures` index, `capabilities` list), `conformance.json` artefact for this module",
        'consumes': f"`{c}@0.1`, the runner and artefact schema (PAP-441, PAP-239), the PAP-42 compose stack for the real-adapter run, `callAs` from PAP-268 where routes are exercised",
        'consumed_by': f"`r4/{k}/wire`, the swap CLI (PAP-442), Gate 1, and every future implementation of the contract",
        'dod': [
            'Suite and fixtures merged; memory doubles pass 100 percent; real adapter passes or every failing case has a linked fix issue; negative doubles fail exactly as predicted',
            f"Registered with the runner; Gate 1 step `conformance:{k}` green; `conformance.json` attached to the PR",
            f"`docs/platform/contracts/{k}.md` gains a \"Conformance\" section listing case ids",
        ],
        'tests': [
            'The suite passes against the memory doubles in CI on every PR that touches the contract or the module.',
            'The suite passes against the real implementation on the compose stack nightly; failures open a Linear comment on the implementation issue with the case ids.',
            'Mutation check: one deliberately broken double per port (committed under `conformance/negative/`) fails exactly its cases and no others.',
            'Fixture validation: every fixture file parses against its schema; hash manifest committed and checked.',
            'Report: `conformance.json` validates against the PAP-239 schema; the contact-sheet reporter lists pass, fail, pending, unsupported counts.',
        ],
        'demo': f"`paperos module conformance {k} --impl memory,default` prints two green columns and the case ids, then a deliberately broken negative double turns exactly its cases red.",
        'edge': [
            'A port that needs a secret (Stripe, Twilio, Google Calendar, Anthropic): the real-adapter run uses recorded HTTP fixtures (`msw`), never live credentials in CI; the live run is a nightly job on staging through the credential broker (PAP-300)',
            'Nondeterministic output (ids, timestamps, model text): fixtures use placeholders and normalisers; assistant and drafting ports assert structure and citations, not prose',
        ],
        'deps': f"`r4/{k}/contract-publish` (hard), PAP-441 runner and PAP-239 artefact schema (hard), PAP-42 compose stack (soft, real-adapter run only).",
        'builder': 'Sentinel', 'reviewer': 'Atlas (Merger)', 'tenant_data': False, 'module_edge': False,
    }
    wire = {
        'key': f'r4/{k}/wire', 'title': f'Wire {k} behind the module registry with an adapter and feature flag', 'type': 'Build', 'tier': 'sonnet', 'effort': 'high',
        'size': 'M', 'priority': p.get('trio_priority', 4), 'surfaces': ['Developer'], 'milestone': p['milestones'][2], 'deferred': p.get('trio_deferred', True),
        'blockedBy': [f'r4/{k}/contract-publish', f'r4/{k}/conformance', 'PAP-434', 'PAP-435', 'PAP-366', 'PAP-267'] + p.get('impl_keys', [])[:4], 'blocks': ['PAP-266'],
        'goal': f"Make `{k}` a swappable module in practice: its implementation binds into the `@paperos/kernel` registry as the default adapter for `{c}`, every consumer resolves the ports from the kernel instead of importing `{p['impl']}`, and a `module.{k}.impl` variant flag can select a second implementation per tenant with shadow-run and five-second rollback (`docs/module-system.md` sections 4 and 6). After this issue, rewriting {k} touches no other module.",
        'scope_in': [
            f"`{p['impl'].split(',')[0].strip()}/src/adapter.ts` (or one file per port): classes or factories implementing each port from `{c}`, registered by `module.ts` `bind(kernel)`; request-scoped ports receive the tenant and actor from the kernel's request scope",
            f"Consumer migration: every import of `{k}` internals from another module (found by `pnpm gen:dep-map --undeclared`) replaced with `kernel.resolve(port)` or a hook from the contract; lint R8 turned from warning to error for this module",
            f"Flag `module.{k}.impl` declared in `flags.yaml` (PAP-366) with variants `default` and `next`; a `next` implementation stub that re-exports the default so the mechanism is exercised before a real rewrite exists",
            'Slot fills and route contributions moved from code into the manifest; event subscriptions declared in `events.subscribes`; shadow mode wiring for the module\'s read ports (`shadow: true` diffs into `swap_shadow_diff`)',
        ],
        'scope_out': ['A real second implementation', 'Changes to the contract (own issue)'],
        'spec': [
            '`bind(kernel)` registers one provider per port with `{ impl: \'default\' }`; boot fails with the port name if a port from `provides` is unbound',
            'Resolution order per request: kill switch, tenant flag rule, audience rule, default (PAP-366 order); the chosen `impl` is echoed as `X-PaperOS-Impl` on API responses and as a data attribute on slot fills',
            'Consumers hold no reference across requests to a resolved request-scoped port',
            'Shadow mode runs the secondary after the primary, never blocks the response, records `{ caseId, requestId, diff }` with a 1 percent sample by default; write ports and sending ports are never shadowed (PAP-435 rule)',
            'Disabling the module (PAP-266 `tenant_module`) unbinds its providers for that tenant; consumers with `requires[].optional=false` fail closed with `MODULE_DISABLED` (409)',
        ],
        'provides': f"`{k}` bound in the kernel as `{c}` provider `default`, flag `module.{k}.impl`, manifest `slots.fills` and `events.subscribes` complete, `X-PaperOS-Impl` on this module's routes",
        'consumes': f"`@paperos/kernel` registry and DI (PAP-434), flag swap mechanism (PAP-435), `{c}@0.1` and its conformance suite, PAP-366 flags, PAP-267 middleware for the header, and this project's Build issues",
        'consumed_by': f"{p['consumers']}, the swap CLI (PAP-442) and PAP-266's removal matrix",
        'dod': [
            f"Kernel binding merged; zero undeclared imports into `{k}` across the monorepo; conformance green through the kernel; flag flip recording attached; shadow diff report empty",
            '`docs/platform/modules.md` module page updated (bindings, flag, slots, events); dependency map regenerated and committed',
        ],
        'tests': {
            'Unit': '`bind` registers every port; unbound port fails boot with its name; request scope carries tenant and actor',
            'Integration': f"conformance suite passes against the kernel-resolved provider (not a direct import); flipping `module.{k}.impl` to `next` for one tenant changes `X-PaperOS-Impl` for that tenant only within 5 s; kill switch returns `default`",
            'Static': f"`pnpm gen:dep-map --undeclared` reports zero undeclared edges into `{k}`; lint R8 error level; `knip` finds no unused exports left behind",
            'E2E': "the module's main flows (from its model issue's Definition of done) pass unchanged after the migration; Gate 3 screenshots identical to baseline",
        },
        'demo': f"Flip `module.{k}.impl` to `next` for the demo tenant in the console, watch `X-PaperOS-Impl: next` appear on the module's routes within five seconds, then hit the kill switch and watch it revert.",
        'edge': [
            'A consumer that cached a port instance at module scope: the lint rule R10 flags it and the integration test proves the flag flip is not observed by a cached instance (so the rule must hold)',
            f"Two tenants on different implementations sharing one worker process: job handlers resolve the port inside the job with the job's tenant scope, never at worker boot",
        ],
        'deps': f"`r4/{k}/contract-publish` and `r4/{k}/conformance` (hard), PAP-434, PAP-435 (hard), PAP-366, PAP-267 (soft), the project's Build issues (hard: nothing to bind before they land).",
        'builder': p['lead'], 'reviewer': 'Sentinel (Code Reviewer)', 'tenant_data': False,
    }
    return [pub, conf, wire]
