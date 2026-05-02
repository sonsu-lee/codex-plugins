# Codex 리서치 플러그인 개념 리서치 보고서

작성일: 2026-05-02  
주제: Codex용 리서치 플러그인을 설계하기 위한 공식 개념, 학술 근거, 재탐색 방향  
리서치 모드: deep-research / workflow-update-review  
확신도: 중간-높음  
검색 기준일: 2026-05-02

## 핵심 답변

Codex용 리서치 플러그인은 “검색을 잘하는 프롬프트”가 아니라, 반복 가능한 연구 절차를 `plugin -> skill -> references/assets -> MCP/tools -> optional subagents -> validation`으로 나눠 패키징하는 구조가 적합하다. OpenAI 공식 문서는 플러그인을 skills, app integrations, MCP servers의 배포 단위로 설명하고, skills는 progressive disclosure로 필요한 때만 전체 지침을 읽는 구조라고 설명한다. 따라서 연구 품질 정책은 플러그인 manifest가 아니라 `SKILL.md`와 `references/`에 두고, retrieval은 MCP/tool에, 회귀 검증은 eval 또는 스크립트에 분리하는 것이 맞다.

학술적으로는 RAG, ReAct, WebGPT, Self-RAG, Chain-of-Verification, ALCE, RAGChecker, STORM이 핵심 토대다. 이들은 각각 외부 근거 사용, 검색-추론-행동 루프, 인용 수집, 자기비판/검증, citation 품질 평가, 장문 리서치 구조화를 다룬다. 연구 플러그인 설계에서 특히 중요한 결론은 “출처를 붙이는 것”만으로는 충분하지 않고, 원문 fetch, claim 단위 검증, citation support 평가, 반례 탐색, 리포트 adequacy 검사가 별도 단계로 있어야 한다는 점이다.

## 주요 결론

- Codex의 공식 구조상 reusable research workflow는 먼저 skill로 설계하고, 공유와 배포가 필요해질 때 plugin으로 묶는 것이 자연스럽다. Skills 문서는 “workflow itself”를 skill로 설계하고 plugin을 배포 단위로 쓰라고 설명한다.
- 연구 플러그인의 핵심 개념은 retrieval보다 verification이다. RAG는 외부 지식 접근과 provenance 문제를 다루지만, ALCE와 RAGChecker는 citation support와 RAG 진단이 별도 평가 문제라는 점을 보여준다.
- “깊은 리서치”는 단일 검색 호출이 아니라 단계적 워크플로다. 공식 deep research 문서는 deep research 모델이 web search, remote MCP, file search 같은 data source를 필요로 하며, MCP는 search/fetch 인터페이스가 중요하다고 설명한다.
- Codex subagent는 기본 기능이지만 연구 플러그인에 무조건 fan-out을 넣으면 비용과 예측 가능성이 나빠진다. 공식 Codex 문서는 subagent가 explicit ask일 때만 spawn되고 토큰을 더 쓴다고 설명한다. 연구 플러그인도 “독립 evidence lane이 있을 때만” 제한적으로 쓰는 편이 맞다.
- 연구 보고서의 신뢰성 리스크는 citation hallucination이다. 2025년 JMIR Mental Health 실험은 GPT-4o가 생성한 176개 인용 중 19.9%가 fabricated였고, fabricated가 아닌 141개 중 54.6%에 bibliographic error가 있었다고 보고했다. 따라서 자동 DOI/Crossref/Semantic Scholar 검증 또는 최소한 source-fetch gate가 필요하다.

## 분석

### 1. Codex 표면: 플러그인은 배포 단위, 스킬은 워크플로 계약

