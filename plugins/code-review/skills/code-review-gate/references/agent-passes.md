# Agent Passes

Use this reference only when the user explicitly asks for strict, independent, parallel, multi-agent, multi-perspective, built-in, or Superpowers-backed review.

All review agent passes are read-only. They must not edit files, propose broad remediation plans, stage changes, commit, push, publish PR comments, or resolve review threads while performing review. If the user explicitly requested follow-up write actions, those happen after the coordinated review under the appropriate implementation, Git, or GitHub workflow.

## When To Use Agents

Use built-in review, Superpowers review, or agents when:
- The user explicitly asks for agents, parallel review, independent review, strict review, multiple perspectives, built-in review, or Superpowers-backed review.
- The diff is large enough that independent review lanes reduce missed findings.
- The review needs separated judgment across scope, correctness, quality, and architecture impact.

Do not use agents when:
- The review is small and a single pass is sufficient.
- The next step depends immediately on one blocking local investigation.
- The user did not ask for delegated or parallel agent work.

## Front-Door Gate Policy

This skill is the front-door acceptance gate for personal code review. Built-in review, Superpowers review, and subagent passes are reviewer backends, not decision owners.

Use them to collect candidate findings or fresh perspectives. The coordinator must still:
- verify or label their evidence
- remove duplicates
- apply this plugin's gate rubric and finding calibration
- decide the final `Pass`, `Conditional Pass`, or `Fail`
- decide whether architecture-review escalation is required

If an external reviewer says "ready to merge" but this gate has a hard failure, the final verdict is not `Pass`.

If an external reviewer reports an issue that does not meet this plugin's finding bar, downgrade it to an open question or omit it.

## Shared Agent Prompt Requirements

Every reviewer receives:
- Review target and base/head or working-tree context.
- Requirements, ticket, plan, or inferred scope.
- Changed files or focused diff instructions.
- The review-only rule.
- Required output: findings with evidence, severity suggestion, confidence, and open questions.

Every reviewer must:
- Ground claims in inspected evidence.
- Ignore unrelated pre-existing issues unless worsened by the change.
- Avoid implementation work.
- Return only review inputs; the coordinator owns final verdict.

## Scope Reviewer

Focus:
- Requirement coverage.
- Missing requested behavior.
- Extra unrequested behavior.
- Scope creep and unrelated cleanup.
- Whether the diff is coherent enough to review.

Output:
- Scope Fit status: pass, conditional, or fail.
- Candidate findings with file:line evidence.
- Any assumptions about inferred intent.

## Correctness Reviewer

Focus:
- Bugs, regressions, edge cases, error paths.
- API, type, data, and compatibility contracts.
- Runtime behavior across old and new paths.
- Whether tests exercise real behavior.

Output:
- Correctness and Regression Gate status.
- Candidate P0/P1/P2 findings.
- Verification gaps and concrete failure scenarios.

## Quality Reviewer

Focus:
- Maintainability, readability, complexity, duplication.
- Responsibility boundaries inside the task.
- Local conventions and established helper APIs.
- Testability and unnecessary abstraction.

Output:
- Structural Soundness, Code Quality, and Convention Fit status.
- Candidate P2/P3 findings unless the quality issue creates realistic broken behavior.
- Local convention evidence.

## Architecture Impact Reviewer

Focus:
- Source of truth.
- API contracts, data models, auth boundaries, state lifecycle.
- Migration, rollout, rollback, compatibility, shared abstractions.
- Whether dedicated architecture-review is required.

Output:
- Architecture Impact: low, medium, or high.
- Architecture Escalation: not required, recommended, or required.
- Candidate findings only when impact blocks the gate.

## Coordinator Rules

The coordinator must:
- Merge overlapping findings into one stable `RG-###` item.
- Recalibrate severity and confidence using `finding-calibration.md`.
- Resolve disagreements by inspecting code directly when possible.
- Keep only findings that meet the finding bar.
- Produce the final score and decision.
- Label agent-derived claims that were not independently verified by the coordinator.

The coordinator must not:
- Treat agent output as authoritative without review.
- Report duplicate findings from multiple passes.
- Let a P3 style issue distract from scope, correctness, regression, or architecture hard gates.
