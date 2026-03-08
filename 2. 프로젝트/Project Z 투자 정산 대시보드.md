# 📊 Project Z 투자 정산 관리 대시보드

**분류:** 투자 관리 / 웹 애플리케이션
**상태:** 배포 완료 (v1.0)
**최종 업데이트:** 2026-02-27
**배포 URL:** https://project-z-dashboard-lime.vercel.app

---

## 개요

일본 엔터테인먼트 프로젝트(Project Z)에 대한 개인 투자 정산을 관리하는 1인 전용 대시보드. 투자금 추적, 정산 관리, ROI 분석, 뉴스 모니터링 등 투자 관련 전체 워크플로우를 하나의 시스템에서 처리.

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| 프레임워크 | Next.js 16 + TypeScript |
| 번들러 | Turbopack |
| 스타일링 | Tailwind CSS v4 + shadcn/ui |
| ORM | Prisma 7 |
| 데이터베이스 | PostgreSQL (Supabase) |
| 인증 | Supabase Auth |
| 차트 | Recharts |
| 캘린더 | FullCalendar |
| 폼 처리 | React Hook Form + Zod |
| 배포 | Vercel |

---

## 주요 기능

### 정산 관리
- 정산 내역 조회/입력/수정
- 정산 캘린더 (FullCalendar 기반)
- 정산 노트 및 첨부파일 관리

### 공연/앨범 관리
- 이벤트(투어/공연/앨범) CRUD
- PnL 상세 분석

### ROI 분석
- 핵심 지표 대시보드
- 환율 민감도 분석 (JPY↔KRW)
- 시나리오 시뮬레이터

### 기타
- 계약 조건 관리
- 멤버 관리
- 뉴스 스크랩 (자동 수집)
- 리스크 체크리스트
- 보고서 생성
- 알림 시스템
- 감사 추적 (Audit Trail)
- 설정 관리

---

## 인프라 구성

### Supabase 프로젝트
- **Project ID:** xitykakeghqcvuwqpgua
- **리전:** AWS ap-southeast-2
- **플랜:** Free (Nano)

### Vercel 프로젝트
- **이름:** project-z-dashboard
- **GitHub 레포:** baht-mania/project-z-dashboard
- **프로덕션 URL:** https://project-z-dashboard-lime.vercel.app

### 환경 변수 (Vercel)
- `DATABASE_URL` — Supabase PostgreSQL 연결
- `NEXT_PUBLIC_SUPABASE_URL` — Supabase 프로젝트 URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` — Supabase anon key

---

## 개발 히스토리

| 날짜 | 작업 내용 |
|------|-----------|
| 2026-02-26 | PRD v2.2 기반 전체 구현 (16단계 개발 완료) |
| 2026-02-27 | 빌드 에러 수정, Vercel 배포, Supabase 연동 |

---

## 관련 파일

- 프로젝트 경로: `/Users/baht/Desktop/5. 넥써쓰_Claude/Project Z ROI Analysis/project-z-dashboard/`
- PRD 문서: `PRD_ProjectZ_v2.2_FINAL.md`
- 개발 가이드: `CLAUDE_CODE_KICKOFF.md`
- DB 스키마: `prisma/schema.prisma`

---

## 알려진 이슈

- [ ] DB 연결 시 Supabase pooler "Tenant or user not found" 에러 (로컬 환경에서 발생, Vercel 서버에서 직접 연결로 해결 시도 중)
- [ ] 뉴스 스크랩 외부 API 키 미설정 (네이버, 구글 CSE)
- [ ] Resend 이메일 API 키 미설정
- [ ] 환율 API 키 미설정

---

## 참고 링크

- [[2026-02-27 Project Z 대시보드 빌드 & 배포]]
