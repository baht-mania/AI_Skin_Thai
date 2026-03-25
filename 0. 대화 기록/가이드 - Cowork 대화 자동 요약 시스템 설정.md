---
date: '2026-03-25'
tags:
  - automation
  - cowork
  - obsidian
  - daily-summary
  - setup-guide
---

# 🔄 Cowork 대화 자동 요약 시스템 — 상세 설정 가이드

> 매일 아침 10시, 전날 Claude 대화를 자동 요약하여 Obsidian `0. 대화 기록/` 폴더에 저장

---

## 사전 준비 체크리스트

- [ ] Claude Desktop 앱이 맥에 설치되어 있음 (없으면 https://claude.ai/download)
- [ ] Claude Pro 또는 Max 플랜 활성화됨
- [ ] Node.js 18 이상 설치됨 (터미널에서 `node -v`로 확인)
- [ ] Obsidian vault 경로 확인: `/Users/baht/Desktop/5. 넥써쓰_Claude/넥써쓰_Vault`

---

## Step 1: Claude Desktop에 Obsidian MCP 서버 등록

Cowork가 Obsidian vault에 읽고 쓸 수 있으려면, Claude Desktop에 Obsidian MCP 서버를 연결해야 합니다.

### 방법 A: Desktop Extensions (쉬운 방법, 추천)

1. **Claude Desktop** 앱을 연다
2. 메뉴 바에서 **Claude → Settings** (또는 `Cmd + ,`)
3. 좌측 메뉴에서 **Extensions** 클릭
4. **"Browse extensions"** 클릭
5. 검색창에 **"Obsidian"** 입력
6. Obsidian 확장이 있으면 클릭 → **Install** → 완료!
7. 설치 후 vault 경로를 물어보면 입력:
   ```
   /Users/baht/Desktop/5. 넥써쓰_Claude/넥써쓰_Vault
   ```

> 만약 Extensions 디렉토리에 Obsidian이 없다면, 방법 B로 진행

### 방법 B: JSON 설정 파일 직접 수정

1. **Claude Desktop** 앱을 연다
2. 메뉴 바에서 **Claude → Settings** (또는 `Cmd + ,`)
3. 좌측 메뉴에서 **Developer** 클릭
4. **"Edit Config"** 버튼 클릭
   - 이렇게 하면 Finder에서 `claude_desktop_config.json` 파일이 열림
   - 파일 위치: `~/Library/Application Support/Claude/claude_desktop_config.json`
5. 파일을 VS Code나 텍스트 편집기로 열어서, 아래 내용으로 수정:

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

> ⚠️ 이미 다른 MCP 서버가 등록되어 있다면, `mcpServers` 객체 안에 `"obsidian": {...}` 부분만 추가하면 됨. 쉼표(`,`) 빠뜨리지 않도록 주의!

6. 파일 저장 후 **Claude Desktop을 완전히 종료** (Cmd+Q, 최소화가 아님!)
7. Claude Desktop을 **다시 실행**
8. 새 대화창에서 입력창 오른쪽 하단에 **MCP 서버 아이콘(🔨)** 이 보이면 성공!

### 연결 확인

Claude Desktop에서 새 대화를 열고 이렇게 질문:

```
내 Obsidian vault에 있는 폴더 목록을 보여줘
```

Claude가 vault의 폴더 구조를 정상적으로 보여주면 연결 완료!

### 트러블슈팅

문제가 생기면 확인할 것들:
- **JSON 문법 오류**: 터미널에서 `cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | python3 -m json.tool` 실행 → 에러 나면 문법 오류
- **npx 경로 문제**: 터미널에서 `which npx` 입력 → 경로 확인. 안 나오면 Node.js 재설치 필요. 경로가 `/usr/local/bin/npx` 가 아니라면 config에서 `"command"` 를 전체 경로로 변경
- **로그 확인**: `~/Library/Logs/Claude/` 폴더에서 `mcp.log` 파일 확인

---

## Step 2: Cowork에서 스케줄 태스크 생성

MCP 서버 연결이 확인되면, 이제 매일 자동 실행될 태스크를 만듭니다.

### 방법 1: /schedule 명령어 (추천 — Claude가 도와줌)

1. Claude Desktop에서 **Cowork** 탭 클릭 (좌측 사이드바)
2. **"+ New task"** 클릭하여 새 태스크 시작
3. 대화창에 `/schedule` 입력 후 엔터
4. Claude가 "create a scheduled task" 스킬을 실행함
5. Claude가 물어보면 아래 내용을 알려줌:

```
매일 아침 10시에 실행되는 태스크를 만들고 싶어.

목적: 전날 Claude와 나눈 모든 대화를 요약해서 Obsidian vault에 자동 저장.

상세 지시사항:
1. past_chats 도구로 어제(전날) 대화를 모두 조회해줘
2. conversation_search로 주요 업무 키워드(CROSS, 웹샵, 로한, FF, GDC, 투자, 이메일)별 대화도 추가 검색해줘
3. 수집된 대화를 아래 포맷으로 요약해서 Obsidian MCP의 write_note로 저장해줘

저장 경로: 0. 대화 기록/YYYY-MM-DD 대화 요약.md
(날짜는 전날 날짜)

마크다운 포맷:
---
date: YYYY-MM-DD
tags: [daily, chat-summary, auto-generated]
---

# 💬 YYYY-MM-DD 대화 요약

## 주요 대화 토픽

### 🔴 업무 관련
- **[대화 제목/주제]** — 핵심 내용 요약 (2-3줄)
  - 결정사항 또는 액션아이템

### 🟡 리서치/분석
- **[주제]** — 요약

### 📥 기타
- **[주제]** — 요약

## 액션 아이템
- [ ] 항목

## 대화 링크
- [대화 제목](https://claude.ai/chat/{uri})

추가 규칙:
- 이미 해당 날짜에 데일리 리뷰(📬) 파일이 있으면 append 모드로 추가
- 대화가 없는 날은 파일을 생성하지 않음
- 이메일 리뷰 내용은 기존 포맷 유지
```

6. Claude가 태스크를 요약하면 **"Let's go"** 또는 확인 클릭
7. "Create scheduled task" 모달이 뜸 → 아래처럼 설정:

| 항목 | 입력값 |
|------|--------|
| **Name** | 데일리 대화 요약 |
| **Description** | 전날 Claude 대화를 요약하여 Obsidian에 자동 저장 |
| **Frequency** | Daily |
| **Time** | 10:00 AM |
| **Model** | Claude Sonnet 4.6 (토큰 절약) |
| **Working folder** | Obsidian vault 폴더 선택 |

8. **"Save"** 클릭 → 완료!

### 방법 2: 사이드바에서 직접 생성

1. Claude Desktop 좌측 사이드바에서 **"Scheduled"** 클릭
2. 우측 상단 **"+ New task"** 클릭
3. 위 표의 항목들을 직접 입력
4. **Prompt Instructions** 필드에 위의 상세 지시사항 전체를 붙여넣기
5. **"Save"** 클릭

> 💡 첫 번째 실행 후 Claude가 자동으로 프롬프트를 개선합니다. 어떤 도구를 사용했고, 어디서 데이터를 찾았는지를 반영해서 두 번째 실행부터 더 정확해집니다.

---

## Step 3: 테스트 실행 & 검증

태스크를 만들었으면 바로 테스트해봅니다.

### 3-1. 수동 실행

1. 좌측 사이드바에서 **"Scheduled"** 클릭
2. 방금 만든 **"데일리 대화 요약"** 태스크를 찾음
3. 태스크 옆의 **"▶ Run now"** (또는 "Run on demand") 클릭
4. Cowork가 새 세션을 열고 태스크를 실행하기 시작함
5. 실행 과정을 실시간으로 볼 수 있음 — Claude가 무엇을 하는지 단계별로 표시됨

### 3-2. 결과 확인

실행이 완료되면:

1. **Obsidian** 열기
2. `0. 대화 기록/` 폴더로 이동
3. 새로운 `YYYY-MM-DD 대화 요약.md` 파일이 생성되었는지 확인
4. 파일을 열어서 다음을 점검:
   - [ ] frontmatter (date, tags)가 정상인지
   - [ ] 대화 토픽이 제대로 분류되었는지 (🔴/🟡/📥)
   - [ ] 액션 아이템이 누락 없이 기록되었는지
   - [ ] 대화 링크가 올바르게 포함되었는지
   - [ ] 기존 데일리 리뷰가 있는 날은 append가 잘 되었는지

### 3-3. 문제 발생 시

**"Obsidian MCP 도구를 찾을 수 없다"는 에러**
→ Step 1로 돌아가서 MCP 서버 연결 재확인. Cowork에서도 MCP가 접근 가능한지 확인.

**대화를 찾지 못한다**
→ Cowork는 claude.ai 웹 대화에 직접 접근하지 못할 수 있음. 이 경우 대안으로:
- Cowork 내부 대화만 요약하도록 변경
- 또는 claude.ai 프로젝트에서 수동으로 "오늘 요약해줘" 사용

**파일이 이상한 위치에 저장됨**
→ 프롬프트의 경로를 확인: `0. 대화 기록/` 이 정확히 맞는지

**토큰 사용량이 너무 많다**
→ Model을 Sonnet 4.6으로 변경 (Opus 대비 토큰 소비 적음)
→ 대화 수가 많은 날은 최근 10개만 요약하도록 프롬프트 수정

### 3-4. 자동 실행 확인 (다음 날)

1. **맥북을 아침 10시 전에 켜놓고**, Claude Desktop이 실행 중인지 확인
2. 10시에 Cowork가 자동으로 태스크를 시작하면 알림이 뜸
3. 완료 후 Obsidian에서 결과 확인
4. 만약 맥이 꺼져 있었다면 → 다음에 맥을 켜고 Claude Desktop을 열 때 자동으로 밀린 태스크를 실행함 (알림으로 안내됨)

> 💡 맥이 항상 10시에 켜져 있도록 하려면: **시스템 설정 → 에너지 → 스케줄** 에서 자동 시작 설정 가능

---

## 매일 10시에 맥 자동으로 깨우기 (선택)

스케줄 태스크가 확실히 실행되도록, 맥이 매일 아침 자동으로 켜지게 설정할 수 있습니다.

### macOS Sequoia 이상

1. **시스템 설정** 열기
2. **일반 → 시동 또는 절전** (또는 **에너지**)
3. **"스케줄..."** 또는 **"시동 또는 깨우기"** 클릭
4. 매일 오전 9:50에 깨우기 설정 (태스크 10시 전에 준비)

### pmset 명령어 (터미널)

```bash
sudo pmset repeat wakeorpoweron MTWRFSU 09:50:00
```

확인:
```bash
pmset -g sched
```

---

## 대안: claude.ai에서 수동 요약

Cowork가 안 돌아가는 날이나, 설정 전에는 이 프로젝트에서 직접 요청하면 됩니다:

**사용법:** 대화에서 아래 중 하나를 입력

- `오늘 요약해줘`
- `어제 대화 정리해줘`
- `이번 주 대화 요약`

→ Claude가 past_chats로 대화 수집 → 요약 → Obsidian에 저장

---

## 알려진 제한사항

1. **맥북이 켜져 있어야 함** — 잠자기 상태에서는 스케줄 실행 안 됨. 단, 다음에 깨어나면 밀린 태스크 자동 실행
2. **세션 메모리 없음** — Cowork는 매 실행마다 새로 시작. 이전 실행 결과를 기억하지 않음
3. **past_chats 범위** — 프로젝트 안/밖 대화가 분리되어 검색됨
4. **토큰 소비** — Cowork 태스크는 일반 채팅보다 2-5배 토큰 사용
5. **첫 실행은 완벽하지 않을 수 있음** — Claude가 첫 실행 후 프롬프트를 자동 개선하므로, 2-3일 정도 결과를 보면서 조정하면 됨

---

## 변경 이력

| 날짜 | 변경 내용 |
|------|-----------|
| 2026-03-25 | 상세 설정 가이드 v2 작성 (Step 1~3 상세화) |
