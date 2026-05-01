# Verification Gates

Apply these checks before making strong claims.

## Claim Decomposition

For each important claim, record:

- exact claim
- source and date
- source tier
- evidence type
- benchmark/task/data involved
- limitation or scope boundary
- whether it changes the workflow recommendation

## Support Labels

- `supported`: primary source directly supports the claim
- `partially-supported`: source supports part of the claim or a narrower version
- `ambiguous`: evidence exists but scope, date, or methodology is unclear
- `contradicted`: credible evidence points the other way
- `unverified`: only secondary or weak evidence found

## Quality Checks

Ask:

- Is this original evidence or a summary?
- Is the source current enough for the question?
- Is the benchmark measuring the user's target behavior?
- Are there hidden constraints, cherry-picked examples, or missing baselines?
- Is the result peer-reviewed, preprint-only, vendor-produced, or community-reported?
- Is there code, data, or a harness that can be inspected?
- Are later updates, errata, or replication attempts available?

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
