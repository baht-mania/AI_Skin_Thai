"""
Claude Telegram Bot - GitHub Gist TASKS.md 연동 버전
Railway 배포용: InlineKeyboard + 4시간 자동알림 + Claude 초안 자동생성
+ D-day 카운트다운 + 주간 리포트 + 태스크 메모 첨부
"""

import os
import re
import json
import logging
import requests
from datetime import datetime, timedelta
from pathlib import Path

import anthropic
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# ─── 설정 ───────────────────────────────────────────────
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
ALLOWED_USER_IDS = [int(x) for x in os.environ.get("ALLOWED_USER_IDS", "").split(",") if x]
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")
SYSTEM_PROMPT = os.environ.get(
    "SYSTEM_PROMPT",
    "너는 게임 및 블록체인 비즈니스 전문 AI 비서다. "
    "한국어로 응답하고, 업무 관리와 리마인더를 도와준다. "
    "간결하고 실용적으로 답변해라."
)

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GIST_ID = os.environ.get("GIST_ID", "a8587b66f6e2b36d85f00d57a9003080")
GIST_FILENAME = os.environ.get("GIST_FILENAME", "TASKS.md")
GIST_API = f"https://api.github.com/gists/{GIST_ID}"
GIST_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

# Slack 주간 리포트 설정
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_REPORT_CHANNEL = os.environ.get("SLACK_REPORT_CHANNEL", "D091YP5F2VC")

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
CONVERSATIONS_FILE = DATA_DIR / "conversations.json"
NOTES_FILE = DATA_DIR / "task_notes.json"

# ConversationHandler 상태
TASK_SELECT_PRIORITY, TASK_INPUT_CONTENT, TASK_INPUT_DEADLINE = range(3)

# 초안 작성 가능 키워드
DRAFT_KEYWORDS = ["이메일", "메일", "슬랙", "메시지", "보고", "초안", "작성", "전달", "공유", "발송"]

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# ─── Gist read/write ────────────────────────────────────

def gist_read() -> str:
    try:
        r = requests.get(GIST_API, timeout=10)
        r.raise_for_status()
        return r.json()["files"][GIST_FILENAME]["content"]
    except Exception as e:
        logger.error(f"Gist read error: {e}")
        return ""


def gist_write(content: str) -> bool:
    try:
        payload = {"files": {GIST_FILENAME: {"content": content}}}
        r = requests.patch(GIST_API, headers=GIST_HEADERS, json=payload, timeout=10)
        r.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Gist write error: {e}")
        return False


# ─── TASKS.md 파싱 ──────────────────────────────────────

def parse_tasks(content: str) -> dict:
    todo_items, done_items = [], []
    in_todo = in_done = False
    for line in content.split("\n"):
        if "## 📌 할 일" in line:
            in_todo, in_done = True, False
        elif "## ✅ 완료" in line:
            in_todo, in_done = False, True
        elif line.startswith("## "):
            in_todo = in_done = False
        todo_match = re.match(r"^- \[ \] (.+)$", line)
        done_match = re.match(r"^- \[x\] (.+)$", line, re.IGNORECASE)
        if in_todo and todo_match:
            todo_items.append({"text": todo_match.group(1).strip(), "raw": line})
        elif (in_todo or in_done) and done_match:
            done_items.append({"text": done_match.group(1).strip(), "raw": line})
    return {"todo": todo_items, "done": done_items}


def clean_task_text(text: str) -> str:
    text = re.sub(r"📅 \d+월 \d+일[^\n]*추가", "", text)
    text = re.sub(r"✅ \d+/\d+[^\n]*완료", "", text)
    return text.strip()


def get_task_deadline(text: str):
    """태스크 텍스트에서 마감일 추출 → datetime 또는 None"""
    m = re.search(r"📅\s*(\d{1,2})/(\d{1,2})", text)
    if m:
        try:
            month, day = int(m.group(1)), int(m.group(2))
            now = datetime.now()
            target = now.replace(month=month, day=day, hour=23, minute=59, second=59)
            # 이미 지난 날짜면 내년으로
            if target < now - timedelta(days=30):
                target = target.replace(year=target.year + 1)
            return target
        except ValueError:
            return None
    return None


def get_dday_text(deadline: datetime) -> str:
    """마감일까지 남은 일수를 텍스트로 반환"""
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    target = deadline.replace(hour=0, minute=0, second=0, microsecond=0)
    diff = (target - now).days
    if diff < 0:
        return f"D+{abs(diff)} ⚠️ 마감 초과!"
    elif diff == 0:
        return "D-Day 🚨"
    elif diff == 1:
        return "D-1 ⏰"
    elif diff <= 3:
        return f"D-{diff} ⚡"
    else:
        return f"D-{diff}"


def mark_done(content: str, keyword: str) -> tuple:
    lines = content.split("\n")
    new_lines, matched_text, success = [], "", False
    for line in lines:
        todo_match = re.match(r"^- \[ \] (.+)$", line)
        if todo_match and not success and keyword.lower() in todo_match.group(1).lower():
            matched_text = todo_match.group(1).strip()
            today = datetime.now().strftime("%-m/%-d")
            new_lines.append(f"- [x] {matched_text} ✅ {today} 완료")
            success = True
        else:
            new_lines.append(line)
    return "\n".join(new_lines), success, matched_text


def add_task_to_content(content: str, task_text: str, deadline: str = "") -> str:
    if deadline:
        full_line = f"- [ ] {task_text} 📅 {deadline}"
    else:
        full_line = f"- [ ] {task_text}"
    result, inserted = [], False
    for line in content.split("\n"):
        result.append(line)
        if not inserted and "## 📌 할 일" in line:
            result.append(full_line)
            inserted = True
    return "\n".join(result)


def escape_md(text: str) -> str:
    for ch in r"_*[]()~`>#+-=|{}.!":
        text = text.replace(ch, f"\\{ch}")
    return text


