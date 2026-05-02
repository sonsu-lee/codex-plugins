---
name: commit-rules
description: Use when creating, preparing, reviewing, splitting, staging, or rewriting Git commits; when writing commit messages; or when another workflow is about to run `git commit`. Enforces one coherent change per commit, Conventional Commit messages, and relevant pre-commit verification. Does not own push, PR creation, branch cleanup, release workflow, or CI debugging.
---

# Commit Rules

## Scope

This skill constrains commit creation only.

It governs:
- commit scope
- staging decisions
- commit message format
- verification required before `git commit`

It does not govern:
- pushing branches
- opening pull requests
- branch cleanup
- release workflow
- CI debugging

When another workflow creates a commit, apply this skill only to that workflow's commit scope, message, staging, and pre-commit verification steps.

## Rules

1. One commit must represent one coherent change that can be described in one sentence.
2. Every commit message must follow Conventional Commits.
3. Every commit must leave the repository in a working state.

## Workflow

Before committing:

1. Inspect `git status --short` and the relevant diff.
2. Identify unrelated or separable changes.
3. If changes are mixed, stage only one coherent unit at a time.
4. Choose the smallest relevant verification set for the staged unit.
5. Run the verification commands before committing.
6. Commit only if verification passes or the user explicitly accepts a documented blocker.
7. Report exactly what was committed and which checks ran.

## Commit Scope

A commit is coherent when a one-sentence summary can explain all staged changes without using "and" to join unrelated work.

Good commit units:
- one feature slice with its tests
- one bug fix with its regression test
- one refactor that preserves behavior
- one docs update about one topic
- one config or dependency change needed for one purpose

Split the commit when staged changes include unrelated behavior, formatting churn, generated output, multiple features, or a fix plus an unrelated cleanup.

Do not silently stage unrelated user changes. If the working tree is mixed and the intended scope is unclear, ask which files belong in the commit.

## Message Format

Use:

```text
<type>[optional scope]: <description>
```

Allowed common types:
- `feat`: user-facing feature
- `fix`: bug fix
- `docs`: documentation only
- `style`: formatting only
- `refactor`: behavior-preserving code change
- `perf`: performance improvement
- `test`: tests only
- `build`: build system or dependency change
- `ci`: CI configuration
- `chore`: maintenance that does not fit another type
- `revert`: revert a previous commit

Message rules:
- Use lowercase type.
- Keep the subject one line and concise.
- Use imperative mood when natural.
- Do not end the subject with a period.
- Use a scope only when it improves clarity.
- Use `!` or a `BREAKING CHANGE:` footer only for an intentional breaking change.

Examples:

```text
feat(commit-rules): add personal commit policy
fix(parser): preserve escaped quotes
docs(research): clarify source verification flow
chore: update local plugin marketplace
```

## Verification

Choose checks from the repository's own scripts, docs, or package metadata. Prefer the narrowest complete set that proves the staged unit works.

Typical checks:
- formatter or lint command for touched files
- relevant unit or integration tests
- type checker when typed code changed
- build command when runtime, bundling, config, or public API changed
- docs or schema validation when documentation, plugin, or config files changed

If no automated check exists, inspect the diff and state that no project verification command is available.

If a check cannot run because dependencies, credentials, services, or tools are missing, do not claim the commit is verified. Explain the blocker and ask whether to commit anyway.

## Conflict Handling

If this skill conflicts with a repository's explicit commit policy, follow the repository policy first.

If another active workflow uses non-Conventional commit messages, this skill takes precedence for the commit message unless the user explicitly asks to use that workflow's format.
