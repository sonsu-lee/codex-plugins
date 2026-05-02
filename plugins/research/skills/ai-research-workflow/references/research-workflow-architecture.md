# Research Workflow Architecture

Use this reference when creating, changing, or evaluating the research plugin workflow.

## Responsibility Boundaries

| Surface | Owns | Does Not Own |
| --- | --- | --- |
| `.codex-plugin/plugin.json` | install metadata, bundled component paths, starter prompts | research logic, source policy, report quality |
| `SKILL.md` | trigger scope, mode selection, stage contract, output contract | long rubrics, provider-specific docs |
| `references/` | source tiers, quality gates, report standards, provider playbooks | final reports or one-off research notes |
| `.mcp.json` / MCP config | retrieval and fetch tools | conclusion, confidence, synthesis |
| `.codex/agents/*.toml` | bounded read-only lane roles | final authority, recursive delegation by default |
| `AGENTS.md` | always-on working agreements | detailed research algorithms |
| hooks/scripts | deterministic checks and repeatable linting | judgement-heavy source evaluation |

## Canonical Workflow

1. `plan`: objective, mode, scope, exclusions, time window, success criteria.
2. `lane-select`: required evidence lanes and source preferences.
3. `retrieve`: candidate discovery from free/canonical sources first.
4. `source-fetch`: original documents, official docs, papers, repos, or API pages.
5. `claim-ground`: support labels and grounding for major claims.
6. `contradiction-check`: conflicts, caveats, later updates, benchmark limits.
7. `synthesize`: decision logic and confidence.
8. `workflow-integrate`: target surface, cost, risk, validation, rollback.
9. `report-write`: reader-facing decision memo.
10. `validate`: gates and static checks.

## Rollback Rule

Rollback to the failed stage, not to the beginning:

- missing canonical source -> `retrieve` or `source-fetch`
- unsupported factual claim -> `claim-ground`
- missing caveat or conflict -> `contradiction-check`
- source list without argument -> `synthesize`
- recommendation without validation or rollback -> `workflow-integrate`
- internal tables visible in final report -> `report-write`
- report too shallow for the mode -> `synthesize` then `report-write`

Use bounded correction passes. If the same gate fails again, state the gap and lower confidence.

## Retrieval Provider Policy

Providers are tools, not authorities.

- Use official docs, canonical scholarly indexes, and primary repos first when the target is known.
- Use Exa, Perplexity, Firecrawl, or similar tools for discovery when the target is unknown or broad.
- Final support must cite the original source, not provider snippets or generated summaries.
- Default to free-first. Stop on quota, payment, or account-backed requirements unless the user explicitly approves escalation.
- Keep provider-specific instructions in provider playbooks, not in the main skill.

## AGENTS.md vs Skill

Put short always-on norms in `AGENTS.md`: original-source preference, Korean reports by default, no paid APIs without approval, and no unsupported claims.

Put conditional research behavior in the skill: modes, evidence lanes, quality gates, subagent rules, and report artifact rules.

## Minimum Viable Validation

Before treating a workflow change as adopted:

- run at least one sample for the affected mode
- check that canonical sources appear for main claims
- check that final reports do not expose internal tables by default
- check that recommendations include target surface, cost, validation, and rollback
- keep a small regression set for `quick-fact`, `official-guidance-review`, `comparison`, `workflow-update-review`, and `deep-research`
