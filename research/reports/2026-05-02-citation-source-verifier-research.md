# Citation/Source Verifier 리서치 보고서

작성일: 2026-05-02  
주제: Codex research plugin용 citation/source verifier 설계 근거와 구현 방향  
리서치 모드: workflow-update-review / literature-scan  
확신도: 중간-높음  
검색 기준일: 2026-05-02

## 핵심 답변

`citation/source verifier`는 한 번의 API 조회로 끝나는 기능이 아니라 세 층의 검증 파이프라인으로 설계해야 한다. 1단계는 URL/DOI/arXiv/OpenReview/PubMed 같은 식별자의 도달성과 canonical source 존재 확인, 2단계는 title/authors/year/venue/identifier 메타데이터 일치, 3단계는 보고서의 cited claim이 실제 source text에 의해 supported/partially supported/unsupported/uncertain인지 판정하는 것이다.

MVP는 deterministic checker로 시작하는 편이 맞다. URL reachability, DOI existence, metadata match, broken-link report는 자동화하고, claim-source support는 SciFact/SemanticCite 계열의 분류 체계를 참고하되 처음에는 LLM-assisted review 또는 warning-only로 두는 것이 안전하다. claim support 판정은 full text 접근, 저작권, OCR/HTML 품질, 분야별 표현 차이 때문에 deterministic하게 강제하기 어렵다.

## 주요 결론

- Crossref는 Crossref DOI와 일반 scholarly metadata 확인의 1차 후보이며, polite pool을 위해 `mailto` 또는 agent header를 넣는 것이 공식 권장이다. 2026년 현재 Crossref 문서는 public/polite/plus pool별 rate/concurrency limit도 명시한다.
- DataCite는 dataset, software, repository artifact DOI에 중요하다. Public API는 인증 없이 DOI metadata retrieval/search에 권장되며, frequent script는 User-Agent와 contact mailto를 넣으라고 안내한다.
- OpenAlex는 DOI 또는 title search 기반 work metadata 보강에 좋다. 2026년 2월 13일 이후 API key가 사실상 규모 있는 사용의 기본이 되었고, free key 기반 호출량/usage model을 확인해야 한다.
- Semantic Scholar는 AI/CS 논문, citation graph, open access PDF URL, abstract, externalIds 보강에 강하다. 공식 문서는 대부분 endpoint가 unauthenticated로 가능하지만 rate-limited이며, API key 사용을 권장한다.
- arXiv와 OpenReview는 AI/ML preprint/conference verification에 직접적이다. arXiv는 `id_list`로 특정 arXiv ID를 조회하고, title/authors/published/updated/doi/category를 Atom metadata로 확인할 수 있다. OpenReview는 Note object의 `id`, `forum`, `content`를 통해 submission metadata를 확인한다.
- URL checker는 HTTP HEAD/GET status만 보면 부족하다. redirects, fragments, robots, private-IP/SSRF 방지, timeout, content-type, canonical URL normalization을 함께 다뤄야 한다.
- 자동 support 판정은 별도 연구 문제다. SciFact는 scientific claim verification을 SUPPORTS/REFUTES/rationale task로 정의했고, SciFact-Open은 대규모 corpus에서 성능이 떨어지는 현실성을 보여준다. SemanticCite는 supported/partially supported/unsupported/uncertain 네 등급과 evidence snippets를 제안한다.

## 분석

### 1. 검증 대상을 분리해야 한다

리서치 보고서에서 “citation이 맞다”는 말은 여러 의미를 가진다. 이를 분리하지 않으면 verifier가 잘못된 통과 신호를 준다.

첫째, source existence다. URL이 열리는지, DOI가 등록되어 있는지, arXiv ID나 OpenReview forum이 실제 record를 가리키는지 확인한다. 이 단계는 비교적 자동화하기 쉽다.

둘째, bibliographic accuracy다. DOI가 존재해도 title, authors, year, venue가 보고서의 citation과 맞지 않을 수 있다. JMIR Mental Health 실험에서 fabricated가 아닌 citation 중 54.6%에 bibliographic error가 있었다는 점은 existence만으로는 부족하다는 근거다.

