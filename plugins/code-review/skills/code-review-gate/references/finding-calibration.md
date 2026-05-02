# Finding Calibration

Use this reference before assigning severity, confidence, score, or final gate decision.

## Finding Bar

Report a finding only when all are true:
- There is concrete evidence in code, diff, tests, config, or a clearly labeled inference.
- The issue affects scope, correctness, regression confidence, architecture impact, maintainability, or convention fit.
- The impact is explainable as a realistic failure, review blocker, or future maintenance cost.
- The correction direction is actionable.

Do not report:
- Pure taste, naming preference, or style without local convention support.
- Pre-existing issues not made worse or newly relevant by the change.
- Broad architecture concerns better handled by the dedicated architecture-review workflow, unless they block this gate as an escalation.
- Speculation without a concrete path to impact.

## Severity

`P0`:
- Data loss, security breach, tenant isolation failure, unrecoverable outage, impossible rollback, or catastrophic production failure.
- Requires immediate block.

`P1`:
- Plausible broken behavior on a normal path.
- Major regression or API contract break.
- Missing required scope.
- Meaningful auth, validation, persistence, migration, or compatibility flaw.
- Regression gate failure for behavior with material blast radius.
- High architecture impact without dedicated architecture review.

`P2`:
- Non-blocking but meaningful maintainability, test-confidence, compatibility, or structural risk.
- Edge case risk with bounded impact.
- Convention drift that may create competing patterns.
- Medium architecture impact with incomplete but recoverable reasoning.

`P3`:
- Minor cleanup opportunity.
- Low-risk clarity improvement.
- Small test or convention improvement that should not block acceptance.

## Confidence

Use `0.90-1.00` when:
- The issue is directly visible in code or tests.
- A concrete failure scenario follows without extra assumptions.
- File and line evidence is tight.

Use `0.70-0.89` when:
- Evidence is strong but depends on one reasonable assumption.
- Runtime behavior is likely but not executed.
- Caller or config context supports the claim.

Use `0.50-0.69` when:
- The issue is plausible but needs confirmation.
- Requirements are inferred.
- The finding should be framed as a risk or open question unless impact is high.

Do not emit findings below `0.50`; place them in open questions or assumptions.

## Hard Gates

The final decision cannot be `Pass` when any of these exist:
- Any `P0` or `P1` finding.
- Scope Fit fails.
- Regression Gate fails for behavior-changing work.
- High Architecture Impact requires dedicated architecture-review.
- Review target or requirements are too ambiguous to judge acceptance.
- Verification evidence is contradicted by code, tests, or diff.

## Score

Score is advisory. Hard gates override score.

Suggested bands:
- `95-100`: No findings; verification and scope are strong.
- `85-94`: Minor P3 issues only; no material risk.
- `70-84`: P2 issues or bounded verification gaps; likely `Conditional Pass`.
- `50-69`: P1 issue, failed regression gate, or material scope uncertainty; `Fail` or strong `Conditional Pass`.
- `<50`: P0, multiple P1s, incoherent scope, or unsafe architecture impact; `Fail`.

Score adjustments:
- Start from 100.
- Subtract 35-60 for P0 depending on containment.
- Subtract 20-35 for each P1.
- Subtract 8-18 for each P2.
- Subtract 1-5 for each P3.
- Cap at 69 when a hard gate fails.
- Cap at 84 when any unresolved P2 affects correctness, regression confidence, or architecture impact.

## Decision

`Pass`:
- No blocking findings.
- Regression Gate passes.
- Architecture escalation is not required.
- Open questions do not affect acceptance.

`Conditional Pass`:
- Only bounded P2/P3 issues remain.
- Verification or architecture follow-up is required but acceptance can proceed after named conditions.

`Fail`:
- Any hard gate fails.
- The change cannot be accepted as-is.
- The reviewer cannot establish task scope well enough to judge the diff.

## Correction Direction

A correction direction should say what must change, not how to implement every step.

Good:
- "Add regression coverage for empty input and make the parser reject malformed values instead of silently returning an empty result."

Too broad:
- "Improve validation."

Too much for v1:
- "Modify files A and B, create helper C, assign worker 1 to tests."
