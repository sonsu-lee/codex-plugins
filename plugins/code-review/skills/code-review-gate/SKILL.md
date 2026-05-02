---
name: code-review-gate
description: "Use when the user asks for a personal code review, review gate, merge-readiness check, PR/diff/commit/branch review, or asks whether current code changes are acceptable. The review pass is read-only: do not edit files, stage changes, commit, publish PR comments, resolve review threads, or produce a remediation plan while performing the gate."
---

# Code Review Gate

## Purpose

Review a code change against the work it was meant to accomplish and decide whether it is acceptable.

This is the primary personal acceptance gate for code review requests. It is not a team-commenting workflow. It checks whether the change stays within scope, works correctly, is structurally sound for the task, follows the codebase, and has enough regression evidence. It may detect architecture impact, but full architecture red-team review belongs to the dedicated architecture-review workflow.

Built-in or Superpowers code review can be used as optional independent reviewer input only when the user explicitly asks for strict, independent, multi-agent, multi-perspective, or Superpowers-backed review. This skill owns the final finding calibration, score, and `Pass`, `Conditional Pass`, or `Fail` verdict.

## Hard Rules

- The review pass is read-only. Do not edit files, apply patches, stage changes, commit, push, publish PR comments, resolve review threads, or start a remediation plan while evaluating the gate.
- If the user explicitly asks for follow-up edits, staging, commits, PR comments, or review-thread actions in the same request, finish the review gate first, then leave this skill's review phase and use the appropriate implementation, Git, or GitHub workflow for that write action.
- Findings must be grounded in inspected code, diff, tests, configs, or clearly labeled inference.
- Do not report vague advice. Every finding needs concrete evidence and impact.
- Do not inflate severity. A finding is blocking only when it can break behavior, violate scope, invalidate regression confidence, or leave high architecture impact unresolved.
- If requirements are missing, infer intent from the diff and branch/commit context, then label that intent as inferred.
- Use the user's language unless they request otherwise.

## References

Use progressive disclosure:

- Read `references/gate-rubric.md` for every substantial review and whenever assigning gate status.
- Read `references/finding-calibration.md` before assigning severity, confidence, score, or final decision.
- Read `references/architecture-impact.md` whenever the change touches APIs, data models, auth, state lifecycle, rollout, rollback, or shared abstractions.
- Read `references/agent-passes.md` only when the user explicitly asks for strict, independent, parallel, multi-agent, multi-perspective, built-in, or Superpowers-backed review.

## Review Target

Resolve the review target before judging:

- If the user names a PR, commit, branch, patch, or file range, review that target.
- If the user provides requirements, ticket text, plan text, or a task summary, treat it as the scope source of truth.
- If no target is named, review the current working tree diff.
- If no explicit requirements exist, inspect nearby git context and changed files to infer the intended task.

For local reviews, inspect:

- `git status --short`
- the relevant diff or commit range
- nearby contracts, tests, schemas, configs, and call sites needed to understand changed behavior
- repository instructions such as `AGENTS.md`, package metadata, and existing test patterns when relevant

## Review Gates

Evaluate every substantial review through these gates:

1. **Scope Fit** - Does the change match the requested task, ticket, plan, or inferred intent? Flag missing requirements, scope creep, unrelated cleanup, and accidental behavior changes.
2. **Correctness** - Look for bugs, edge cases, regressions, error handling gaps, type or API contract violations, stale state, ordering issues, and compatibility breaks.
3. **Structural Soundness** - Within the task scope, check responsibility boundaries, state flow, dependency direction, data flow, and whether the change bypasses established abstractions.
4. **Code Quality** - Check complexity, duplication, readability, maintainability, testability, and whether the change adds unnecessary abstraction.
5. **Convention Fit** - Check consistency with local style, framework patterns, naming, test style, repository rules, and existing helper APIs.
6. **Regression Gate** - Decide whether existing or new tests, builds, type checks, or manual verification are enough for the risk of the change. Missing appropriate verification is a gate finding.
7. **Architecture Impact** - Check whether the change affects source of truth, API contracts, data models, auth or tenant boundaries, state lifecycle, migrations, rollout or rollback, or shared platform abstractions.