셋째, claim support다. source가 존재하고 metadata가 맞아도 cited sentence를 실제로 지지하지 않을 수 있다. ALCE도 citation quality를 별도 평가 축으로 둔다. SemanticCite는 이 문제를 full-text source analysis와 four-class classification으로 접근한다. MVP에서는 이 세 번째 단계를 “자동 실패”가 아니라 “검토 필요”로 시작하는 편이 낫다.

### 2. 무료 API 조합

| Provider | 강점 | 추천 용도 | 주요 주의점 |
| --- | --- | --- | --- |
| Crossref REST API | Crossref DOI, journal/proceedings metadata, bibliographic query | DOI existence, title/author/year/container match | non-Crossref DOI는 404가 가능하므로 DataCite/OpenAlex fallback 필요 |
| DataCite REST API | dataset/software/repository DOI metadata | research artifact DOI 검증 | Public API는 Findable DOI 중심; draft/registered state는 member auth 필요 |
| OpenAlex API | DOI/title search, authorships, source, OA location, citation metadata | broad metadata cross-check, DOI가 없어도 title search | 2026년 key/usage model 확인 필요; content download는 비용 큼 |
| Semantic Scholar Graph API | paper search/match, externalIds, citation graph, OA PDF, abstract | AI/CS paper matching, citation graph 보강 | key와 rate limit 정책 확인; title match는 false positive 가능 |
| arXiv API | arXiv ID, title, authors, abstract, DOI/category/version metadata | AI/ML preprint verification | legacy API는 3초 delay/단일 connection 권장 |
| OpenReview API | submission/review/forum Note metadata | ICLR/NeurIPS 등 OpenReview-hosted paper verification | venue-specific schema/readers visibility 주의 |
| PubMed / NCBI E-utilities | PMID/PMCID/DOI, biomedical metadata and abstracts | medical/life-science claims | PubMed coverage에 한정; ESearch 후 EFetch/ESummary 필요 |

이 조합에서 우선순위는 DOI 또는 explicit identifier가 있을 때 identifier lookup을 먼저 하고, 없으면 title/bibliographic search를 하며, 결과가 애매하면 여러 provider의 metadata agreement를 보는 방식이 좋다.

### 3. 추천 파이프라인

1. Input parsing  
   Markdown 보고서에서 URL, DOI, arXiv ID, OpenReview URL, PubMed URL/PMID, Semantic Scholar URL, citation-like bibliography line을 추출한다. URL과 citation text를 source block으로 묶고, 인라인 citation이 붙은 근처 sentence를 claim candidate로 잡는다.

2. URL/source reachability  
   HTTP `HEAD`를 먼저 시도하고, 405/403/불완전 header/동적 사이트에서는 bounded `GET`으로 fallback한다. RFC 9110은 HEAD가 GET과 같은 header를 보내야 하지만 일부 header가 생략될 수 있음을 설명한다. W3C Link Checker처럼 redirect와 fragment를 구분하고, private IP, localhost, link-local, file scheme 접근은 기본 차단한다.

3. Identifier verification  
   DOI는 Crossref -> DataCite -> OpenAlex -> Semantic Scholar 순으로 조회한다. arXiv ID는 arXiv `id_list`, OpenReview URL은 forum/note metadata, PMID는 ESearch/ESummary/EFetch를 사용한다. 각 provider 응답을 normalized metadata로 모은다.

4. Metadata matching  
   title similarity, first-author/author-overlap, year tolerance, venue/container match, DOI/arXiv/PMID exact match를 계산한다. exact identifier match가 있으면 높은 confidence를 주되, title/year가 크게 다르면 `metadata_mismatch`로 경고한다.

5. Claim support sampling  
   모든 문장을 판정하지 말고, 중요한 결론/숫자/비교/정책/학술 claim 위주로 claim을 추출한다. abstract, official page, fetched HTML, OA full text snippet을 evidence pool로 만들고 `supported`, `partially_supported`, `unsupported`, `uncertain`, `not_checked`로 분류한다.

