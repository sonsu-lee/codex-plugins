# Report Substance Standards

Use this reference before planning or writing any report-producing research mode.

## Core Rule

The report must do the job a research report is supposed to do: help an informed reader understand the issue, trust the evidence trail, see the tradeoffs, and decide what to do next.

Do not judge adequacy by line count, word count, or a fixed number of citations. Those are weak proxies. A report is adequate when its claims, evidence, reasoning, caveats, and recommendations are complete enough for the selected mode and the user's decision.

## Reader Sufficiency Test

Before finalizing, ask whether a skeptical but fair reader could answer these questions from the report:

- What is the direct answer?
- What are the main conclusions and why do they follow?
- Which evidence is canonical, current, and directly relevant?
- Which assumptions, caveats, or disagreements could weaken the conclusion?
- How do the compared options differ in practice?
- What should the user do, how should they validate it, and when should they roll it back?
- What important lane was not checked, and does that limitation change confidence?

If the answer to any relevant question is missing, the report is not ready.

## Mode Adequacy

### `quick-fact`

Adequate when the answer is narrow, directly sourced, and does not require a saved report.

### `official-guidance-review`

Adequate when the report distinguishes product surfaces, dates or versions, official scope, and concrete implications. It should not generalize from one official page if adjacent official pages are necessary to interpret the behavior.

### `literature-scan`

Adequate when the report identifies the main research themes, methodology limits, benchmark scope, disagreement or missing evidence, and what remains unproven. It should use primary scholarly or benchmark sources enough to explain the shape of the field, not just cite one convenient paper.

### `comparison`

Adequate when each meaningful option is represented fairly, the comparison criteria are explicit, and the report explains adoption conditions rather than only ranking options. A table is useful only after the narrative has explained the tradeoffs.

### `workflow-update-review`

Adequate when the report connects evidence to concrete workflow changes and explains target surface, cost, risk, validation signal, and rollback condition. It must show why the change belongs in a skill, plugin, agent, AGENTS.md, MCP config, hook, automation, or nowhere.

### `deep-research`

Adequate when the report covers all evidence lanes naturally required by the question, resolves or states contradictions, explains the decision logic, and gives actionable recommendations. It should feel like a decision memo, not a source digest.

### Workflow Architecture Reports

Adequate when the report distinguishes these surfaces and does not collapse them into one prompt:

- plugin manifest and install metadata
- skill trigger and workflow contract
- references and progressive disclosure
- MCP or retrieval provider configuration
- custom agents and orchestration rules
- AGENTS.md or global instructions
- hooks, scripts, or evals for deterministic validation

The report must explain which surface should change, why that surface is appropriate, how to validate the change, and when to roll it back.

## Evidence Lane Expectations

Pick lanes based on the question. Do not create irrelevant lanes to look comprehensive.

- Official guidance: product docs, help articles, release notes, model/system cards, vendor engineering posts.
- Academic or benchmark: papers, preprints, proceedings, benchmark definitions, leaderboards, author repos.
- Implementation reality: source repos, issues, changelogs, examples, SDK docs.
- Protocol or specification: standards, schemas, API references, security considerations.
- Community signal: X/HN/Reddit/blogs only as discovery or weak context, never final support.
- Workflow translation: how the evidence changes a skill, plugin, agent, AGENTS.md, config, or operating process.

An evidence lane is required when omitting it would make a reasonable reader question the conclusion.

## Report Content Requirements

For non-quick reports, include:

- a direct answer in the first screen
- major conclusions that are argued, not merely asserted
- analysis that explains causal or operational logic
- a comparison, prioritization, or decision frame when choices exist
- risks and limitations tied to the recommendation
- concrete execution recommendations
- canonical source links sufficient to verify key claims

For workflow-changing reports, each recommendation must state:

- target surface: skill, plugin, agent, AGENTS.md, MCP config, hook, automation, or no change
- reason and evidence
- cost or operational burden
- validation signal
- rollback or stop condition

For research plugin changes, also state whether the change affects retrieval, verification, synthesis, reporting, orchestration, or regression checks.

## Anti-Shallow Checks

Before finalizing a report-producing mode, reject the draft if any condition is true:

- It mostly summarizes sources instead of answering the question.
- It has citations but the conclusions do not logically follow from them.
- It misses an evidence lane a reasonable reader would expect.
- It lacks caveats, counterarguments, or failure modes.
- It gives workflow recommendations without validation or rollback conditions.
- It answers a broad architecture question with only a table.
- It exposes internal quality gates instead of writing reader-facing analysis.

## When To Keep It Short

Keep output short only when:

- the mode is `quick-fact`
- the user explicitly says chat-only or concise
- the answer is a narrow official guidance check with one authoritative source
- writing a file would add no value

Even then, preserve citation quality and uncertainty.
