---
name: ai-research-workflow
description: Use for AI/ML research tasks that require recent papers, official model or coding-agent guidance, benchmark interpretation, source quality checks, or translating evidence into local workflow/plugin/agent recommendations. Especially relevant for free-first literature scans, OpenAI/Anthropic guidance reviews, and evidence-backed workflow updates.
---

# AI Research Workflow

Use this skill to turn AI research questions into source-backed, workflow-relevant conclusions.

Primary scope:

- AI/ML papers, preprints, benchmarks, evals, and implementation repos
- official guidance from model labs and tooling vendors
- agentic coding, research-agent, planning, review, and subagent workflows
- evidence-backed updates to local prompts, skills, plugins, AGENTS.md, or agent roles

Do not use this skill for narrow library API questions when a documentation-specific skill or MCP source can answer directly.

## Operating Contract

The workflow owns four things:

1. find relevant sources
2. verify important claims against original material
3. separate strong evidence from weak signals
4. translate findings into practical workflow recommendations

This skill is the reasoning, verification, and report layer. MCP servers and search providers are retrieval layers only. Do not let a search provider summary, ranking, or generated answer define the conclusion.

Never treat a search result summary, social post, or blog paraphrase as final evidence. Fetch or inspect the original source for any claim that affects the conclusion.

For complex research tasks, structure working prompts and notes with XML-style tags so instructions, context, documents, claims, evidence, and output requirements are not confused with each other. The final answer should follow the output contract below unless the user asks for XML.

## Research Modes

Classify the request first:

- `quick-fact`: one or two direct facts with original-source confirmation
- `official-guidance-review`: vendor docs, model cards, release notes, or best-practice posts
- `literature-scan`: papers/preprints around a concept, method, or benchmark
- `comparison`: compare methods, models, tools, or workflow patterns
- `workflow-update-review`: decide whether evidence should change a prompt, skill, plugin, or agent workflow
- `deep-research`: broad synthesis with contradiction checks and evidence matrix

Escalate to `deep-research` when the user asks to research, investigate broadly, compare workflow architecture, design a plugin/agent/process, or produce a report. Do not collapse broad workflow questions into a short comparison brief.

## Source Plan

Select the source mix needed to answer a skeptical reader's likely questions. Do not optimize for source count; optimize for whether the evidence is sufficient for the conclusion.

- For OpenAI product behavior or Codex guidance, prefer official OpenAI documentation and help articles first.
- For Anthropic/Claude Code workflow design, prefer official Claude Code docs and Anthropic engineering posts first.
- For current libraries, APIs, and SDK behavior, use Context7 or official documentation before broad web search.
- For papers and recent AI research, use free official indexes and canonical sources first when the target is clear: arXiv, OpenReview, Crossref, OpenAlex, Semantic Scholar, PubMed, Europe PMC, Unpaywall, publisher pages, or GitHub.
- Use Exa as a free-tier discovery layer when the target source is unclear, when broad web discovery is needed, or when you need to find official pages, benchmark repos, implementation repos, and recent discussions quickly.
- For implementation reality, inspect GitHub repos, issues, release notes, and benchmark harnesses.
- For community signals, use X/HN/Reddit/blogs only as discovery leads, not as final evidence.

## Budget Policy

Default to free-first research:

- Do not use paid search, paid API keys, deep research, advanced search, scraping at scale, or bulk content extraction unless the user explicitly asks for it.
- The bundled Exa MCP should be treated as free-tier discovery only. Keep result counts small and fetch only sources likely to affect the conclusion.
- If a free quota or rate limit is hit, stop using that source and fall back to official free APIs, native web search, or ask before switching to a paid/account-backed path.
- Final evidence must come from canonical source pages, official APIs, or original documents, not from Exa summaries.

Read `references/source-tiers.md` when the answer depends on source quality.
Read `references/research-workflow-architecture.md` when designing, changing, or evaluating the research plugin workflow itself.
Read `references/exa-playbook.md` when Exa is available or the task involves literature discovery.
Read `references/ai-research-domains.md` for useful AI research source domains.
Read `references/verification-gates.md` for claim checks, support labels, and contradiction handling.
Read `references/quality-gates.md` before final synthesis for moderate, deep, comparison, literature-scan, official-guidance-review, or workflow-update-review tasks.
Read `references/report-substance-standards.md` before planning, researching, or writing `comparison`, `workflow-update-review`, `literature-scan`, or `deep-research` reports.
Read `references/report-writing-style.md` before writing any Markdown report artifact.
Read `references/agent-orchestration.md` when the user asks for deep, parallel, multi-agent, squad, or delegated research.
Read `references/prompt-accuracy-playbook.md` when designing research prompts, evaluating answer accuracy, adding examples, handling long documents, or recommending workflow/prompt changes.
Read `references/workflow-integration.md` before recommending changes to local workflows.

