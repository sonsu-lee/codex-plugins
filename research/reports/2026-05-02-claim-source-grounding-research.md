# Claim-Source Grounding 리서치 보고서

작성일: 2026-05-02
주제: 리서치 도구의 주장-근거-원문 확인 처리와 research 플러그인의 누락/미강제 이유
리서치 모드: workflow-update-review / deep-research
확신도: 중간-높음
검색 기준일: 2026-05-02

## 핵심 답변

사용자의 문제 제기가 맞다. 리서치 산출물의 기본 단위는 “출처 목록”이 아니라 “주장 -> 근거 -> 원문/레퍼런스 -> 적합성 판단”이어야 한다. 공식 리서치 제품들은 대체로 citations/source links를 제공해 사용자가 검증 가능하게 만들지만, claim 단위로 “이 citation이 이 문장을 실제로 support하는가”를 완전 자동 hard gate로 보장한다고 설명하지는 않는다. 반면 학술 연구는 이 문제를 별도 과제로 다룬다. ALCE는 citation quality를 fluency/correctness와 분리했고, Automatic Evaluation of Attribution은 cited reference가 generated statement를 fully support하는지 검증하는 문제를 명시했으며, FActScore/SAFE는 long-form 답변을 atomic facts로 쪼개 support 여부를 평가한다.

우리 플러그인에서도 원문 확인 개념은 빠져 있지 않았다. `source-fetch`, `claim-ground`, `verification-gates`에 이미 들어 있다. 다만 구현상 “claim별 원문 확인 ledger”를 필수 산출물이나 자동 hard gate로 만들지는 않았다. 이유는 MVP가 URL/DOI/arXiv/PubMed 같은 deterministic existence/metadata 검증을 먼저 다루도록 범위를 잡았고, claim-source semantic support는 source 접근성, PDF/HTML 품질, paywall, 저작권, false positive/negative 때문에 바로 hard gate로 올리기 어렵다고 판단했기 때문이다. 하지만 현재 구조에서는 이 판단이 너무 보수적이었다. 다음 개선은 claim-source ledger와 access path를 명시적으로 추가하는 방향이 맞다.

## 주요 결론

- 리서치 도구들은 이 문제를 “어느 정도” 고려한다. OpenAI Deep Research는 구조화된 보고서와 citations/source links를 제공하고, OpenAI 소개 글은 source의 sentence/passage를 cite할 수 있다고 설명한다. Gemini Deep Research와 Perplexity도 sources/citations를 사용자 검증 장치로 둔다. 다만 공식 문서상 이들이 모든 최종 claim에 대해 자동으로 source support를 판정하는 hard gate를 제공한다고 보기는 어렵다.
- 학술 연구는 사용자가 말한 구조를 더 직접적으로 다룬다. ALCE는 cited answer의 citation quality를 평가하고, Automatic Evaluation of Attribution은 cited reference가 generated statement를 fully support하는지 검증하는 문제를 “open problem”으로 둔다. FActScore와 SAFE는 long-form 답변을 원자적 사실/개별 fact로 분해하고 reliable source 또는 search result support를 확인한다.
- claim-source support는 existence/metadata 검증과 다르다. DOI가 존재하고 title/year가 맞아도, 그 논문이 보고서 문장을 실제로 지지하지 않을 수 있다. 그래서 우리 플러그인의 `verify_sources.py`가 현재 하는 URL/DOI/arXiv/PubMed 검증은 필요한 하위 단계지만 충분조건은 아니다.
- 우리 쪽에서 “안 넣은” 것이 아니라 “workflow 지침에는 넣고 자동 강제는 보류한” 상태다. 현재 `SKILL.md`는 original source fetch와 claim grounding을 요구하고, `verification-gates.md`는 support/access path를 확인하라고 한다. 하지만 report 작성 전에 claim별 원문 확인 ledger를 만들도록 강제하지는 않는다.
- 개선 방향은 명확하다. `source-fetch`를 단순 단계명이 아니라 claim-source ledger를 만드는 단계로 격상하고, 각 주요 claim에 `reference`, `access_path`, `grounding_snippet_or_metadata`, `support_label`, `fit_judgement`를 요구해야 한다. 자동화는 처음부터 hard fail이 아니라 `missing_original_check`, `support_needs_review`, `metadata_only_support` 같은 warning/fail 등급으로 시작하는 편이 안전하다.

