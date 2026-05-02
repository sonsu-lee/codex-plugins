# Research Concepts For Plugin Design

Use this reference when translating academic or official research-agent ideas into the research plugin.

## Core Thesis

The research plugin should not be a long prompt for searching. It should be a staged workflow that separates retrieval, source fetching, claim grounding, contradiction checks, synthesis, reporting, and validation.

Official Codex concepts map cleanly to this split:

- plugin: installable bundle of skills, MCP servers, app integrations, assets, and metadata
- skill: reusable workflow contract and trigger surface
- references: long policies, quality rubrics, source tiers, and provider playbooks loaded only when needed
- MCP/search tools: retrieval and fetch surfaces, not authorities
- subagents: optional independent evidence lanes, not final decision makers
- scripts/hooks/evals: deterministic checks such as URL, DOI, report-shape, and regression validations

## Academic Patterns To Preserve

| Pattern | Practical lesson for this plugin |
| --- | --- |
| RAG | Use external sources for knowledge-intensive claims; do not rely on model memory for current or scholarly facts. |
| ReAct | Interleave search, inspection, query revision, and synthesis rather than doing one retrieval pass. |
| WebGPT | Keep a traceable source trail so factual accuracy can be reviewed from original references. |
| Self-RAG | Decide whether retrieval is needed, whether retrieved passages are relevant, and whether the answer is supported. |
| Chain-of-Verification | Draft conclusions, derive verification questions, answer them independently from sources, then revise. |
| ALCE | Citation quality is a separate evaluation target from fluency and answer correctness. |
| RAGChecker | Diagnose retrieval and generation failures separately; a good answer can fail because retrieval missed sources or because synthesis overreached. |
| STORM | For broad reports, discover perspectives and build an outline before writing. |

## Design Rules

1. Retrieval is evidence discovery, not evidence validation.
2. A source is not final support until its original page, paper, repository, API response, or metadata has been fetched or inspected.
3. Citations must support the attached claim, not merely the surrounding topic.
4. For scholarly work, verify bibliographic existence when the citation affects a conclusion: DOI, title, venue, authors, year, or canonical index page.
5. Prefer source-specific grounding snippets or metadata fields for high-impact claims.
6. Use contradiction searches for broad, current, benchmark, or workflow-changing conclusions.
7. Keep source-quality judgment in skills/references; keep provider setup in MCP config.
8. Use subagents only for independent lanes with bounded outputs: sources, gaps, and decision impact.

## When To Escalate Verification

Escalate from ordinary source checks to citation/source verification when:

- the output is a literature scan, scholarly report, benchmark report, or official-guidance review
- a recommendation depends on a paper, benchmark, product policy, or API limit
- the model generated or reformatted bibliographic details
- the source is niche, recent, low-visibility, or likely to be confused with similar work
- the claim cites a DOI, arXiv ID, conference acceptance, version, release date, pricing, or policy
- a source is only available through a summary, search snippet, or secondary blog

## Workflow Implications

- `source-fetch` should fetch original documents, not just result snippets.
- `claim-ground` should decompose major conclusions into checkable claims.
- `contradiction-check` should look for newer versions, retractions, failed replications, benchmark caveats, and domain-specific limitations.
- `validate` should include static report checks and, when available, deterministic citation/source checks.
- `workflow-integrate` should state target surface, cost, validation signal, and rollback condition for any plugin or skill change.

## Anti-Patterns

- Treating an LLM-generated bibliography as evidence.
- Treating search-provider summaries as final sources.
- Adding many retrieval MCPs before defining source quality rules.
- Spawning multiple agents without a coordinator-owned synthesis.
- Answering broad architecture questions with a source list or table only.
- Making every request deep research when a quick-fact or official guidance check is enough.