def format_todo_message(todo_items: list) -> str:
    if not todo_items:
        return "📭 진행 중인 태스크가 없습니다\\."

    today = datetime.now().strftime("%-m/%-d")
    today_items = [t for t in todo_items if f"📅 {today}" in t["text"]]
    urgent = [t for t in todo_items if "🔴" in t["text"]]
    normal = [t for t in todo_items if "🟡" in t["text"]]
    others = [t for t in todo_items if "🔴" not in t["text"] and "🟡" not in t["text"]]

    lines = [f"📋 *진행 중인 태스크* \\({len(todo_items)}개\\)\n"]

    if today_items:
        lines.append("🚨 *오늘 마감*")
        for t in today_items:
            lines.append(f"  • {escape_md(clean_task_text(t['text']))}")
        lines.append("")

    if urgent:
        lines.append("🔴 *즉시 처리*")
        for t in urgent:
            dl = get_task_deadline(t["text"])
            dday = f" \\[{escape_md(get_dday_text(dl))}\\]" if dl else ""
            lines.append(f"  • {escape_md(clean_task_text(t['text']))}{dday}")
        lines.append("")

    if normal:
        lines.append("🟡 *우선 처리*")
        for t in normal:
            dl = get_task_deadline(t["text"])
            dday = f" \\[{escape_md(get_dday_text(dl))}\\]" if dl else ""
            lines.append(f"  • {escape_md(clean_task_text(t['text']))}{dday}")
        lines.append("")

    if others:
        lines.append("📌 *기타*")
        for t in others:
            dl = get_task_deadline(t["text"])
            dday = f" \\[{escape_md(get_dday_text(dl))}\\]" if dl else ""
            lines.append(f"  • {escape_md(clean_task_text(t['text']))}{dday}")

    return "\n".join(lines)


def get_draftable_tasks(todo_items: list) -> list:
    """초안 작성 가능한 태스크 필터링"""
    today = datetime.now().strftime("%-m/%-d")
    result = []
    for t in todo_items:
        text = t["text"].lower()
        has_deadline_today = f"📅 {today}" in t["text"]
        has_draft_keyword = any(kw in text for kw in DRAFT_KEYWORDS)
        if has_draft_keyword:
            result.append({**t, "is_today": has_deadline_today})
    return result


# ─── 태스크 메모/노트 관리 ──────────────────────────────

def load_notes() -> dict:
    """태스크별 메모 로드"""
    return load_json(NOTES_FILE, {})


def save_notes(notes: dict):
    """태스크별 메모 저장"""
    save_json(NOTES_FILE, notes)


def get_task_key(task_text: str) -> str:
    """태스크 텍스트에서 고유 키 생성 (우선순위 이모지, 날짜 제거)"""
    key = re.sub(r"[🔴🟡📅✅]\s*", "", task_text)
    key = re.sub(r"\d{1,2}/\d{1,2}[^\s]*", "", key)
    key = re.sub(r"\s+", " ", key).strip().lower()
    return key[:80]  # 최대 80자


def add_note_to_task(task_text: str, note: str) -> bool:
    """태스크에 메모 추가"""
    notes = load_notes()
    key = get_task_key(task_text)
    if key not in notes:
        notes[key] = {"task": task_text, "notes": [], "created": datetime.now().isoformat()}
    notes[key]["notes"].append({
        "text": note,
        "timestamp": datetime.now().strftime("%m/%d %H:%M"),
    })
    save_notes(notes)
    return True


def get_task_notes(task_text: str) -> list:
    """태스크의 메모 목록 조회"""
    notes = load_notes()
    key = get_task_key(task_text)
    if key in notes:
        return notes[key]["notes"]
    return []


def find_task_notes_by_keyword(keyword: str) -> list:
    """키워드로 태스크 메모 검색"""
    notes = load_notes()
    results = []
    for key, data in notes.items():
        if keyword.lower() in key or keyword.lower() in data.get("task", "").lower():
            results.append(data)
    return results


# ─── 주간 리포트 생성 ────────────────────────────────────

def generate_weekly_report(content: str) -> str:
    """TASKS.md 기반 주간 리포트 생성"""
    parsed = parse_tasks(content)
    todo = parsed["todo"]
    done = parsed["done"]

    now = datetime.now()
    week_start = (now - timedelta(days=now.weekday())).strftime("%-m/%-d")
    week_end = now.strftime("%-m/%-d")

    # 이번 주 완료 항목 필터링 (✅ M/D 완료 패턴)
    this_week_done = []
    for d in done:
        m = re.search(r"✅\s*(\d{1,2})/(\d{1,2})\s*완료", d["text"])
        if m:
            done_month, done_day = int(m.group(1)), int(m.group(2))
            try:
                done_date = now.replace(month=done_month, day=done_day)
                monday = now - timedelta(days=now.weekday())
                monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
                if done_date >= monday:
                    this_week_done.append(d)
            except ValueError:
                pass

    # 마감 임박 태스크
    deadline_tasks = []
    for t in todo:
        dl = get_task_deadline(t["text"])
        if dl:
            deadline_tasks.append({"task": t, "deadline": dl, "dday": get_dday_text(dl)})
    deadline_tasks.sort(key=lambda x: x["deadline"])

    # 리포트 텍스트 생성
    lines = [
        f"📊 *주간 업무 리포트* ({escape_md(week_start)} ~ {escape_md(week_end)})\n",
        f"━━━━━━━━━━━━━━━━━━━━\n",
    ]

    # 완료 항목
    lines.append(f"✅ *이번 주 완료* ({len(this_week_done)}건)")
    if this_week_done:
        for d in this_week_done:
            lines.append(f"  • {escape_md(clean_task_text(d['text']))}")
    else:
        lines.append("  \\(없음\\)")
    lines.append("")

    # 미완료 항목
    lines.append(f"📌 *진행 중* ({len(todo)}건)")
    urgent = [t for t in todo if "🔴" in t["text"]]
    normal = [t for t in todo if "🟡" in t["text"]]
    other = [t for t in todo if "🔴" not in t["text"] and "🟡" not in t["text"]]

    for t in urgent:
        dl = get_task_deadline(t["text"])
        dday = f" [{get_dday_text(dl)}]" if dl else ""
        lines.append(f"  🔴 {escape_md(clean_task_text(t['text']))}{escape_md(dday)}")
    for t in normal:
        dl = get_task_deadline(t["text"])
        dday = f" [{get_dday_text(dl)}]" if dl else ""
        lines.append(f"  🟡 {escape_md(clean_task_text(t['text']))}{escape_md(dday)}")
    for t in other[:5]:
        lines.append(f"  📌 {escape_md(clean_task_text(t['text']))}")
    if len(other) > 5:
        lines.append(f"  _\\.\\.\\. 외 {len(other)-5}건_")
    lines.append("")

    # 마감 임박
    upcoming = [dt for dt in deadline_tasks if (dt["deadline"] - now).days <= 7]
    if upcoming:
        lines.append("⏰ *다음 주 마감 임박*")
        for dt in upcoming[:5]:
            lines.append(f"  • {escape_md(clean_task_text(dt['task']['text']))} \\[{escape_md(dt['dday'])}\\]")
        lines.append("")

    # 통계
    total_tasks = len(todo) + len(this_week_done)
    completion_rate = round(len(this_week_done) / total_tasks * 100) if total_tasks > 0 else 0
    lines.append("📈 *주간 통계*")
    lines.append(f"  완료율: {completion_rate}% \\({len(this_week_done)}/{total_tasks}\\)")
    lines.append(f"  잔여 태스크: {len(todo)}건")

    return "\n".join(lines)


