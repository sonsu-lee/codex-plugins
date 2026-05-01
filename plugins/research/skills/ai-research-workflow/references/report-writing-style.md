# Report Writing Style

Use this reference when writing the final Markdown report for a research task.

## Core Principle

The final report is for decision-making, not for exposing the research workbench.

Keep claim ledgers, evidence matrices, quality gates, and rollback notes as internal working artifacts. Include them in the final report only when the user explicitly asks for debug details, audit trails, or appendices.

## Reader-Facing Report Rules

- Start with a direct answer or decision summary.
- Make each section serve one clear reader purpose.
- Explain analysis as a coherent argument, not as a source-by-source dump.
- Use tables only for comparison, prioritization, decision summaries, or tradeoff framing.
- Avoid internal labels such as `Evidence Matrix`, `Quality Gate Results`, `Claim Ledger`, and `Rollback` in the final report.
- Prefer Korean for report prose unless the user asks for another language.
- Keep the chat response short after writing the report: conclusion, confidence, report path, and next action.

## Citation Rules

- Tie important factual claims to canonical sources.
- Search summaries, social posts, and uncited blogs are discovery leads only.
- Use short inline source labels near the relevant claim when useful, then list full URLs under `참고 출처`.
- Separate `내용 근거` from `형식 참고` when the report format itself was researched.
- Do not over-cite generic interpretation sentences that merely connect already cited evidence.

## Default Report Shape

Use `assets/research-report-template.md` as the default artifact shape:

1. Title and metadata
2. `핵심 답변`
3. `주요 결론`
4. `분석`
5. `비교 또는 판단 프레임` when useful
6. `리스크와 한계`
7. `실행 권고`
8. `참고 출처`

## Mode Adaptations

- `quick-fact`: usually no report file; answer directly with one or two citations.
- `official-guidance-review`: emphasize current official guidance, version/date caveats, and concrete implications.
- `literature-scan`: emphasize themes, disagreement, benchmark/task scope, and what remains unproven.
- `comparison`: include at most one concise comparison table unless the user asks for exhaustive detail.
- `workflow-update-review`: include execution recommendations, validation, and rollback conditions in prose or a compact decision table.
- `deep-research`: include a longer analysis section and explicit limitations, but keep internal gates out of the final report.

## Common Failure Modes

- Dumping the evidence matrix into the report instead of synthesizing it.
- Reporting quality gate scores as if the user asked for process telemetry.
- Listing many sources without explaining what they change.
- Hiding uncertainty because the report has a polished structure.
- Using broad AI research claims without tying them back to the user's workflow.
