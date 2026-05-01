# Source Tiers

Use source tiers to decide how strongly a finding should affect conclusions or workflow changes.

## S-tier

Use as primary evidence when current and directly relevant.

- official documentation, release notes, model/system cards, pricing/rate-limit pages
- conference proceedings or peer-reviewed papers
- official benchmark definitions, harnesses, and leaderboards
- primary GitHub repositories from the authors or maintainers
- reproducible eval artifacts with clear methodology

## A-tier

Strong but not final without context checks.

- arXiv or OpenReview preprints
- well-documented independent evals
- maintained implementation repos
- lab/company engineering blogs with concrete methodology
- papers with accessible code, data, or benchmark scripts

## B-tier

Useful for interpretation and discovery.

- technical blogs with citations
- newsletters or analyst posts that summarize primary material
- talks, slide decks, or interviews from credible practitioners
- issue discussions with maintainer participation

## C-tier

Discovery signals only.

- X, Hacker News, Reddit, Discord, forum threads
- personal opinions without reproducible evidence
- unverified benchmark screenshots
- vendor claims without methodology

## Rules

- Do not use C-tier sources as final support for a recommendation.
- Prefer original sources over summaries.
- If S-tier and A-tier sources conflict, state the conflict and inspect dates, scope, and methodology.
- For workflow changes, require at least one S-tier source or two independent A-tier sources unless the user explicitly accepts experimental changes.
