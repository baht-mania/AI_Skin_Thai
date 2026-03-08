# 💬 대화 기록 — 2026-03-04 Claude Code 토큰 리밋 오류 & CLAUDE.md 작성

**날짜:** 2026-03-04
**모델:** Claude Opus 4.6
**세션 목적:** gdc-cross-token 프로젝트 Claude Code 세션 복구 방안 마련

---

## 대화 내용

### 문제 상황
- `gdc-cross-token` 프로젝트 버그 픽싱 중 "Prompt is too long" 오류 발생
- `/compact` 명령어도 실패 → 완전 복구 불가 상태
- 진행 중이던 디버깅 컨텍스트 전부 손실

### 해결 방안
- Esc 2회 → `/clear` → 새 세션 시작
- 컨텍스트 복구를 위한 `CLAUDE.md` 파일 프로젝트 루트에 생성

### CLAUDE.md 포함 내용
- 프로젝트 개요 & 기술 스택 (Next.js/TS/Supabase/Tailwind/shadcn)
- 디렉토리 구조
- 현재 작업 상태 (버그 픽싱 단계)
- 운영 가이드라인: package-lock.json, node_modules 읽지 않기, `/compact` 선제적 사용

### 교훈
- Claude Code 장시간 세션 시 토큰 리밋 주의
- CLAUDE.md를 통한 컨텍스트 영속화 필수

---

## 산출물

| 유형 | 내용 |
|------|------|
| CLAUDE.md | gdc-cross-token 프로젝트 컨텍스트 파일 |

---

*태그: #대화기록 #Claude #ClaudeCode #GDC2026 #토큰리밋 #트러블슈팅*
