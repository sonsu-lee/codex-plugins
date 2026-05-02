# Exa Playbook

Use Exa as a free-tier discovery layer, not as the final judge.

## Default Mode

The research plugin may bundle Exa's hosted MCP free path as an optional discovery provider:

```json
{
  "command": "npx",
  "args": ["-y", "mcp-remote", "https://mcp.exa.ai/mcp"]
}
```

This intentionally does not read `EXA_API_KEY` from the environment and does not attach account-backed headers. Do not switch to a key-backed Exa server unless the user explicitly asks for paid or account-backed usage.

Exa is not the default authority. Prefer official docs, canonical scholarly pages, and primary repos when the target source is already known.

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
  "numResults": 5
}
```

Official guidance scan:

```json
{
  "query": "agentic coding best practices planning verification subagents",
  "numResults": 5
}
```

Implementation scan:

```json
{
  "query": "repository benchmark agentic coding terminal bench swe bench harness",
  "numResults": 5
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
- Resolve canonical IDs when possible: DOI, arXiv ID, OpenReview URL, PMID, PMCID, Semantic Scholar paper ID, GitHub repo, or publisher URL.
- Prefer free official APIs and canonical pages for verification after Exa discovers candidates.
- Check whether a paper is peer-reviewed, preprint-only, updated, withdrawn, or superseded.
- For benchmarks, inspect the task definition and whether the cited score is from the official leaderboard, paper, or vendor post.
- For code, prefer maintained repos with tests, releases, issues, or reproducibility notes.
- Do not copy Exa summaries into the answer as if they were source text.

## Cost Control

- Start with 3 to 5 results.
- Fetch full text only for sources likely to affect the conclusion.
- Use only the default free hosted MCP tools unless the user explicitly approves paid/account-backed usage.
- Do not use Exa deep search, advanced search, monitors, bulk crawling, or high-result queries by default.
- If Exa returns a quota/rate-limit/payment error, stop using Exa for that task and fall back to official free APIs or native web search.
- Summarize retrieved evidence before opening another retrieval lane.
