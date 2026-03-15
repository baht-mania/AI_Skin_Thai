# 📁 K-Sun Shield by FULLMOON

**분류:** 뷰티/웰니스 플랫폼
**상태:** 진행중 (프로토타입 MVP)
**시작일:** 2026-03-14
**최종 업데이트:** 2026-03-15

---

## 개요

태국 세븐일레븐 매장 QR코드 기반 PWA 서비스. 스마트폰 카메라로 AI 피부 진단(자외선 손상도, 기미, 홍조, 피부 거칠기) 후 한국 콜마 처방 데이터 기반 K-뷰티 제품 추천 및 구매까지 원스톱으로 제공.

**브랜드 전략:** 올리브영의 'FULLMOON' 전략 — "온전한 나"를 의미하며, 단순 선케어를 넘어 수면 건강식품, 홈케어, 이너뷰티 등 라이프스타일 전반을 아우르는 웰니스 플랫폼.

**Tech Stack:** HTML/CSS/JS (프로토타입) → Next.js + TypeScript + MediaPipe Face Mesh + OpenCV.js (프로덕션 예정)
**파트너:** 한국콜마(제품/처방), 태국 세븐일레븐(유통), TrueMoney(결제)
**타겟 시장:** 태국 우선 → 동남아 확장 (베트남, 말레이시아, 인도네시아, 필리핀)

---

## 관련 파일

- `K-Sun-Shield-PRD.md` — 제품 기획서 (PRD v1.0, Gemini 피드백 반영)
- `k-sun-shield-prototype.html` — 인터랙티브 프로토타입 MVP (4,200줄+)
- [[신규 프로젝트 (태국 화장품 사업)]] — 초기 아이디어 메모

---

## 목표 및 KPI

| 지표 | 목표 | 현재 | 달성률 |
|------|------|------|-------|
| PRD 문서 | 완성 | v1.0 완성 | 100% |
| 프로토타입 MVP | 전체 플로우 | 9개 화면 동작 | 75-80% |
| Vision Engine | 실제 분석 | CIELAB+Sobel 구현 | 90% |
| 로그인 시스템 | Google/LINE | UI 구현 (OAuth 미연동) | 50% |
| 결제 시스템 | 4가지 수단 | UI 구현 (API 미연동) | 40% |
| 백엔드 API | 5개 엔드포인트 | 미구현 | 0% |
| 다국어 (태국어) | 3개 언어 | 한국어+영어 | 66% |

---

## 비즈니스 모델

### 수익 구조 (3가지)
1. **제품 판매 리베이트:** 60바트/개 (마진 10%) → 1년차 28.8M바트, 3년차 540M바트
2. **데이터 라이선싱:** 콜마에 익명화 진단 데이터 판매 → 1년차 30M바트
3. **광고/마케팅 수수료:** CPM 기반 → 1년차 12M바트

### Unit Economics
- CAC: 3바트 (세븐일레븐 오프라인 거점 활용)
- LTV: 494바트 (3년 기준)
- LTV/CAC: 164배

### 제품 전략 (Phase 1→2)
- Phase 1 (1-2년): 콜마 브랜드 레버리지 → 마진 10%
- Phase 2 (3년차~): 진단 데이터 500만건 축적 후 자체 PB 전환 → 마진 40%

---

## 기술 아키텍처

### Vision Engine (프론트엔드 온디바이스)
- **Face Detection:** MediaPipe Face Mesh (468개 랜드마크)
- **ROI Masking:** 양 볼(Cheeks) + 이마(Forehead) 좌표 기반 추출
- **Color Analysis:** RGB → XYZ → CIELAB 변환 (L값: 밝기/기미, a값: 붉은기/홍조)
- **Texture Analysis:** Sobel Edge Detection (엣지 밀도 → 피부 거칠기)
- **White Calibration:** 흰색 기준점 기반 화이트밸런스 보정 (저사양 안드로이드 대응)
- **Score Formula:** overall = L(0.4) + redness(0.3) + texture(0.3)

### Privacy First
- Local Processing Only (canvas → 즉시 메모리 해제)
- No Image Upload (JSON 수치만 서버 전송)
- 태국 PDPA 준수

### 백엔드 (프로덕션 예정)
```
POST /api/v1/diagnose        — 진단 결과 저장
GET  /api/v1/prescription    — 처방 조회 (콜마 DB 매칭)
POST /api/v1/coupon/generate — 쿠폰 발급
GET  /api/v1/products/{id}   — 매장 인벤토리
GET  /api/analytics          — 분석 데이터 조회
```

---

## 프로토타입 화면 구성 (9개)

| # | 화면 | 기능 | 상태 |
|---|------|------|------|
| 1 | Login | Google/LINE/게스트 로그인 | ✅ UI 완성 |
| 2 | Home | FULLMOON 브랜딩, 게이미피케이션 Hook, 동의 체크 | ✅ 완성 |
| 3 | Scan | 카메라 + MediaPipe 468 랜드마크 시각화 + 5단계 분석 모션 + 자동 캡처 | ✅ 완성 |
| 4 | Analyzing | 레이저 스캔 + 실제 CIELAB/Sobel 분석 실행 + 단계별 텍스트 | ✅ 완성 |
| 5 | Result | Tone-down Score + 지표 카드 + 전문가 리포트 + 상품 추천 (단일 5개 + 세트 3개) | ✅ 완성 |
| 6 | Purchase | 장바구니 + 할인 계산 + 4가지 결제 수단 + 결제 완료 모달 | ✅ 완성 |
| 7 | Search | 검색바 + 카테고리 필터 + 2열 상품 그리드 | ✅ 완성 |
| 8 | Payments | 주문 내역 + 누적 구매 + 등급 표시 | ✅ 완성 |
| 9 | Profile | 사용자 정보 + 피부 기록 + 등급 진행률 + 메뉴 | ✅ 완성 |