def generate_weekly_report_slack(content: str) -> str:
    """Slack 포스팅용 주간 리포트 (Slack mrkdwn 포맷)"""
    parsed = parse_tasks(content)
    todo = parsed["todo"]
    done = parsed["done"]

    now = datetime.now()
    week_start = (now - timedelta(days=now.weekday())).strftime("%-m/%-d")
    week_end = now.strftime("%-m/%-d")

    # 이번 주 완료 항목 필터링
    this_week_done = []
    for d in done:
        m = re.search(r"✅\s*(\d{1,2})/(\d{1,2})\s*완료", d["text"])
        if m:
            done_month, done_day = int(m.group(1)), int(m.group(2))
            try:
                done_date = now.replace(month=done_month, day=done_day)
                monday = now - timedelta(days=now.weekday())
                monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
                if done_date >= monday:
                    this_week_done.append(d)
            except ValueError:
                pass

    lines = [
        f"📊 *주간 업무 리포트* ({week_start} ~ {week_end})",
        "━━━━━━━━━━━━━━━━━━━━",
        "",
        f"✅ *이번 주 완료* ({len(this_week_done)}건)",
    ]

    if this_week_done:
        for d in this_week_done:
            lines.append(f"  • {clean_task_text(d['text'])}")
    else:
        lines.append("  (없음)")
    lines.append("")

    lines.append(f"📌 *진행 중* ({len(todo)}건)")
    for t in todo:
        priority = ""
        if "🔴" in t["text"]:
            priority = "🔴 "
        elif "🟡" in t["text"]:
            priority = "🟡 "
        dl = get_task_deadline(t["text"])
        dday = f" [{get_dday_text(dl)}]" if dl else ""
        lines.append(f"  {priority}{clean_task_text(t['text'])}{dday}")
    lines.append("")

    total_tasks = len(todo) + len(this_week_done)
    completion_rate = round(len(this_week_done) / total_tasks * 100) if total_tasks > 0 else 0
    lines.append(f"📈 완료율: {completion_rate}% ({len(this_week_done)}/{total_tasks}) | 잔여: {len(todo)}건")

    return "\n".join(lines)


def post_to_slack(channel: str, text: str) -> bool:
    """Slack 채널에 메시지 포스팅"""
    if not SLACK_BOT_TOKEN:
        logger.warning("SLACK_BOT_TOKEN not set, skipping Slack post")
        return False
    try:
        r = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={
                "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
                "Content-Type": "application/json",
            },
            json={"channel": channel, "text": text, "mrkdwn": True},
            timeout=10,
        )
        data = r.json()
        if not data.get("ok"):
            logger.error(f"Slack post error: {data.get('error')}")
            return False
        return True
    except Exception as e:
        logger.error(f"Slack post exception: {e}")
        return False


# ─── 대화 저장/로드 ─────────────────────────────────────

def load_json(path: Path, default=None):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default or {}


def save_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_conversation(user_id: str) -> list:
    return load_json(CONVERSATIONS_FILE).get(user_id, [])


def save_conversation(user_id: str, messages: list):
    convos = load_json(CONVERSATIONS_FILE)
    convos[user_id] = messages[-50:]
    save_json(CONVERSATIONS_FILE, convos)


def is_authorized(user_id: int) -> bool:
    return not ALLOWED_USER_IDS or user_id in ALLOWED_USER_IDS


# ─── Claude API ─────────────────────────────────────────

async def ask_claude(user_id: str, user_message: str) -> str:
    messages = get_conversation(user_id)
    messages.append({"role": "user", "content": user_message})
    try:
        response = client.messages.create(model=MODEL, max_tokens=2048, system=SYSTEM_PROMPT, messages=messages)
        assistant_msg = response.content[0].text
        messages.append({"role": "assistant", "content": assistant_msg})
        save_conversation(user_id, messages)
        return assistant_msg
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return f"⚠️ Claude API 오류: {str(e)}"


