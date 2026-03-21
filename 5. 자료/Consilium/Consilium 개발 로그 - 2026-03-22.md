---
date: '2026-03-22'
tags:
  - Consilium
  - MiroFish
  - 개발로그
  - 배포
status: 완료
project: Consilium
---
# Consilium 개발 로그 — 2026-03-22

## 개요
MiroFish 오픈소스를 포크하여 **Consilium** (AI 시뮬레이션 기반 전략 컨설팅 플랫폼)으로 리브랜딩 및 배포 완료.

---

## 배포 정보

| 항목 | 값 |
|------|-----|
| **프로덕션 URL** | https://consilium.baht.dev |
| **프론트엔드** | Vercel (baht-manias-projects/miro-fish) |
| **백엔드** | Render (mirofish-21f5.onrender.com) |
| **도메인** | `consilium.baht.dev` (Cloudflare DNS → Vercel) |
| **인증** | Supabase (`epqvuixgkoueaoxktouk.supabase.co`) |
| **GitHub** | https://github.com/baht-mania/MiroFish |

---

## 구현 완료 기능

### 코어
- [x] MiroFish 포크 + 환경 세팅 (OpenRouter + Zep Cloud)
- [x] Molty Royale 중국 진출 시뮬레이션 실행 (17 에이전트, 10라운드)
- [x] 전략 보고서 생성 완료

### 리브랜딩 (MiroFish → Consilium)
- [x] 브랜드명 변경: **Consilium** (라틴어 "전략적 조언")
- [x] BI 로고 SVG 제작 (LINE green #06C755 네트워크 아이콘)
- [x] 파비콘 제작 (네트워크 "C" 형태)
- [x] 전체 UI 톤앤매너를 컨설팅 전문가 어투로 변경
- [x] 지식 그래프 시각화 (48개 노드 + 78개 엣지, 레이더 그리드, 데이터 파티클)

### UI/UX
- [x] 다크모드 지원
- [x] 다국어 지원 (한국어, 영어, 중국어, 태국어, 일본어)
- [x] 반응형 텍스트 (`clamp()` 적용)
- [x] 랜딩페이지 분리 (`/` 마케팅 vs `/dashboard` 워크스페이스)
- [x] 패널 비율 5:5 정렬
- [x] "v0.1-미리보기" 텍스트 제거
- [x] GitHub 링크 제거 + 카피라이트 추가

### 인증/보안
- [x] Supabase 이메일 로그인
- [x] 회원가입 버튼 제거 (고정 계정 방식)
- [x] 라우트 보호 (미인증 → /login 리다이렉트)

### 기능
- [x] 시뮬레이션 히스토리 페이지 (`/history`)
- [x] PDF 보고서 다운로드 (html2pdf.js, A4 Consilium 브랜딩)
- [x] 프롬프트 템플릿 라이브러리 (게임/블록체인/엔터/핀테크 4카테고리)
- [x] 비용 대시보드 (localStorage 기반, 일일 예산 관리)
- [x] 샘플 리포트 페이지 (`/sample-report`, 로그인 불필요)
- [x] 실시간 시뮬레이션 진행률 (SVG 원형 프로그레스, 라이브 액션 피드)
- [x] 보고서 공유 링크 (`/shared/:id`, 공개 URL)
- [x] 게임사업 담당자용 프롬프트 예시 (5개 언어별 현지화)
- [x] 예상 결과물 섹션 (전략 보고서, 네트워크 지도, 에이전트 인터뷰, 여론 타임라인)

---

## 라우트 구조

```
공개    /              → 마케팅 랜딩
공개    /login         → 로그인
공개    /sample-report → 샘플 리포트 (Molty Royale 중국 진출)
공개    /shared/:id    → 공유 보고서
인증    /dashboard     → 시뮬레이션 대시보드
인증    /project/:id   → 프로젝트 상세
인증    /history       → 분석 히스토리
```

---

## 주요 파일 위치

| 파일 | 내용 |
|------|------|
| `frontend/src/i18n/ko.json` | 한국어 텍스트 전체 |
| `frontend/src/views/LandingView.vue` | 마케팅 랜딩페이지 |
| `frontend/src/views/Home.vue` | 대시보드 (시뮬레이션 워크스페이스) |
| `frontend/src/views/MainView.vue` | 프로젝트 상세 |
| `frontend/src/views/LoginView.vue` | 로그인 |

---

## 수동 텍스트 수정 & 배포 방법

```bash
# 1. 텍스트 수정
code frontend/src/i18n/ko.json

# 2. 로컬 확인
cd frontend && npm run dev

# 3. 빌드 + 푸시 (Vercel 자동 배포)
npm run build && cd .. && git add -A && git commit -m "update: 텍스트 수정" && git push fork main
```

---

## 향후 추가 고려 기능

| 우선순위 | 기능 |
|----------|------|
| 🟡 | 에이전트 커스터마이징 (수/유형/성격 직접 설정) |
| 🟡 | Google/Kakao 소셜 로그인 |
| 🔵 | API 키 자체 입력 (사용자 비용 자체 부담) |
| 🔵 | 시뮬레이션 A/B 비교 모드 |
| 🔵 | Webhook/Slack 알림 |

---

## 관련 노트
- [[Nexth - Molty Royale 중국 진출 전략 메모]]
- [[MiroFish - Molty Royale 중국 시장 시뮬레이션 보고서]]
