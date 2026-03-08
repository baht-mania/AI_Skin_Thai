# Raid Labs DCF Valuation Simulator

**분류:** 투자 분석 도구
**상태:** 진행중
**시작일:** 2026-03-03
**최종 업데이트:** 2026-03-04

---

## 개요

Raid Labs 매수 의사결정을 위한 DCF(Discounted Cash Flow) 밸류에이션 시뮬레이터 웹앱.
3개 매출 스트림(NFT 마켓플레이스, 게임퍼블리싱, 아이템거래) 기반 월별 매출/비용을 계산하고, 5개년(2026~2030) DCF 모델을 실시간으로 시뮬레이션한다.

- **매수가 33억원 기준** 저평가/고평가 판단
- **슬라이더 기반** 실시간 민감도 분석 (성장률, 마진, WACC 등)

---

## 관련 파일

- `dcf-simulator/` — Next.js 프로젝트 루트
- `PRD-DCF-Simulator.md` — 기획 문서 (PRD)
- `Raid Labs_dcf-simulation_V2.html.html` — HTML 프로토타입 (레퍼런스)

---

## 기술 스택

| 항목 | 기술 |
|------|------|
| Framework | Next.js 15 (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS + CSS Variables |
| State | React useState/useMemo (클라이언트 전용) |
| Deployment | Vercel |

---

## 인프라

- **GitHub:** https://github.com/baht-mania/Raidlabs_dcf_simulator
- **Vercel:** https://dcf-simulator.vercel.app
- **로컬 개발:** `npm run dev` → localhost:3003

---

## 진행 상황

- [x] PRD 작성
- [x] HTML 프로토타입 완성
- [x] Next.js + TypeScript 프로젝트 초기화
- [x] 디자인 시스템 (다크 테마, 폰트, 컬러)
- [x] DCF 계산 로직 구현
- [x] 전체 UI 컴포넌트 구현
- [x] GitHub 커밋 및 푸시
- [x] Vercel 배포
- [ ] 반응형 모바일 최적화

---

## 관련 문서

- [[Project Z 투자 정산 대시보드]]

---

*태그: #프로젝트 #DCF #밸류에이션 #투자분석 #RaidLabs*
