# Workflow Integration

Use this reference when research findings may change local agent workflows.

## Integration Targets

- `AGENTS.md`: durable project rules, commands, constraints, and team conventions
- global prompt or local config: broad behavior preferences and model/runtime defaults
- skill: reusable workflow that should trigger only for relevant tasks
- plugin: bundle of related skills, assets, and optional integrations
- reference file: detailed rubric, provider playbook, source policy, or report standard loaded only when needed
- MCP config: retrieval or fetch providers, not synthesis policy
- custom agent: focused role with separate context and bounded responsibility
- hook or script: deterministic repeated checks such as report linting or regression samples
- automation: repeated checks, monitors, or scheduled follow-ups

## Placement Rules

- Put always-on repo conventions in `AGENTS.md`.
- Put conditional workflows in skills.
- Put external tool bundles or grouped capabilities in plugins.
- Put long criteria and provider details in references to preserve progressive disclosure.
- Put retrieval providers in MCP config, but keep source policy and conclusion logic in skills/references.
- Put role-specific behavior in custom agents.
- Put deterministic repeated actions in hooks or automations when available.
- Do not put long research notes into global instructions.

## Recommendation Format

For each proposed change, include:

- `change`: exact rule or workflow modification
- `where`: target file or component
- `why`: evidence-backed reason
- `trigger`: when it should activate
- `cost`: token, time, money, or complexity impact
- `risk`: how it can fail
- `validation`: how to test whether it helps
- `rollback`: when to remove or downgrade it

## Workflow Heuristics

Prefer workflows that:

- force original-source checks for high-stakes claims
- keep context small through progressive disclosure
- separate discovery, evaluation, synthesis, and implementation
- keep retrieval, verification, synthesis, reporting, and regression concerns separately testable
- require tests, lint, screenshots, or other verifiable completion criteria
- use subagents only for independent lanes with bounded outputs

Avoid workflows that:

- load long references on every task
- rely on social posts as final evidence
- turn every task into deep research
- create many agents without a coordinator and output contract
- add MCP dependencies that fail silently or require hidden credentials
