"""
Claude Telegram Bot - GitHub Gist TASKS.md 연동 버전
Railway 배포용
"""

import os
import re
import json
import logging
import requests
from datetime import datetime, timedelta
from pathlib import Path

import anthropic
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
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

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
CONVERSATIONS_FILE = DATA_DIR / "conversations.json"

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# ─── Gist read/write ────────────────────────────────────

def gist_read() -> str:
    try:
        # Public Gist는 토큰 없이 읽기 가능
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
    """표시용 텍스트 정리 - 날짜 태그 유지하되 불필요한 텍스트 제거"""
    text = re.sub(r"📅 \d+월 \d+일[^\n]*추가", "", text)
    text = re.sub(r"✅ \d+/\d+[^\n]*완료", "", text)
    return text.strip()


def get_deadline(text: str) -> str:
    """태스크 텍스트에서 마감일 추출. 예: '세마인 제출 📅 3/17' → '3/17'"""
    match = re.search(r"📅 (\d{1,2}/\d{1,2})$", text.strip())
    if match:
        return match.group(1)
    return ""


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
            lines.append(f"  • {escape_md(clean_task_text(t['text']))}")
        lines.append("")

    if normal:
        lines.append("🟡 *우선 처리*")
        for t in normal:
            lines.append(f"  • {escape_md(clean_task_text(t['text']))}")
        lines.append("")

    if others:
        lines.append("📌 *기타*")
        for t in others:
            lines.append(f"  • {escape_md(clean_task_text(t['text']))}")

    return "\n".join(lines)


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


# ─── 핸들러 ─────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("🚫 권한이 없습니다.")
        return
    await update.message.reply_text(
        "👋 안녕하세요\\! Claude 업무 비서입니다\\.\n\n"
        "📌 *명령어:*\n"
        "/tasks \\- 태스크 목록\n"
        "/task urgent/normal/low 내용 마감일 \\- 태스크 추가\n"
        "/done 키워드 \\- 완료 처리\n"
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


async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    args = context.args if context.args else []
    if not args:
        await update.message.reply_text(
            "사용법: /task \\[urgent/normal/low\\] 내용 \\[마감일 M/D\\]\n"
            "예\\) /task urgent 세마인베스트먼트 제출 3/17\n"
            "예\\) /task normal Verse8 계약 확인\n"
            "예\\) /task low 일본 여행 계획",
            parse_mode="MarkdownV2"
        )
        return

    # 우선순위 파싱
    priority_map = {"urgent": "🔴", "normal": "🟡", "low": ""}
    if args[0].lower() in priority_map:
        priority = priority_map[args[0].lower()]
        remaining = args[1:]
    else:
        priority = ""
        remaining = args

    if not remaining:
        await update.message.reply_text("태스크 내용을 입력해주세요\\.", parse_mode="MarkdownV2")
        return

    # 마감일 파싱 (마지막 인자가 M/D 형식이면)
    deadline = ""
    if re.match(r"^\d{1,2}/\d{1,2}$", remaining[-1]):
        deadline = remaining[-1]
        task_body = " ".join(remaining[:-1])
    else:
        task_body = " ".join(remaining)

    # 최종 태스크 텍스트
    full_text = f"{priority} {task_body}".strip() if priority else task_body

    content = gist_read()
    if not content:
        await update.message.reply_text("⚠️ Gist 읽기 실패\\.", parse_mode="MarkdownV2")
        return

    if gist_write(add_task_to_content(content, full_text, deadline)):
        label_map = {"🔴": "긴급", "🟡": "보통", "": "일반"}
        priority_label = label_map.get(priority, "일반")
        deadline_text = f" \\| 마감: {escape_md(deadline)}" if deadline else ""
        await update.message.reply_text(
            f"✅ 태스크 추가됨\\! \\[{priority_label}\\]{deadline_text}\n📌 {escape_md(full_text)}",
            parse_mode="MarkdownV2"
        )
    else:
        await update.message.reply_text("⚠️ Gist 저장 실패\\.", parse_mode="MarkdownV2")


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
            lines.append(f"  • {escape_md(clean_task_text(t['text']))}")
        lines.append("")

    if normal:
        lines.append("🟡 *우선 처리*")
        for t in normal:
            lines.append(f"  • {escape_md(clean_task_text(t['text']))}")
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
        BotCommand("tasks", "TASKS.md 목록"),
        BotCommand("task", "태스크 추가"),
        BotCommand("done", "태스크 완료 (키워드)"),
        BotCommand("remind", "시각 알림"),
        BotCommand("remind_after", "N분 후 알림"),
        BotCommand("remind_date", "날짜 지정 알림"),
        BotCommand("clear", "대화 초기화"),
    ])
    MORNING_HOUR = int(os.environ.get("MORNING_REMINDER_HOUR", "9"))
    application.job_queue.run_daily(
        daily_task_reminder,
        time=datetime.now().replace(hour=MORNING_HOUR, minute=0, second=0).time(),
        name="daily_morning_reminder",
    )
    logger.info(f"✅ Gist ID: {GIST_ID}")
    logger.info(f"✅ Daily reminder: {MORNING_HOUR}:00")


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tasks", list_tasks))
    app.add_handler(CommandHandler("task", add_task))
    app.add_handler(CommandHandler("done", done_task))
    app.add_handler(CommandHandler("remind", remind))
    app.add_handler(CommandHandler("remind_after", remind_after))
    app.add_handler(CommandHandler("remind_date", remind_date))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("🚀 Bot started with GitHub Gist TASKS.md integration!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
