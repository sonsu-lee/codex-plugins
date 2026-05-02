# Quality Gates

Use these gates to decide whether the research is good enough to synthesize, whether it needs a bounded correction pass, or whether the answer must be explicitly low confidence.

The goal is not to prove the conclusion is true in an absolute sense. The goal is to verify that the conclusion is supported well enough for the requested use.

## Modes

Apply gates by mode:

- `quick-fact`: use only hard fails and the source/claim gates.
- `official-guidance-review`: source, claim, contradiction, and applicability gates.
- `literature-scan`: source, coverage, claim, contradiction, and applicability gates.
- `comparison`: source, coverage, claim, contradiction, and synthesis gates.
- `workflow-update-review`: all gates, including validation and rollback.
- `deep-research`: all gates, including substance and coverage adequacy, with one extra correction pass allowed.

## Hard Fails

Any hard fail blocks a confident conclusion regardless of numeric score:

- No canonical source for the main claim.
- A key claim is supported only by a search summary, snippet, social post, or uncited blog.
- A high-impact factual claim has no source-specific grounding quote, exact snippet, table, figure, code reference, or explicit metadata field.
- The source is stale for a time-sensitive claim and no date/version caveat is stated.
- The task asks for official guidance, but no official source was checked.
- The task asks for academic evidence, but no primary paper/preprint/proceedings page or trusted scholarly index was checked.
- A contradiction was found but not represented in the synthesis.
- The final recommendation depends on a source the workflow could not inspect.
- A broad report-producing request is answered without meeting the reader-sufficiency criteria from `report-substance-standards.md`.

Hard fail action:

1. roll back to the named stage
2. perform one bounded correction pass
3. if still failing, mark the conclusion `low confidence` and state the unresolved gap

Do not default to more search for every failure. Missing evidence rolls back to retrieval; weak argument rolls back to synthesis; missing validation or rollback rolls back to workflow integration; internal validation artifacts in the user report roll back to report writing.

## Score Scale

Score each gate from 0 to 3:

- `0`: missing or invalid
- `1`: weak; enough to discuss but not enough to conclude
- `2`: adequate; supports a cautious conclusion
- `3`: strong; supports a normal confident conclusion

Overall status:

- `pass`: no hard fails, all required gates >= 2, average >= 2.2
- `partial`: no hard fails after correction, at least one required gate = 1, average >= 1.7
- `fail`: hard fail remains or average < 1.7

Do not hide partial/fail status. A partial result can still be useful if the gaps are explicit.

## Gates

### 1. Scope Gate

Checks:

- Research question is restated.
- Mode is selected.
- Scope boundaries and excluded areas are explicit.
- Time window is stated for recent/current topics.

Rollback target: `plan`

### 2. Source Gate

Checks:

- Canonical sources were checked for main claims.
- Source tiers are assigned.
- Dates, versions, or publication status are captured where relevant.
- Exa/native search is used only as discovery unless the source itself is canonical.

Rollback target: `retrieve`

Use `source-fetch` instead when candidates exist but the original source, exact metadata, or grounding snippet has not been inspected.

### 3. Coverage Gate

Checks:

- Required evidence lanes were covered for the mode.
- The report covers the evidence lanes required by `report-substance-standards.md`, or states why a missing lane does not change confidence.
- Important missing lanes are listed as gaps.
- At least one contradiction/failure-mode search was attempted for deep or workflow-changing conclusions.
- The answer is not based on a single source unless the task is a narrow fact lookup.

Rollback target: `retrieve`

### 4. Claim Grounding Gate

Checks:

- Major claims appear in a claim ledger.
- Each major claim has a support label.
- High-impact claims have a grounding quote, exact snippet, metadata field, code reference, table, or figure.
- Unsupported or overbroad claims are retracted or downgraded.

Rollback target: `claim-ground`

### 5. Contradiction Gate

Checks:

- Conflicting evidence, newer updates, retractions, benchmark caveats, and failure cases were searched when relevant.
- Contradictions are represented in the synthesis.
- The conclusion explains why one source is preferred when sources disagree.

Rollback target: `contradiction-check`

### 6. Applicability Gate

Checks:

- Evidence scope matches the user's target workflow.
- Benchmark/task conditions are not overstated.
- Vendor claims are separated from independent or academic evidence.
- Limitations are tied to the recommendation.

Rollback target: `source-evaluate`

### 7. Synthesis Gate

Checks:

- Evidence and interpretation are separated.
- Confidence is proportional to evidence quality.
- Caveats and gaps are explicit.
- The answer avoids claiming consensus when the evidence is mixed.

Rollback target: `synthesize`

### 8. Workflow Recommendation Gate

Use only when recommending prompt, skill, plugin, agent, config, or process changes.

Checks:

- Each recommendation has evidence, cost, risk, validation, and rollback.
- Experimental recommendations are labeled as experiments.
- The recommendation target is appropriate: AGENTS.md, skill, plugin, custom agent, config, or automation.

Rollback target: `workflow-integrate`

### 9. Report Adequacy Gate

Use when writing a Markdown report.

Checks:

- The report has enough narrative analysis for the selected mode.
- The first screen contains a direct answer and major conclusions.
- The report uses sources to support analysis, not as a bare bibliography.
- The report answers the likely questions of a skeptical but fair reader.
- The report includes risks, limitations, and execution recommendations when relevant.
- The report does not expose internal validation tables by default.
- The report is not just a comparison table or source list for a broad research request.

Rollback target: `report-write`

Use `synthesize` before `report-write` when the report is well formatted but lacks decision logic, tradeoff analysis, or enough argument for the selected mode.

## Correction Pass Limits

Default limits:

- `quick-fact`: 0 correction passes unless source support is missing
- `official-guidance-review`, `comparison`, `literature-scan`, `workflow-update-review`: 1 correction pass
- `deep-research`: 2 correction passes

A correction pass must be bounded:

- name the failed gate
- name the rollback target
- retrieve or inspect only the missing evidence needed for that gate
- update the claim ledger
- rerun only the failed gate and directly dependent gates

If the same gate fails again, stop and report the gap. Do not loop indefinitely.

## Internal Gate Result Format

Use this compact format in internal notes or in an audit/debug appendix only when the user explicitly asks for it. Do not include this table in the default reader-facing report.

| Gate | Score | Status | Notes | Rollback |
| --- | ---: | --- | --- | --- |
| Source | 2 | pass | Canonical sources checked | none |
| Claim grounding | 1 | partial | Two claims lack grounding | claim-ground |

Status values: `pass`, `partial`, `fail`, `not-applicable`.

## Confidence Mapping

Use gate results to set confidence:

- `high`: status pass, no unresolved important contradictions, strong source tier coverage
- `medium`: status pass or partial, no hard fail, limitations do not invalidate the conclusion
- `low`: status partial/fail, unresolved hard gap, weak source coverage, or important contradiction remains

Confidence is about support quality, not how plausible the conclusion feels.
