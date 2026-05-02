# Verification Gates

Apply these checks before making strong claims.

## Claim Decomposition

For each important claim, record:

- exact claim
- source and date
- canonical URL
- source tier
- access path: full text, abstract, metadata, official doc, code, changelog, table, figure, API response, repository, benchmark, or not checked
- evidence type
- grounding quote or exact snippet when available
- fit judgement: why this source is appropriate support for this claim
- benchmark/task/data involved
- limitation or scope boundary
- whether it changes the workflow recommendation

## Support Labels

- `supported`: primary source directly supports the claim
- `partially-supported`: source supports part of the claim or a narrower version
- `ambiguous`: evidence exists but scope, date, or methodology is unclear
- `contradicted`: credible evidence points the other way
- `unverified`: only secondary or weak evidence found
- `retracted`: initially considered but removed because no supporting source or quote was found

## Claim-Source Ledger

For `literature-scan`, `comparison`, `workflow-update-review`, and `deep-research`, keep an internal claim-source ledger for major claims. The ledger should connect:

```text
claim -> reference -> canonical URL -> access path -> grounding -> support label -> fit judgement -> limitations
```

Use `assets/claim-source-ledger-template.md` when available. Validate it with `scripts/lint_claim_source_ledger.py` when a ledger artifact is written.

Do not expose the full ledger in the reader-facing report unless the user explicitly asks for an audit appendix.

## Quote-First Grounding

For high-impact factual claims, extract a short grounding quote or exact snippet before synthesis. If no quote or source-specific support can be found, downgrade the support label or retract the claim.

Use quotes internally to anchor analysis. In final answers, keep quoted text short and prefer citation links plus paraphrase unless the user explicitly asks for exact excerpts.

## Citation And Source Verification

For scholarly, benchmark, official-guidance, legal, medical, financial, or workflow-changing claims, verify both existence and support:

- Existence: the source can be traced to a canonical URL, DOI, arXiv ID, OpenReview/proceedings page, publisher page, official API response, repository, or trusted scholarly index record.
- Metadata: title, authors, date/year, venue/version, and identifier match the claim closely enough for the use.
- Support: the source actually supports the sentence it is attached to, not only the broad topic.
- Freshness: current claims use current docs, release notes, policy pages, or recent metadata.
- Access path: record whether support came from full text, abstract, metadata, changelog, code, table, figure, or API response.

If bibliographic metadata exists but the source was not inspected, label the related claim `partially-supported` unless metadata alone is enough for the claim.

## Quality Checks

Ask:

- Is this original evidence or a summary?
- Is the source current enough for the question?
- Is the benchmark measuring the user's target behavior?
- Are there hidden constraints, cherry-picked examples, or missing baselines?
- Is the result peer-reviewed, preprint-only, vendor-produced, or community-reported?
- Is there code, data, or a harness that can be inspected?
- Are later updates, errata, or replication attempts available?
- Can each final claim be traced to a source, quote, snippet, or explicit absence of evidence?
- Could the citation be fabricated, misattributed, stale, or attached to a stronger claim than it supports?

## Contradiction Search

For deep or workflow-changing conclusions, actively search for:

- failed replications
- benchmark contamination or memorization concerns
- changed pricing, limits, or availability
- newer model/tool behavior
- known failure cases
- maintainer issues or deprecations

## Decision Threshold

Workflow changes require one of:

- one directly relevant S-tier source
- two independent A-tier sources
- one A-tier source plus successful local validation
- explicit user approval for an experimental rule

When evidence is weak, propose the change as an experiment with a rollback condition.

## Accuracy Review

Before final synthesis, run a compact accuracy pass:

- Remove claims that do not have source support.
- Separate evidence from interpretation.
- Mark uncertainty directly instead of filling gaps from general knowledge.
- Check whether the retrieval failed, the source lacks the needed fact, or the synthesis overreached.
- Check whether cited sources exist and whether their metadata matches the report.
- Move, rewrite, downgrade, or remove citations that do not support the attached sentence.
- For workflow recommendations, state the validation method that would confirm the change is useful.