## 분석

### 1. 제품형 리서치 도구들은 citation transparency를 강조하지만 claim support 보증은 약하다

OpenAI Help Center는 Deep Research가 사용자가 source를 선택하고, 계획을 검토/수정한 뒤, citations 또는 source links가 포함된 구조화 보고서를 제공한다고 설명한다. 같은 문서는 완료된 결과에 `sources used` 섹션과 activity history가 있어 검토와 재사용을 돕는다고 설명한다. OpenAI 소개 글은 Deep Research가 browsing/reasoning task로 훈련됐고 source의 sentence 또는 passage를 cite할 수 있다고 설명한다. 이는 단순 URL 목록보다 강한 source traceability다.

하지만 여기서 말하는 것은 주로 “검증 가능성”이다. 즉 사용자가 citation/source link를 눌러 확인할 수 있게 하는 기능이다. 공식 문서가 “모든 문장에 대해 source가 실제 support하는지 자동 판정해 hard gate로 막는다”고 설명하지는 않는다.

Gemini Deep Research도 비슷하다. Google 도움말은 사용자가 source를 선택할 수 있고, 기본적으로 Google Search가 research source에 포함되며, Gemini가 research plan을 만들고 여러 source를 분석해 report를 생성한다고 설명한다. Perplexity Help Center는 각 답변이 original source로 연결되는 numbered citation을 포함해 사용자가 검증하거나 더 탐색할 수 있다고 설명한다. Elicit은 hallucination을 줄이기 위해 source text에 faithful하게 유지하려고 하며, 복사/붙여넣기를 권장하지 않고 이해를 돕는 용도라고 설명한다.

즉 제품들은 “source transparency”와 “user-verifiable output”을 중요하게 본다. 하지만 사용자의 요구인 “주장마다 reference를 붙이고, 그 reference의 원문 관련 내용이 실제로 적절한지 판단”은 제품 설명보다 한 단계 더 깊은 **claim-level attribution verification**이다.

### 2. 학술 연구는 이 문제를 핵심 문제로 본다

ALCE는 LLM이 citation이 있는 text를 생성하는 것을 평가하기 위한 benchmark다. 이 논문은 fluency, correctness, citation quality를 별도 축으로 둔다. arXiv abstract 기준으로, ELI5 dataset에서 best model도 complete citation support가 50% 부족했다. 이 결과는 “citation이 달려 있다”와 “citation이 답변을 충분히 support한다”가 다르다는 강한 근거다.

Automatic Evaluation of Attribution by LLMs는 더 직접적이다. 이 논문은 generative search engine이 external reference를 넣어 claim을 support하려 하지만, generated statement가 cited reference에 의해 fully supported되는지 검증하는 attribution evaluation은 open problem이라고 설명한다. 즉 사용자가 말한 “레퍼런스가 관련 내용에 적절한지 판단”은 이미 독립 연구 문제로 정식화돼 있다.

의학 영역의 SourceCheckup 논문도 같은 결론을 지지한다. 이 논문은 “LLM이 생성한 source가 claim을 실제 support하는가?”를 묻고, 상용 LLM 답변의 상당 부분이 source에 의해 완전히 support되지 않는다고 보고한다. 특히 RAG를 붙여도 개별 statement unsupported 문제가 남는다고 한다. 이는 retrieval이 있어도 claim-source 적합성 판단이 별도 단계로 필요하다는 근거다.

FActScore는 long-form text를 atomic facts로 분해하고, 각 atomic fact가 reliable knowledge source에 의해 support되는 비율을 측정한다. SAFE도 long-form response를 individual facts로 쪼개고, Google Search query와 multi-step reasoning으로 각 fact가 search result에 의해 support되는지 판단한다. FELM은 factuality annotation에 reference links that support or contradict the statement를 붙인다. 이 계열 연구들은 모두 “문서 전체 점수”보다 “claim/fact 단위 support”가 필요하다는 방향이다.

### 3. 왜 일반 리서치 도구들이 이걸 완전히 강제하지 않나

기술적으로는 가능하지만 운영 비용과 실패 모드가 크다.

첫째, 원문 접근성이 균일하지 않다. 공식 문서는 HTML로 충분할 수 있고, 논문은 abstract/PDF/full text/appendix/table이 나뉜다. GitHub 근거는 README가 아니라 code, issue, release note일 수 있다. PubMed는 abstract만 있고 full text가 없을 수 있다. Claim support가 full text에 있는데 tool이 abstract만 읽었다면 false unsupported가 된다.

