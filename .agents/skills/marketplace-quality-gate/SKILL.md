---
name: marketplace-quality-gate
description: "Use when validating personal Codex marketplace plugins for artifact correctness, role overlap, trigger boundaries, orchestration readiness, plugin.json files, SKILL.md frontmatter, references, capabilities, default prompts, or marketplace readiness."
---

# Marketplace Quality Gate

## Purpose

Validate whether plugins in this personal marketplace are installable, coherent, non-duplicative, and ready to coexist as Codex plugin workflows.

This gate is narrower than general code review and broader than format validation. It checks `plugins/*`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, skill frontmatter, `agents/openai.yaml`, references, scripts, placeholders, capability/behavior consistency, role uniqueness, trigger collision, and cross-plugin orchestration.

## Boundary With Plugin Creator

`plugin-creator` owns creation: scaffolding plugin folders, generating `.codex-plugin/plugin.json`, creating optional folders, and appending marketplace entries.

`marketplace-quality-gate` owns audit: validating already-created or changed plugin artifacts, detecting marketplace drift, checking duplicate responsibilities, and judging whether plugins route cleanly together.

Do not create, scaffold, rewrite, or auto-fill plugin files during this gate. If creation or metadata writing is needed, say that `plugin-creator` should be used before rerunning this gate.

## Hard Rules

- Read-only gate. Do not edit plugin files, stage changes, commit, publish, or rewrite metadata while evaluating.
- Run the deterministic checker before making qualitative claims whenever the repo is available.
- Treat checker findings as evidence, not as the full review. The model still owns qualitative plugin design judgment.
- Do not duplicate `code-review` for general code correctness. Focus on plugin artifact quality and marketplace readiness.
- Do not duplicate `plugin-creator` for scaffold creation or marketplace entry writing. Focus on post-creation audit and readiness.
- Do not perform specialist reviews inside this gate. Escalate general code issues to `code-review` and high-impact design issues to `architecture-review`.
- Use the user's language unless they request otherwise.

## References

- Read `references/plugin-artifact-rubric.md` for every substantial marketplace quality review.
- Read `references/marketplace-rules.md` when `.agents/plugins/marketplace.json` is in scope.
- Read `references/skill-rules.md` when reviewing `SKILL.md`, references, scripts, or `agents/openai.yaml`.
- Read `references/orchestration-rules.md` when reviewing multiple plugins, role overlap, trigger collision, or delegation boundaries.

## Deterministic Checker

Use:

```bash
python3 .agents/skills/marketplace-quality-gate/scripts/check_plugin_quality.py .
```

For machine-readable output:

```bash
python3 .agents/skills/marketplace-quality-gate/scripts/check_plugin_quality.py . --json
```

The checker covers:

- JSON parsing for plugin manifests and marketplace metadata
- required manifest and marketplace fields
- marketplace path and duplicate entry consistency
- duplicate marketplace source paths
- placeholder or TODO residue
- skills path existence
- skill frontmatter YAML parsing and required fields
- `agents/openai.yaml` parsing
- broken local reference links from `SKILL.md`
- duplicate skill names, exact skill descriptions, and exact `agents/openai.yaml` default prompts
- coarse capability consistency signals

## Workflow

1. Resolve scope.
   - If the user names a plugin, review that plugin and its marketplace entry.
   - If the user names changed files, review the affected plugin artifacts.
   - If no scope is named, review all plugins and the marketplace.
2. Run the deterministic checker.
3. Build a role map for the reviewed plugins.
   - Identify each plugin's front-door requests, specialist responsibilities, and escalation targets.
   - Mark overlaps as acceptable only when the boundary is explicit.
4. Inspect relevant plugin manifests, skills, UI metadata, references, and marketplace entries.
5. Apply the qualitative rubric and orchestration rules.
6. Emit findings first, then a gate summary.

## Finding Format

Use stable ids in discovery order: `PQ-001`, `PQ-002`, `PQ-003`.

Severity:

- `P0`: Marketplace/plugin artifact cannot be parsed, installed, or resolved.
- `P1`: Plugin can mis-trigger, misrepresent capabilities, or has broken required metadata.
- `P2`: Maintainability, progressive disclosure, UI metadata, or reference quality risk.
- `P3`: Minor polish or consistency issue.

Each finding must include:

- id
- severity
- confidence
- gate: `Artifact`, `Marketplace`, `Role Boundary`, `Trigger Collision`, `Orchestration`, `Capability Consistency`, or `Skill Quality`
- source: checker or review
- file/path evidence
- problem
- impact
- correction direction

## Gate Decision

- `Pass`: no blocking findings; deterministic checker has no findings; qualitative review has no material risks.
- `Conditional Pass`: non-blocking P2/P3 findings, bounded metadata polish, or role overlap with a clear correction direction remains.
- `Fail`: any P0/P1 finding, broken marketplace resolution, invalid JSON/YAML, missing required paths, misleading capability/trigger metadata, unbounded role duplication, or trigger collision likely to misroute common requests.

## Required Output

```markdown
## Findings

[PQ-001] [P1] Title
- Confidence:
- Gate:
- Source:
- Evidence:
- Problem:
- Impact:
- Correction direction:

## Gate Summary

- Decision:
- Checked scope:
- Deterministic checker:
- Marketplace:
- Plugin manifests:
- Skills:
- References:
- Capability consistency:
- Role map:
- Trigger collision:
- Orchestration:

## Open Questions / Assumptions

## Verdict
```

If no findings exist, say so explicitly and list the checks run.
