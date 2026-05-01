# Exa Playbook

Use Exa as a retrieval layer, not as the final judge.

## When Exa Helps

- recent papers and preprints
- cross-domain search where keywords are not enough
- finding related implementation repos, benchmark pages, and discussion
- fetching clean page content for model context
- discovering sources before deeper verification

## Search Patterns

Paper scan:

```json
{
  "query": "agentic coding benchmark long horizon software engineering agents",
  "category": "research paper",
  "numResults": 10,
  "includeDomains": [
    "arxiv.org",
    "openreview.net",
    "proceedings.mlr.press",
    "aclanthology.org",
    "paperswithcode.com"
  ],
  "contents": {
    "highlights": true
  }
}
```

Official guidance scan:

```json
{
  "query": "agentic coding best practices planning verification subagents",
  "includeDomains": [
    "openai.com",
    "developers.openai.com",
    "help.openai.com",
    "anthropic.com",
    "code.claude.com",
    "docs.claude.com"
  ],
  "contents": {
    "highlights": true
  }
}
```

Implementation scan:

```json
{
  "query": "repository benchmark agentic coding terminal bench swe bench harness",
  "includeDomains": [
    "github.com",
    "paperswithcode.com"
  ],
  "contents": {
    "highlights": true
  }
}
```

## Date Handling

Use date filters for fast-moving AI topics:

- last 30 days: product releases, pricing, model availability, tool behavior
- last 6 months: agent workflow practices and benchmark changes
- no date limit: foundational methods or older benchmark definitions

Always state the date window when it matters.

## Verification Rules

- Fetch the original paper or official page before relying on a claim.
- Check whether a paper is peer-reviewed, preprint-only, updated, withdrawn, or superseded.
- For benchmarks, inspect the task definition and whether the cited score is from the official leaderboard, paper, or vendor post.
- For code, prefer maintained repos with tests, releases, issues, or reproducibility notes.
- Do not copy Exa summaries into the answer as if they were source text.

## Cost Control

- Start with 5 to 10 results.
- Fetch full text only for sources likely to affect the conclusion.
- Use deep search only for broad synthesis or when ordinary search misses important context.
- Summarize retrieved evidence before opening another retrieval lane.