OpenAI Codex 공식 문서는 plugin을 reusable workflow를 위해 skills, app integrations, MCP servers를 묶는 단위로 설명한다. plugin은 “무엇을 설치할 수 있는가”와 “어떤 구성요소를 포함하는가”를 나타내는 배포 표면이다. 반면 skill은 Codex에 task-specific capability를 부여하는 authoring format이다. `SKILL.md`는 name, description, instructions를 갖고, optional scripts, references, assets를 둘 수 있다. Codex는 skill 목록의 짧은 metadata만 먼저 보고, 필요할 때 전체 `SKILL.md`를 읽는 progressive disclosure 구조를 사용한다.

이 구조에서 연구 플러그인은 다음처럼 나누는 것이 좋다.

| 표면 | 맡길 내용 | 피해야 할 내용 |
| --- | --- | --- |
| `.codex-plugin/plugin.json` | 이름, 버전, 설명, bundled skills/MCP/app 경로, marketplace 표시 정보 | 연구 방법론, source policy, 긴 rubric |
| `skills/<name>/SKILL.md` | 트리거 조건, 연구 모드, 단계 계약, 산출물 계약 | 긴 논문 요약, 공급자별 세부 playbook |
| `references/` | source tier, quality gate, report standard, provider playbook | 매번 읽어야 하는 짧은 실행 규칙 |
| `assets/` | report template, evidence matrix template, checklist | 동적 결론이나 최신 source list |
| `.mcp.json` | 검색, fetch, scholarly index, docs provider 같은 retrieval tool 구성 | source 품질 판단이나 최종 결론 |
| custom agents | 독립 evidence lane 탐색, adversarial source review, workflow translation | 최종 결론 소유권, 무제한 재귀 delegation |
| scripts/hooks/evals | citation verifier, report linter, regression sample runner | 판단이 많이 필요한 source evaluation 자체 |

현재 로컬 `research` 플러그인은 이미 이 방향과 맞는다. manifest는 배포 정보를 담고, `ai-research-workflow` skill은 plan, retrieve, source-fetch, claim-ground, contradiction-check, synthesize, workflow-integrate, report-write, validate의 절차를 정의한다. 다음 개선은 “개념 추가”보다 “검증 자동화와 regression samples” 쪽이 우선이다.

### 2. RAG 계열: 검색은 시작점이지 충분조건이 아니다

Lewis et al.의 RAG 논문은 parametric memory만으로는 factual knowledge 접근, provenance, world knowledge update가 제한된다고 보고, pretrained model과 non-parametric memory를 결합하는 접근을 제시했다. 이는 연구 플러그인의 기본 전제다. 플러그인은 모델이 기억하는 사실을 그대로 믿지 말고, 외부 출처와 fetch 가능한 문서에 연결해야 한다.

하지만 RAG만으로 연구 품질이 끝나지 않는다. Self-RAG는 고정 개수 passage를 무차별적으로 넣는 방식이 불필요하거나 부적절한 retrieval을 만들 수 있다고 보고, 필요할 때 retrieval하고 retrieved passage와 generation을 reflection token으로 평가하는 방식을 제안했다. 연구 플러그인 관점에서는 “검색했는가?”보다 “검색이 필요한가?”, “찾은 문서가 관련 있는가?”, “답변이 문서에 의해 지지되는가?”를 별도 gate로 분리해야 한다.

RAGChecker는 RAG 시스템의 평가는 retrieval module과 generation module을 따로 진단해야 한다는 점을 강조한다. 따라서 research plugin의 validation은 단일 점수보다 다음을 나눠야 한다.

- retrieval recall: 필요한 canonical source를 찾았는가
- source precision: 가져온 문서가 실제 질문에 직접 관련 있는가
- grounding: 주요 claim이 fetch한 원문 또는 metadata에 의해 지지되는가
- synthesis: 출처 나열이 아니라 결론의 논리가 충분한가
- citation quality: citation이 claim 단위로 맞는가

### 3. ReAct/WebGPT 계열: research agent는 행동 로그와 citation trail이 필요하다

