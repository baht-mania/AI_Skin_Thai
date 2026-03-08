# 💬 대화 기록 — 2026-03-04 Obsidian MCP 연동 트러블슈팅

**날짜:** 2026-03-04
**모델:** Claude Opus 4.6
**세션 목적:** Claude Desktop ↔ Obsidian MCP 연동 시 실시간 동기화 문제 해결

---

## 대화 내용

### 문제
Claude Desktop과 Obsidian 연동 후 대화 기록이 실시간으로 Vault에 반영되지 않음

### 트러블슈팅 과정

**1단계: 기본 체크**
- Obsidian 실행 확인, Claude Desktop 재시작, config.json 경로 확인

**2단계: config.json 수정**
- 위치: `~/Library/Application Support/Claude/claude_desktop_config.json`
- 기존 `mcp-obsidian` 패키지에서 에러 발생 ("Server transport closed unexpectedly")

**3단계: MCP 서버 패키지 교체**
- 기존: `mcp-obsidian` (불안정, 연결 끊김 반복)
- 변경: `@mauricio.wolff/mcp-obsidian@latest` (14가지 도구 지원, 안정적)

**최종 config:**
```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": ["@mauricio.wolff/mcp-obsidian@latest", "/Users/baht/Desktop/5. 넥써쓰_Claude/넥써쓰_Vault"]
    }
  }
}
```

### 핵심 학습
- Claude-Obsidian 연동은 실시간 푸시가 아닌 "요청 시 조회" 구조
- MCP 서버 running 상태여도 도구 허용(Allow Always) 팝업이 필요
- 서버 불안정 시 패키지 교체가 가장 빠른 해결책

---

*태그: #대화기록 #Claude #Obsidian #MCP #트러블슈팅*
