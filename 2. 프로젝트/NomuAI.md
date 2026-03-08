# 📁 NomuAI

**분류:** AI 학습 앱
**상태:** 진행중
**시작일:** 2026-02-24
**최종 업데이트:** 2026-02-28

---

## 개요

공인노무사 1차·2차 동시 합격을 목표로 하는 AI 기반 전략적 학습 웹앱 (PWA 지원). "1.5차 병행 학습" 컨셉으로 1차 객관식 문제를 풀면서 2차 키워드·판례를 자연스럽게 습득하는 구조.

**GitHub:** https://github.com/baht-mania/nomu_ai
**배포:** https://nomu-ai.vercel.app
**Tech Stack:** Next.js 14 + TypeScript + Tailwind CSS + shadcn/ui + Zustand + Recharts + Framer Motion + Supabase + next-themes

**장기 목표:** 노무사 → 경찰공무원, 부동산중개사 등 다중 시험 플랫폼 확장

---

## 관련 파일

- `nomu-prd.md` — 제품 기획서 (PRD v1.1)
- `nomu-prd-v2.md` — 제품 기획서 (PRD v0.2)
- `src/` — Next.js 앱 소스 코드
- `.env.local.example` — 환경변수 템플릿 (Supabase)

---

## 목표 및 KPI

| 지표 | 목표 | 현재 | 달성률 |
|------|------|------|-------|
| 1차 과목 콘텐츠 | 5과목 | 5과목 | 100% |
| Mock 문항 수 | 200+ | 82문항 | 41% |
| 핵심 기능 구현 | 15개 | 15개 | 100% |
| Supabase 연동 | 완료 | 실연동 완료 | 80% |
| Claude API 연동 | 완료 | Mock | 0% |
| 다크모드 | 완료 | 완료 | 100% |

---

## 진행 상황

- [x] Phase 1 — MVP 프로토타입 (Mock 데이터 기반)
  - [x] 프로젝트 셋업 (Next.js 14, shadcn/ui, Zustand)
  - [x] 랜딩 페이지
  - [x] 대시보드 (통계, 주간 차트, 히트맵)
  - [x] 학습 선택 페이지
  - [x] 문제 풀이 페이지 (타이머, 피드백, AI 해설, 키워드 브릿지)
  - [x] 세션 결과 페이지
  - [x] Mock AI 스트리밍 API
  - [x] PWA 설정 (manifest, service worker)
- [x] Phase 0.15 — 콘텐츠 확장 + 추가 기능
  - [x] 4과목 추가 (노동법II, 민법, 사회보험법, 경영조직론) — 60문항
  - [x] 오답노트 기능 (/wrongnote) — 과목/날짜 필터, 다시 풀기
  - [x] 약점 분석 기능 (/analysis) — 레이더 차트, 챕터별 정답률
  - [x] 5과목 전체 학습 활성화
  - [x] GitHub 푸시 + Vercel 배포
- [x] Phase 0.2 — 디자인 리뉴얼 + 스마트 홈
  - [x] 디자인 리뉴얼 (Pretendard 폰트, 카드/버튼 리디자인)
  - [x] 5탭 네비게이션 (홈/학습/복습/분석/설정)
  - [x] 스마트 홈 화면 (인사 카드, 오늘의 학습 플랜, 주간 히트맵)
  - [x] 3-Layer AI 해설 (캐시→API→템플릿 fallback)
  - [x] 온보딩 플로우 (목표→진단→맞춤 플랜)
  - [x] 설정 페이지 + 버전 히스토리
  - [x] 버전 체계 변경 (v0.x)
  - [x] Study 과목 리스팅 개선 (개요 + 챕터 뱃지)
  - [x] 백색소음 사운드 개선 (카페/모닥불/숲속)
  - [x] "토스 스타일" 텍스트 제거
  - [x] 이메일 매직 링크 로그인
- [x] Phase 0.2.1 — 고급 기능 추가
  - [x] 업데이트 배너 "오늘 다시 보지 않기"
  - [x] 하단 네비 클릭 애니메이션 (Framer Motion)
  - [x] 다크모드 지원 (next-themes, 라이트/다크/시스템)
  - [x] 학습 화면 디자인 대폭 개선 (과목 색상 사이드바, 번호 뱃지, 정오답 아이콘)
  - [x] 백색소음 기능 (Web Audio API, 5가지 소리, 미니 플레이어)
  - [x] 타임 블로킹/포모도로 타이머 (원형 프로그레스, 집중/휴식 모드)
  - [x] Supabase Auth 인프라 (이메일+Google+카카오 로그인, 미들웨어)
  - [x] 전국 석차 레이더 (일별 순위, Top 10, 내 순위 카드)
- [ ] Phase 3 — 백엔드 고도화
  - [x] Supabase 프로젝트 생성 + DB 스키마 적용
  - [x] 환경변수 설정 (.env.local + Vercel)
  - [x] 랭킹 데이터 Supabase 실연동 (Mock → RPC)
  - [x] 학습 결과 DB 저장 (question_attempts + daily_stats)
  - [x] 로그인 시 프로필 로드 + 헤더 표시
  - [ ] Google/Kakao OAuth 프로바이더 설정
  - [ ] Claude API 연동 (Mock → Real 전환)
  - [ ] 결제 시스템 (프리미엄 플랜)