ReAct는 reasoning trace와 task-specific action을 interleaving해서 계획 추적, 예외 처리, 외부 source 접근을 결합한다. 연구 플러그인으로 번역하면 `retrieve -> inspect -> revise query -> compare -> synthesize` 루프가 필요하다. 단, 최종 보고서에 내부 reasoning을 노출하라는 의미는 아니다. 사용자에게는 근거, 한계, 결론의 논리를 보여주고, 내부 루프는 검증 가능한 tool result와 source trail로 남기는 쪽이 적합하다.

WebGPT는 browsing environment에서 search/navigation을 하며 답변을 작성하고, factual accuracy 평가를 쉽게 하기 위해 browsing 중 references를 수집하도록 했다. 이 논문은 research plugin의 product requirement를 분명히 한다. 최종 보고서에는 출처 목록만 있어서는 부족하고, 어떤 결론이 어떤 source에서 왔는지 추적 가능해야 한다.

### 4. CoVe/Self-RAG/ALCE: claim-grounding과 citation evaluation을 별도 단계로 둬야 한다

Chain-of-Verification은 초안 작성 후 verification questions를 계획하고 독립적으로 답한 뒤 최종 답변을 생성하는 절차가 hallucination을 줄인다고 보고했다. Research plugin에는 이 아이디어를 그대로 “초안 후 검증 질문 생성”으로 넣을 수 있다. 예를 들면:

- 이 결론이 의존하는 factual claim은 무엇인가?
- 각 claim에 canonical source가 있는가?
- 같은 주제의 최신 공식 문서나 후속 논문이 반대하는가?
- citation은 claim을 실제로 지지하는가?
- 연구 범위를 벗어난 과잉 일반화가 있는가?

ALCE는 LLM citation generation을 fluency, correctness, citation quality 차원에서 평가하고, ELI5 dataset에서 최고 모델도 citation support가 50% 부족했다고 보고했다. 이 결과는 “인라인 citation을 달았다”를 통과 기준으로 삼으면 안 된다는 경고다. 연구 플러그인의 report linter는 적어도 다음을 검사해야 한다.

- source URL이 실제로 열리는가
- source title/date/metadata가 맞는가
- citation이 붙은 문장이 source 내용과 일치하는가
- citation 없는 고위험 factual claim이 남아 있는가
- bibliography만 맞고 claim support가 없는 경우를 잡는가

2025년 JMIR Mental Health 실험도 같은 방향을 뒷받침한다. 특정 분야에서 LLM이 만든 citation은 fabricated reference와 DOI 오류가 많이 발생했다. 이 근거를 research plugin에 반영하면, “논문/학술 정보” 모드에서는 citation verifier를 강하게 적용하고, 검증 실패 citation은 보고서에서 제거하거나 “미확인”으로 낮춰야 한다.

### 5. STORM: 장문 리포트에는 perspective discovery와 outline stage가 필요하다

STORM은 Wikipedia식 장문 글쓰기를 위해 pre-writing stage를 명시한다. diverse perspectives를 찾고, grounded source 기반 질문을 만들며, 수집 정보를 outline으로 정리한 뒤 작성한다. Research plugin에는 이것을 `lane-select`와 `report planning`으로 반영할 수 있다.

실무적으로는 모든 질문을 STORM식 장문 절차로 처리하면 과하다. 하지만 다음 조건에서는 STORM식 구조가 유용하다.

- 사용자가 “개념들”, “학술 정보”, “기반으로 재탐색”처럼 넓은 seed research를 요청한 경우
- 비교 대상이나 evidence lane이 여럿인 경우
- 최종 산출물이 리포트, 전략 메모, skill/plugin 설계로 이어지는 경우
- 반론, 실패 사례, source bias를 명시해야 하는 경우

### 6. Agent/workflow 설계: 단순한 workflow부터 시작하고 subagent는 evidence lane에만

Anthropic의 “Building effective agents”는 workflows와 agents를 구분한다. workflows는 predefined code path로 LLM과 tools를 orchestration하고, agents는 LLM이 자신의 process와 tool usage를 동적으로 지휘한다. 또한 가장 단순한 solution에서 시작하고, complexity는 필요할 때 올리라고 권한다.

