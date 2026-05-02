# Skill Rules

Use this when reviewing skills, references, scripts, or `agents/openai.yaml`.

## SKILL.md

Required:
- YAML frontmatter with `name`
- YAML frontmatter with `description`
- concise trigger description
- core workflow and hard rules

Good skill descriptions:
- say when to use the skill
- include important exclusions
- avoid grabbing unrelated requests

Risky skill descriptions:
- are so broad that they overlap many plugins
- omit review-only/write-owning boundaries
- describe implementation details instead of trigger conditions
- copy another skill's trigger language without naming the boundary

## agents/openai.yaml

Recommended for each skill:
- `interface.display_name`
- `interface.short_description`
- `interface.default_prompt`

The UI metadata should match `SKILL.md`. It should not advertise actions the skill does not perform.

Default prompts should exercise the skill's own workflow. If a default prompt would be better handled by another plugin, narrow it or add an explicit escalation boundary.

## References

References are useful when:
- criteria are too detailed for `SKILL.md`
- checks differ by subdomain
- a workflow has strict calibration rules

Every referenced local markdown file should exist. Avoid deep reference chains.

## Scripts

Scripts are appropriate for deterministic checks:
- JSON parsing
- YAML parsing
- required fields
- path existence
- placeholder detection
- link consistency

Scripts should avoid rewriting repo files unless the skill explicitly owns write actions.

## Capability Consistency

Read-only skills:
- review, validate, inspect, summarize, report
- manifest can use `Read`

Write-owning skills:
- edit, create, delete, fix, stage, commit, push, publish, resolve
- manifest should include `Write`

When a plugin mixes read-only and write-owning skills, the manifest should include `Write`, and each skill should define its own phase boundaries.

## Trigger And Routing Boundaries

Check trigger text across all marketplace skills when multiple plugins are in scope:

- Exact duplicate skill names are normally a hard routing risk.
- Exact duplicate descriptions or default prompts are a role-boundary warning unless intentionally documented.
- Shared generic words such as "review", "quality", "create", "commit", or "research" are acceptable only when each description adds the qualifying domain.
- A front-door skill may detect specialist needs, but it should escalate instead of reproducing the specialist skill's full workflow.
