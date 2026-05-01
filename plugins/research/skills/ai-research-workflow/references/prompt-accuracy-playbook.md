# Prompt Accuracy Playbook

Use this reference when the research task depends on prompt quality, answer accuracy, long documents, or workflow changes.

## Accuracy Loop

Default optimization order:

1. Start with the simplest prompt and an expected output shape.
2. Define success criteria before adding more tools or context.
3. Run the task, inspect failures, and classify each failure.
4. If the failure is missing or stale knowledge, improve retrieval and source grounding.
5. If the failure is inconsistent behavior or formatting, improve instructions, examples, and output contract.
6. Re-test after each change; do not add more context or tools without a failure hypothesis.

For research workflows, use retrieval and source verification before considering prompt expansion. More context can add noise if it is not relevant.

## Prompt Structure

For complex prompts, use XML-style tags in working prompts and delegated tasks:

```xml
<research_request>
  <objective>...</objective>
  <constraints>free-first, cite original sources, no paid APIs</constraints>
  <success_criteria>...</success_criteria>
</research_request>

<instructions>
  <step>Classify the research mode.</step>
  <step>Retrieve candidate sources.</step>
  <step>Build a claim ledger before synthesis.</step>
</instructions>

<documents>
  <document index="1">
    <source>...</source>
    <date>...</date>
    <document_content>...</document_content>
  </document>
</documents>

<output_contract>
  <section>working conclusion</section>
  <section>evidence by source tier</section>
  <section>caveats and gaps</section>
</output_contract>
```

Use tags to separate instructions, context, examples, documents, claims, and output format. Keep tag names consistent across prompts.

## Long Documents

When working with long documents or many sources:

- Put source documents and metadata in tagged document blocks.
- Put the final research question and output contract after the documents.
- Ask for short grounding quotes or exact snippets before synthesis.
- Avoid dumping every retrieved source into context; include the smallest relevant subset.

## Examples

Use examples only when they reduce recurring formatting or reasoning errors. Prefer 3 to 5 examples that mirror the actual task and include edge cases.

Wrap examples separately:

```xml
<examples>
  <example>
    <input>...</input>
    <good_output>...</good_output>
    <why_it_is_good>...</why_it_is_good>
  </example>
</examples>
```

Do not add examples just to make the prompt look thorough. If failures are caused by missing knowledge, improve retrieval instead.

## Claim Ledger

Before final synthesis, create a compact ledger:

```text
claim:
source:
tier:
support: supported | partially-supported | ambiguous | contradicted | unverified | retracted
grounding:
limitation:
workflow impact:
```

Final answers should not include the whole ledger unless useful, but conclusions should be traceable to it.

## Hallucination Controls

- Allow uncertainty: say "not found", "unclear", or "not enough evidence" when support is missing.
- Restrict factual claims to retrieved or canonical sources for source-sensitive tasks.
- Verify important claims with citations or short source snippets.
- Retract unsupported claims instead of weakening them into vague language.
- Search for contradictions before recommending workflow changes.

## Evaluation

For reusable prompt or workflow changes, define a small eval before adopting the change:

- 5 to 20 representative prompts or research questions
- expected output sections
- required citation/source behavior
- failure cases that should be caught
- scoring rubric: correct, partially correct, unsupported, or wrong

Prefer code/rule-based checks when possible. Use LLM grading only with a clear rubric and spot checks.

## Tool Discipline

- Use official or canonical sources first when the target source is known.
- Use Exa free-tier discovery when the source is unknown or broad discovery is needed.
- Run independent retrieval lanes in parallel only when they do not depend on each other.
- Do not guess tool parameters; search or inspect enough context to know what to call.
- Stop and ask before switching to paid, account-backed, bulk, or deep-search paths.
