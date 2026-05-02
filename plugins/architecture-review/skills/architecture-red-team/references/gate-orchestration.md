# Gate Orchestration

Use this reference when the user asks for stricter, more independent architecture judgment.

## Goal

Reduce single-pass bias by separating three concerns:

- Reconstructing the intended context and reference baseline.
- Attacking the design for contradictions and failure modes.
- Judging the quality gate independently from the attack narrative.

This separation is useful because a reviewer can otherwise bend the baseline to fit the implementation, defend its first interpretation, or score the design based on the findings it already chose to emphasize.

## Modes

### Standard

Use one reviewer pass.

Best for:

- Small design questions.
- Low-risk PRs.
- Early informal feedback.

Output:

- Interpreted intent.
- Architecture context.
- Reference baseline.
- Core objections.
- Quality gate.
- Verdict.

### Strict

Use separate written passes in one agent:

1. Baseline pass.
2. Red-team attack pass.
3. Gate judgment pass.

Best for:

- User asks for a strict quality gate.
- The design crosses multiple system areas.
- The review is important but subagents are not available or not explicitly requested.

State that the passes are separated but not independently executed.

### Council

Use separate subagents only when the user explicitly asks for independent agents, council review, or delegated/parallel judgment and the active environment permits subagents.

Roles:

1. **Context / Baseline Reviewer**
   - Input: original design/context only.
   - Task: reconstruct intent, classify architecture context, define reference baseline, identify critical quality attributes.
   - Must not attack or score the design.

2. **Red-Team Reviewer**
   - Input: original design/context plus the baseline, if available.
   - Task: find contradictions, unjustified deviations, missing invariants, and concrete failure scenarios.
   - Must not assign the final score.

3. **Gate Judge**
   - Input: original design/context, baseline output, red-team output, and `review-rubric.md`.
   - Task: independently score the design, identify hard gate failures, choose decision, and name blocking conditions.
   - Must not blindly copy findings; must map them to the rubric.

## Isolation Rules

- Give each role only the context it needs.
- Do not show the Red-Team Reviewer the intended final score.
- Do not ask the Baseline Reviewer to find defects.
- Do not ask the Red-Team Reviewer to decide whether to revert.
- Require the Gate Judge to inspect the original context and rubric, not only the red-team output.
- If a subagent result is weak or generic, do not inflate it. Treat it as weak evidence and make the final synthesis narrower.

## Parent Synthesis

The parent reviewer owns the final answer. It should:

- Merge duplicate objections.
- Downgrade unsupported claims to assumptions or open questions.
- Preserve disagreements that matter.
- Apply the quality gate thresholds and hard failures.
- Keep the review-only boundary: recommend stopping, redesigning, or reverting, but do not edit files or perform the revert.

## Council Output Shape

```markdown
## Independent-Pass Summary

- Baseline reviewer:
- Red-team reviewer:
- Gate judge:

## Interpreted Intent

## Architecture Context

## Reference Baseline

## Core Objections

## Unjustified Deviations

## Missing Invariants

## Unproven Assumptions / Open Questions

## Architecture Quality Gate

## Verdict
```