6. Report output  
   verifier는 원문을 고쳐 쓰기보다 JSON/Markdown 경고를 내야 한다. 예: `broken_link`, `doi_not_found`, `metadata_mismatch`, `citation_support_unknown`, `citation_not_supporting_claim`, `provider_rate_limited`.

### 4. Matching heuristic 초안

MVP는 설명 가능한 rule scoring이 낫다.

| Signal | 처리 |
| --- | --- |
| DOI exact match | 가장 강한 existence signal. Crossref 실패 시 DataCite/OpenAlex fallback |
| arXiv ID exact match | preprint existence 강함. version 차이는 warning |
| PMID/PMCID exact match | biomedical existence 강함 |
| title similarity >= 0.92 | strong title match |
| title similarity 0.80-0.92 | candidate match; author/year 확인 필요 |
| first author exact/normalized match | title ambiguity 줄임 |
| year exact 또는 +-1 | acceptable; online-first/print-year 차이 caveat |
| venue/container match | optional support; abbreviations 때문에 strict fail 금지 |
| multiple providers agree | confidence boost |
| one provider only, title-only match | partial confidence |

처음부터 ML ranker를 넣기보다 이 rule layer를 만들고, false positive/negative fixture를 쌓은 뒤 필요할 때 embedding 또는 LLM judge를 추가하는 편이 유지보수성이 좋다.

### 5. Claim-source support는 별도 단계로 다뤄야 한다

SciFact는 scientific claim verification을 evidence abstracts 선택, SUPPORTS/REFUTES label, rationale identification으로 정의한다. SciFact-Open은 open-domain corpus 500K abstracts 환경에서 기존 시스템이 최소 15 F1 하락을 보였다고 보고했다. 즉, “문장 하나와 논문 하나가 의미상 맞는지”는 쉬운 문제가 아니다.

SemanticCite는 최신 citation verification 연구로, full-text source analysis, relevant snippets, supported/partially supported/unsupported/uncertain classification을 제안한다. 이 방향은 research plugin에 잘 맞지만, MVP에서 full automation으로 막는 것은 위험하다. 특히 full text가 없거나 paywall/저작권 문제가 있을 때는 abstract만 보고 unsupported로 단정하면 안 된다.

따라서 support checker는 단계적으로 도입한다.

- Stage A: citation/source existence와 metadata mismatch만 fail 가능
- Stage B: claim support는 `unknown` 또는 `needs_review` warning
- Stage C: high-impact claims에 한해 fetched snippets 기반 LLM judge를 사용
- Stage D: 충분한 fixture와 human review가 쌓이면 일부 obvious unsupported만 fail 처리

## 구현 권고

1. `scripts/verify_sources.py` 또는 동등한 작은 CLI로 시작한다.  
   대상 surface: research plugin의 `scripts/` 또는 repo-level tooling  
   입력: Markdown report path  
   출력: JSONL + human-readable Markdown summary  
   검증 범위: URL reachability, DOI/arXiv/OpenReview/PubMed existence, metadata match

2. provider adapter를 분리한다.  
   `crossref`, `datacite`, `openalex`, `semantic_scholar`, `arxiv`, `openreview`, `pubmed`, `generic_url` 모듈로 나누고, 모두 같은 normalized record를 반환하게 한다.

3. 네트워크 정책을 보수적으로 둔다.  
   timeout, retry with backoff, per-host concurrency limit, User-Agent/contact, Crossref `mailto`, arXiv 3초 delay, private IP 차단, robots 고려를 기본값으로 둔다.

4. support verification은 MVP에 fail gate로 넣지 않는다.  
   처음에는 `needs_review` warning으로 보고하고, 보고서의 high-impact claim만 표본 검증한다.

5. fixture 기반 테스트를 먼저 만든다.  
   최소 fixture: valid DOI, fake DOI, title-only valid paper, DOI/title mismatch, redirecting URL, 404 URL, arXiv ID, OpenReview URL, PubMed DOI, claim supported by abstract, claim not supported by abstract.

