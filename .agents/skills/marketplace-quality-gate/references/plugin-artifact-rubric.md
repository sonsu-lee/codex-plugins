# Plugin Artifact Rubric

Use this for qualitative plugin and marketplace review after running the deterministic checker.

## Purpose And Scope

Pass:
- The plugin has a clear single purpose.
- It serves this personal marketplace rather than an undefined general audience.
- It does not duplicate another plugin without a clear boundary.

Conditional:
- The purpose is useful but the trigger or default prompts need tightening.
- The plugin is coherent but future write-owning workflows should be split later.

Fail:
- The plugin's purpose is too broad to predict when it should trigger.
- The plugin conflicts with an existing plugin such as `code-review` or `architecture-review`.
- The plugin claims a workflow it does not actually implement.

## Boundary With Creator Workflows

Pass:
- The plugin is already scaffolded and this review only judges readiness.
- Any creation, marketplace writing, or metadata autofill need is routed to `plugin-creator`.

Conditional:
- The plugin is mostly audit-focused but wording could imply it creates or rewrites plugin files.

Fail:
- The marketplace quality workflow tries to scaffold, generate, or rewrite plugin artifacts.
- The plugin duplicates `plugin-creator` instead of auditing output from it.

## Artifact Coherence

Pass:
- `plugin.json`, marketplace entry, skill description, UI metadata, and default prompts describe the same capability.
- Capabilities match behavior: read-only gates use `Read`; write-owning workflows use `Write`.
- Homepage/repository paths point to the actual plugin.

Conditional:
- Metadata is accurate but bland or underspecified.
- Default prompts are usable but not representative enough.

Fail:
- Manifest says one thing and skill behavior says another.
- Capability metadata understates or overstates write actions.
- Default prompts route users to workflows the plugin cannot perform.

## Progressive Disclosure

Pass:
- `SKILL.md` contains core workflow and references only what is needed.
- Detailed criteria live in `references/`.
- Scripts own deterministic checks instead of prose asking the model to reimplement them.

Conditional:
- `SKILL.md` is slightly dense but still under control.
- References exist but could be split by concern.

Fail:
- `SKILL.md` is bloated with rarely needed details.
- References are mentioned but missing or too vague to guide use.
- Deterministic validation is described but not executable.

## Marketplace Readiness

Pass:
- The plugin can be discovered through marketplace metadata.
- The install path, name, category, and policy match local conventions.
- There are no placeholders, broken paths, or invalid metadata.
- Marketplace entries do not duplicate names or source paths.

Conditional:
- Metadata polish remains but installability is not affected.

Fail:
- Marketplace path cannot resolve.
- Duplicate entries or mismatched names make plugin selection ambiguous.
- Required metadata is missing or stale.

## Role Uniqueness

Pass:
- Each plugin has one clear owner responsibility.
- Similar plugins have explicit front-door, specialist, or escalation boundaries.
- The plugin name, manifest description, skill description, and default prompts reinforce the same role.

Conditional:
- Roles overlap but the intended boundary can be inferred from surrounding docs.
- One plugin needs wording changes to avoid claiming another plugin's specialist workflow.

Fail:
- Two plugins claim the same primary user request without a boundary.
- A broad "review", "quality", "create", "commit", or "research" trigger would likely route unrelated work to the wrong plugin.
- A plugin performs a specialist workflow that should be escalated to another plugin.

## Trigger Collision

Pass:
- Skill descriptions describe concrete triggering conditions and exclusions.
- Default prompts are representative and do not advertise another plugin's workflow.
- Exact duplicate skill names, descriptions, or default prompts are absent or intentionally explained.

Conditional:
- Trigger wording is usable but could be narrower.
- Duplicate wording exists only in examples and does not affect discovery.

Fail:
- Multiple skills use the same trigger language for different workflows.
- A skill description summarizes broad process instead of when to use the skill.
- Default prompts are generic enough to pull requests away from a better plugin.

## Orchestration Readiness

Pass:
- The review can describe which plugin should own each common request.
- Specialist escalation is explicit: general code review to `code-review`, deep design red-team to `architecture-review`, creation to `plugin-creator`, commit preparation to `commit-rules`.
- A plugin does not imitate another plugin's full workflow internally.

Conditional:
- Escalation rules exist but are only implied.
- The marketplace works but would benefit from a short boundary note.

Fail:
- Common requests have no clear owner.
- A plugin both routes to and duplicates the same specialist workflow.
- The marketplace ordering or descriptions make a lower-fit plugin look like the primary entry point.