둘째, parsing 품질이 낮을 수 있다. PDF, table, figure, code, changelog는 일반 HTML보다 구조 추출이 어렵다. 인용된 claim이 table이나 appendix에 있으면 단순 snippet search로는 놓치기 쉽다.

셋째, semantic support 판정은 단순 문자열 매칭이 아니다. “이 source가 claim을 직접 support하는가, 일부만 support하는가, 더 좁은 claim만 support하는가, 오히려 반대하는가”는 자연어 추론 문제다. Automatic Evaluation of Attribution, FActScore, SAFE 같은 연구가 존재하는 것 자체가 이 문제가 단순하지 않다는 증거다.

넷째, UX와 비용 문제가 있다. 모든 claim을 atomic fact로 쪼개고, 각 fact마다 source를 열고, support label을 붙이면 깊은 리서치에는 좋지만 quick answer에는 과하다. 그래서 상용 제품은 대체로 citations/source links를 제공하고 사용자가 검토하게 하는 쪽을 기본 UX로 둔다.

### 4. 우리 플러그인에서 왜 hard gate로 안 넣었나

우리 쪽 판단은 “원문 확인이 덜 중요하다”가 아니었다. 오히려 반대였다. 원문 확인은 `SKILL.md`의 operating contract와 default procedure에 이미 들어 있다. `source-fetch`는 original sources를 fetch/inspect하라고 되어 있고, `claim-ground`는 source/support/grounding/limitation/applicability를 요구한다. `verification-gates.md`도 existence, metadata, support, freshness, access path를 분리한다.

문제는 구현 우선순위였다. 이전 커밋에서 우리는 자동화 가능한 deterministic layer를 먼저 만들었다. URL reachability, DOI existence, DataCite fallback, arXiv metadata, PubMed metadata, report section lint는 비교적 명확히 pass/fail을 줄 수 있다. 반면 claim-source support는 LLM judge, full text fetch, snippet extraction, PDF parsing, source access path 기록이 필요하고, 충분한 fixture 없이 hard gate로 올리면 잘못된 실패를 많이 낼 수 있다.

그래서 현재 구조는 다음 상태다.

```text
개념/정책: 들어 있음
단계명: source-fetch, claim-ground로 들어 있음
자동 검증: existence/metadata/report-shape 위주
부족한 부분: claim별 원문 확인 ledger와 support-fit judgement 강제
```

즉 “왜 안 넣었나”에 대한 정확한 답은, **MVP에서 claim-support semantic verification을 hard gate로 넣기에는 비용과 false failure 위험이 컸고, 먼저 deterministic verifier를 만든 뒤 warning-only support check로 확장하려는 rollout을 택했기 때문**이다. 하지만 지금 관점에서 보면, workflow contract가 충분히 강제적이지 않다. 사용자의 지적처럼 claim-source-grounding을 별도 내부 산출물로 올리는 것이 맞다.

## 비교 또는 판단 프레임

| 수준 | 무엇을 보장하나 | 예 | 한계 | 우리 플러그인 적용 |
| --- | --- | --- | --- | --- |
| Source list | 참고 출처가 있다 | 보고서 하단 URL 목록 | 어떤 문장을 support하는지 불명확 | 부족 |
| Inline citation | 문장 근처에 citation이 있다 | Perplexity/OpenAI/Gemini reports | citation이 실제 support하는지 별도 문제 | 최소 기준 |
| Source existence/metadata | URL/DOI/arXiv/PubMed가 실제다 | `verify_sources.py` | source가 claim을 support하는지는 모름 | 이미 일부 구현 |
| Original-source access path | full text/abstract/code/API 등 무엇을 봤는지 기록 | source-fetch ledger | 수동/반자동 운영 필요 | 추가 필요 |
| Claim-source support judgment | claim이 source에 의해 supported/partial/unsupported인지 판단 | ALCE, attribution eval, FActScore, SAFE | 비용, parsing, LLM judge 신뢰도 문제 | warning-first로 추가 |
| Hard support gate | unsupported claim을 보고서에서 차단 | 고신뢰 audit workflow | false fail, latency 증가 | high-impact claim부터 단계 적용 |

## 리스크와 한계

