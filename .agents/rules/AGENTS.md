---
description: 카드뉴스 생성 에이전트 전역 규칙 (Verified Real News Card Agent Rules)
---

# Verified Real News Card Agent Rules

이 워크스페이스(`beyond-x`)는 에이전트가 **백그라운드에서 스스로 가짜뉴스·과장 정보·클릭베이트를 필터링 및 교차검증**하고, 최종 카드뉴스 이미지에는 **검증된 '진짜 뉴스' 본연의 핵심 스토리와 인사이트만 깔끔하고 임팩트 있게** 담아내는 카드뉴스 제작 워크스페이스입니다.

## 1. 백그라운드 팩트 필터링 & 클린 카드 원칙 (Silent Verification, Clean Visuals)
1. **내부 교차검증 (Silent Cross-Verification)**:
   - 에이전트는 카드뉴스 제작 전 공식 기술 블로그, 학술 논문(arXiv, Nature, Science 등), 정부·공공기관 발표, 주요 글로벌 통신사(Reuters, AP, Bloomberg) 등 1차 출처를 최소 2곳 이상 교차 확인하여 가짜뉴스와 과장 루머를 스스로 걸러낸다.
2. **카드뉴스 내 메타 문구 배제 (No Fact-Check Clutter on Cards)**:
   - 카드뉴스 슬라이드 이미지 안에는 `"팩트체크 판정"`, `"교차검증 3건 완료"`, `"판정 등급: MISLEADING"` 같은 검증 과정 메타 문구를 노출하지 않는다.
   - 카드뉴스는 **토스 피드 · 14F · 롱블랙 · 뉴닉**처럼 독자가 순수하게 뉴스 스토리 자체에 몰입할 수 있도록 **짧고 강렬한 카피(슬라이드당 2~3줄, 40~50자 이내)와 50% 이상의 여백**으로만 구성한다.
   - 검증에 사용한 상세 출처 링크는 `manuscript.md` 원고 파일 및 마지막 슬라이드 하단 캡션에만 간결하게 기록한다.

## 2. 타이포그래피 & 디자인 황금 법칙
- **폰트**: `NotoSansKR-VF.ttf` (`Black 900` / `Bold 700` / `Medium 500`) 및 `NotoSerifKR-VF.ttf` (`Black 900`) 가변 폰트와 좁은 자간(`tracking -3 ~ -4`)을 사용하여 매거진급 타이포그래피를 구현한다.
- **1 Card = 1 Point**: 한 장에 여러 개의 박스를 쪼개 넣지 않고, 단 하나의 핵심 문장이나 단 하나의 거대한 숫자(Big Number)만 배치한다.

## 3. 도메인 우선순위 및 확장성
- 기본 도메인은 **1순위 `ai-tech` (AI · 테크 · 과학)**이며, `.agents/skills/fact-card-news/config/domains.json`에 저장된 나머지 4개 분야(`economy`, `health`, `society`, `global`)도 언제든 호출 가능하다.