OpenAI Agents SDK 문서도 manager-style orchestration과 handoffs를 구분한다. manager가 final answer를 소유하고 specialist agents를 tool처럼 호출하는 방식은 연구 플러그인에 잘 맞는다. 최종 결론과 confidence는 coordinator가 유지하고, paper scout, official guidance scout, source evaluator 같은 lane agent는 bounded evidence만 반환해야 한다.

Codex subagent 공식 문서는 복잡하고 병렬적인 task에 subagent가 유용하지만, explicit ask일 때만 spawn되고 토큰 비용이 더 든다고 설명한다. 따라서 research plugin의 기본값은 single-agent staged workflow이고, subagent는 다음 조건에서만 권장한다.

- 독립 evidence lane이 2개 이상이고 서로 결과를 기다릴 필요가 없을 때
- source-quality review를 본 조사와 분리해야 할 때
- user가 deep/parallel/multi-agent research를 명시했을 때
- 각 subagent의 output contract가 “sources, gaps, decision impact”처럼 좁을 때

### 7. MCP와 retrieval provider: search/fetch 계약을 명확히 해야 한다

OpenAI deep research 문서는 deep research model이 web search, remote MCP, file search 같은 data source를 필요로 하고, remote MCP의 경우 search와 fetch read-only interface가 필요하다고 설명한다. 별도 MCP 문서도 ChatGPT deep research/company knowledge/API deep research에 맞추려면 `search`와 `fetch`를 구현해야 한다고 설명한다.

Research plugin에 이 원칙을 적용하면, MCP는 “답변 생성기”가 아니라 retrieval/fetch provider다. 좋은 MCP integration의 기준은 다음이다.

- search result에 `id`, `title`, `url`, metadata가 있다.
- fetch가 full text 또는 충분한 excerpt와 canonical URL을 돌려준다.
- result와 document ID가 stable하다.
- provider summary만 최종 evidence로 쓰지 않는다.
- private data MCP와 public web search를 섞을 때 prompt injection/exfiltration 위험을 줄이기 위해 단계 분리를 한다.

OpenAI deep research 문서는 MCP와 web search를 함께 사용할 때 prompt injection과 exfiltration 위험이 있다고 경고하고, trusted MCP, tool-call logging, public research와 private MCP 단계를 분리하는 mitigation을 제안한다. 연구 플러그인에도 이 정책은 들어가야 한다.

## 비교 또는 판단 프레임

| 설계 선택지 | 적합한 경우 | 부적합한 경우 | 권장 |
| --- | --- | --- | --- |
| 단일 긴 프롬프트 | 개인용 임시 실험, 빠른 프로토타입 | 반복 연구, 팀 공유, 회귀 검증 필요 | 비권장 |
| 하나의 `SKILL.md` 중심 | 초기 MVP, trigger와 단계 계약 검증 | source policy와 rubric이 길어질 때 | 초기 권장 |
| `SKILL.md` + `references/` | source tier, quality gate, report standard가 필요한 리서치 | very narrow quick-fact only | 강력 권장 |
| MCP/search provider 추가 | 최신 자료, 외부 문서, 논문/공식 문서 fetch가 필요 | provider가 search summary만 제공하고 원문 fetch가 약할 때 | 조건부 권장 |
| custom subagents | 병렬 evidence lane, adversarial source review, workflow translation | 모든 요청을 deep research로 처리할 때 | 조건부 권장 |
| scripts/hooks/evals | citation verification, report linting, regression samples | 판단 자체를 완전 자동화하려 할 때 | 강력 권장 |

## 재탐색 후보

다음 주제들은 플러그인의 다음 버전을 정할 때 추가로 파고들 가치가 있다.

