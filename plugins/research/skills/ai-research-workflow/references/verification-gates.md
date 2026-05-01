# Verification Gates

Apply these checks before making strong claims.

## Claim Decomposition

For each important claim, record:

- exact claim
- source and date
- source tier
- evidence type
- grounding quote or exact snippet when available
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

## Quote-First Grounding

For high-impact factual claims, extract a short grounding quote or exact snippet before synthesis. If no quote or source-specific support can be found, downgrade the support label or retract the claim.

Use quotes internally to anchor analysis. In final answers, keep quoted text short and prefer citation links plus paraphrase unless the user explicitly asks for exact excerpts.

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
- For workflow recommendations, state the validation method that would confirm the change is useful.