## Default Procedure

Use explicit stages so failures can roll back to the right place:

1. `plan`: restate the objective, classify the mode, set scope, exclusions, time window, and success criteria.
2. `lane-select`: define the evidence lanes needed by the question, each with source preferences and reader-sufficiency targets from `references/report-substance-standards.md`.
3. `retrieve`: retrieve candidates from official free sources, Exa free-tier discovery, GitHub, scholarly indexes, and web search as appropriate.
4. `source-fetch`: fetch or inspect original sources for all claims that affect the conclusion.
5. `claim-ground`: build a compact claim ledger; each major claim needs source, support label, grounding, limitation, and applicability.
6. `contradiction-check`: search for contradictions, failed replication, benchmark caveats, later updates, or scope conflicts.
7. `synthesize`: combine evidence into conclusions, not source-by-source summaries.
8. `workflow-integrate`: if workflow changes are requested, map findings to skill, plugin, MCP, AGENTS.md, custom agent, hook, automation, config, or no change.
9. `report-write`: write the reader-facing Markdown report unless the user explicitly asks for chat-only output.
10. `validate`: run quality gates and static report checks. If a hard fail occurs, roll back only to the named failed stage and make a bounded correction pass.

Do not route every failure back to `retrieve`. A weak conclusion usually needs `synthesize`; missing rollback/validation details need `workflow-integrate`; internal tables in the report need `report-write`.

For deep work, keep an evidence matrix internally. Use `assets/evidence-matrix-template.md` only if the user explicitly asks for an evidence artifact or audit appendix.

## Report Artifact

At the end of a research task, create a Markdown report file.

- If the user gives an output path, use it.
- Otherwise write to `research/reports/YYYY-MM-DD-<topic-slug>.md` in the current workspace.
- Use `assets/research-report-template.md` as the reader-facing report shape.
- Default report prose to Korean unless the user asks for another language.
- Start the report with the direct answer and major conclusions, then analysis, risks/limits, execution recommendations, and sources.
- For `comparison`, `workflow-update-review`, `literature-scan`, and `deep-research`, meet the relevant substance standard in `references/report-substance-standards.md`. An under-argued report is a failed report even if it has citations.
- Keep internal validation material out of the final report. `Claim ledger`, `Evidence Matrix`, `Quality Gate Results`, `Workflow Implications`, and rollback tables are working artifacts, not default report sections.
- Keep the chat response short: core conclusion, confidence, report path, and one recommended next action.
- Do not write a report for tiny `quick-fact` answers unless the user asked for a saved artifact.
- If no workspace write access is available, return the report in chat and state that the file could not be written.

## Subagents

Use subagents only when the user explicitly asks for deep/parallel agent work or when the surrounding instructions allow delegation. Good independent lanes:

- official vendor guidance
- academic papers and benchmarks
- implementation repos and issues
- community signals and operational reports
- source-quality/adversarial review

Project-scoped custom agents are available for research workflows:

- `research_head`
- `paper_scout`
- `official_guidance_scout`
- `source_evaluator`
- `workflow_translator`

The coordinating agent keeps the research question, source-tier rules, conflict resolution, and final synthesis.

For report-producing research, the main thread or `research_head` owns final synthesis and report creation. Subagents return evidence inputs, gaps, and decision impact; they do not write the final report or decide confidence by themselves.

## Output Contract

Default answer shape:

1. direct conclusion
2. confidence level
3. report path when a Markdown report was written
4. one practical next action

The chat answer should be short. Put the full synthesis in the Markdown report when a report is written.

Do not confuse a short chat answer with a short report. The chat response should be brief; the saved report should be deep enough for the selected mode.

For workflow-update reviews, include:

- proposed rules or workflow changes as reader-facing recommendations
- target surface: plugin, skill, AGENTS.md, config, or agent prompt
- evidence summary and confidence
- cost, risk, validation, and rollback conditions

Do not present the internal quality gate table or full evidence matrix in the final report unless explicitly requested.

Keep the chat response concise. In the saved report, use the canonical sources needed to support the argument; avoid both source padding and thin sourcing.