Use `references/gate-rubric.md` for detailed pass, conditional, and fail criteria.

## Architecture Escalation

Always run the lightweight architecture impact gate. Do not duplicate the full architecture-red-team rubric here.

Escalate to the dedicated architecture-review workflow when impact is high, including:

- source of truth moves or becomes ambiguous
- data model, migration strategy, or API contract changes across callers
- auth, permission, tenant isolation, sandbox, or trust boundary changes
- state lifecycle, concurrency, retry, rollback, or old/new version overlap is material
- shared abstraction, platform layer, or cross-subsystem ownership changes

When escalation is required, the final decision cannot be `Pass`. Use `Conditional Pass` or `Fail` and name the architecture-review condition.

Use `references/architecture-impact.md` for low, medium, and high impact thresholds.

## Optional Agent Passes

Default to one reviewer pass. Use built-in review, Superpowers review, or read-only subagents only when the user explicitly asks for agents, parallel review, independent review, strict review, multiple perspectives, or Superpowers-backed review.

Allowed independent passes:

- `Scope Reviewer` - requirements fit, missing work, extra work, scope creep
- `Correctness Reviewer` - bugs, edge cases, regressions, test gaps
- `Quality Reviewer` - code quality, conventions, maintainability
- `Architecture Impact Reviewer` - lightweight architecture escalation signals

Review subagents must not edit files. The coordinator merges their results, removes duplicates, recalibrates severity and confidence, and owns the final verdict.

External reviewer output is advisory. Do not delegate the gate decision to built-in review, Superpowers review, or any subagent. Incorporate their concrete findings only after verifying or labeling the evidence, then apply this skill's severity, hard-gate, score, and architecture escalation rules.

Use `references/agent-passes.md` for role prompts and coordinator rules.

## Severity

- `P0`: Data loss, security breach, unrecoverable outage, impossible rollback, or catastrophic production failure.
- `P1`: Plausible broken behavior, major regression, hard scope violation, invalid verification, or unresolved high architecture impact.
- `P2`: Non-blocking but meaningful quality, maintainability, compatibility, or test-confidence risk.
- `P3`: Minor issue or bounded cleanup opportunity that should not block acceptance.

## Scoring And Gate Decision

Provide a 100-point score as a useful signal, but hard gates override score.

Decision labels:

- `Pass`: No blocking findings, regression gate passes, and architecture escalation is not required.
- `Conditional Pass`: The change can proceed only after named non-catastrophic conditions are resolved or verified.
- `Fail`: A P0/P1 issue, scope failure, regression gate failure, or unresolved high architecture impact blocks acceptance.

A high numeric score cannot override a failed regression gate, failed scope gate, P0/P1 finding, or required architecture escalation.

Use `references/finding-calibration.md` to calibrate severity, confidence, hard gates, and score.

## Finding Format

Use stable finding ids in discovery order: `RG-001`, `RG-002`, `RG-003`.

Each finding must include:

- id
- severity
- confidence
- gate
- file:line evidence
- problem
- impact
- correction direction

The correction direction should state what needs to change. Do not create a detailed remediation plan, allowed-file list, or parallel work assignment in this v1 skill.

## Required Output

Lead with findings. Keep the summary secondary.

```markdown
## Findings

[RG-001] [P1] Title
- Confidence:
- Gate:
- Evidence:
- Problem:
- Impact:
- Correction direction:

## Gate Summary

- Decision:
- Score:
- Scope Fit:
- Correctness:
- Structural Soundness:
- Code Quality:
- Convention Fit:
- Regression Gate:
- Architecture Impact:
- Architecture Escalation:

## Open Questions / Assumptions

## Reviewed Scope

## Verdict
```

If there are no findings, state that clearly and still report residual risk, checks inspected or run, and any verification gaps.