async def generate_draft(task_text: str) -> str:
    """태스크 텍스트 기반으로 Claude가 초안 생성"""
    clean_text = clean_task_text(task_text)
    prompt = (
        f"다음 업무 태스크에 대한 초안을 작성해줘:\n\n"
        f"태스크: {clean_text}\n\n"
        f"이메일이나 슬랙 메시지 초안이라면 수신자, 제목, 본문 형식으로 작성해줘. "
        f"보고서나 문서라면 주요 항목과 내용을 작성해줘. "
        f"간결하고 실무적으로 작성해줘. "
        f"게임 및 블록체인 비즈니스 맥락(넥써쓰 게임사업부)을 고려해줘."
    )
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        logger.error(f"Draft generation error: {e}")
        return f"⚠️ 초안 생성 오류: {str(e)}"


# ─── /task ConversationHandler ──────────────────────────

async def task_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return ConversationHandler.END
    keyboard = [
        [
            InlineKeyboardButton("🔴 긴급", callback_data="priority_urgent"),
            InlineKeyboardButton("🟡 보통", callback_data="priority_normal"),
            InlineKeyboardButton("📌 일반", callback_data="priority_low"),
        ],
        [InlineKeyboardButton("❌ 취소", callback_data="priority_cancel")],
    ]
    await update.message.reply_text(
        "우선순위를 선택해주세요:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return TASK_SELECT_PRIORITY


async def task_priority_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "priority_cancel":
        await query.edit_message_text("취소됐습니다.")
        return ConversationHandler.END
    priority_map = {
        "priority_urgent": ("🔴", "긴급"),
        "priority_normal": ("🟡", "보통"),
        "priority_low": ("", "일반"),
    }
    emoji, label = priority_map[query.data]
    context.user_data["task_priority"] = emoji
    context.user_data["task_priority_label"] = label
    await query.edit_message_text(f"[{label}] 선택됨.\n\n태스크 내용을 입력해주세요:")
    return TASK_INPUT_CONTENT


async def task_content_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    content = update.message.text.strip()
    context.user_data["task_content"] = content
    keyboard = [
        [
            InlineKeyboardButton("📅 마감일 있음", callback_data="deadline_yes"),
            InlineKeyboardButton("없음", callback_data="deadline_no"),
        ]
    ]
    await update.message.reply_text(
        f"내용: {content}\n\n마감일이 있나요?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return TASK_INPUT_DEADLINE


async def task_deadline_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "deadline_no":
        await query.edit_message_text("저장 중...")
        await _save_task(query, context, deadline="")
        return ConversationHandler.END
    else:
        await query.edit_message_text("마감일을 입력해주세요 (예: 3/20):")
        return TASK_INPUT_DEADLINE


async def task_deadline_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deadline_text = update.message.text.strip()
    if not re.match(r"^\d{1,2}/\d{1,2}$", deadline_text):
        await update.message.reply_text("M/D 형식으로 입력해주세요. 예) 3/20")
        return TASK_INPUT_DEADLINE
    await _save_task_message(update, context, deadline=deadline_text)
    return ConversationHandler.END


async def _save_task(query, context: ContextTypes.DEFAULT_TYPE, deadline: str):
    priority = context.user_data.get("task_priority", "")
    label = context.user_data.get("task_priority_label", "일반")
    content = context.user_data.get("task_content", "")
    full_text = f"{priority} {content}".strip() if priority else content
    gist_content = gist_read()
    if not gist_content:
        await query.edit_message_text("⚠️ Gist 읽기 실패.")
        return
    if gist_write(add_task_to_content(gist_content, full_text, deadline)):
        deadline_text = f" | 마감: {deadline}" if deadline else ""
        await query.edit_message_text(
            f"✅ 태스크 추가됨! [{label}]{deadline_text}\n📌 {full_text}"
        )
    else:
        await query.edit_message_text("⚠️ Gist 저장 실패.")


async def _save_task_message(update: Update, context: ContextTypes.DEFAULT_TYPE, deadline: str):
    priority = context.user_data.get("task_priority", "")
    label = context.user_data.get("task_priority_label", "일반")
    content = context.user_data.get("task_content", "")
    full_text = f"{priority} {content}".strip() if priority else content
    gist_content = gist_read()
    if not gist_content:
        await update.message.reply_text("⚠️ Gist 읽기 실패.")
        return
    if gist_write(add_task_to_content(gist_content, full_text, deadline)):
        deadline_text = f" | 마감: {deadline}" if deadline else ""
        await update.message.reply_text(
            f"✅ 태스크 추가됨! [{label}]{deadline_text}\n📌 {full_text}"
        )
    else:
        await update.message.reply_text("⚠️ Gist 저장 실패.")


async def task_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("취소됐습니다.")
    return ConversationHandler.END


# ─── 초안 작성 CallbackQuery ────────────────────────────

async def draft_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("draft_yes_"):
        task_index = int(query.data.replace("draft_yes_", ""))
        tasks_data = context.bot_data.get("draftable_tasks", [])
        if task_index >= len(tasks_data):
            await query.edit_message_text("⚠️ 태스크를 찾을 수 없습니다.")
            return
        task = tasks_data[task_index]
        await query.edit_message_text(f"✍️ 초안 작성 중...\n📌 {clean_task_text(task['text'])}")
        draft = await generate_draft(task["text"])
        header = f"📝 *초안 작성 완료*\n태스크: {escape_md(clean_task_text(task['text']))}\n\n"
        full_msg = header + escape_md(draft)
        if len(full_msg) > 4000:
            await context.bot.send_message(chat_id=query.message.chat_id, text=header, parse_mode="MarkdownV2")
            chunks = [draft[i:i+3500] for i in range(0, len(draft), 3500)]
            for chunk in chunks:
                await context.bot.send_message(chat_id=query.message.chat_id, text=chunk)
        else:
            await context.bot.send_message(chat_id=query.message.chat_id, text=full_msg, parse_mode="MarkdownV2")

    elif query.data.startswith("draft_no_"):
        await query.edit_message_text("초안 작성을 건너뜁니다.")


# ─── 핸들러 ─────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("🚫 권한이 없습니다.")
        return
    await update.message.reply_text(
        "👋 안녕하세요\\! Claude 업무 비서입니다\\.\n\n"
        "📌 *명령어:*\n"
        "/tasks \\- 태스크 목록 \\(D\\-day 포함\\)\n"
        "/task \\- 태스크 추가 \\(버튼 선택\\)\n"
        "/done 키워드 \\- 완료 처리\n"
        "/note 키워드 \\| 메모 \\- 태스크에 메모 첨부\n"
        "/notes 키워드 \\- 태스크 메모 조회\n"
        "/report \\- 주간 리포트 생성\n"
        "/remind HH:MM 내용 \\- 알림\n"
        "/remind\\_after 분 내용 \\- N분 후 알림\n"
        "/remind\\_date M/D HH:MM 내용 \\- 날짜 알림\n"
        "/clear \\- 대화 초기화",
        parse_mode="MarkdownV2",
    )


async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    content = gist_read()
    if not content:
        await update.message.reply_text("⚠️ Gist에서 TASKS\\.md를 읽지 못했습니다\\.", parse_mode="MarkdownV2")
        return
    parsed = parse_tasks(content)
    await update.message.reply_text(format_todo_message(parsed["todo"]), parse_mode="MarkdownV2")


async def done_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text(
            "사용법: `/done 키워드`\n예\\) `/done Verse8`", parse_mode="MarkdownV2"
        )
        return
    keyword = " ".join(context.args)
    content = gist_read()
    if not content:
        await update.message.reply_text("⚠️ Gist 읽기 실패\\.", parse_mode="MarkdownV2")
        return
    new_content, success, matched_text = mark_done(content, keyword)
    if success:
        if gist_write(new_content):
            await update.message.reply_text(
                f"🎉 완료 처리됨\\!\n~~{escape_md(matched_text)}~~", parse_mode="MarkdownV2"
            )
        else:
            await update.message.reply_text("⚠️ Gist 저장 실패\\.", parse_mode="MarkdownV2")
    else:
        parsed = parse_tasks(content)
        lines = [f"⚠️ `{escape_md(keyword)}` 키워드 매칭 없음\\.\n", "*현재 미완료 태스크:*"]
        for t in parsed["todo"][:10]:
            lines.append(f"• {escape_md(clean_task_text(t['text'])[:60])}")
        await update.message.reply_text("\n".join(lines), parse_mode="MarkdownV2")


# ─── /note, /notes - 태스크 메모 첨부 ───────────────────

async def add_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/note 키워드 | 메모 내용"""
    if not is_authorized(update.effective_user.id):
        return

    text = " ".join(context.args) if context.args else ""
    if "|" not in text:
        await update.message.reply_text(
            "사용법: `/note 키워드 | 메모 내용`\n"
            "예\\) `/note 드래곤소드 | 웹젠 지분 25% 보유 확인 필요`\n"
            "예\\) `/note V8 | 넥슨 공동투자 $60M 밸류`",
            parse_mode="MarkdownV2"
        )
        return

    parts = text.split("|", 1)
    keyword = parts[0].strip()
    note_text = parts[1].strip()

    if not keyword or not note_text:
        await update.message.reply_text("키워드와 메모 내용을 모두 입력해주세요\\.", parse_mode="MarkdownV2")
        return

    # 해당 키워드에 매칭되는 태스크 찾기
    content = gist_read()
    if not content:
        # Gist 실패해도 메모 자체는 저장
        add_note_to_task(keyword, note_text)
        await update.message.reply_text(
            f"📎 메모 저장됨 \\(태스크 매칭 없이 키워드 저장\\)\n"
            f"키워드: `{escape_md(keyword)}`\n"
            f"메모: {escape_md(note_text)}",
            parse_mode="MarkdownV2"
        )
        return

    parsed = parse_tasks(content)
    matched_task = None
    for t in parsed["todo"]:
        if keyword.lower() in t["text"].lower():
            matched_task = t
            break

    if matched_task:
        add_note_to_task(matched_task["text"], note_text)
        existing_notes = get_task_notes(matched_task["text"])
        await update.message.reply_text(
            f"📎 메모 추가됨\\! \\(총 {len(existing_notes)}개\\)\n"
            f"태스크: {escape_md(clean_task_text(matched_task['text'])[:50])}\n"
            f"메모: {escape_md(note_text)}",
            parse_mode="MarkdownV2"
        )
    else:
        # 매칭되는 태스크 없어도 키워드 기준으로 저장
        add_note_to_task(keyword, note_text)
        await update.message.reply_text(
            f"📎 메모 저장됨 \\(매칭 태스크 없음, 키워드로 저장\\)\n"
            f"키워드: `{escape_md(keyword)}`\n"
            f"메모: {escape_md(note_text)}",
            parse_mode="MarkdownV2"
        )


async def view_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/notes 키워드 - 태스크 메모 조회"""
    if not is_authorized(update.effective_user.id):
        return

    if not context.args:
        # 전체 메모 요약 표시
        notes = load_notes()
        if not notes:
            await update.message.reply_text("📭 저장된 메모가 없습니다\\.", parse_mode="MarkdownV2")
            return
        lines = [f"📎 *저장된 메모 목록* \\({len(notes)}개 태스크\\)\n"]
        for key, data in list(notes.items())[:10]:
            task_display = data.get("task", key)[:40]
            count = len(data.get("notes", []))
            lines.append(f"  • {escape_md(task_display)} \\({count}개\\)")
        if len(notes) > 10:
            lines.append(f"\n_\\.\\.\\. 외 {len(notes)-10}개_")
        lines.append("\n`/notes 키워드`로 상세 조회")
        await update.message.reply_text("\n".join(lines), parse_mode="MarkdownV2")
        return

    keyword = " ".join(context.args)
    results = find_task_notes_by_keyword(keyword)

    if not results:
        await update.message.reply_text(
            f"📭 `{escape_md(keyword)}` 관련 메모 없음\\.", parse_mode="MarkdownV2"
        )
        return

    for data in results[:3]:
        task_display = clean_task_text(data.get("task", ""))[:50]
        lines = [f"📎 *{escape_md(task_display)}*\n"]
        for note in data.get("notes", []):
            lines.append(f"  💬 {escape_md(note['text'])}")
            lines.append(f"     _{escape_md(note.get('timestamp', ''))}_")
        await update.message.reply_text("\n".join(lines), parse_mode="MarkdownV2")


# ─── /report - 주간 리포트 ──────────────────────────────

async def weekly_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/report - 주간 리포트 생성 + Slack 포스팅 옵션"""
    if not is_authorized(update.effective_user.id):
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    content = gist_read()
    if not content:
        await update.message.reply_text("⚠️ Gist 읽기 실패\\.", parse_mode="MarkdownV2")
        return

    report = generate_weekly_report(content)
    await update.message.reply_text(report, parse_mode="MarkdownV2")

    # Slack 포스팅 버튼
    keyboard = [
        [
            InlineKeyboardButton("📤 Slack에 포스팅", callback_data="report_slack"),
            InlineKeyboardButton("❌ 닫기", callback_data="report_close"),
        ]
    ]
    await update.message.reply_text(
        "Slack에 주간 리포트를 포스팅할까요?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def report_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """주간 리포트 Slack 포스팅 콜백"""
    query = update.callback_query
    await query.answer()

    if query.data == "report_close":
        await query.edit_message_text("확인.")
        return

    if query.data == "report_slack":
        await query.edit_message_text("📤 Slack 포스팅 중...")

        content = gist_read()
        if not content:
            await query.edit_message_text("⚠️ Gist 읽기 실패.")
            return

        slack_report = generate_weekly_report_slack(content)
        success = post_to_slack(SLACK_REPORT_CHANNEL, slack_report)

        if success:
            await query.edit_message_text("✅ Slack 포스팅 완료! (전준영 DM)")
        else:
            if not SLACK_BOT_TOKEN:
                await query.edit_message_text(
                    "⚠️ SLACK_BOT_TOKEN이 설정되지 않았습니다.\n"
                    "Railway Variables에 SLACK_BOT_TOKEN을 추가해주세요."
                )
            else:
                await query.edit_message_text("⚠️ Slack 포스팅 실패. 로그를 확인해주세요.")


# ─── 알림 ────────────────────────────────────────────────

async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    if len(context.args) < 2:
        await update.message.reply_text("사용법: `/remind HH:MM 내용`", parse_mode="MarkdownV2")
        return
    time_str, reminder_text = context.args[0], " ".join(context.args[1:])
    try:
        hour, minute = map(int, time_str.split(":"))
        now = datetime.now()
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        context.job_queue.run_once(send_reminder, when=(target - now).total_seconds(),
                                   data={"chat_id": update.effective_chat.id, "text": reminder_text})
        await update.message.reply_text(
            f"⏰ 알림 설정\\!\n시각: *{escape_md(target.strftime('%m/%d %H:%M'))}*\n내용: {escape_md(reminder_text)}",
            parse_mode="MarkdownV2")
    except ValueError:
        await update.message.reply_text("시간 형식 오류\\. HH:MM으로 입력해주세요\\.", parse_mode="MarkdownV2")


async def remind_after(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    if len(context.args) < 2:
        await update.message.reply_text("사용법: `/remind_after 분 내용`", parse_mode="MarkdownV2")
        return
    try:
        minutes = int(context.args[0])
    except ValueError:
        await update.message.reply_text("숫자를 입력해주세요\\.", parse_mode="MarkdownV2")
        return
    reminder_text = " ".join(context.args[1:])
    context.job_queue.run_once(send_reminder, when=minutes * 60,
                               data={"chat_id": update.effective_chat.id, "text": reminder_text})
    await update.message.reply_text(
        f"⏰ {minutes}분 후 알림\\!\n내용: {escape_md(reminder_text)}", parse_mode="MarkdownV2")


async def remind_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    if len(context.args) < 3:
        await update.message.reply_text("사용법: `/remind_date M/D HH:MM 내용`", parse_mode="MarkdownV2")
        return
    try:
        month, day = map(int, context.args[0].split("/"))
        hour, minute = map(int, context.args[1].split(":"))
        reminder_text = " ".join(context.args[2:])
        now = datetime.now()
        target = now.replace(month=month, day=day, hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now:
            target = target.replace(year=target.year + 1)
        context.job_queue.run_once(send_reminder, when=(target - now).total_seconds(),
                                   data={"chat_id": update.effective_chat.id, "text": reminder_text})
        await update.message.reply_text(
            f"📅 알림 설정\\!\n날짜: *{escape_md(target.strftime('%Y/%m/%d %H:%M'))}*\n내용: {escape_md(reminder_text)}",
            parse_mode="MarkdownV2")
    except ValueError:
        await update.message.reply_text("형식 오류\\. `/remind_date M/D HH:MM 내용`", parse_mode="MarkdownV2")


async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    await context.bot.send_message(
        chat_id=data["chat_id"],
        text=f"🔔 *리마인더*\n\n{escape_md(data['text'])}",
        parse_mode="MarkdownV2"
    )


# ─── D-day 마감 임박 자동 알림 ──────────────────────────

async def deadline_check(context: ContextTypes.DEFAULT_TYPE):
    """매일 오전 + 4시간 알림 시 마감 임박 태스크 별도 강조 알림"""
    if not ALLOWED_USER_IDS:
        return

    content = gist_read()
    if not content:
        return

    parsed = parse_tasks(content)
    todo = parsed["todo"]

    now = datetime.now()
    alerts = []

    for t in todo:
        dl = get_task_deadline(t["text"])
        if not dl:
            continue
        diff_days = (dl.replace(hour=0, minute=0, second=0, microsecond=0) -
                     now.replace(hour=0, minute=0, second=0, microsecond=0)).days

        if diff_days < 0:
            alerts.append(("🚨 *마감 초과\\!*", t, f"D\\+{abs(diff_days)}"))
        elif diff_days == 0:
            alerts.append(("🔥 *오늘 마감\\!*", t, "D\\-Day"))
        elif diff_days == 1:
            alerts.append(("⏰ *내일 마감\\!*", t, "D\\-1"))

    if not alerts:
        return

    lines = ["🚨 *마감 임박 알림*\n"]
    for label, task, dday in alerts:
        lines.append(f"{label} \\[{dday}\\]")
        lines.append(f"  📌 {escape_md(clean_task_text(task['text']))}")
        # 해당 태스크의 메모도 표시
        task_notes = get_task_notes(task["text"])
        if task_notes:
            latest = task_notes[-1]
            lines.append(f"  💬 _{escape_md(latest['text'][:50])}_")
        lines.append("")

    msg = "\n".join(lines)
    for user_id in ALLOWED_USER_IDS:
        try:
            await context.bot.send_message(chat_id=user_id, text=msg, parse_mode="MarkdownV2")
        except Exception as e:
            logger.error(f"Deadline check failed for {user_id}: {e}")


# ─── 4시간마다 자동 태스크 현황 + 초안 제안 ─────────────

async def auto_task_update(context: ContextTypes.DEFAULT_TYPE):
    if not ALLOWED_USER_IDS:
        return

    content = gist_read()
    if not content:
        logger.warning("auto_task_update: Gist read failed")
        return

    parsed = parse_tasks(content)
    todo = parsed["todo"]
    if not todo:
        return

    now = datetime.now()
    status_msg = f"🕐 *{escape_md(now.strftime('%H:%M'))} 업무 현황*\n\n" + format_todo_message(todo)

    for user_id in ALLOWED_USER_IDS:
        try:
            await context.bot.send_message(chat_id=user_id, text=status_msg, parse_mode="MarkdownV2")
        except Exception as e:
            logger.error(f"auto_task_update status failed for {user_id}: {e}")

    # D-day 체크도 함께 실행
    await deadline_check(context)

    # 초안 작성 가능한 태스크 확인
    draftable = get_draftable_tasks(todo)
    if not draftable:
        return

    context.bot_data["draftable_tasks"] = draftable

    for user_id in ALLOWED_USER_IDS:
        try:
            draft_lines = ["✍️ *초안 작성 가능한 태스크가 있습니다\\.*\n대신 초안을 작성해드릴까요?\n"]
            keyboard_rows = []
            for i, task in enumerate(draftable[:5]):
                clean = clean_task_text(task["text"])
                today_mark = " 🚨" if task.get("is_today") else ""
                draft_lines.append(f"{i+1}\\. {escape_md(clean)}{today_mark}")
                keyboard_rows.append([
                    InlineKeyboardButton(f"✍️ {i+1}번 초안 작성", callback_data=f"draft_yes_{i}"),
                    InlineKeyboardButton(f"❌ {i+1}번 건너뜀", callback_data=f"draft_no_{i}"),
                ])
            await context.bot.send_message(
                chat_id=user_id,
                text="\n".join(draft_lines),
                parse_mode="MarkdownV2",
                reply_markup=InlineKeyboardMarkup(keyboard_rows)
            )
        except Exception as e:
            logger.error(f"auto_task_update draft failed for {user_id}: {e}")


# ─── 매일 아침 알림 ──────────────────────────────────────

async def daily_task_reminder(context: ContextTypes.DEFAULT_TYPE):
    if not ALLOWED_USER_IDS:
        return
    content = gist_read()
    if not content:
        return
    parsed = parse_tasks(content)
    todo = parsed["todo"]
    if not todo:
        return

    today = datetime.now().strftime("%-m/%-d")
    today_items = [t for t in todo if f"📅 {today}" in t["text"]]
    urgent = [t for t in todo if "🔴" in t["text"]]
    normal = [t for t in todo if "🟡" in t["text"]]
    others = [t for t in todo if "🔴" not in t["text"] and "🟡" not in t["text"]]

    lines = [f"🌅 *오늘의 태스크* \\({len(todo)}개\\)\n"]

    if today_items:
        lines.append("🚨 *오늘 마감*")
        for t in today_items:
            lines.append(f"  • {escape_md(clean_task_text(t['text']))}")
        lines.append("")

    if urgent:
        lines.append("🔴 *즉시 처리*")
        for t in urgent:
            dl = get_task_deadline(t["text"])
            dday = f" \\[{escape_md(get_dday_text(dl))}\\]" if dl else ""
            lines.append(f"  • {escape_md(clean_task_text(t['text']))}{dday}")
        lines.append("")

    if normal:
        lines.append("🟡 *우선 처리*")
        for t in normal:
            dl = get_task_deadline(t["text"])
            dday = f" \\[{escape_md(get_dday_text(dl))}\\]" if dl else ""
            lines.append(f"  • {escape_md(clean_task_text(t['text']))}{dday}")
        lines.append("")

    if others:
        lines.append("📌 *기타*")
        for t in others[:5]:
            lines.append(f"  • {escape_md(clean_task_text(t['text']))}")
        if len(others) > 5:
            lines.append(f"  _\\.\\.\\. 외 {len(others)-5}개_")

    msg = "\n".join(lines)
    for user_id in ALLOWED_USER_IDS:
        try:
            await context.bot.send_message(chat_id=user_id, text=msg, parse_mode="MarkdownV2")
        except Exception as e:
            logger.error(f"Daily reminder failed for {user_id}: {e}")

    # 아침에도 D-day 체크 실행
    await deadline_check(context)


# ─── 주간 리포트 자동 포스팅 (매주 금요일 18:00) ────────

async def auto_weekly_report(context: ContextTypes.DEFAULT_TYPE):
    """매주 금요일 자동 주간 리포트 생성 + Slack 포스팅"""
    content = gist_read()
    if not content:
        logger.warning("auto_weekly_report: Gist read failed")
        return

    # Slack 포스팅
    slack_report = generate_weekly_report_slack(content)
    slack_success = post_to_slack(SLACK_REPORT_CHANNEL, slack_report)

    # Telegram에도 알림
    report = generate_weekly_report(content)
    for user_id in ALLOWED_USER_IDS:
        try:
            await context.bot.send_message(chat_id=user_id, text=report, parse_mode="MarkdownV2")
            slack_status = "✅ Slack 포스팅 완료" if slack_success else "⚠️ Slack 포스팅 실패"
            await context.bot.send_message(chat_id=user_id, text=f"📊 주간 리포트 자동 생성됨\n{slack_status}")
        except Exception as e:
            logger.error(f"auto_weekly_report failed for {user_id}: {e}")


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    save_conversation(str(update.effective_user.id), [])
    await update.message.reply_text("🔄 대화 기록이 초기화되었습니다.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = await ask_claude(str(update.effective_user.id), update.message.text)
    if len(reply) > 4000:
        for chunk in [reply[i:i+4000] for i in range(0, len(reply), 4000)]:
            await update.message.reply_text(chunk)
    else:
        await update.message.reply_text(reply)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    doc = update.message.document
    caption = update.message.caption or "이 파일의 내용을 분석하고 요약해줘."
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        file_bytes = await (await doc.get_file()).download_as_bytearray()
        ext = Path(doc.file_name).suffix.lower() if doc.file_name else ""
        if ext in {".txt", ".py", ".js", ".json", ".csv", ".md", ".html", ".yaml", ".yml", ".ts"}:
            content = file_bytes.decode("utf-8", errors="replace")
            reply = await ask_claude(str(update.effective_user.id),
                                     f"[파일: {doc.file_name}]\n\n```\n{content[:10000]}\n```\n\n{caption}")
        else:
            reply = f"📎 {doc.file_name}\n현재 텍스트 파일만 분석 가능합니다."
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"⚠️ 파일 처리 오류: {str(e)}")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    caption = update.message.caption or "이 이미지를 분석해줘."
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        import base64
        file_bytes = await (await update.message.photo[-1].get_file()).download_as_bytearray()
        b64 = base64.b64encode(bytes(file_bytes)).decode("utf-8")
        response = client.messages.create(
            model=MODEL, max_tokens=2048, system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
                {"type": "text", "text": caption},
            ]}])
        await update.message.reply_text(response.content[0].text)
    except Exception as e:
        await update.message.reply_text(f"⚠️ 이미지 처리 오류: {str(e)}")


# ─── 메인 ────────────────────────────────────────────────

async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "봇 시작"),
        BotCommand("tasks", "태스크 목록 (D-day 포함)"),
        BotCommand("task", "태스크 추가 (버튼 선택)"),
        BotCommand("done", "태스크 완료 (키워드)"),
        BotCommand("note", "태스크에 메모 첨부"),
        BotCommand("notes", "태스크 메모 조회"),
        BotCommand("report", "주간 리포트 생성"),
        BotCommand("remind", "시각 알림"),
        BotCommand("remind_after", "N분 후 알림"),
        BotCommand("remind_date", "날짜 지정 알림"),
        BotCommand("clear", "대화 초기화"),
    ])

    # 매일 아침 9시 알림
    MORNING_HOUR = int(os.environ.get("MORNING_REMINDER_HOUR", "9"))
    application.job_queue.run_daily(
        daily_task_reminder,
        time=datetime.now().replace(hour=MORNING_HOUR, minute=0, second=0).time(),
        name="daily_morning_reminder",
    )

    # 4시간마다 자동 태스크 현황 + D-day 체크 + 초안 제안
    application.job_queue.run_repeating(
        auto_task_update,
        interval=14400,  # 4시간 = 14400초
        first=14400,     # 봇 시작 후 4시간 뒤부터 시작
        name="auto_task_update",
    )

    # 매주 금요일 18:00 주간 리포트 자동 포스팅
    application.job_queue.run_daily(
        auto_weekly_report,
        time=datetime.now().replace(hour=18, minute=0, second=0).time(),
        days=(4,),  # 금요일 = 4 (Monday=0)
        name="weekly_report_friday",
    )

    logger.info(f"✅ Gist ID: {GIST_ID}")
    logger.info(f"✅ Daily reminder: {MORNING_HOUR}:00")
    logger.info("✅ Auto task update: every 4 hours")
    logger.info("✅ Weekly report: Friday 18:00")
    logger.info(f"✅ Slack report channel: {SLACK_REPORT_CHANNEL}")


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).post_init(post_init).build()

    # /task ConversationHandler
    task_conv = ConversationHandler(
        entry_points=[CommandHandler("task", task_start)],
        states={
            TASK_SELECT_PRIORITY: [CallbackQueryHandler(task_priority_selected, pattern="^priority_")],
            TASK_INPUT_CONTENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, task_content_received)],
            TASK_INPUT_DEADLINE: [
                CallbackQueryHandler(task_deadline_choice, pattern="^deadline_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, task_deadline_received),
            ],
        },
        fallbacks=[CommandHandler("cancel", task_cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tasks", list_tasks))
    app.add_handler(task_conv)
    app.add_handler(CommandHandler("done", done_task))
    app.add_handler(CommandHandler("note", add_note))
    app.add_handler(CommandHandler("notes", view_notes))
    app.add_handler(CommandHandler("report", weekly_report))
    app.add_handler(CommandHandler("remind", remind))
    app.add_handler(CommandHandler("remind_after", remind_after))
    app.add_handler(CommandHandler("remind_date", remind_date))
    app.add_handler(CommandHandler("clear", clear))

    # 초안 + 리포트 CallbackQuery
    app.add_handler(CallbackQueryHandler(draft_callback, pattern="^draft_"))
    app.add_handler(CallbackQueryHandler(report_callback, pattern="^report_"))

    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🚀 Bot started with D-day + Weekly Report + Task Notes!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
