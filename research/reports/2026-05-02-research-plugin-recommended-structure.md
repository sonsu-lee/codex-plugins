# Research 플러그인 권장 구조 및 개선 리서치 보고서

작성일: 2026-05-02
주제: Codex marketplace용 범용 research plugin의 권장 구조와 개선 우선순위
리서치 모드: deep-research / workflow-update-review
확신도: 중간-높음
검색 기준일: 2026-05-02

## 핵심 답변

`research` 플러그인은 “잘 검색하는 프롬프트”가 아니라, 재사용 가능한 연구 절차를 `plugin manifest -> skill -> references/assets -> retrieval MCP -> optional subagents -> scripts/hooks/evals`로 분리한 evidence-first workflow로 유지하는 것이 맞다. OpenAI Codex 문서는 플러그인이 skills, apps, MCP servers를 묶는 배포 단위이고, skill이 재사용 워크플로우의 authoring format이라고 설명한다([OpenAI Codex Plugins](https://developers.openai.com/codex/plugins), [Agent Skills](https://developers.openai.com/codex/skills)). 또한 Codex skills는 progressive disclosure로 필요한 때만 `SKILL.md` 전체를 읽기 때문에, 긴 source policy와 품질 rubric은 `references/`로 빼는 현재 구조가 적절하다([Agent Skills](https://developers.openai.com/codex/skills)).

가장 중요한 개선은 새 검색 provider 추가보다 검증 자동화다. RAG, ReAct, WebGPT, Self-RAG, Chain-of-Verification, ALCE, RAGChecker, STORM의 공통 메시지는 retrieval, source fetch, claim grounding, contradiction check, synthesis, report adequacy, regression evaluation을 분리해야 한다는 것이다([RAG](https://arxiv.org/abs/2005.11401), [ReAct](https://arxiv.org/abs/2210.03629), [WebGPT](https://arxiv.org/abs/2112.09332), [Self-RAG](https://arxiv.org/abs/2310.11511), [CoVe](https://arxiv.org/abs/2309.11495), [ALCE](https://arxiv.org/abs/2305.14627), [RAGChecker](https://arxiv.org/abs/2408.08067), [STORM](https://arxiv.org/abs/2402.14207)). 현재 플러그인은 이 방향을 이미 갖추고 있으므로, 다음 단계는 citation/source verifier를 확장하고, mode별 regression sample과 report lint를 추가하며, MCP provider를 `search/fetch` 계약 기준으로 평가하는 것이다([OpenAI MCP](https://developers.openai.com/api/docs/mcp)).

## 주요 결론

- 현재 `plugins/research` 구조는 공식 Codex 구조와 잘 맞는다. `plugin.json`은 배포/marketplace 정보, `SKILL.md`는 트리거와 단계 계약, `references/`는 긴 정책, `assets/`는 템플릿, `.mcp.json`은 retrieval tool 설정, `scripts/verify_sources.py`는 deterministic 검증을 맡는 분리가 타당하다.
- 범용 research plugin의 핵심 품질 기준은 “출처를 붙였는가”가 아니라 “주요 claim이 원문 또는 canonical metadata에 의해 지지되는가”다. ALCE는 citation quality를 별도 평가 축으로 두고, 최고 모델도 ELI5에서 complete citation support가 50% 부족했다고 보고했다([ALCE](https://arxiv.org/abs/2305.14627)).
- Citation hallucination은 실무 리스크다. 2025년 JMIR Mental Health 실험은 GPT-4o가 생성한 176개 citation 중 35개(19.9%)가 fabricated였고, fabricated가 아닌 141개 중 64개(45.4%)도 오류를 포함했다고 보고했다([JMIR Mental Health](https://mental.jmir.org/2025/1/e80371/)). 따라서 scholarly/literature 모드에서는 DOI/arXiv/OpenReview/PubMed/URL 검증을 기본으로 둬야 한다.
- Subagent는 기본 구조가 아니라 선택적 확장이어야 한다. Codex 문서는 subagent가 명시 요청 때만 spawn되고 token을 더 쓴다고 설명하며, Anthropic도 단순한 composable pattern에서 시작하고 complexity는 필요할 때만 올리라고 권한다([Codex Subagents](https://developers.openai.com/codex/subagents), [Anthropic Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)).
- MCP는 답변 생성기가 아니라 retrieval/fetch surface로 취급해야 한다. OpenAI deep research MCP 문서는 `search`와 `fetch` read-only tools를 요구하고, deep research 문서는 web search, file search, remote MCP를 지원하되 function calling 같은 일반 tool은 지원하지 않는다고 설명한다([OpenAI MCP](https://developers.openai.com/api/docs/mcp), [OpenAI Deep Research](https://developers.openai.com/api/docs/guides/deep-research)).
- 모델은 기본적으로 고정하지 않고 parent session에서 상속하는 편이 낫다. Codex custom agent 문서는 `model`과 `model_reasoning_effort`가 optional이며 생략 시 parent session에서 상속된다고 설명한다. 반면 role별 `model_reasoning_effort`는 현재처럼 고정하는 편이 재현성과 비용 통제에 유리하다([Codex Subagents](https://developers.openai.com/codex/subagents)).

## 분석

### 1. 권장 파일 구조

범용 research plugin은 다음 구조를 권장한다.

```text
plugins/research/
  .codex-plugin/
    plugin.json
  .mcp.json
  skills/
    ai-research-workflow/
      SKILL.md
      references/
        source-tiers.md
        research-workflow-architecture.md
        research-concepts.md
        prompt-accuracy-playbook.md
        citation-source-verification.md
        verification-gates.md
        quality-gates.md
        report-substance-standards.md
        report-writing-style.md
        workflow-integration.md
        agent-orchestration.md
        exa-playbook.md
        ai-research-domains.md
      scripts/
        verify_sources.py
        test_verify_sources.py
      assets/
        research-report-template.md
        evidence-matrix-template.md
  assets/
    marketplace screenshots or examples
```

현재 repo는 이 구조에 거의 도달해 있다. 다만 `assets/`가 skill 내부가 아니라 plugin root에 있고, `scripts/`는 skill 내부에 있다. 둘 다 동작상 문제는 없지만 marketplace 사용자가 plugin을 훑을 때 “skill에 필요한 템플릿/스크립트”와 “plugin 소개용 자산”의 의미가 섞일 수 있다. OpenAI skill 문서가 skill directory 아래에 optional `scripts/`, `references/`, `assets/`를 둘 수 있다고 설명하므로, 장기적으로는 report template과 evidence matrix template을 skill-local assets로 옮기거나 `SKILL.md`에서 root assets 경로를 명시하는 편이 낫다([Agent Skills](https://developers.openai.com/codex/skills)).

표면별 책임은 다음처럼 유지한다.

| Surface | 맡길 내용 | 개선 방향 |
| --- | --- | --- |
| `.codex-plugin/plugin.json` | marketplace 표시, 버전, bundled skills/MCP paths, default prompts | research 방법론을 넣지 말고 설치/표시 품질만 관리 |
| `.mcp.json` | retrieval provider 설정 | provider를 answer source가 아니라 discovery/fetch tool로 표시 |
| `SKILL.md` | trigger, mode routing, stage contract, output contract | mode routing이 과한 deep research로 흐르지 않게 조건을 더 선명화 |
| `references/` | source tiers, gates, provider playbooks, report standards | 긴 rubric을 progressive disclosure로만 로드 |
| `assets/` | report/evidence templates, examples | marketplace image와 workflow template을 분리 |
| `scripts/` | deterministic checks, source extraction, verifier tests | URL/identifier/metadata 검증을 단계적으로 확장 |
| custom agents | independent evidence lanes | explicit deep/parallel 요청에서만 사용 |
| evals/hooks | regression and report lint | mode별 샘플 보고서를 fixture로 관리 |

### 2. 현재 플러그인 평가

현재 `plugins/research/skills/ai-research-workflow/SKILL.md`는 좋은 출발점이다. `quick-fact`, `official-guidance-review`, `literature-scan`, `comparison`, `workflow-update-review`, `deep-research`를 분리하고, `plan -> lane-select -> retrieve -> source-fetch -> claim-ground -> contradiction-check -> synthesize -> workflow-integrate -> report-write -> validate`의 단계를 명시한다. 이는 ReAct의 reasoning/action interleaving, WebGPT의 reference trail, Self-RAG의 retrieval 필요성 판단, CoVe의 검증 질문, STORM의 pre-writing perspective discovery를 실무 workflow로 번역한 형태다.

가장 강한 부분은 “provider는 authority가 아니다”라는 운영 계약이다. 이 규칙은 연구 플러그인의 품질을 결정한다. 검색 결과, Exa 요약, social post, blog paraphrase는 discovery lead일 뿐이며, 최종 근거는 원문 페이지, 논문, 공식 문서, repository, API response여야 한다.

보완할 부분은 adoption validation이다. 지금은 report quality gate와 source verifier가 있지만, “이 skill 변경이 실제로 더 나은가”를 보는 작은 regression suite가 아직 약하다. OpenAI evaluation best practices 문서는 workflow, single-agent, multi-agent 구조의 nondeterminism을 분리해 평가하라고 설명하고, multi-agent architecture는 eval이 이끌어야 하며 처음부터 multi-agent로 시작하면 불필요한 복잡성이 생길 수 있다고 경고한다([OpenAI Evaluation Best Practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)). Research plugin도 prompt/rubric을 바꿀 때마다 최소 5개 모드 샘플을 다시 돌리는 쪽이 맞다.

### 3. 근거 기반 설계 원칙

첫째, retrieval은 필요조건이지 충분조건이 아니다. RAG 논문은 parametric memory만으로는 지식 접근, provenance, world knowledge update가 제한된다고 설명한다([RAG](https://arxiv.org/abs/2005.11401)). 그러나 Self-RAG는 고정 개수 passage를 무차별적으로 넣는 RAG가 오히려 유연성을 떨어뜨리거나 부적절한 generation을 만들 수 있다고 지적한다([Self-RAG](https://arxiv.org/abs/2310.11511)). 따라서 research plugin은 “항상 많이 검색”이 아니라 mode별로 retrieval 필요성과 source relevance를 판단해야 한다.

둘째, research workflow는 원문 inspection과 claim grounding을 별도 단계로 가져야 한다. WebGPT는 long-form QA에서 browsing 중 references를 수집하게 만들어 factual accuracy 평가를 쉽게 했다([WebGPT](https://arxiv.org/abs/2112.09332)). ReAct는 reasoning trace와 action을 interleaving해 외부 source에서 추가 정보를 얻는 구조를 제안했다([ReAct](https://arxiv.org/abs/2210.03629)). CoVe는 초안, verification questions, independent answers, final verified response의 절차를 통해 hallucination을 줄이는 방법을 제시했다([CoVe](https://arxiv.org/abs/2309.11495)). 플러그인 관점에서는 `source-fetch`, `claim-ground`, `contradiction-check`가 이 기능을 담당한다.

셋째, citation quality는 별도 평가 대상이다. ALCE는 fluency, correctness, citation quality를 분리했고, RAGChecker는 retrieval module과 generation module을 각각 진단하는 fine-grained framework를 제안했다([ALCE](https://arxiv.org/abs/2305.14627), [RAGChecker](https://arxiv.org/abs/2408.08067)). 이 둘을 합치면 research plugin의 validation은 `URL/identifier existence`, `metadata match`, `nearby claim support`, `retrieval coverage`, `synthesis adequacy`로 분리해야 한다.

넷째, 장문 보고서는 outline 이전에 perspective discovery가 필요하다. STORM은 grounded long-form article 작성에서 pre-writing stage를 연구 대상으로 삼고, 다양한 관점 발견, source-grounded question asking, outline curation을 명시한다([STORM](https://arxiv.org/abs/2402.14207)). Research plugin의 `lane-select`는 이 역할을 해야 한다. 특히 workflow architecture, literature scan, comparison, deep research에서는 “공식 문서 lane”, “학술/benchmark lane”, “implementation reality lane”, “security/risk lane”, “workflow translation lane”을 먼저 정한 뒤 조사해야 한다.

다섯째, agent orchestration은 기본값이 아니라 조건부다. Anthropic의 “Building effective agents”는 workflows를 predefined code path, agents를 model-driven process/tool usage로 구분하고, 가장 단순한 solution에서 시작하라고 권한다([Anthropic Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)). OpenAI Agents SDK도 manager agent가 final answer를 소유하고 specialist agents를 bounded subtask로 호출하는 “agents as tools” 패턴을 설명한다([OpenAI Agents SDK Orchestration](https://openai.github.io/openai-agents-python/multi_agent/)). Research plugin에 적용하면 final synthesis는 coordinator가 맡고, paper scout나 source evaluator는 evidence, gaps, decision impact만 반환해야 한다.

### 4. 모델과 effort 고정 판단

결론은 `model`은 기본 고정하지 않고, `model_reasoning_effort`만 역할별로 고정하는 것이다. Codex custom agent 문서는 project-scoped agent TOML에서 `model`, `model_reasoning_effort`, `sandbox_mode` 같은 config key를 넣을 수 있고, optional field를 생략하면 parent session에서 상속된다고 설명한다([Codex Subagents](https://developers.openai.com/codex/subagents)). OpenAI 모델 목록은 2026-05-02 기준 `gpt-5.5`를 복잡한 reasoning/coding의 시작점으로 제시하고, 비용/지연이 중요하면 더 작은 variant를 쓰라고 설명한다([OpenAI Models](https://developers.openai.com/api/docs/models)). 이 권장은 시간이 지나면 바뀌므로 marketplace plugin의 agent 파일에 특정 model ID를 박아두면 빠르게 낡을 수 있다.

반면 reasoning effort는 역할의 성격과 더 직접적으로 연결된다. `research_head`, `source_evaluator`, `workflow_translator`는 synthesis, contradiction, rollback 판단을 하므로 `high`가 적절하다. `paper_scout`, `official_guidance_scout`는 bounded retrieval lane이므로 `medium`이 비용과 품질의 균형점이다. `xhigh`는 결과 우선 모드에서 매력적이지만, 모든 parent model이 지원한다고 가정하기 어렵고 비용/latency가 커진다. 따라서 기본 config에는 넣지 않고, 특정 hard run에서 parent session이나 명시 요청으로 올리는 쪽이 안전하다.

### 5. 우선순위별 개선안

| 우선순위 | 개선 | 대상 surface | 근거 | 비용/리스크 | 검증 신호 | 롤백 조건 |
| --- | --- | --- | --- | --- | --- | --- |
| P0 | `verify_sources.py`를 URL/DOI/arXiv/OpenReview/PubMed metadata 검증까지 확장 | `scripts/verify_sources.py` | ALCE/JMIR 근거상 citation existence와 metadata 오류가 주요 리스크 | provider rate limit, false negative | fixture에서 valid/fake/mismatch citation 분리 성공 | offline 환경에서 workflow를 자주 막으면 warning-only |
| P0 | mode별 regression sample 추가 | `research/reports/fixtures/` 또는 `scripts/` | OpenAI eval guidance: workflow 단계별 nondeterminism 평가 필요 | fixture 유지보수 | quick-fact, official, literature, comparison, workflow-update, deep sample 통과 | 비용 대비 signal이 약하면 sample 수 축소 |
| P1 | report linter 추가 | `scripts/lint_report.py` | source list dump, unsupported claim, internal table 노출 방지 | LLM-free lint는 semantic support 한계 | 필수 섹션, citation presence, forbidden internal headings 검사 | false positive가 많으면 advisory로 낮춤 |
| P1 | MCP provider playbook에 `discovery-only`와 `canonical-support` label 추가 | `references/exa-playbook.md`, `.mcp.json` notes | MCP/search provider summary를 final evidence로 쓰면 안 됨 | provider별 문서 drift | 보고서가 original source를 cite하고 provider를 cite하지 않음 | provider가 fetch를 제공하지 않으면 discovery-only 유지 |
| P1 | skill-local assets 경로 정리 | `skills/ai-research-workflow/assets/` 또는 `SKILL.md` 경로 명시 | Codex skill 문서의 optional assets 구조와 일치 | 파일 이동으로 기존 참조 깨질 수 있음 | skill 실행 시 template 경로 혼동 없음 | marketplace packaging에서 root asset이 더 편하면 현 구조 유지 |
| P2 | custom research agents를 plugin 안에서 명시적으로 문서화 | `references/agent-orchestration.md`, future `.codex/agents/` | Codex subagents는 explicit ask이고 비용 증가 | agent fan-out 남용 | deep/parallel 요청에서만 사용됨 | 일반 요청에서 latency 증가하면 비활성화 |
| P2 | private/public source safety gate 추가 | `references/verification-gates.md`, `SKILL.md` | OpenAI deep research 문서가 prompt injection/exfiltration risk와 staged workflow를 권고 | 절차 증가 | private MCP와 public web이 분리됨 | private data를 다루지 않는 marketplace MVP에서는 문서화만 |

### 6. 추천 실행 순서

1. `verify_sources.py`를 확장한다.
   대상: `plugins/research/skills/ai-research-workflow/scripts/verify_sources.py`
   변경: 현재 URL/DOI/arXiv/OpenReview/PubMed extraction과 Crossref 기반 DOI 확인의 MVP를 유지하되, DataCite/OpenAlex/Semantic Scholar fallback은 optional adapter로 분리한다. 처음에는 URL reachability, identifier existence, title/year/author metadata mismatch만 hard/warning으로 나누고, claim-source support는 `needs_review` warning으로 둔다.
   검증: valid DOI, fake DOI, DOI/title mismatch, arXiv ID, OpenReview URL, PubMed URL, localhost URL block fixture를 추가한다.
   롤백: 네트워크 실패가 보고서 생성을 막으면 `--offline`과 `--warning-only`를 기본으로 되돌린다.

2. mode별 regression suite를 만든다.
   대상: `scripts/` 또는 `research/evals/`
   변경: 최소 6개 프롬프트를 fixture로 둔다. `quick-fact`, `official-guidance-review`, `literature-scan`, `comparison`, `workflow-update-review`, `deep-research` 각각 하나씩 두고, 예상 산출물은 “필수 섹션, source tier, canonical source, confidence, validation/rollback 포함 여부”로 검사한다.
   검증: skill/reference 변경 후 regression을 실행해 report shape와 source behavior가 유지되는지 확인한다.
   롤백: fixture가 지나치게 brittle하면 hard exact match 대신 pass/fail rubric으로 완화한다.

3. `SKILL.md`의 mode routing을 조금 더 보수적으로 만든다.
   대상: `plugins/research/skills/ai-research-workflow/SKILL.md`
   변경: broad architecture/report 요청은 deep research로 두되, 단일 공식 문서 확인이나 좁은 API fact는 quick/official로 제한한다. `deep-research`의 기본 산출물 비용을 명시하고, 사용자가 chat-only를 원하면 보고서 생성을 생략하는 조건을 더 분명히 한다.
   검증: 간단한 질문이 긴 보고서로 과잉 처리되지 않는지 regression sample로 확인한다.
   롤백: deep research 품질이 낮아지면 `workflow-update-review`와 `deep-research` 경계를 다시 넓힌다.

4. provider policy를 source-quality policy와 분리해서 더 강하게 적는다.
   대상: `references/exa-playbook.md`, `references/source-tiers.md`, `.mcp.json` 설명
   변경: Exa나 web search는 candidate discovery, official docs/arXiv/OpenReview/repo/API response는 final support로 구분한다. `fetch unavailable -> discovery-only` label을 둔다.
   검증: 보고서 참고 출처에 search provider 페이지가 final support로 들어가지 않는지 확인한다.
   롤백: 특정 provider가 canonical source 그 자체인 경우 예외 규칙을 추가한다.

5. marketplace polish는 기능 검증 뒤에 한다.
   대상: `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`
   변경: `homepage`/`repository`가 현재 로컬 경로와 다르므로 배포 전 정리한다. `defaultPrompt`는 “free-first original-source research”, “verify citations in a report”, “turn evidence into workflow recommendations”처럼 실제 value proposition을 더 직접적으로 보여주는 문장으로 바꾼다. screenshots는 리포트 예시나 source verification output을 추가한다.
   검증: fresh Codex thread에서 marketplace install 후 skill 목록, MCP availability, report writing, verifier command가 정상 동작하는지 확인한다.
   롤백: marketplace metadata 변경은 기능에 영향이 없으므로 표시 품질 문제가 있으면 이전 copy로 되돌린다.

## 리스크와 한계

- OpenAI Codex plugin/skill/subagent 문서는 제품 표면이 빠르게 바뀔 수 있다. 이 보고서는 2026-05-02에 확인한 공식 문서를 기준으로 한다.
- 학술 근거는 research plugin 설계에 직접적인 제품 실험이 아니라 패턴 근거로 사용했다. RAG, ReAct, WebGPT, Self-RAG, CoVe, ALCE, RAGChecker, STORM은 각각 retrieval, action loop, citation trail, self-critique, verification, citation evaluation, RAG diagnostics, outline/perspective discovery에 대한 근거를 제공하지만, 이 플러그인의 실제 효과는 local regression으로 확인해야 한다.
- Citation support 자동 판정은 어려운 문제다. Existence/metadata 검증은 deterministic하게 시작할 수 있지만, cited claim이 source text에 의해 정말 지지되는지는 full text 접근성, 저작권, 분야별 표현 차이 때문에 처음부터 hard gate로 두면 false negative가 생긴다.
- Subagent를 많이 쓰면 token/latency가 늘고 synthesis ownership이 흐려진다. 명시적 deep/parallel 요청과 독립 evidence lane이 있을 때만 쓰는 보수적 정책을 유지해야 한다.
- MCP provider가 원문 fetch 없이 summary만 제공하면 최종 evidence로 쓰기 어렵다. 이런 provider는 discovery-only로 표시해야 한다.

## 실행 권고

1. P0는 `verify_sources.py` 확장과 regression sample이다. 이 둘이 있어야 플러그인 개선이 실제 품질 향상인지 확인할 수 있다.
2. P1은 report linter와 provider classification이다. citation이 존재해도 claim support가 약한 보고서를 줄이는 데 직접적이다.
3. P2는 subagent와 marketplace polish다. 기능 품질이 안정된 뒤에 “official guidance scout / paper scout / source evaluator / workflow translator” 같은 역할을 명시적으로 노출하는 편이 낫다.
4. 다음 변경을 적용할 때는 `quick-fact`, `official-guidance-review`, `literature-scan`, `workflow-update-review`, `deep-research` 샘플을 최소 1개씩 실행하고, canonical source citation과 validation/rollback 포함 여부를 확인한다.

## 참고 출처

### 내용 근거

- OpenAI Developers, “Plugins - Codex”: https://developers.openai.com/codex/plugins
- OpenAI Developers, “Agent Skills - Codex”: https://developers.openai.com/codex/skills
- OpenAI Developers, “Subagents - Codex”: https://developers.openai.com/codex/subagents
- OpenAI API, “Deep research”: https://developers.openai.com/api/docs/guides/deep-research
- OpenAI API, “Building MCP servers for ChatGPT Apps and API integrations”: https://developers.openai.com/api/docs/mcp
- OpenAI Agents SDK, “Agent orchestration”: https://openai.github.io/openai-agents-python/multi_agent/
- OpenAI API, “Evaluation best practices”: https://developers.openai.com/api/docs/guides/evaluation-best-practices
- Anthropic Engineering, “Building effective agents”: https://www.anthropic.com/engineering/building-effective-agents
- Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks”: https://arxiv.org/abs/2005.11401
- Yao et al., “ReAct: Synergizing Reasoning and Acting in Language Models”: https://arxiv.org/abs/2210.03629
- Nakano et al., “WebGPT: Browser-assisted question-answering with human feedback”: https://arxiv.org/abs/2112.09332
- Asai et al., “Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection”: https://arxiv.org/abs/2310.11511
- Dhuliawala et al., “Chain-of-Verification Reduces Hallucination in Large Language Models”: https://arxiv.org/abs/2309.11495
- Gao et al., “Enabling Large Language Models to Generate Text with Citations”: https://arxiv.org/abs/2305.14627
- Ru et al., “RAGChecker: A Fine-grained Framework for Diagnosing Retrieval-Augmented Generation”: https://arxiv.org/abs/2408.08067
- Shao et al., “Assisting in Writing Wikipedia-like Articles From Scratch with Large Language Models”: https://arxiv.org/abs/2402.14207
- JMIR Mental Health, “Influence of Topic Familiarity and Prompt Specificity on Citation Fabrication in Mental Health Research Using Large Language Models”: https://mental.jmir.org/2025/1/e80371/

### 형식 참고

- Local skill reference, `plugins/research/skills/ai-research-workflow/references/research-workflow-architecture.md`
- Local skill reference, `plugins/research/skills/ai-research-workflow/references/report-substance-standards.md`
- Local skill reference, `plugins/research/skills/ai-research-workflow/references/quality-gates.md`