---

## FULLMOON 등급 제도

| 등급 | 아이콘 | 조건 (누적 구매) | 할인 | 혜택 |
|------|--------|-----------------|------|------|
| New Moon | 🌑 | 0฿~ | 5% | 기본 할인 |
| Crescent | 🌒 | 1,000฿~ | 10% | 무료 배송 |
| Half Moon | 🌓 | 5,000฿~ | 15% | 생일 쿠폰 |
| Full Moon | 🌕 | 15,000฿~ | 20% | 전용 상품 + 1:1 상담 |

---

## 상품 라인업

### 단일 상품 (5개)
| 상품 | 카테고리 | 원가 | 할인가 | 할인율 |
|------|---------|------|--------|-------|
| K-Sun Shield 수딩 선스틱 ☀️ | 선케어 | 749฿ | 599฿ | 20% |
| FULLMOON 나이트 리페어 세럼 🌙 | 스킨케어 | 1,290฿ | 890฿ | 31% |
| FULLMOON 콜라겐 이너뷰티 젤리 ✨ | 이너뷰티 | 590฿ | 450฿ | 24% |
| FULLMOON 딥슬립 아로마 미스트 😴 | 수면/웰니스 | 690฿ | 520฿ | 25% |
| FULLMOON 비타민C 브라이트닝 앰플 💎 | 스킨케어 | 1,490฿ | 990฿ | 34% |

### 세트 상품 (3개)
| 세트 | 구성 | 원가 | 세트가 | 할인율 | 뱃지 |
|------|------|------|--------|-------|------|
| 데일리 케어 | 선스틱+세럼+앰플 | 3,529฿ | 2,290฿ | 35% | BEST |
| 토탈 뷰티 | 전 5종 | 4,809฿ | 2,990฿ | 38% | PREMIUM |
| 슬립 웰니스 | 세럼+미스트+젤리 | 2,570฿ | 1,590฿ | 38% | NEW |

---

## 디자인 시스템

### Color Palette
- Main Purple: `#2D1B69`
- Dark Navy: `#1A0E3F`
- Gold: `#F7C948`
- Orange: `#FF6B35`

### Typography
- Font: -apple-system, "Noto Sans KR"
- h1: 28px Bold / p: 13px Regular / Price: 14px Bold

### 컴포넌트 (K-prefix)
KButton, KBadge, KScoreCircle, KIndicatorCard, KProductCard, KCartItem, KMembershipTierCard, KBottomBar

---

## 진행 상황

- [x] Phase 0 — 아이디어 및 시장 조사
  - [x] 태국 선케어 시장 분석
  - [x] 파트너십 구조 설계 (콜마, 세븐일레븐, TrueMoney)
- [x] Phase 1 — PRD 작성
  - [x] PRD v1.0 완성 (비즈니스 모델, 기술 아키텍처, UX 플로우)
  - [x] Gemini 피드백 반영 (미백 톤 전환, White Calibration, PB 전략, 게이미피케이션)
- [x] Phase 2 — 프로토타입 MVP
  - [x] 5단계 화면 구조 (Home → Scan → Analyzing → Result → Purchase)
  - [x] Vision Engine (MediaPipe + CIELAB + Sobel Edge Detection)
  - [x] FULLMOON 브랜딩 + 디자인 시스템 적용
  - [x] 장바구니 + 등급 제도 (4단계)
  - [x] 상품 라인업 (단일 5개 + 세트 3개 + 원가/할인율)
  - [x] Google/LINE 로그인 화면
  - [x] 하단 네비 4탭 (홈/검색/결제/프로필)
  - [x] 결제 디테일 (할인 계산 + 4가지 결제 수단 + 완료 모달)
  - [x] 얼굴 분석 5단계 모션 (랜드마크 → 메시 → ROI → 준비 → 카운트다운)
  - [x] 카메라 권한 1회만 요청
  - [x] 데모 모드 (카메라 없는 환경 시연)
- [ ] Phase 3 — 프로덕션 개발
  - [ ] Next.js + TypeScript 프로젝트 전환
  - [ ] Google/LINE OAuth 실제 연동
  - [ ] 백엔드 API 5개 엔드포인트 구현
  - [ ] TrueMoney 결제 API 연동
  - [ ] 태국어 다국어 지원
  - [ ] Google Maps 매장 연동
  - [ ] PWA 빌드 + 배포

---

## 시장 확장 로드맵

| Phase | 기간 | 타겟 | 목표 |
|-------|------|------|------|
| Phase 1 | 1-2년 | 태국 (방콕 500매장) | 월 50만→200만 사용자 |
| Phase 2 | 2-4년 | 베트남, 말레이시아, 인도네시아, 필리핀 | 1,870개 매장, 연 506M바트 |

---

## Gemini 피드백 (반영 완료)

1. ✅ **"공포→미백" 톤 전환** — Screen 4를 Tone-down Score 중심으로 재설계
2. ✅ **White Reference Calibration** — 저사양 안드로이드 대응 화이트밸런스 보정
3. ✅ **콜마→PB 전환 전략** — Phase 1 브랜드 레버리지 → Phase 2 자체 PB (마진 10%→40%)
4. ✅ **게이미피케이션 Hook** — "내 피부 점수는 몇 점?" + 매장 평균 점수 + 소셜 공유

---

*태그: #프로젝트 #뷰티 #태국 #웰니스 #FULLMOON #콜마 #세븐일레븐 #AI피부진단 #MediaPipe*
