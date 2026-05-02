# Gate Rubric

Use this reference for every substantial code review gate. The review asks whether the change is acceptable within the requested task scope, not whether the repository could be improved in general.

## Scope Fit

Pass:
- The changed behavior matches the task, ticket, plan, user request, or clearly inferred intent.
- Supporting changes are necessary for the requested work.
- No unrelated cleanup, opportunistic refactor, or unrequested feature is mixed in.

Conditional:
- Intent is inferred rather than explicit, but the diff strongly supports the inferred scope.
- Small adjacent cleanup is present and low risk, but should be called out.
- A requirement may be incomplete but does not change the core behavior.

Fail:
- The change solves a different problem than requested.
- Required behavior is missing.
- Unrelated behavior change, broad refactor, dependency change, generated churn, or API change is mixed into the task.
- The diff makes acceptance impossible to judge because the scope is too broad or incoherent.

Review moves:
- Compare actual changed behavior to the stated scope line by line.
- Separate missing work from extra work.
- Treat "nice to have" additions as scope risk unless they are necessary for the task.

## Correctness

Pass:
- Main behavior, edge cases, and error paths are handled for the risk level of the change.
- Changed contracts are honored at callers and callees.
- Compatibility with existing data, state, and users is preserved or explicitly handled.

Conditional:
- A plausible edge case is not covered but has bounded impact.
- Error handling is imperfect but does not hide failures or corrupt state.
- Runtime verification is missing for a low-risk path but static evidence is strong.

Fail:
- A realistic input, state transition, ordering, retry, null/empty case, permission case, or compatibility path breaks.
- A caller can observe inconsistent state or a broken API contract.
- A catch-all, fallback, or default path silently accepts invalid behavior.
- A change weakens auth, validation, isolation, persistence integrity, or rollback behavior.

Review moves:
- Trace data and state through the changed path.
- Check old and new callers when interfaces move.
- Prefer concrete failure scenarios over abstract concerns.

## Structural Soundness

Pass:
- Responsibilities remain clear inside the task boundary.
- The change follows established ownership, state flow, and dependency direction.
- New abstractions remove real complexity or match existing patterns.

Conditional:
- A boundary is slightly blurred but contained to the touched module.
- A helper is acceptable now but should not be expanded without redesign.
- Structure is adequate for the task but likely needs follow-up if the feature grows.

Fail:
- The change creates a new source of truth without ownership clarity.
- State is duplicated or synchronized manually without a defined lifecycle.
- A module bypasses existing policy, validation, data access, or platform abstractions.
- The implementation couples unrelated layers or makes future changes brittle under normal evolution.

Review moves:
- Judge structure at the scale of the task, not at whole-system architecture depth.
- Escalate to architecture review only when the boundary or source-of-truth concern crosses subsystem lines.

## Code Quality

Pass:
- The implementation is readable, direct, maintainable, and testable.
- Complexity is proportional to the behavior.
- Duplication is either avoided or consciously cheaper than abstraction.

Conditional:
- Naming or decomposition could be clearer, but behavior remains easy to verify.
- A small duplication is acceptable because abstraction would be premature.
- Complexity is tolerable for a transitional change.

Fail:
- Control flow, hidden mutation, global state, broad catch blocks, or implicit coupling makes behavior hard to reason about.
- The change adds unnecessary abstraction, generic framework code, or future-proofing that obscures the task.
- Test setup or implementation structure makes meaningful regression coverage difficult.

Review moves:
- Flag quality issues only when they create reviewable maintenance or correctness risk.
- Do not report subjective style preferences as findings.

## Convention Fit

Pass:
- The change follows existing style, naming, framework patterns, file organization, helper APIs, and test idioms.
- New code fits local error handling and logging conventions.

Conditional:
- A minor convention mismatch exists but does not affect behavior or maintainability.
- The repo has mixed patterns and the chosen pattern is defensible.

Fail:
- The change ignores established local helpers, policy layers, data access patterns, or framework conventions.
- It introduces a second competing pattern without justification.
- It violates repository instructions, generated-file boundaries, or public API conventions.

Review moves:
- Prefer local precedent over generic best practice.
- Check nearby files before claiming a convention violation.

## Regression Gate

Pass:
- Appropriate tests, type checks, builds, or focused manual validation cover the behavior and risk.
- Existing tests genuinely exercise the changed path.
- The review can name the verification evidence inspected or run.

Conditional:
- Verification exists but misses one bounded edge case.
- A check cannot run for environmental reasons, and the proof gap is explicit.
- The change is low risk and code inspection is enough, with rationale.

Fail:
- No meaningful verification covers changed behavior that can regress.
- Tests only assert mocks, snapshots, wiring, or implementation details while missing real behavior.
- The change affects runtime, API, data, auth, or state behavior without proportional regression evidence.
- Verification claims are made without fresh evidence or inspectable support.

Review moves:
- Require stronger evidence as blast radius grows.
- Treat missing regression coverage as a gate finding, not a minor suggestion, when behavior can break.

## Architecture Impact

Pass:
- No source-of-truth, API, data, auth, lifecycle, rollout, rollback, or shared abstraction impact.
- Architecture impact is local and explained by the task.

Conditional:
- Medium impact exists but the change includes sufficient compatibility and rollback reasoning.
- Architecture questions are bounded and can be resolved before acceptance.

Fail:
- High impact exists and no dedicated architecture review or design rationale is present.
- The change crosses ownership or trust boundaries without migration, compatibility, or rollback reasoning.

Review moves:
- Use `architecture-impact.md` for thresholds.
- Do not run a full architecture red-team inside this skill.