1. `citation verification pipeline for LLM research reports Crossref Semantic Scholar DOI validation`
2. `RAG evaluation claim grounding citation support benchmark ALCE RAGChecker`
3. `agentic deep research search reasoning agents benchmark 2025 2026`
4. `prompt injection risks retrieval augmented generation MCP web search exfiltration`
5. `multi-agent research workflow source evaluator paper scout official guidance scout`
6. `OpenAI Codex plugin skills MCP subagents official docs`
7. `AGENTS.md impact AI coding agents runtime token consumption`
8. `STORM multi perspective question asking long form grounded article generation`

## 리스크와 한계

- Codex plugin/skills/subagents 문서는 2026년 5월 2일 기준 공식 문서를 확인했다. Codex는 릴리스가 빠르므로 manifest schema, marketplace 정책, skill metadata는 구현 전 다시 확인해야 한다.
- 학술 논문 중 일부는 arXiv preprint다. RAG, ReAct, ALCE, WebGPT, STORM처럼 널리 참조되는 연구도 있지만, 연구 플러그인 설계에 그대로 적용할 때는 사용자의 task 분포와 실제 실패 사례로 검증해야 한다.
- Citation hallucination 수치는 domain, model, prompt, tool access에 따라 달라진다. JMIR 결과는 mental health literature review 조건의 실험이므로 모든 학술 영역에 같은 비율로 일반화하면 안 된다. 다만 “citation verification이 필요하다”는 방향성은 강하게 지지한다.
- Deep research model/API 문서의 `o3-deep-research`, `o4-mini-deep-research`는 OpenAI API product surface에 대한 내용이다. Codex plugin 내부 workflow가 반드시 이 모델을 호출해야 한다는 뜻은 아니다.
- Subagent는 비용과 latency를 늘린다. 연구 품질 향상보다 orchestration overhead가 커질 수 있으므로, explicit deep/parallel request와 독립 lane 조건이 없으면 기본값으로 쓰지 않는 편이 낫다.

## 실행 권고

1. `research` 플러그인의 핵심 skill은 지금처럼 staged research workflow로 유지한다.  
   대상 surface: `skills/ai-research-workflow/SKILL.md`  
   근거: Codex skills는 reusable workflow authoring format이고 plugin은 배포 단위라는 공식 설명.  
   비용: skill instructions가 길어질수록 유지보수 비용 증가.  
   검증: quick-fact, official-guidance-review, literature-scan, workflow-update-review, deep-research 샘플을 각각 1개씩 돌려 보고 산출물 품질을 비교한다.  
   중단 조건: 대부분 요청에서 과한 절차 때문에 응답 시간이 크게 늘면 mode routing을 더 보수적으로 조정한다.

2. source policy, quality gates, report standards는 `references/`에 계속 둔다.  
   대상 surface: `references/source-tiers.md`, `references/quality-gates.md`, `references/report-substance-standards.md`  
   근거: progressive disclosure 구조상 긴 rubric은 항상 로드하지 않는 편이 context 효율적이다.  
   비용: reference 간 중복과 drift 관리 필요.  
   검증: 보고서가 source list dump가 아니라 결론, 근거, 한계, 실행 권고를 포함하는지 lint/checklist로 확인한다.  
   중단 조건: skill이 reference를 너무 자주 과다 로드하면 trigger 조건과 “read only when” 규칙을 더 좁힌다.

3. citation/source verifier를 scripts 또는 hook 후보로 추가한다.  
   대상 surface: `scripts/` 또는 validation hook  
   근거: ALCE, RAGChecker, JMIR citation fabrication 결과가 citation support와 bibliographic accuracy를 별도 문제로 보여준다.  
   비용: Crossref/Semantic Scholar/OpenAlex API 제한, 네트워크 의존성, false negative 처리 필요.  
   검증: report Markdown에서 URL live check, DOI/title match, cited claim 근처 source presence를 검사한다.  
   중단 조건: verifier가 canonical source를 과도하게 실패 처리하거나 offline 환경에서 workflow를 막으면 warning-only mode로 낮춘다.

