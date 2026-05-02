# Citation And Source Verification

Use this reference when verifying citations, source URLs, DOI/arXiv/OpenReview/PubMed identifiers, or report source support.

## Verification Layers

1. Existence: the source can be reached or located through a canonical identifier.
2. Metadata: title, authors, year, venue/version, and identifiers match the report.
3. Support: the source actually supports the cited claim.

Do not collapse these layers. A DOI can exist while the title is wrong. A paper can exist while the cited sentence overstates what the paper says.

## MVP Policy

Use deterministic checks as hard gates first:

- URL reachability and redirect status
- unsafe URL blocking for localhost, private IPs, link-local hosts, and unsupported schemes
- DOI existence through Crossref, then DataCite/OpenAlex/Semantic Scholar as follow-up providers when implemented
- arXiv ID existence through arXiv metadata
- OpenReview forum/note metadata for OpenReview-hosted papers
- PubMed PMID/DOI metadata for biomedical sources
- title/year/author matching when expected metadata is available

Treat claim-source support as warning-only until there are enough fixtures and reviewed examples. Full support classification needs fetched text, abstracts, or snippets and should use labels such as `supported`, `partially_supported`, `unsupported`, `uncertain`, and `not_checked`.

## Tooling

`scripts/verify_sources.py` is the local MVP verifier.

Typical offline extraction:

```bash
python3 plugins/research/skills/ai-research-workflow/scripts/verify_sources.py research/reports/report.md --offline --json /tmp/source-check.json
```

Network verification should use polite provider behavior:

- include a descriptive `User-Agent`
- include Crossref `mailto` when a contact is configured
- respect provider rate limits
- use per-host concurrency limits
- use timeouts and bounded reads
- avoid bulk full-text download unless explicitly approved

## Provider Notes

| Provider | Use for | Notes |
| --- | --- | --- |
| Crossref | Crossref DOI metadata | Public access works, but polite pool with contact info is preferred. |
| DataCite | Dataset/software/repository DOI metadata | Public API is suitable for findable DOI retrieval. |
| OpenAlex | broad work metadata and title search | API key requirements and usage pricing can change; verify current docs first. |
| Semantic Scholar | paper search, external IDs, citation graph, OA PDF metadata | API key is recommended; unauthenticated access is shared and rate-limited. |
| arXiv | arXiv IDs and preprint metadata | Legacy API asks clients to use at most one request every three seconds. |
| OpenReview | submission/forum metadata | Note visibility and content schema vary by venue. |
| PubMed | biomedical identifiers and abstracts | Use ESearch for IDs, ESummary/EFetch for metadata and records. |

## Failure Labels

- `blocked`: unsafe URL or unsupported scheme
- `failed`: network or parsing failure
- `not_found`: provider returned no matching record
- `metadata_mismatch`: source exists but expected metadata does not match
- `not_checked`: offline mode, unsupported provider, or support check intentionally skipped
- `needs_review`: claim support cannot be determined deterministically

## Rollout

1. Start with URL, DOI, arXiv, and offline extraction.
2. Add DataCite/OpenAlex/Semantic Scholar fallback adapters.
3. Add report fixtures with known true and false citations.
4. Add warning-only claim support checks for high-impact claims.
5. Promote only low-risk deterministic failures to hard gates.
