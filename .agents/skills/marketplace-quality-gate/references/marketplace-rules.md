# Marketplace Rules

Use this when `.agents/plugins/marketplace.json` is in scope.

## Required Shape

The marketplace root should include:
- `name`
- `interface.displayName`
- `plugins`

Each plugin entry should include:
- `name`
- `source.source`
- `source.path`
- `policy.installation`
- `policy.authentication`
- `category`

## Local Path Rules

For this repository:
- `source.source` should be `local`.
- `source.path` should be `./plugins/<plugin-name>`.
- The path should contain `.codex-plugin/plugin.json`.
- The manifest `name` should match the marketplace entry `name`.

## Policy Rules

Default personal marketplace policy:
- `policy.installation`: `AVAILABLE`
- `policy.authentication`: `ON_INSTALL`

Use other values only when a plugin has a specific product or authentication reason.

## Ordering

Append new plugins unless the user explicitly asks to reorder.

Ordering should remain stable because it affects UI presentation and review diffs.

Ordering is not a substitute for clear skill boundaries. If two plugins can handle the same natural-language request, fix descriptions, default prompts, or escalation notes instead of relying on list order.

## Marketplace Orchestration

For this personal marketplace, each plugin should have a clear role:

- `research`: AI research, papers, official guidance, and workflow evidence.
- `commit-rules`: commit preparation, commit messages, and coherent staging policy.
- `architecture-review`: specialist architecture red-team and high-impact design review.
- `code-review`: personal code change acceptance gate.
- `marketplace-quality-gate`: internal skill for plugin artifact, marketplace, role-boundary, and orchestration checks.

Accept controlled overlap only when the workflow boundary is explicit. For example, `code-review` may detect high architecture impact, but should escalate full design review to `architecture-review`; `marketplace-quality-gate` may detect missing scaffold artifacts, but should route creation to `plugin-creator`.

## Failure Conditions

Fail the gate when:
- marketplace JSON cannot parse
- duplicate plugin names exist
- duplicate source paths exist
- entry path does not exist
- entry path points to a manifest with a different name
- required policy fields are missing
- local source path is not repo-relative
- two marketplace plugins claim the same primary role without an explicit boundary
