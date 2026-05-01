---
name: ai-research-workflow
description: Use for AI/ML research tasks that require recent papers, official model or coding-agent guidance, benchmark interpretation, source quality checks, or translating evidence into local workflow/plugin/agent recommendations. Especially relevant for Exa-backed literature scans, OpenAI/Anthropic guidance reviews, and evidence-backed workflow updates.
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

Escalate modes only when the user asks for depth or when the question cannot be answered safely from a narrow source set.

## Source Plan

Select the smallest useful source mix:

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
Read `references/exa-playbook.md` when Exa is available or the task involves literature discovery.
Read `references/ai-research-domains.md` for useful AI research source domains.
Read `references/verification-gates.md` for claim checks, support labels, and contradiction handling.
Read `references/quality-gates.md` before final synthesis for moderate, deep, comparison, literature-scan, official-guidance-review, or workflow-update-review tasks.
Read `references/agent-orchestration.md` when the user asks for deep, parallel, multi-agent, squad, or delegated research.
Read `references/prompt-accuracy-playbook.md` when designing research prompts, evaluating answer accuracy, adding examples, handling long documents, or recommending workflow/prompt changes.
Read `references/workflow-integration.md` before recommending changes to local workflows.

## Default Procedure

1. Restate the research objective and classify the mode.
2. Define 2 to 5 search lanes, each with source preferences.
3. Retrieve candidates from official free sources, Exa free-tier discovery, GitHub, and web search as appropriate.
4. Fetch original sources for all important claims.
5. Build a claim ledger: each major claim needs source, support label, limitation, and applicability.
6. Extract short grounding quotes or exact snippets for high-impact claims before synthesis; do not output long quoted passages.
7. Search for contradiction, failed replication, benchmark caveats, or later updates.
8. If subagents were used, merge lane outputs and resolve conflicts before quality gates.
9. Run the quality gates. If a hard fail or gate failure occurs, roll back to the named stage and make one bounded correction pass before synthesis.
10. Produce a concise synthesis with explicit confidence and gaps.
11. If workflow changes are requested, propose concrete edits and the evidence supporting each edit.
12. Write a Markdown research report unless the user explicitly asks for chat-only output.

For deep work, keep an evidence matrix. Use `assets/evidence-matrix-template.md` as the output shape if the user asks for an artifact.

## Report Artifact

At the end of a research task, create a Markdown report file.

- If the user gives an output path, use it.
- Otherwise write to `research/reports/YYYY-MM-DD-<topic-slug>.md` in the current workspace.
- Use `assets/research-report-template.md` as the report shape.
- Keep the chat response short and link to the report path.
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

## Output Contract

Default answer shape:

1. working conclusion
2. evidence by source tier
3. practical workflow implication
4. caveats and missing evidence
5. quality gate status
6. report path when a Markdown report was written
7. recommended next action

For workflow-update reviews, include:

- `change`: the proposed rule or workflow change
- `where`: plugin, skill, AGENTS.md, config, or agent prompt
- `evidence`: sources and support level
- `risk`: cost, complexity, brittleness, or false-positive risk
- `rollback`: how to revert if it performs poorly

Be concise. Prefer a small number of strong sources over a long list of weak ones.
