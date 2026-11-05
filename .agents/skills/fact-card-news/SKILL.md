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

## 렌더링 명령어

```powershell
python .agents/skills/fact-card-news/scripts/render_cards.py output/YYYYMMDD_<slug>/storyboard.json
```