## 리스크와 한계

- Provider coverage가 다르다. Crossref, DataCite, OpenAlex, Semantic Scholar 중 하나에 없다고 source가 가짜라는 뜻은 아니다.
- Metadata는 불완전하거나 stale할 수 있다. 특히 preprint -> proceedings -> journal 확장 과정에서 title/year/venue가 바뀐다.
- DOI는 landing page resolution과 metadata registry가 다를 수 있다. DOI URL이 열려도 metadata mismatch가 있을 수 있고, 반대로 landing page가 일시적으로 죽어도 DOI record는 유효할 수 있다.
- Claim support는 full text 접근성에 크게 좌우된다. abstract만으로 source가 claim을 지지하지 않는다고 단정하면 false negative가 생긴다.
- URL checking은 SSRF 위험이 있다. verifier가 내부 네트워크, localhost, cloud metadata endpoint를 열지 않게 막아야 한다.
- Rate limits와 API key 정책은 자주 바뀐다. OpenAlex는 2026년 기준 API key/usage model이 바뀌었으므로 구현 전 문서를 다시 확인해야 한다.

## 다음 액션

1. 이 보고서를 바탕으로 `citation-source-verification.md` reference를 research plugin에 추가한다.
2. 그 다음 `scripts/verify_sources.py` MVP를 TDD로 만든다.
3. MVP는 URL/identifier/metadata 검증까지만 fail gate로 삼고, claim support는 warning-only로 둔다.
4. 샘플 보고서 3개를 fixture로 삼아 false positive/false negative를 기록한다.

## 참고 출처

### 공식 API와 표준

- Crossref, “Access and authentication”: https://www.crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication/
- Crossref REST API docs: https://github.com/CrossRef/rest-api-doc
- DataCite, “Introduction to the DataCite REST API”: https://support.datacite.org/docs/api
- DataCite, “Retrieving a single DOI”: https://support.datacite.org/docs/api-get-doi
- OpenAlex, “Authentication & Pricing”: https://developers.openalex.org/guides/authentication
- OpenAlex API docs: https://developers.openalex.org/
- Semantic Scholar API overview: https://www.semanticscholar.org/product/api
- Semantic Scholar Academic Graph API docs: https://api.semanticscholar.org/api-docs/graph
- arXiv API User's Manual: https://info.arxiv.org/help/api/user-manual.html
- Terms of Use for arXiv APIs: https://info.arxiv.org/help/api/tou.html
- OpenReview, “Introduction to Notes”: https://docs.openreview.net/getting-started/objects-in-openreview/introduction-to-notes
- NCBI, “The 9 E-utilities and Associated Parameters”: https://www.nlm.nih.gov/dataguide/eutilities/utilities.html
- PubMed Help: https://pubmed.ncbi.nlm.nih.gov/help/
- RFC 9110, “HTTP Semantics”: https://www.rfc-editor.org/rfc/rfc9110
- W3C Link Checker Documentation: https://dev.w3.org/perl/modules/W3C/LinkChecker/docs/checklink

### 학술 근거

- Gao et al., “Enabling Large Language Models to Generate Text with Citations”: https://arxiv.org/abs/2305.14627
- Ru et al., “RAGChecker: A Fine-grained Framework for Diagnosing Retrieval-Augmented Generation”: https://arxiv.org/abs/2408.08067
- Wadden et al., “Fact or Fiction: Verifying Scientific Claims”: https://arxiv.org/abs/2004.14974
- Wadden et al., “SciFact-Open: Towards open-domain scientific claim verification”: https://arxiv.org/abs/2210.13777
- Haan, “SemanticCite: Citation Verification with AI-Powered Full-Text Analysis and Evidence-Based Reasoning”: https://arxiv.org/abs/2511.16198
- JMIR Mental Health, “Influence of Topic Familiarity and Prompt Specificity on Citation Fabrication in Mental Health Research Using Large Language Models”: https://mental.jmir.org/2025/1/e80371/
