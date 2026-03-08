# 📖 Andy's Reading World

> **상태:** 개발 완료 (v1.1)
> **완료일:** 2026-02-24
> **대상 사용자:** Andy (G7, 국제학교)

---

## 프로젝트 개요

Andy의 영어 Reading 능력과 어휘력 향상을 위해 개발된 개인 맞춤형 영어 리딩 웹앱.
사전 제작된 30개의 논픽션 아티클(6개 토픽 x 5개)을 Andy의 관심사(농구, 인형뽑기 등)에 맞춰 제공하고, 게이미피케이션 요소(XP, 레벨업, 업적)로 학습 동기를 부여한다.

> **v1.1 변경사항:** 실시간 Claude API 호출 방식에서 사전 생성 콘텐츠 방식으로 전환. API 키 없이 즉시 사용 가능.

**프로젝트 경로:** `/Users/baht/Desktop/5. 넥써쓰_Claude/andys-reading-world/`

---

## 기술 스택

| 항목 | 기술 |
|------|------|
| 프레임워크 | Next.js 16 (App Router, Static Export) |
| 언어 | TypeScript |
| 콘텐츠 | 사전 생성 정적 데이터 (30개 아티클) |
| 스타일링 | Tailwind CSS v4 |
| 데이터 저장 | localStorage (서버리스) |
| 폰트 | Inter (Google Fonts) |

> **참고:** v1.0에서는 Claude API를 실시간 호출했으나, v1.1부터 API 의존성을 제거하고 정적 콘텐츠로 전환했다. `@anthropic-ai/sdk` 패키지 제거됨.

---

## 콘텐츠 구성

30개 아티클이 사전 제작되어 `src/lib/content.ts`에 포함:

| 토픽 | 아티클 수 | 난이도 범위 |
|------|-----------|-------------|
| 🏀 Basketball | 5 | 3, 5, 5, 7, 8 |
| 🎮 Claw Machines | 5 | 3, 5, 5, 7, 8 |
| 🔬 Science | 5 | 3, 5, 5, 7, 8 |
| 💻 Technology | 5 | 3, 5, 5, 7, 8 |
| 🦁 Animals | 5 | 3, 5, 5, 7, 8 |
| 🚀 Space | 5 | 3, 5, 5, 7, 8 |

각 아티클에 포함된 항목:
- 300~450 단어 본문 (13세 남학생 대상 논픽션)
- 5~8개 핵심 어휘 (정의 + 예문 포함)
- 5문제 독해 퀴즈 (4지선다 + 해설)

---

## 주요 기능

### 1. 토픽 기반 리딩
사전 제작된 아티클 중 선택한 토픽과 난이도에 가장 가까운 것을 자동 선택한다.
- 6개 토픽: Basketball, Claw Machines, Science, Technology, Animals, Space
- 난이도 1~10 슬라이더로 어휘 수준 조절
- 이미 읽은 아티클은 자동 건너뛰기 (중복 방지)
- 모든 아티클 읽기 완료 시 안내 메시지 표시

### 2. 어휘 학습 시스템
아티클 내 오렌지색으로 하이라이트된 단어를 클릭하면 뜻과 예문 팝업이 표시된다.
- 클릭 한 번으로 개인 단어장에 저장
- 단어당 10 XP 획득
- 단어장에서 Learning / Mastered 상태 관리

### 3. 독해 퀴즈
아티클 읽기 완료 후 사전 제작된 5문제 독해 퀴즈를 풀 수 있다.
- 4지선다 객관식
- 정답/오답 즉시 피드백 + 해설 제공
- 정답당 20 XP 획득

### 4. 게이미피케이션
XP 기반 레벨업 시스템으로 학습 동기를 부여한다.

| 활동 | 획득 XP |
|------|---------|
| 아티클 읽기 완료 | 50 XP |
| 퀴즈 정답 (1문제) | 20 XP |
| 새 단어 학습 | 10 XP |
| 연속 학습 보너스 | 25 XP |

- 500 XP마다 레벨업
- 연속 학습 스트릭 추적
- 레벨별 칭호: Beginner Reader → Book Explorer → Word Warrior → Knowledge Knight → Reading Champion → Legendary Scholar

### 5. 업적 시스템
10가지 업적으로 도전 목표 제공:

| 업적 | 조건 |
|------|------|
| First Steps | 첫 아티클 읽기 |
| Word Collector | 10개 단어 학습 |
| Vocabulary Master | 50개 단어 학습 |
| Perfect Score | 퀴즈 100% 정답 |
| On Fire | 3일 연속 학습 |
| Unstoppable | 7일 연속 학습 |
| Rising Star | 레벨 5 달성 |
| Reading Champion | 레벨 10 달성 |
| Bookworm | 10개 아티클 읽기 |
| Knowledge Seeker | 25개 아티클 읽기 |

### 6. 단어장 (Word Bank)
학습한 단어를 체계적으로 관리하는 개인 단어장.
- 검색 및 필터 (All / Learning / Mastered)
- 플래시카드 연습 모드
- 마스터 토글로 학습 진행 추적

---

## 페이지 구성

| 페이지 | 경로 | 설명 |
|--------|------|------|
| 대시보드 | `/` | 환영 메시지, 레벨/XP, 스탯, 토픽 퀵스타트 |
| 리딩 | `/read` | 토픽 선택, 난이도 조절, 아티클 읽기 |
| 퀴즈 | `/quiz` | 독해 퀴즈 5문제, 결과 요약 |
| 단어장 | `/wordbank` | 단어 관리, 검색, 플래시카드 연습 |
| 업적 | `/achievements` | 업적 진행률, 잠금/해제 현황 |

---

## 실행 방법

```bash
cd /Users/baht/Desktop/5. 넥써쓰_Claude/andys-reading-world
npm run dev -- --port 3333
```

브라우저에서 `http://localhost:3333` 접속.

> **API 키 불필요.** v1.1부터 모든 콘텐츠가 사전 생성되어 별도 설정 없이 즉시 사용 가능.

---

## 프로젝트 구조

```
andys-reading-world/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # 루트 레이아웃 (메타데이터)
│   │   ├── AppShell.tsx        # 클라이언트 셸 (네비게이션)
│   │   ├── page.tsx            # 대시보드
│   │   ├── globals.css         # 글로벌 스타일 + 테마
│   │   ├── read/page.tsx       # 리딩 페이지
│   │   ├── quiz/page.tsx       # 퀴즈 페이지
│   │   ├── wordbank/page.tsx   # 단어장 페이지
│   │   └── achievements/page.tsx # 업적 페이지
│   └── lib/
│       ├── types.ts            # 공유 타입 정의
│       ├── storage.ts          # localStorage 유틸리티
│       ├── gamification.ts     # 게이미피케이션 로직
│       └── content.ts          # 사전 생성 아티클 30개 (3,200+ 줄)
├── public/
│   └── favicon.svg             # 파비콘
├── next.config.ts              # Static Export 설정
└── package.json
```

---

## 디자인 특징

- 밝고 컬러풀한 톤 (보라-인디고 그라디언트 기반)
- 반응형: 데스크탑(사이드바) / 모바일(하단 네비게이션)
- XP 바 쉬머 애니메이션, 카드 호버 이펙트
- 13세 남학생에게 어필하는 게이미피케이션 UI

---

## 배포

`output: 'export'` 설정으로 완전 정적 사이트 생성 가능:

```bash
npm run build
```

`out/` 폴더에 정적 HTML 파일이 생성되며, Vercel / Netlify / GitHub Pages 등에 즉시 배포 가능.

---

## 향후 개선 아이디어

- [ ] 콘텐츠 추가 (토픽당 10개로 확장)
- [ ] 읽기 속도 측정 기능
- [ ] 단어 복습 알림 (스페이스드 리피티션)
- [ ] 읽기 기록 통계 차트
- [ ] 다크 모드 지원
- [ ] 다른 관심사 토픽 추가
- [ ] Claude API 연동 복원 (무한 콘텐츠 생성)

---

## 개발 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| v1.0 | 2026-02-24 | 최초 릴리즈 - Claude API 실시간 콘텐츠 생성 |
| v1.1 | 2026-02-24 | API 의존성 제거, 사전 생성 콘텐츠 30개로 전환, 정적 Export 지원 |

---

## 관련 문서

- [[게임 로컬라이제이션 툴]]

---

*태그: #Andy #영어학습 #리딩 #NextJS #게이미피케이션 #정적사이트 #개발완료 #넥써쓰*