4. MCP는 provider summary가 아니라 search/fetch 가능한 source access에 집중한다.  
   대상 surface: `.mcp.json`과 provider playbooks  
   근거: deep research MCP 문서는 search/fetch read-only interface를 요구하고, OpenAI deep research 문서는 supported tools와 MCP safety risks를 명시한다.  
   비용: provider별 auth, quota, schema drift.  
   검증: 각 provider가 query -> result metadata -> fetch text/url 경로를 제공하는지 sample test를 만든다.  
   중단 조건: 원문 fetch 없이 요약만 제공하는 provider는 discovery-only로 downgrade한다.

5. custom research agents는 “나중에” 추가하되 역할을 좁힌다.  
   대상 surface: `.codex/agents/*.toml` 또는 plugin-bundled agent config가 지원되는 경우 해당 표면  
   근거: Codex subagents와 OpenAI/Anthropic orchestration guidance 모두 specialist 역할과 coordinator ownership을 권한다.  
   비용: token, latency, coordination overhead.  
   검증: official guidance, papers, source evaluation, workflow translation 네 lane을 병렬로 돌렸을 때 single-agent 대비 품질 개선이 있는지 비교한다.  
   중단 조건: subagent 결과를 parent가 재검증하느라 총 시간이 늘고 품질 개선이 작으면 기본 비활성화한다.

## 참고 출처

### Codex 및 OpenAI 공식 문서

- OpenAI Developers, “Plugins - Codex”: https://developers.openai.com/codex/plugins
- OpenAI Developers, “Build plugins - Codex”: https://developers.openai.com/codex/plugins/build
- OpenAI Developers, “Agent Skills - Codex”: https://developers.openai.com/codex/skills
- OpenAI Developers, “Subagents - Codex”: https://developers.openai.com/codex/subagents
- OpenAI Developers, “Best practices - Codex”: https://developers.openai.com/codex/learn/best-practices
- OpenAI Developers, “Deep research - OpenAI API”: https://developers.openai.com/api/docs/guides/deep-research
- OpenAI Developers, “Building MCP servers for ChatGPT Apps and API integrations”: https://developers.openai.com/api/docs/mcp
- OpenAI Developers, “Evaluate agent workflows”: https://developers.openai.com/api/docs/guides/agent-evals
- OpenAI Developers, “Evaluation best practices”: https://developers.openai.com/api/docs/guides/evaluation-best-practices
- OpenAI Agents SDK, “Agent orchestration”: https://openai.github.io/openai-agents-python/multi_agent/
- OpenAI Agents SDK, “Agents”: https://openai.github.io/openai-agents-python/agents/

### 학술 및 연구 근거

- Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks”: https://arxiv.org/abs/2005.11401
- Yao et al., “ReAct: Synergizing Reasoning and Acting in Language Models”: https://arxiv.org/abs/2210.03629
- Nakano et al., “WebGPT: Browser-assisted question-answering with human feedback”: https://arxiv.org/abs/2112.09332
- Asai et al., “Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection”: https://arxiv.org/abs/2310.11511
- Dhuliawala et al., “Chain-of-Verification Reduces Hallucination in Large Language Models”: https://arxiv.org/abs/2309.11495
- Gao et al., “Enabling Large Language Models to Generate Text with Citations”: https://arxiv.org/abs/2305.14627
- Shao et al., “Assisting in Writing Wikipedia-like Articles From Scratch with Large Language Models”: https://arxiv.org/abs/2402.14207
- Ru et al., “RAGChecker: A Fine-grained Framework for Diagnosing Retrieval-Augmented Generation”: https://arxiv.org/abs/2408.08067
- Lulla et al., “On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents”: https://arxiv.org/abs/2601.20404
- JMIR Mental Health, “Influence of Topic Familiarity and Prompt Specificity on Citation Fabrication in Mental Health Research Using Large Language Models”: https://mental.jmir.org/2025/1/e80371/
- Anthropic Engineering, “Building effective agents”: https://www.anthropic.com/engineering/building-effective-agents
