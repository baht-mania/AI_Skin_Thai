---
date: '2026-03-25'
tags:
  - automation
  - cowork
  - obsidian
  - daily-summary
  - setup-guide
---

# 🔄 Cowork 대화 자동 요약 시스템 설정 가이드

> 매일 아침 10시, 전날 Claude 대화를 자동 요약하여 Obsidian `0. 대화 기록/` 폴더에 저장

---

## 아키텍처

```
매일 10:00 AM (Cowork 스케줄)
    ↓
Cowork 세션 시작
    ↓
claude.ai 프로젝트 대화 수집 (past_chats / conversation_search)
    ↓
대화 요약 생성
    ↓
Obsidian MCP로 vault에 저장 (0. 대화 기록/YYYY-MM-DD.md)
    ↓
(선택) 텔레그램 알림
```

## 전제조건

- [x] Obsidian MCP 서버 연결 (현재 활성화됨)
- [ ] Claude Desktop 앱 설치 및 로그인
- [ ] Cowork 기능 활성화 (Pro/Max 플랜)
- [ ] 맥북이 매일 10시에 켜져 있어야 함 (잠자기 해제 또는 항시 켜놓기)

## 설정 방법

### Step 1: Cowork에서 스케줄 태스크 생성

1. Claude Desktop 앱 실행
2. Cowork 사이드바에서 **"Scheduled"** 클릭
3. 새 스케줄 태스크 생성:

| 항목 | 설정값 |
|------|--------|
| **이름** | 데일리 대화 요약 |
| **설명** | 전날 Claude 대화를 요약하여 Obsidian에 저장 |
| **빈도** | 매일 (Daily) |
| **시간** | 오전 10:00 |
| **모델** | Claude Sonnet 4.6 (토큰 절약) 또는 Opus 4.6 |

4. **프롬프트 지시사항**에 아래 내용 입력:

```
## 태스크: 전날 Claude 대화 요약 → Obsidian 저장

### 수행 절차
1. past_chats 도구로 어제(전날) 대화를 모두 조회한다
2. conversation_search로 주요 키워드별 대화를 추가 검색한다
3. 수집된 대화를 아래 포맷으로 요약한다
4. Obsidian MCP의 write_note로 저장한다

### 저장 경로
`0. 대화 기록/YYYY-MM-DD 대화 요약.md`

### 마크다운 포맷
```markdown
---
date: YYYY-MM-DD
tags: [daily, chat-summary, auto-generated]
---

# 💬 YYYY-MM-DD 대화 요약

## 주요 대화 토픽

### 🔴 업무 관련
- **[대화 제목/주제]** — 핵심 내용 요약 (2-3줄)
  - 결정사항 또는 액션아이템이 있으면 기록
  - 관련 파일이나 링크가 있으면 포함

### 🟡 리서치/분석
- **[주제]** — 요약

### 📥 기타
- **[주제]** — 요약

## 액션 아이템
- [ ] 항목1
- [ ] 항목2

## 대화 링크
- [대화 제목](https://claude.ai/chat/{uri})
```

### 주의사항
- 이메일 리뷰 대화가 있으면 기존 데일리 리뷰 포맷(📬)과 병합
- 이미 해당 날짜 파일이 있으면 append 모드로 추가
- 대화가 없는 날은 파일을 생성하지 않음
```

5. **MCP 서버 연결** 확인:
   - Obsidian MCP가 Cowork에서도 접근 가능해야 함
   - Claude Desktop 설정 → MCP Servers에 Obsidian 추가

### Step 2: MCP 서버 설정 (Claude Desktop)

Claude Desktop의 `claude_desktop_config.json`에 Obsidian MCP 서버가 등록되어 있는지 확인:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": ["-y", "obsidian-mcp"],
      "env": {
        "OBSIDIAN_VAULT_PATH": "/Users/baht/Desktop/5. 넥써쓰_Claude/넥써쓰_Vault"
      }
    }
  }
}
```

> 경로는 실제 vault 위치에 맞게 수정

### Step 3: 테스트 실행

1. Cowork에서 스케줄 태스크를 **"Run Now"**로 수동 실행
2. `0. 대화 기록/` 폴더에 파일이 생성되는지 확인
3. 포맷이 기존 데일리 리뷰와 일관성 있는지 검토

### Step 4: (선택) 텔레그램 알림 추가

기존 텔레그램 봇에 완료 알림을 보내려면, Cowork 프롬프트에 추가:

```
마지막으로, 요약이 완료되면 텔레그램 봇을 통해 알림을 보낸다:
"✅ 데일리 대화 요약 완료: X개 대화, Y개 액션아이템"
```

## 대안: claude.ai 프로젝트에서 수동 실행

Cowork 설정 전이나, 맥북이 꺼져 있는 날에는 이 프로젝트에서 직접 요청:

**명령어:** `오늘 요약해줘` 또는 `어제 대화 정리해줘`

→ Claude가 past_chats로 대화 조회 → 요약 생성 → Obsidian에 저장

## 알려진 제한사항

1. **Cowork 스케줄은 맥북이 켜져 있어야 실행됨** — 잠자기 상태에서는 실행 안 됨
2. **past_chats 범위** — 프로젝트 안에서는 해당 프로젝트 대화만, 프로젝트 밖에서는 일반 대화만 검색 가능
3. **세션 메모리 없음** — Cowork는 매 세션마다 새로 시작하므로, 프롬프트에 모든 지시사항을 포함해야 함
4. **토큰 소비** — Cowork 태스크는 일반 채팅보다 토큰을 많이 사용함

## 변경 이력

| 날짜 | 변경 내용 |
|------|-----------|
| 2026-03-25 | 초기 설정 가이드 작성 |
