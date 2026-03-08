# 🤖 Claude 텔레그램 봇 - 세팅 가이드

## 전체 구조
```
텔레그램 (당신) ←→ 텔레그램 서버 ←→ Railway 서버 (봇) ←→ Claude API
```

---

## Step 1: 텔레그램 봇 만들기 (2분)

1. 텔레그램에서 **@BotFather** 를 검색하여 대화 시작
2. `/newbot` 입력
3. 봇 이름 입력 (예: `내 Claude 비서`)
4. 봇 유저네임 입력 (예: `my_claude_assistant_bot`) — 반드시 `bot`으로 끝나야 함
5. **토큰이 발급됩니다** → 복사해서 안전하게 보관 (예: `7123456789:AAF...`)

### 내 텔레그램 User ID 확인하기
1. 텔레그램에서 **@userinfobot** 을 검색하여 대화 시작
2. 아무 메시지나 보내면 내 User ID를 알려줌 (숫자)
3. 이 숫자를 메모 → ALLOWED_USER_IDS에 사용

---

## Step 2: Anthropic API 키 발급 (3분)

1. https://console.anthropic.com 접속
2. 계정 생성 (Google/이메일)
3. 좌측 메뉴 → **API Keys** 클릭
4. **Create Key** 클릭 → 키 복사 (예: `sk-ant-...`)
5. 크레딧 충전: **Billing** → 결제 수단 등록 → 최소 $5 충전

### 비용 참고
- Claude Sonnet: 입력 $3 / 출력 $15 (100만 토큰당)
- 일반적인 업무 대화 기준 **월 $5~15** 정도
- Haiku 모델 사용 시 더 저렴 (약 1/10)

---

## Step 3: Railway에 배포하기 (5분)

### 3-1. GitHub에 코드 올리기

```bash
# 터미널에서 실행
cd telegram-claude-bot
git init
git add .
git commit -m "Initial commit: Claude Telegram Bot"
```

GitHub에서 새 리포지토리 생성 후:
```bash
git remote add origin https://github.com/YOUR_USERNAME/claude-telegram-bot.git
git branch -M main
git push -u origin main
```

### 3-2. Railway 배포

1. https://railway.app 접속 → GitHub 계정으로 로그인
2. **New Project** → **Deploy from GitHub repo** 선택
3. 방금 만든 리포지토리 선택
4. **Variables** 탭에서 환경변수 추가:

| 변수명 | 값 |
|--------|-----|
| `TELEGRAM_TOKEN` | BotFather에서 받은 토큰 |
| `ANTHROPIC_API_KEY` | Anthropic API 키 |
| `ALLOWED_USER_IDS` | 내 텔레그램 User ID |
| `CLAUDE_MODEL` | `claude-sonnet-4-20250514` (또는 `claude-haiku-4-5-20251001`) |
| `MORNING_REMINDER_HOUR` | `9` (매일 아침 알림 시각) |

5. **Deploy** 클릭 → 배포 완료!

### Railway 비용
- 무료 체험 $5 크레딧 제공
- 이후 Hobby Plan: **월 $5** (충분)
- 봇 하나 운영에 리소스를 거의 안 씀

---

## Step 4: 테스트

1. 텔레그램에서 내 봇을 검색 (Step 1에서 설정한 유저네임)
2. `/start` 입력 → 환영 메시지 확인
3. 아무 질문이나 보내기 → Claude 응답 확인
4. `/task 테스트 태스크` → 태스크 추가 확인
5. `/remind_after 1 테스트 알림` → 1분 후 알림 확인

---

## 사용법 요약

### 💬 일반 대화
그냥 메시지를 보내면 Claude가 답변합니다.
```
블록체인 게임에서 듀얼 토큰 모델의 장단점은?
```

### 📋 태스크 관리
```
/task 투자자 미팅 자료 준비
/task 토크노믹스 모델 검토
/tasks           ← 목록 보기
/done 1          ← 1번 완료
```

### ⏰ 알림
```
/remind 14:00 팀 미팅
/remind 09:30 데일리 스크럼
/remind_after 30 보고서 제출      ← 30분 후
/remind_after 120 미팅 준비       ← 2시간 후
```

### 📎 파일 분석
- 텍스트 파일 (.txt, .py, .sol, .json 등): 직접 분석
- 이미지: Claude Vision으로 분석
- 파일 보내면서 캡션에 질문 가능

### 🔄 자동 알림
- **매일 아침 9시**: 미완료 태스크 목록 자동 전송

---

## 커스터마이징

### 시스템 프롬프트 변경
Railway Variables에서 `SYSTEM_PROMPT`를 수정하면 봇의 성격/전문 분야를 바꿀 수 있습니다.

예시:
```
너는 Web3 게임 프로젝트 매니저 AI다. 토크노믹스, NFT 설계, 커뮤니티 관리에 전문적이다. 항상 실행 가능한 액션 아이템과 함께 답변해라.
```

### 모델 변경
- 빠른 응답: `claude-haiku-4-5-20251001` (저렴, 빠름)
- 깊은 분석: `claude-sonnet-4-20250514` (균형)
- 최고 품질: `claude-opus-4-20250514` (최고, 비용 높음)

### 아침 알림 시간 변경
`MORNING_REMINDER_HOUR`를 원하는 시각으로 (0~23)

---

## 문제 해결

| 증상 | 해결 |
|------|------|
| 봇이 응답 안 함 | Railway 로그 확인 → 환경변수 체크 |
| API 오류 | Anthropic 크레딧 잔액 확인 |
| 알림이 안 옴 | ALLOWED_USER_IDS가 올바른지 확인 |
| 권한 없음 메시지 | ALLOWED_USER_IDS에 내 ID 추가 |
