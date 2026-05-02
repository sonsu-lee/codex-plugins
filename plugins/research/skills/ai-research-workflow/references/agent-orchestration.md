# Agent Orchestration

Use these project-scoped custom agents for deep or parallel research workflows. The agent definitions live in `.codex/agents/`.

Codex only spawns subagents when explicitly asked. Do not use these agents for routine narrow questions.

## Agents

| Agent | Use For | Avoid When |
| --- | --- | --- |
| `research_head` | Coordinating a deep research plan, evidence lanes, gate status, and report outline | The main thread can coordinate a small task directly |
| `paper_scout` | Papers, preprints, benchmark papers, scholarly metadata, canonical IDs | Official product behavior is the only source needed |
| `official_guidance_scout` | OpenAI, Anthropic, model-lab, vendor, or tool guidance | The request is academic-only |
| `source_evaluator` | Adversarial quality gate pass, source tier review, unsupported claim detection | Evidence has not been gathered yet |
| `workflow_translator` | Converting verified findings into skill/plugin/agent/config/process recommendations | Evidence is weak or still disputed |

## Model And Effort Policy

Default project agents should usually pin `model_reasoning_effort` by role and leave `model` unset.

Rationale:

- Codex custom agent files may include `model` and `model_reasoning_effort`, and omitted optional fields inherit from the parent session.
- OpenAI model recommendations and aliases change over time. Marketplace research workflows should inherit the user's current best/default model unless an eval-proven lane needs a specific model.
- Reasoning effort is part of the role contract and changes less often than model IDs. It is reasonable to fix effort for repeatability.

Recommended defaults:

| Agent | Model | Effort | Reason |
| --- | --- | --- | --- |
| `research_head` | inherit | `high` | coordination, claim ledger, quality gate, and report-outline decisions need deeper reasoning |
| `paper_scout` | inherit | `medium` | bounded scholarly retrieval lanes need accuracy but should stay cost-aware |
| `official_guidance_scout` | inherit | `medium` | official-doc checks are source-bound and usually narrower |
| `source_evaluator` | inherit | `high` | adversarial support checks and contradiction review need deeper reasoning |
| `workflow_translator` | inherit | `high` | maps evidence into reversible workflow changes with cost, risk, validation, and rollback |

Do not set `xhigh` as a default unless the parent workflow explicitly prioritizes maximum quality over cost and the active model is known to support it. Prefer raising the parent session effort for one hard run over baking `xhigh` into marketplace agent files.

Pin a concrete `model` only when all are true:

- a regression or eval shows a specific model materially improves the lane
- the expected users accept the cost and availability constraints
- the agent file or release notes state why the model is pinned
- there is a rollback condition for stale model behavior, pricing, or availability

## Activation Rule

Use agent orchestration only when the work is broad enough to need it:

- the selected mode is `deep-research`, `workflow-update-review`, `literature-scan`, or a broad `comparison`
- at least two independent evidence lanes are needed
- the user explicitly asks for deep, parallel, delegated, or agent-group work, or the active runtime instructions allow delegation

Do not use agents for narrow official-doc checks or quick facts.

## Default Topology

For `deep-research`:

1. Main thread or `research_head` defines scope, lanes, and output contract.
2. `paper_scout` handles the academic/benchmark lane when papers matter.
3. `official_guidance_scout` handles vendor/documentation guidance.
4. Optional implementation lane stays in the main thread unless the user explicitly asks for another worker.
5. `source_evaluator` reviews evidence and quality gates.
6. `workflow_translator` maps supported findings to workflow changes.
7. Main thread writes the Markdown report.

Deep reports should cover the evidence lanes naturally required by the question and meet `report-substance-standards.md`. Do not use agents to create a bundle of summaries; use them to broaden coverage and stress-test the synthesis.

For `workflow-update-review`:

1. Use `official_guidance_scout` for official guidance.
2. Use `paper_scout` only if academic or benchmark evidence materially affects the workflow.
3. Use `source_evaluator` before accepting the recommendation.
4. Use `workflow_translator` to produce reversible changes.

For `comparison`:

1. Split independent evidence lanes by source type, not by conclusion.
2. Use `source_evaluator` after the lane outputs are available.
3. Keep final synthesis in the main thread.

## Delegation Rules

- Give every subagent a bounded lane, source preferences, and output contract.
- Tell each subagent not to edit files.
- Tell each subagent to keep Exa as free-tier discovery only.
- Require canonical sources for final evidence.
- Require each lane to return gaps and contradictions, not just positive evidence.
- Require each lane to explain how its evidence changes the final decision or why it should not affect the decision.
- Require each lane to return decision impact, not a standalone report.
- Do not let subagents recursively spawn more agents unless the user explicitly asks for recursive delegation.

## Lane Prompt Template

```xml
<research_lane>
  <objective>...</objective>
  <mode>...</mode>
  <source_preferences>official | academic | implementation | evaluation</source_preferences>
  <budget_policy>free-first; no paid API; Exa discovery only</budget_policy>
  <required_output>
    checked sources;
    evidence rows;
    grounding snippets;
    caveats;
    unresolved gaps
  </required_output>
</research_lane>
```

## Aggregation Rules

The main thread owns:

- conflict resolution
- quality gate scoring
- confidence mapping
- final recommendation
- report file creation

Subagent outputs are evidence inputs, not final conclusions.

If subagent outputs conflict, prefer the source with the higher tier, newer applicable date, narrower product scope, and clearer methodology. If the conflict still matters, represent it in the synthesis and lower confidence.
