# Orchestration Rules

Use this when reviewing multiple marketplace plugins, role overlap, trigger collision, or delegation boundaries.

## Role Model

Classify each plugin as one or more of:

- `front-door`: primary entry point for a broad user request.
- `specialist`: deeper workflow for a narrower domain.
- `support`: utility workflow used before or after another workflow.
- `gate`: read-only pass/fail or readiness judgment.

The same plugin can have more than one label, but its primary owner role should be clear.

## Expected Boundaries

- `plugin-creator`: creates and scaffolds plugin artifacts. It may write files.
- `marketplace-quality-gate`: audits existing plugin artifacts and marketplace orchestration as an internal skill. It is read-only.
- `code-review`: judges whether a code change passes a personal review gate.
- `architecture-review`: performs specialist architecture red-team review.
- `commit-rules`: prepares coherent commits and commit messages.
- `research`: gathers evidence from papers, official guidance, and workflow references.

## Acceptable Overlap

Overlap is acceptable when:

- One plugin detects a need and explicitly escalates to a specialist.
- One plugin performs a lightweight check and refuses to imitate the full specialist workflow.
- The skill descriptions make the front-door versus specialist split obvious.
- Default prompts do not advertise another plugin's primary workflow.

## Routing Risks

Flag a finding when:

- Two plugins claim the same primary request.
- A plugin's trigger is broad enough to intercept another plugin's obvious request.
- A default prompt uses generic phrasing that hides the plugin's domain.
- A read-only gate promises write actions.
- A support plugin starts acting like a front-door workflow without a boundary.

## Review Method

1. Build a compact role map: plugin name, primary role, common triggers, escalation targets.
2. Compare exact skill names, skill descriptions, and UI default prompts first.
3. Compare semantic overlap next: look for shared verbs and domains.
4. Treat deterministic duplicate text as evidence, not final proof.
5. For each overlap, decide whether it is an intended boundary, a documentation gap, or a routing failure.
