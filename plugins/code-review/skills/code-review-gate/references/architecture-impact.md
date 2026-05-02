# Architecture Impact

Use this reference whenever a change touches APIs, data models, auth, state lifecycle, rollout, rollback, or shared abstractions.

This skill performs only a lightweight architecture impact gate. Full red-team architecture review stays in the dedicated architecture-review workflow.

## Low Impact

Low impact usually stays inside the normal code-review gate:
- Local implementation detail changes.
- UI or handler behavior with unchanged contracts.
- Tests, small helpers, or private functions with no ownership shift.
- Refactors that preserve public behavior and source of truth.
- Local error handling improvements that do not change policy.

Review action:
- Note `Architecture Impact: Low`.
- Do not escalate unless another gate finds a concrete issue.

## Medium Impact

Medium impact can remain in code-review if the diff includes enough rationale and compatibility evidence:
- New local abstraction inside one module.
- Internal API shape changes with all callers updated.
- State flow changes that remain inside one component or service.
- Data transformation changes without migration or persistence ownership changes.
- Behavior changes behind an existing boundary with clear tests.

Review action:
- Check compatibility, rollback, and regression evidence.
- Use `Conditional Pass` if rationale or verification is incomplete.
- Escalate only if open questions affect system direction.

## High Impact

High impact requires dedicated architecture-review before `Pass`:
- Source of truth moves, splits, duplicates, or becomes ambiguous.
- Database schema, persistent data semantics, migrations, or backfills change.
- Public API, wire format, event schema, SDK surface, or cross-service contract changes.
- Auth, authorization, tenant isolation, sandboxing, secrets, or trust boundaries change.
- State lifecycle, concurrency, retries, idempotency, consistency model, or old/new version overlap changes materially.
- Rollout, rollback, or compatibility depends on operational assumptions not shown in the change.
- Shared platform abstractions, framework layers, policy layers, or ownership boundaries change.
- The change introduces a new subsystem integration or external dependency with runtime failure modes.

Review action:
- Set `Architecture Impact: High`.
- Set `Architecture Escalation: Required`.
- Final decision cannot be `Pass`.
- Do not perform the full architecture review here; name the specific architecture questions that must be reviewed.

## Escalation Finding

Use a finding when architecture impact blocks acceptance:

```markdown
[RG-00X] [P1] Architecture review required for source-of-truth change
- Confidence: 0.85
- Gate: Architecture Impact
- Evidence: path/to/file:line
- Problem: The change moves X from server-owned state to client-owned cache without defining ownership or old-client behavior.
- Impact: Old and new clients can observe inconsistent state during rollout.
- Correction direction: Run architecture-review and define source of truth, compatibility, and rollback invariants before acceptance.
```

## Boundary With Structural Soundness

Structural Soundness inside code-review:
- The task-local implementation has unclear responsibilities.
- A helper bypasses local module conventions.
- State flow inside one component is confusing but contained.

Architecture-review escalation:
- Ownership or source of truth changes across modules or services.
- Trust boundaries or data contracts change.
- Operational rollout, rollback, or migration must be designed.

When uncertain, label the architecture impact as `Medium` or `High` and explain the uncertainty instead of pretending the risk is settled.