- 상용 제품 문서는 내부 검증 알고리즘을 모두 공개하지 않는다. 따라서 “고려하지 않는다”가 아니라 “공개 문서상 claim-level hard guarantee로 설명하지 않는다”가 정확하다.
- 학술 연구의 support 평가 방법은 benchmark나 domain에 따라 성능이 다르다. SAFE/FActScore/ALCE를 그대로 플러그인에 넣으면 비용과 복잡도가 커진다.
- claim-source support를 자동 hard gate로 바로 넣으면 false negative가 생길 수 있다. 특히 PDF table, figure, appendix, paywalled source, code-level evidence가 문제다.
- 우리 현재 verifier는 source existence/metadata layer다. 이를 claim support verifier처럼 오해하면 안 된다.

## 실행 권고

1. `SKILL.md`의 `source-fetch`를 “claim-source ledger 생성 단계”로 강화한다.
   대상 surface: skill
   검증: deep/workflow 보고서 생성 시 주요 claim마다 source/access_path/support_label이 내부 notes에 생기는지 확인한다.
   롤백: quick-fact까지 과도하게 느려지면 deep/workflow/literature 모드로만 제한한다.

2. `verification-gates.md`의 claim decomposition 필드에 `access_path`와 `fit_judgement`를 추가한다.
   대상 surface: reference
   검증: source_evaluator가 metadata-only support와 original-inspected support를 구분하는지 확인한다.
   롤백: 필드가 과도해져 사용되지 않으면 high-impact claim에만 요구한다.

3. `citation-source-verification.md`에 claim-source support rollout을 더 분명히 한다.
   대상 surface: reference
   검증: `supported`, `partially_supported`, `unsupported`, `uncertain`, `not_checked`, `metadata_only` 같은 label이 일관되게 쓰이는지 확인한다.
   롤백: LLM judge 결과가 불안정하면 human-review-needed warning으로 낮춘다.

4. `scripts/verify_sources.py`는 existence/metadata verifier로 이름과 역할을 명확히 유지한다.
   대상 surface: script/docs
   검증: CLI output에 “support not checked” 또는 “metadata-only”가 명확히 드러나는지 확인한다.
   롤백: 사용자가 이 스크립트를 support verifier로 오해하면 별도 `verify_claim_support.py`로 분리한다.

5. 다음 구현은 `claim_support_ledger.md` 또는 JSON schema부터 시작한다.
   대상 surface: assets/scripts
   검증: 샘플 보고서 하나에서 주요 claim 5개를 ledger로 만들고, source_evaluator가 unsupported/partial claim을 찾아내는지 본다.
   롤백: ledger 작성 비용이 너무 크면 `deep-research`, `workflow-update-review`, `literature-scan`에만 적용한다.

## 참고 출처

### 내용 근거

- OpenAI Help Center, “Deep research in ChatGPT”: https://help.openai.com/en/articles/10500283-deep-research
- OpenAI, “Introducing deep research”: https://openai.com/index/introducing-deep-research/
- Google Help, “Use Deep Research in Gemini Apps”: https://support.google.com/gemini/answer/15719111
- Perplexity Help Center, “How does Perplexity work?”: https://www.perplexity.ai/help-center/en/articles/10352895-how-does-perplexity-work
- Elicit Help Center, “Citing Elicit, search methodology, and using Elicit's content in your own work”: https://support.elicit.com/en/articles/549697
- Gao et al., “Enabling Large Language Models to Generate Text with Citations”: https://arxiv.org/abs/2305.14627
- Yue et al., “Automatic Evaluation of Attribution by Large Language Models”: https://arxiv.org/abs/2305.06311
- Wu et al., “How well do LLMs cite relevant medical references? An evaluation framework and analyses”: https://arxiv.org/abs/2402.02008
- Min et al., “FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation”: https://aclanthology.org/2023.emnlp-main.741/
- Wei et al., “Long-form factuality in large language models”: https://arxiv.org/abs/2403.18802
- Chen et al., “FELM: Benchmarking Factuality Evaluation of Large Language Models”: https://arxiv.org/abs/2310.00741

### 형식 참고

- Local reference, `plugins/research/skills/ai-research-workflow/references/research-concepts.md`
- Local reference, `plugins/research/skills/ai-research-workflow/references/citation-source-verification.md`
- Local reference, `plugins/research/skills/ai-research-workflow/references/verification-gates.md`
