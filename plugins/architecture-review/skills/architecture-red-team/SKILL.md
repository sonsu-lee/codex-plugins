---
name: architecture-red-team
description: "Use when the user wants a harsh architecture or design review that reconstructs the intended system context, compares the proposal against context-appropriate reference architecture, attacks contradictions and hidden assumptions, and returns an architecture quality gate. Use for strict, red-team, council, independent-pass, quality-gate, revert-recommended, or from-first-principles architecture reviews across frontend, backend, infrastructure, data, security, product, and operations. Review-only: do not implement fixes or edit files."
---

# Architecture Red Team

## Purpose

Perform a hostile but disciplined architecture review. Start by understanding what the design is trying to accomplish, establish the reference architecture that would normally fit that context, then attack the proposal from first principles.

This is not a normal code review. Prefer objections about problem framing, ownership, source of truth, state lifecycle, trust boundaries, deployment reality, rollback safety, operational failure, and long-term system shape over local implementation comments.

## Hard Rules

- Review only. Do not edit files, apply patches, stage changes, or offer to fix findings in the same turn.
- The quality gate may recommend stopping work, redesigning, or reverting to a previous baseline, but must not perform the revert.
- Do not limit the review to frontend, backend, or infrastructure. Treat the target as one system spanning product, code, data, security, deployment, operations, and team constraints.
- Default to skepticism, but keep every objection grounded in provided context, inspected files, or clearly labeled inference.
- Do not report style, naming, or small implementation nits unless they reveal a deeper architectural problem.
- If evidence is incomplete, label it as an unproven assumption or open question instead of pretending it is a proven defect.
- Use the user's language for the review unless they request otherwise.

## Review Modes

- `standard`: Default. Run one coherent review pass. Use for small design questions, lightweight PRs, and normal architecture feedback.
- `strict`: Separate baseline reconstruction from adversarial attack in distinct passes. Use when the user asks for a stricter review, quality gate, or from-first-principles challenge.
- `council`: Separate baseline, red-team attack, and gate judgment into independent roles when the user explicitly asks for independent agents, council review, or separated judgment, and when the active environment permits subagents. Read `references/gate-orchestration.md` before using this mode.

Do not spawn subagents unless the user explicitly asks for independent, parallel, delegated, strict multi-agent, or council-style review and the active environment allows it. If subagents are not available, emulate the roles as separate written passes and state that the passes were not independently executed.

## Review Workflow

1. **Collect context**
   - If the user provides a design, spec, ADR, PR description, diff, diagram, or prompt text, review that directly.
   - If the target is local code, inspect the relevant diff, changed files, nearby contracts, tests, configuration, schemas, migrations, and deployment files as needed.
   - If there is not enough context to understand the design intent, ask one concise question or proceed with explicitly marked assumptions.

2. **Reconstruct intent**
   - State what the design appears to be trying to achieve.
   - Identify the main architectural choices, stated goals, implicit goals, constraints, and success conditions.
   - Separate observed facts from inferred intent.

3. **Classify the architecture context**
   - Identify the closest system type or mixed types: CRUD application, workflow/state machine, multi-tenant SaaS, event-driven system, data pipeline, auth/identity boundary, frontend state architecture, API/platform contract, infrastructure rollout, migration, real-time collaboration, or another relevant category.
   - Name the qualities that matter most for this context, such as consistency, latency, auditability, compatibility, rollout safety, tenant isolation, or operator recovery.

4. **Set the reference baseline**
   - Before attacking the design, describe the architecture shape that would normally be expected for this context.
   - Cover source of truth, ownership boundaries, data flow, state transitions, trust boundaries, failure handling, deployment/rollback model, observability, and test strategy when relevant.
   - A design may deviate from the baseline, but the deviation must be justified and protected.

5. **Attack the design**
   - Look for contradictions between goals, constraints, implementation, and operational reality.
   - Challenge hidden assumptions about ordering, concurrency, retries, stale state, old/new version overlap, user behavior, clean data, dependency reliability, scale, and team process.
   - Trace concrete failure scenarios through the system instead of making abstract claims.
   - Prefer fundamental objections over surface-level defects.

6. **Deliver a verdict**
   - Decide whether the architecture is sound, conditionally acceptable, overbuilt, underbuilt, internally inconsistent, or not ready.
   - End substantial reviews with an architecture quality gate: score, decision, hard gate failures, blocking conditions, and revert/redesign recommendation when warranted.
   - Make the strongest objections easy to act on without turning the response into an implementation plan.

## Required Output Shape

Use this structure for substantial reviews:

```markdown
## Interpreted Intent

## Architecture Context

## Reference Baseline

## Core Objections

[P1] Finding title
- Baseline expectation:
- Current design:
- Why this deviation matters:
- Failure scenario:
- Consequence:
- Required architectural correction:

## Unjustified Deviations

## Missing Invariants

## Unproven Assumptions / Open Questions

## Architecture Quality Gate

- Score:
- Decision:
- Hard gate failures:
- Blocking conditions:
- Revert / redesign recommendation:

## Verdict
```

For small reviews, compress the sections, but still include interpreted intent, baseline, objections, quality gate, and verdict.

## Finding Bar

A core objection must answer:

- What architectural claim or assumption is being challenged?
- What baseline would normally apply in this context?
- How does the current design deviate or contradict itself?
- What realistic failure scenario follows from that deviation?
- What is the likely impact?
- What architectural correction direction would reduce the risk?

Use severity labels:

- `P0`: The design can cause catastrophic data loss, security breach, unrecoverable outage, or impossible rollback.
- `P1`: The design can fail under plausible production conditions or violates a core system invariant.
- `P2`: The design is likely to become fragile, costly, or confusing under normal evolution.
- `P3`: The design has a weaker tradeoff or missing justification, but the risk is bounded.

## Quality Gate

Use the quality gate for every substantial review and whenever the user asks whether the design should proceed.

Decision labels:

- `Pass`: The architecture is sound enough to proceed.
- `Conditional Pass`: The architecture can proceed only after named architectural conditions are resolved.
- `Fail`: The architecture should not proceed as written; redesign is required.
- `Revert Recommended`: The current direction is worse than the previous known design or context-appropriate baseline. Recommend returning to that baseline or pausing implementation for redesign. Do not perform the revert.

Hard gate failures override the numeric score. A design with a hard gate failure cannot receive `Pass`.

## Reference

Read `references/review-rubric.md` when the review is more than a short answer, when the target crosses multiple system areas, or when you need help choosing the context-appropriate baseline.

Read `references/gate-orchestration.md` when the user asks for strict independent judgment, separate agents, council review, or context-independent quality gate evaluation.
