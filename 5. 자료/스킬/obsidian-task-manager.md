---
name: obsidian-task-manager
created: '2026-03-17'
type: skill
---

# obsidian-task-manager

넥써쓰_Vault TASKS.md 관리 규칙 및 MCP 연동 패턴.

## Vault 정보
- TASKS.md 경로: `/TASKS.md` (vault root)
- MCP Tool: `obsidian:read_note`, `obsidian:patch_note`, `obsidian:write_note`

## TASKS.md 구조 규칙
- 섹션 2개만: `## 📌 할 일` + `## ✅ 완료`
- 섹션 내 우선순위: 🔴긴급(오늘) / 🟡이번주 / 🔵진행중 / 📥백로그
- 모든 태스크는 날짜순, 성격 무관하게 할 일 섹션에 추가

## 태스크 형식
```
- [ ] {이모지} {내용} 📅 {날짜}    ← 미완료
- [x] {내용} ✅ {완료일}           ← 완료
```

## 핵심 운영 원칙
- 추가: `patch_note`로 해당 섹션 마지막에 삽입
- 완료: `patch_note`로 `[ ]` → `[x]` 변경 후 완료 섹션 상단으로 이동
- 전체 재작성 시에만 `write_note` 사용 (데이터 손실 위험 주의)
- frontmatter `updated` 날짜 수정 시마다 갱신

## 자동 추가 트리거
Claude는 대화 중 아래 상황에서 태스크 추가를 제안:
- "~해야 해", "~나중에 확인" 발언
- 미팅 후 액션 아이템 발생
- 이메일/계약 F/U 필요
- 대표 지시 사항 언급

## 프로젝트 노트 경로
- 프로젝트: `/2. 프로젝트/{프로젝트명}.md`
- 미팅: `/3. 미팅/{날짜}_{상대방}.md`
- 대표님 미팅: `/4. 장대표님 미팅/{날짜}.md`

> 전체 스킬 파일: obsidian-task-manager.skill
