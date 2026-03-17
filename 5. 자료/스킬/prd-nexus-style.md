---
name: prd-nexus-style
created: '2026-03-17'
type: skill
---

# prd-nexus-style

넥써쓰 바트의 PRD 작성 스타일. NomuAI, Project Z, GDC 토큰 앱, 아이템크로스 실제 패턴 기반.

## PRD 헤더
```
PRD: {제품명} v{버전}
작성자: 전준영 (바트)
작성일: YYYY-MM-DD
상태: Draft / Review / Confirmed
```

## 표준 10섹션 구조
1. **개요** — 배경·목적 / 목표(비즈니스·사용자·기술) / Out of Scope
2. **사용자 및 시장** — 페르소나 / TAM·SAM·SOM / 경쟁
3. **기능 요구사항** — MoSCoW 우선순위 + 기능 목록 + 핵심 기능 상세
4. **비기능 요구사항** — 성능, 보안, 가용성, 확장성, 규정
5. **기술 스택** — Frontend / Backend / DB / 인프라 / AI / 블록체인
6. **수익 모델** — 모델별 단가·예상 수익
7. **마일스톤** — Phase 1~3, 기간, 담당
8. **성공 지표 (KPI)** — 목표값, 측정 방법, 주기
9. **리스크 및 의존성**
10. **미결 사항 (Open Questions)**

## CLAUDE.md 템플릿
Claude Code 연동 시 프로젝트 루트에 생성:
- 프로젝트 개요 / 기술 스택 / 파일 구조 / 개발 명령어 / 환경변수 위치 / 현재 상태

## 작성 팁
- 버전 관리: v1.0 → v1.1 → v2.0 (주요 변경 시 메이저 업)
- PRD 완성 후 ceo-report-template으로 1페이지 요약 별도 작성
- Toss 플랫폼 검토 시: 결제·수수료 정책, SDK 연동 요구사항 섹션 추가

> 전체 스킬 파일: prd-nexus-style.skill
