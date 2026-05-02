# Architecture Red-Team Rubric

Use this rubric to compare a proposal against a context-appropriate architecture baseline before attacking it.

## Baseline Axes

For the target context, establish what a robust design would normally define:

- **Problem frame**: the actual user/business/system problem, non-goals, and success conditions.
- **Source of truth**: which component owns durable state, derived state, cache state, and user-visible truth.
- **Ownership boundary**: which service/module/team owns each decision, state transition, side effect, and contract.
- **State model**: allowed states, transitions, invariants, terminal states, retry behavior, and reconciliation.
- **Data lifecycle**: creation, mutation, deletion, retention, backfill, migration, audit, and recovery.
- **Trust boundary**: authentication, authorization, tenant isolation, identity propagation, and enforcement points.
- **Integration contract**: API versioning, backward compatibility, schema compatibility, client/server responsibilities, and error contracts.
- **Failure model**: timeout, partial success, duplicate execution, stale reads, dependency degradation, retries, rollback, and operator recovery.
- **Deployment model**: old/new version overlap, expand/contract migrations, feature flags, rollback ordering, config drift, and secrets.
- **Observability**: metrics, logs, traces, audit events, alerts, and manual diagnosis paths.
- **Test strategy**: unit, integration, contract, migration, e2e, load, chaos, and rollback validation matched to actual risk.
- **Evolution pressure**: expected scale, number of use cases, team ownership, future product changes, and abstraction cost.

## Context Patterns

Use these patterns as starting points, not rigid templates.

### CRUD / Admin Workflow

Expected baseline:

- One clear durable source of truth.
- Simple request/response flow before async complexity.
- Server-side validation and authorization.
- Explicit empty, error, and permission states.
- Focused tests around validation, persistence, and permissions.

Red flags:

- Event-driven or generic abstractions before multiple concrete use cases exist.
- Client-owned truth for data that the server must enforce.
- Hidden lifecycle encoded as loose booleans without named states.

### Workflow / State Machine

Expected baseline:

- Named states and allowed transitions.
- Idempotent transition commands.
- Durable audit trail for important transitions.
- Recovery path for stuck or partial transitions.

Red flags:

- State spread across unrelated flags, timestamps, and side effects.
- No invariant for retries, cancellation, or re-entry.
- Business rules enforced only in UI flow.

### Multi-Tenant SaaS

Expected baseline:

- Tenant identity propagated through every backend boundary.
- Authorization enforced server-side close to data access.
- Data model makes tenant isolation explicit.
- Tests cover cross-tenant access and ownership transfer.

Red flags:

- Tenant filtering treated as a UI or query convention.
- Cache keys or background jobs omit tenant identity.
- Shared resources have unclear ownership.

### Event-Driven / Async System

Expected baseline:

- Clear event ownership, schema versioning, delivery semantics, idempotency, replay behavior, and dead-letter handling.
- Consumers tolerate duplicates, reordering, and old event versions.
- Side effects are isolated behind idempotency or transactional boundaries.

Red flags:

- Exactly-once behavior assumed without enforcement.
- Events used to avoid defining a transaction boundary.
- No plan for poison messages, replay, or partial downstream failure.

### Data Pipeline / Migration

Expected baseline:

- Expand/contract rollout when live compatibility matters.
- Backfill safety, resumability, validation, and rollback story.
- Clear treatment of partial migration and old readers/writers.

Red flags:

- One-shot migration with no verification or recovery.
- Schema and code deploy order must be perfect.
- Derived data lacks reconciliation or source-of-truth checks.

### Auth / Identity / Permission Boundary

Expected baseline:

- Backend enforcement at the data or service boundary.
- Explicit identity model, trust boundary, permission derivation, and audit path.
- Deny-by-default behavior for ambiguous state.

Red flags:

- Frontend gates treated as authorization.
- Tokens, sessions, roles, or tenant memberships assumed stable without refresh/revocation handling.
- Permission cache invalidation not defined.

### Frontend State Architecture

Expected baseline:

- Clear split between server state, client UI state, URL state, optimistic state, and cached derived state.
- Loading, error, empty, stale, offline, and permission states are modeled.
- Server remains source of truth for enforceable data.

Red flags:

- Optimistic state has no reconciliation path.
- Client state machine contradicts backend lifecycle.
- Cache invalidation depends on user navigation or timing.

### API / Platform Contract

Expected baseline:

- Stable contract, versioning/migration plan, compatibility policy, typed error semantics, and consumer expectations.
- Contract tests for important consumers.

Red flags:

- Response shape or semantics change without compatibility story.
- Internal implementation concepts leak into public API.
- Errors are strings or ambiguous statuses that clients must reverse-engineer.

### Infrastructure / Rollout

Expected baseline:

- Deployment ordering, rollback, feature flag behavior, configuration, secret rotation, observability, and capacity assumptions are explicit.
- Old and new versions can overlap safely.

Red flags:

- Rollback contradicts data migration.
- Config or secret changes require perfect manual sequencing.
- Health checks do not cover the new critical dependency.

## Attack Questions

Ask these aggressively:

- If the main assumption is false, what breaks first?
- Where is the single source of truth, and who can contradict it?
- What invariant must always hold, and where is it enforced?
- What happens after partial success followed by retry?
- What happens when the same operation runs twice?
- What happens when old and new code run at the same time?
- What happens when a user changes tenant, role, ownership, or identity mid-flow?
- What happens when the dependency is slow, unavailable, or returns stale data?
- What happens when rollback occurs after data shape changes?
- What is being called "simple" while moving complexity somewhere else?
- What abstraction was introduced before the design has enough examples to justify it?
- What important behavior exists only as convention, naming, or developer memory?

## Architecture Quality Gate

End substantial reviews with a quality gate. The score is a decision aid, not a substitute for judgment.

### Scorecard

Use a 100-point score:

| Area | Points | What Good Looks Like |
| --- | ---: | --- |
| Context fit | 15 | The design fits the actual problem, scale, constraints, and team/operational context. |
| Reference baseline alignment | 15 | Deviations from the expected architecture are explicit, justified, and protected. |
| Source of truth and ownership | 15 | Durable state, derived state, side effects, and decision ownership are unambiguous. |
| State and invariant model | 15 | Critical states, transitions, terminal states, retries, and invariants are defined and enforced. |
| Failure, retry, and recovery | 15 | Partial failure, duplicate execution, stale reads, timeouts, dependency degradation, and recovery are handled. |
| Security and trust boundaries | 10 | Auth, authorization, tenant isolation, identity propagation, and enforcement points are explicit. |
| Deployment, rollback, and migration | 10 | Old/new version overlap, expand/contract rollout, rollback order, and data compatibility are safe. |
| Observability and test strategy | 5 | Monitoring and tests match the actual architectural risk. |

### Decision Thresholds

- `Pass`: 85-100 with no hard gate failures.
- `Conditional Pass`: 70-84 with no hard gate failures, or minor hardening work clearly bounded.
- `Fail`: 50-69, or any hard gate failure that requires redesign before proceeding.
- `Revert Recommended`: 0-49, or the current direction is materially worse than the previous design/baseline and continued implementation will deepen the architectural debt.

### Hard Gate Failures

Hard gate failures override the score:

- Critical state has no clear source of truth.
- Ownership boundary is ambiguous for critical decisions, side effects, or lifecycle transitions.
- Authorization, tenant isolation, or trust boundary is unenforced or only enforced in the frontend.
- Data loss, duplicate irreversible side effects, or corruption is plausible under retry, concurrency, or partial failure.
- Critical workflow has no stated invariant or no enforcement point for the invariant.
- Rollback contradicts the migration or data-shape strategy.
- The design depends on old and new versions never overlapping during deploy.
- A public or cross-team contract changes without compatibility, versioning, or consumer migration strategy.
- The design introduces async/event-driven behavior without idempotency, delivery semantics, replay handling, or poison-message strategy where those risks matter.

### Gate Output

Use this shape:

```markdown
## Architecture Quality Gate

Score: 58 / 100
Decision: Fail

Hard gate failures:
- Critical state has no single source of truth.
- Retry after partial success can duplicate side effects.

Blocking conditions:
- Define ownership and source of truth for account state.
- Define idempotency and recovery for retry after partial success.

Revert / redesign recommendation:
Do not proceed with this architecture as written. Return to the previous baseline or pause implementation until ownership and recovery are redesigned.
```

## Output Discipline

- Report material architecture objections first.
- Treat missing context as an assumption gap, not as proof.
- Do not pad the review with generic risks.
- Do not propose a full redesign unless the current design is fundamentally wrong.
- Prefer correction directions over implementation steps.
- Separate "wrong for this context" from "different from my preference."
