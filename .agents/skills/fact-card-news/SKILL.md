---
name: fact-card-news
description: >-
  백그라운드에서 가짜뉴스와 과장 정보를 필터링(1차 출처 교차검증)하고, 카드 표면에는 검증된 진짜 뉴스 스토리만
  [토스 피드 × 14F 스타일] (스타일 A: 여백 50% + 초대형 볼드 타이포 + 네온 형광펜 하이라이트 + 다크/화이트 반전)의
  6장 고해상도 카드뉴스(1080x1350 PNG + preview.html + manuscript.md)로 자동 생성하는 스킬. 향후 쇼츠/블로그 OSMU 확장의 원천 데이터를 겸한다.
---

# Verified Real News Card Generator (`fact-card-news`)

이 스킬은 에이전트가 **백그라운드에서 스스로 1차 출처(논문, 공식 기술 리포트, 정부 발표, 주요 통신사)를 교차검증**하여 가짜뉴스를 걸러내고, 최종 카드뉴스 이미지에는 **검증 과정 사족("팩트체크 판정", "교차검증 완료" 등) 없이 순수하게 뉴스 본연의 스토리와 핵심 숫자만 토스 피드 × 14F 스타일(스타일 A)**로 담아냅니다.

---

## 핵심 워크플로우 (5개 주제 후보 제시 → 사용자 선택 → 카드뉴스 제작)

사용자가 특정 주제를 미리 지정하지 않고 `"오늘 카드뉴스 만들어줘"`라고 요청하거나, 매일 아침 자동화(`Daily AI Card News Generator`)가 실행될 때는 다음 순서를 따릅니다:

1. **오늘의 검증된 후보 주제 5가지 발굴**:
   - `search_web`을 사용해 최신 AI·테크(`ai-tech`) 분야의 1차 출처 기반 핵심 뉴스 **5가지 후보**를 찾고 `output/YYYYMMDD_candidates/candidates.json`에 저장합니다:
   ```json
   {
     "date": "2026.11.08",
     "candidates": [
       { "no": 1, "title": "후보 1 제목", "summary": "핵심 내용 1줄 요약", "source": "OpenAI / arXiv 등" },
       { "no": 2, "title": "후보 2 제목", "summary": "핵심 내용 1줄 요약", "source": "Google DeepMind 등" },
       { "no": 3, "title": "후보 3 제목", "summary": "핵심 내용 1줄 요약", "source": "Anthropic / MIT 등" },
       { "no": 4, "title": "후보 4 제목", "summary": "핵심 내용 1줄 요약", "source": "Meta / Nature 등" },
       { "no": 5, "title": "후보 5 제목", "summary": "핵심 내용 1줄 요약", "source": "Gartner / Reuters 등" }
     ]
   }
   ```
2. **디스코드(또는 채팅창)에서 1~6번 선택받기 (`6번` = 새로운 주제 5개 다시 뽑기)**:
   - 아래 스크립트를 실행해 디스코드로 5가지 후보 + `6번(새로운 주제 5가지 다시 가져오기)` 옵션을 전송하고, 사용자가 디스코드에서 `1`~`6`을 입력하거나 `1️⃣`~`6️⃣` 이모지를 누를 때까지 대기하여 선택된 번호(`SELECTED_CHOICE`)를 받아옵니다:
   ```powershell
   python .agents/skills/fact-card-news/scripts/discord_topic_selector.py output/YYYYMMDD_candidates/candidates.json
   ```
   - **만약 `SELECTED_CHOICE=6` (`SELECTED_ACTION=REFRESH`)이 반환되면**:
     - 이전 후보들과 **중복되지 않는 새로운 1차 출처 AI·테크 뉴스 후보 5가지**를 다시 검색하여 `candidates.json` (`"round": 2` 등 표시)을 업데이트한 뒤, `discord_topic_selector.py`를 다시 실행합니다 (사용자가 `1`~`5`번 중 하나를 선택할 때까지 반복).
   - 만약 `DISCORD_BOT_TOKEN`이 설정되지 않았다면, 디스코드 웹훅으로 후보 5가지를 발송한 뒤 `ask_question` 도구로 사용자에게 1~6번 중 하나를 선택받습니다.