---

## 앱 구조

```
src/
├── app/
│   ├── page.tsx              ← 랜딩
│   ├── home/                 ← 스마트 홈 (v0.2)
│   ├── study/                ← 학습 선택 + 문제 풀이
│   ├── result/               ← 세션 결과
│   ├── wrongnote/            ← 오답노트
│   ├── analysis/             ← 약점 분석
│   ├── settings/             ← 설정 + 버전 히스토리 (v0.2)
│   ├── onboarding/           ← 온보딩 (v0.2)
│   ├── timer/                ← 포모도로 타이머 (v0.2.1)
│   ├── ranking/              ← 전국 석차 (v0.2.1)
│   ├── auth/                 ← 로그인/회원가입 (v0.2.1)
│   ├── dashboard/            ← 대시보드 (레거시)
│   └── api/ai/explain/       ← Mock AI API
├── components/
│   ├── layout/               ← 헤더, 하단 네비, 앱 셸
│   ├── study/                ← 문제 풀이 (옵션, 피드백, 해설, 백색소음)
│   ├── home/                 ← 홈 화면 (인사, 학습 플랜, 히트맵, 순위)
│   ├── onboarding/           ← 온보딩 스텝 (목표, 진단, 플랜)
│   ├── timer/                ← 포모도로 (타이머, 설정)
│   ├── ranking/              ← 순위 (리더보드, 내 순위)
│   ├── auth/                 ← 인증 리스너
│   ├── dashboard/            ← 대시보드 컴포넌트
│   ├── result/               ← 결과 컴포넌트
│   └── ui/                   ← shadcn 컴포넌트
├── stores/
│   ├── session-store.ts      ← 세션 상태 관리
│   ├── answer-store.ts       ← 답안 기록 + 통계
│   ├── user-store.ts         ← 유저 프로필/설정 (v0.2)
│   ├── auth-store.ts         ← 인증 상태 (v0.2.1)
│   ├── sound-store.ts        ← 백색소음 (v0.2.1)
│   └── timer-store.ts        ← 포모도로 (v0.2.1)
├── lib/
│   ├── supabase/             ← Supabase 클라이언트 (v0.2.1)
│   │   └── api.ts            ← Supabase API 헬퍼 (v0.3)
│   ├── theme-provider.tsx    ← 다크모드 (v0.2.1)
│   ├── audio-engine.ts       ← Web Audio API (v0.2.1)
│   ├── ranking-data.ts       ← 순위 데이터 (v0.2.1)
│   ├── version-data.ts       ← 버전 히스토리 (v0.2)
│   ├── explanation-template.ts ← 해설 템플릿 (v0.2)
│   ├── animations.ts         ← Framer Motion (v0.2)
│   ├── types.ts              ← 타입 정의
│   ├── constants.ts          ← 과목/챕터 상수
│   └── utils.ts              ← 유틸리티
└── middleware.ts              ← Supabase 세션 (v0.2.1)

supabase/
└── schema.sql                 ← DB 스키마
```

---

## 콘텐츠 현황

| 과목 | 문항 수 | 브릿지 | 해설 |
|------|---------|--------|------|
| 노동법I | 22 | 10 | 10 |
| 노동법II | 15 | 2 | 5 |
| 민법 | 15 | 2 | 5 |
| 사회보험법 | 15 | 2 | 0 |
| 경영조직론 | 15 | 2 | 0 |
| **합계** | **82** | **18** | **20** |

---

## 커밋 히스토리

| 커밋 | 설명 | 날짜 |
|------|------|------|
| `4902f37` | feat: v0.2 업데이트 — 5가지 개선 | 2026-02-28 |
| `97117a7` | feat: Supabase 실연동 — 랭킹, 학습 결과 저장, 프로필 로드 | 2026-02-28 |
| `b808999` | feat: Supabase DB 스키마 추가 | 2026-02-28 |
| `96598ee` | fix: Supabase 환경변수 없을 때 미들웨어 크래시 방지 | 2026-02-28 |
| `8f13819` | v0.2.1 — 다크모드, 백색소음, 포모도로, Supabase 로그인, 전국 석차 | 2026-02-28 |
| `4e9f5dc` | fix: Zustand persist 셀렉터 hydration 에러 수정 | 2026-02-28 |
| `74c8bb7` | v0.2 — 디자인 리뉴얼, 스마트 홈, 3-Layer AI 해설 | 2026-02-28 |
| `e92954d` | v0.15 — 5과목 콘텐츠 확장 + 오답노트/분석 기능 | 2026-02-25 |
| `2ddd600` | v0.1 — MVP 프로토타입 | 2026-02-24 |

---

## 관련 문서

- [[게임 로컬라이제이션 툴]] — 동일 기술 스택 참고

---

*태그: #프로젝트 #AI #학습앱 #노무사 #NextJS #Supabase #다크모드*