3. **선택된 주제로 6장 카드뉴스 제작 + 인스타 & 스레드(Threads) 원고 작성 + 디스코드 전송**:
   - 사용자가 선택한 번호의 주제를 심층 교차검증하여 `storyboard.json` 및 `manuscript.md`를 생성하고, `render_cards.py`와 `send_discord.py`를 차례로 실행합니다.
   - **`manuscript.md` 필수 구성 및 말투(Tone & Manner) 규칙 (총 2개의 ````text` 코드블록 작성 — `send_discord.py`가 순서대로 각각 발송함)**:
     - **말투 & 이모지 원칙 (필수 ⭐)**: 딱딱한 뉴스 리포트·논문 요약투(`~했습니다`, `~붕괴됨`, `~분석됨`)는 절대 금지합니다! 똑똑하고 친근한 현업 동료가 커피 마시며 핵심만 재밌게 짚어주는 **부드럽고 찰진 구어체(`~거든요`, `~더라고요`, `~인데요`, `솔직히`)**와 **적절한 이모지(`🤔`, `💥`, `📉`, `😅`, `💡`, `🚀`, `🛠️`, `😂`)**를 적극 활용해 가독성과 체류 시간을 극대화합니다.
     1. **첫 번째 ````text` 블록 (인스타그램 본문 캡션 + 핵심 해시태그 5개)**:
        - 공감 가는 구어체 훅(Hook)으로 시작하고, 본문 단락마다 직관적인 이모지 포인트(`🧠 1.`, `😅 2.`, `💡 3.`)와 실무 체크리스트(`✅`)를 넣어 술술 읽히게 작성합니다.
        - **해시태그 5개 제한 엄수 (필수 ⭐)**: 인스타그램 해시태그 최대 5개 제한에 맞춰, 무의미한 광범위 태그나 브랜드 태그 나열을 빼고 **탐색 탭 노출과 검색 유입에 가장 유용한 알짜 해시태그 딱 5개만** 엄선합니다.
          - 구성 공식 (총 5개): **해당 뉴스 핵심 키워드 태그 2~3개** (예: `#구글제미나이 #AI에이전트`) + **실무·트렌드 고효율 타깃 태그 2~3개** (`#생성형AI #AI트렌드 #개발자그램 #기획자인사이트 #일잘러팁` 중 주제에 가장 잘 맞는 것 선택)
     2. **두 번째 ````text` 블록 (스레드 Threads 바이럴용 '날것 음슴체 + 소신발언/팩폭' 원고 — 최대 500자 제한 엄수 ⭐)**:
        - **글자 수 절대 규칙**: 스레드(Threads)는 **공백·줄바꿈·이모지 포함 최대 500자 제한**이 있으므로, 붙여넣기 시 글자 수 초과가 절대 발생하지 않도록 **반드시 공백·줄바꿈 포함 `320~420자 이내`로 작성**합니다.
        - **스레드 네이티브 날것 반말·음슴체 + 팩폭 말투 (존댓말·이모지 도배 절대 금지 ⭐)**:
          - 스레드에서 존댓말(`~습니다`, `~해요`, `~잖아요?`)이나 문장마다 이모지를 도배(`1️⃣`, `📉`, `💡`)하면 광고/AI 봇처럼 보여 도달률이 급락합니다.
          - 이모지는 **0개(완전 배제)**로 작성하고, 친한 현업 동료에게 카톡하듯 툭 던지는 **날것의 반말·음슴체(`~임`, `~함`, `~음`, `~거임`, `ㅋㅋ`)**로 찰지게 작성합니다.
          - 모바일 가독성을 위해 **1~2줄마다 엔터(줄바꿈)**를 쳐서 호흡을 짧게 끊어줍니다.
        - **터지는 스레드 '소신발언/팩폭' 4단 구조**:
          1. **첫 줄 소신발언/팩폭 훅**: 인사말 없이 현업의 안일한 통념을 깨는 뼈 때리는 한두 줄로 시작 (예: `"소신발언 하나 함. 아직도 AI 창 하나 띄워놓고 채팅치듯 일하는 사람들 솔직히 흐름 놓친 거임."`)
          2. **날것 팩트 3줄 요약**: 실험/출시 결과를 친구한테 썰 풀듯 `1. 2. 3.`으로 짧고 강하게 요약 (`1. ~함 / 2. ~임 / 3. 제일 소름인 건 ~함`)
          3. **현업 팩폭 / 일침**: 뉴스 요약을 넘어 실무자의 뼈를 때리는 인사이트 2~3줄 (`"이제 ~하는 사람이 아니라 ~하는 사람이 다 해먹는 시대임. 혼자 야근하지 말고 ~해라 ㅋㅋ"`)
          4. **도발적 댓글 유도**: 마지막 줄은 댓글창(토론)이 열리도록 반말 질문이나 도발로 마무리 (`"반박 시 너네 말이 맞음. 요즘 실무 메인으로 쓰는 AI 뭐임?"`)

---

## 핵심 디자인 & 카피 원칙 (Style A: Toss × 14F)

1. **사족 배제 (Clean News Storytelling)**: 카드 이미지 안에 `"팩트체크 판정"`, `"교차검증 3건"` 같은 메타 문구를 넣지 않습니다.
2. **초단문 카피 (1 Card = 1 Point)**: 한 장당 글자 수는 **40~50자 이내(2~3줄)**로 제한하고, 어려운 전문용어 대신 직관적인 비유(`"기출문제 암기"` 등)를 사용합니다.
3. **다크 ↔ 라이트 배경 반전**: 1·2장(다크) → 3장(라이트 빅넘버) → 4장(다크 대조) → 5장(라이트 인사이트) → 6장(다크 결론)으로 스크롤 리듬감을 줍니다.

---

## `storyboard.json` 6장 표준 스키마

`output/YYYYMMDD_<slug>/storyboard.json` 파일을 아래 구조로 생성한 뒤 렌더러를 실행합니다.

```json
{
  "meta": {
    "domain": "ai-tech",
    "tag_label": "AI · TECH",
    "brand": "__beyondx__",
    "date": "2026.11.05",
    "slug": "ai_coding_benchmark_truth",
    "title": "OpenAI가 결국 코딩 시험지를 버린 진짜 이유"
  },
  "slides": [
    {
      "slide_no": 1,
      "layout": "cover",
      "tag": "AI · TECH",
      "headline_lines": [
        "OpenAI가 결국",
        "코딩 시험지를 버린",
        "진짜 이유"
      ],
      "highlight_line_index": 1,
      "sub_lines": [
        "업계 표준이던 코딩 평가 'SWE-bench',",
        "왜 하루아침에 퇴출당했을까요?"
      ]
    },
    {
      "slide_no": 2,
      "layout": "hook",
      "tag": "AI · TECH",
      "headline_lines": [
        "80점 넘었다며 자랑할 땐 언제고,",
        "왜 갑자기 시험지를 바꿨을까?"
      ],
      "quote_label": "그동안 화제였던 뉴스",
      "quote_lines": [
        "“최신 AI 코딩 점수가 80%에 육박해",
        "이제 시니어 개발자를 넘어섰다!”"
      ],
      "bottom_lines": [
        "하지만 현업 개발자들의 체감은 달랐고,",
        "논문 감사 결과 놀라운 이유가 밝혀졌습니다."
      ]
    },
    {
      "slide_no": 3,
      "layout": "big_number",
      "tag": "핵심 데이터",
      "headline_lines": [
        "코드는 열어보지도 않고",
        "정답 위치를 맞힌 비율"
      ],
      "big_number": "76%",
      "number_caption": "추론한 게 아니라 예전 기출문제를 외운 것",
      "bottom_lines": [
        "AI가 학습할 때 이미 깃허브 답안지를 봤던 거죠.",
        "실력이 아니라 '암기력' 점수였던 셈입니다."
      ]
    },
    {
      "slide_no": 4,
      "layout": "contrast",
      "tag": "점수 비교",
      "headline_lines": [
        "기출문제를 뺏고",
        "처음 보는 새 문제를 줬더니?"
      ],
      "top_box": {
        "label": "기존 시험지 (SWE-bench Verified)",
        "value": "70~80%대",
        "desc": "학습 데이터에 노출된 과거 공개 이슈"
      },
      "bottom_box": {
        "label": "새 실무 시험지 (SWE-bench Pro)",
        "value": "23.1% 급락",
        "desc": "데이터 오염을 차단한 다국어 실전 과제"
      }
    },
    {
      "slide_no": 5,
      "layout": "insight",
      "tag": "실무 포인트",
      "headline_lines": [
        "그래서 개발자는",
        "앞으로 어떻게 될까?"
      ],
      "points": [
        {
          "num": "01",
          "title": "단순 코더에서 '설계·검증자'로",
          "body": "",
          "lines": [
            "반복 코딩은 AI가 빠르게 대신하지만,",
            "보안과 전체 구조 설계는 여전히 사람의 몫입니다."
          ]
        },
        {
          "num": "02",
          "title": "홍보용 벤치마크 점수 맹신 금물",
          "body": "",
          "lines": [
            "공개 리더보드 숫자에 현혹되지 말고,",
            "우리 회사의 실제 비공개 코드로 직접 검증하세요."
          ]
        }
      ]
    },
    {
      "slide_no": 6,
      "layout": "outro",
      "tag": "AI · TECH",
      "headline_lines": [
        "AI는 개발자를 대체하는 게 아니라",
        "개발자의 무기를 바꿉니다",
        ""
      ],
      "highlight_line_index": 1,
      "summary_lines": [
        "기출문제 암기 착시를 걷어내고,",
        "진짜 실무에 통하는 AI 활용법을 준비할 때입니다."
      ],
      "sources_short": [
        "· OpenAI, 'Why SWE-bench Verified no longer measures frontier coding' (2026.02)",
        "· arXiv, 'The SWE-Bench Illusion: LLMs Remember Instead of Reason'",
        "· Epoch AI & Scale AI, 'SWE-bench Pro Benchmark Analysis'"
      ]
    }
  ]
}
```

---

## 렌더링 및 디스코드 발송 명령어

1. **6장 고해상도 슬라이드(`1080x1350`) 및 `preview.html` 생성**:
```powershell
python .agents/skills/fact-card-news/scripts/render_cards.py output/YYYYMMDD_<slug>/storyboard.json
```

2. **디스코드 웹훅 자동 전송** (`.env`에 `DISCORD_WEBHOOK_URL`이 설정된 경우 이미지 6장 + 인스타 캡션 발송):
```powershell
python .agents/skills/fact-card-news/scripts/send_discord.py output/YYYYMMDD_<slug>
```
