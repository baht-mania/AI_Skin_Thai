"""
Claude Telegram Bot - 대화 + 알림 + 태스크 관리 + 파일 처리
Railway/Fly.io 등 클라우드 서버에 배포하여 24시간 운영 가능
"""

import os
import json
import logging
import asyncio
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

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
TASKS_FILE = DATA_DIR / "tasks.json"
CONVERSATIONS_FILE = DATA_DIR / "conversations.json"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─── Claude 클라이언트 ──────────────────────────────────
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# ─── 데이터 저장/로드 ──────────────────────────────────
def load_json(path: Path, default=None):
    if default is None:
        default = {}
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def save_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_conversation(user_id: str) -> list:
    convos = load_json(CONVERSATIONS_FILE)
    return convos.get(user_id, [])


def save_conversation(user_id: str, messages: list):
    convos = load_json(CONVERSATIONS_FILE)
    # 최근 50개 메시지만 유지 (토큰 절약)
    convos[user_id] = messages[-50:]
    save_json(CONVERSATIONS_FILE, convos)


def get_tasks() -> list:
    return load_json(TASKS_FILE, default=[])


def save_tasks(tasks: list):
    save_json(TASKS_FILE, tasks)


# ─── 권한 체크 ─────────────────────────────────────────
def is_authorized(user_id: int) -> bool:
    if not ALLOWED_USER_IDS:
        return True  # 설정 안 하면 누구나 사용 가능
    return user_id in ALLOWED_USER_IDS


# ─── Claude API 호출 ──────────────────────────────────
async def ask_claude(user_id: str, user_message: str) -> str:
    messages = get_conversation(user_id)
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        assistant_msg = response.content[0].text
        messages.append({"role": "assistant", "content": assistant_msg})
        save_conversation(user_id, messages)
        return assistant_msg
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return f"⚠️ Claude API 오류: {str(e)}"


# ─── 텔레그램 핸들러 ──────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("🚫 권한이 없습니다.")
        return
    await update.message.reply_text(
        "👋 안녕하세요! Claude 업무 비서입니다.\n\n"
        "📌 **사용 가능한 명령어:**\n"
        "/chat - 일반 대화 (기본 모드)\n"
        "/task 내용 - 태스크 추가\n"
        "/tasks - 태스크 목록 보기\n"
        "/done 번호 - 태스크 완료 처리\n"
        "/remind HH:MM 내용 - 알림 설정\n"
        "/remind_after 분 내용 - N분 후 알림\n"
        "/clear - 대화 기록 초기화\n"
        "/help - 도움말",
        parse_mode="Markdown",
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    await update.message.reply_text(
        "🤖 **Claude 업무 비서 사용법**\n\n"
        "**💬 대화**: 메시지를 보내면 Claude가 답변합니다.\n"
        "예) '블록체인 게임의 토큰 이코노미 설계 방법 알려줘'\n\n"
        "**📋 태스크 관리**:\n"
        "`/task 투자자 미팅 자료 준비` → 추가\n"
        "`/tasks` → 전체 목록\n"
        "`/done 1` → 1번 완료\n\n"
        "**⏰ 알림**:\n"
        "`/remind 14:00 팀 미팅` → 오후 2시 알림\n"
        "`/remind_after 30 보고서 제출` → 30분 후 알림\n\n"
        "**📎 파일 처리**:\n"
        "파일(문서/이미지)을 보내면 Claude가 분석합니다.\n\n"
        "**🔄 초기화**:\n"
        "`/clear` → 대화 기록 리셋",
        parse_mode="Markdown",
    )


# ─── 태스크 관리 ──────────────────────────────────────

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("사용법: `/task 할 일 내용`", parse_mode="Markdown")
        return

    tasks = get_tasks()
    task = {
        "id": len(tasks) + 1,
        "content": text,
        "created": datetime.now().isoformat(),
        "done": False,
        "user_id": update.effective_user.id,
    }
    tasks.append(task)
    save_tasks(tasks)
    await update.message.reply_text(f"✅ 태스크 추가됨: **{text}**\n(#{task['id']})", parse_mode="Markdown")


async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    tasks = get_tasks()
    active = [t for t in tasks if not t["done"]]
    if not active:
        await update.message.reply_text("📭 진행 중인 태스크가 없습니다.")
        return

    lines = ["📋 **진행 중인 태스크:**\n"]
    for t in active:
        lines.append(f"  {t['id']}. {t['content']}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def done_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("사용법: `/done 번호`", parse_mode="Markdown")
        return

    try:
        task_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("번호를 입력해주세요.")
        return

    tasks = get_tasks()
    for t in tasks:
        if t["id"] == task_id and not t["done"]:
            t["done"] = True
            t["completed"] = datetime.now().isoformat()
            save_tasks(tasks)
            await update.message.reply_text(f"🎉 완료: **{t['content']}**", parse_mode="Markdown")
            return
    await update.message.reply_text("해당 태스크를 찾을 수 없습니다.")


# ─── 알림 (리마인더) ──────────────────────────────────

async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """특정 시각에 알림: /remind 14:30 미팅 준비"""
    if not is_authorized(update.effective_user.id):
        return
    if len(context.args) < 2:
        await update.message.reply_text(
            "사용법: `/remind HH:MM 알림 내용`\n예) `/remind 14:30 팀 미팅`",
            parse_mode="Markdown",
        )
        return

    time_str = context.args[0]
    reminder_text = " ".join(context.args[1:])

    try:
        hour, minute = map(int, time_str.split(":"))
        now = datetime.now()
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)  # 이미 지난 시간이면 내일

        delay = (target - now).total_seconds()
        chat_id = update.effective_chat.id

        context.job_queue.run_once(
            send_reminder,
            when=delay,
            data={"chat_id": chat_id, "text": reminder_text},
            name=f"remind_{chat_id}_{target.isoformat()}",
        )

        await update.message.reply_text(
            f"⏰ 알림 설정 완료!\n"
            f"시각: **{target.strftime('%m/%d %H:%M')}**\n"
            f"내용: {reminder_text}",
            parse_mode="Markdown",
        )
    except ValueError:
        await update.message.reply_text("시간 형식이 올바르지 않습니다. HH:MM 형식으로 입력해주세요.")


async def remind_after(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """N분 후 알림: /remind_after 30 보고서 제출"""
    if not is_authorized(update.effective_user.id):
        return
    if len(context.args) < 2:
        await update.message.reply_text(
            "사용법: `/remind_after 분 알림 내용`\n예) `/remind_after 30 보고서 제출`",
            parse_mode="Markdown",
        )
        return

    try:
        minutes = int(context.args[0])
    except ValueError:
        await update.message.reply_text("분(숫자)을 입력해주세요.")
        return

    reminder_text = " ".join(context.args[1:])
    chat_id = update.effective_chat.id
    target = datetime.now() + timedelta(minutes=minutes)

    context.job_queue.run_once(
        send_reminder,
        when=minutes * 60,
        data={"chat_id": chat_id, "text": reminder_text},
        name=f"remind_{chat_id}_{target.isoformat()}",
    )

    await update.message.reply_text(
        f"⏰ {minutes}분 후 알림 설정!\n내용: {reminder_text}",
        parse_mode="Markdown",
    )


async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    """알림 전송 콜백"""
    data = context.job.data
    await context.bot.send_message(
        chat_id=data["chat_id"],
        text=f"🔔 **리마인더**\n\n{data['text']}",
        parse_mode="Markdown",
    )


# ─── 매일 아침 미완료 태스크 알림 ───────────────────────

async def daily_task_reminder(context: ContextTypes.DEFAULT_TYPE):
    """매일 아침 미완료 태스크 알림"""
    tasks = get_tasks()
    active = [t for t in tasks if not t["done"]]
    if not active or not ALLOWED_USER_IDS:
        return

    lines = ["🌅 **오늘의 미완료 태스크:**\n"]
    for t in active:
        created = datetime.fromisoformat(t["created"]).strftime("%m/%d")
        lines.append(f"  {t['id']}. {t['content']}  _(등록: {created})_")
    lines.append(f"\n총 **{len(active)}개** 태스크가 남아있습니다.")
    msg = "\n".join(lines)

    for user_id in ALLOWED_USER_IDS:
        try:
            await context.bot.send_message(
                chat_id=user_id, text=msg, parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Daily reminder failed for {user_id}: {e}")


# ─── 대화 초기화 ─────────────────────────────────────

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    user_id = str(update.effective_user.id)
    save_conversation(user_id, [])
    await update.message.reply_text("🔄 대화 기록이 초기화되었습니다.")


# ─── 일반 메시지 (Claude 대화) ────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return

    user_id = str(update.effective_user.id)
    text = update.message.text

    # 타이핑 표시
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    reply = await ask_claude(user_id, text)

    # 텔레그램 메시지 길이 제한 (4096자)
    if len(reply) > 4000:
        chunks = [reply[i : i + 4000] for i in range(0, len(reply), 4000)]
        for chunk in chunks:
            await update.message.reply_text(chunk)
    else:
        await update.message.reply_text(reply)


# ─── 파일 처리 (문서/이미지 분석) ──────────────────────

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """문서 파일을 받아 Claude에게 분석 요청"""
    if not is_authorized(update.effective_user.id):
        return

    doc = update.message.document
    caption = update.message.caption or "이 파일의 내용을 분석하고 요약해줘."

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    try:
        file = await doc.get_file()
        file_bytes = await file.download_as_bytearray()

        # 텍스트 파일인 경우
        text_extensions = {".txt", ".py", ".js", ".json", ".csv", ".md", ".html", ".xml", ".yaml", ".yml", ".sol", ".rs", ".ts"}
        ext = Path(doc.file_name).suffix.lower() if doc.file_name else ""

        if ext in text_extensions:
            content = file_bytes.decode("utf-8", errors="replace")
            prompt = f"[파일: {doc.file_name}]\n\n```\n{content[:10000]}\n```\n\n{caption}"
            reply = await ask_claude(str(update.effective_user.id), prompt)
        else:
            reply = (
                f"📎 파일 수신: **{doc.file_name}** ({doc.file_size:,} bytes)\n\n"
                "현재 텍스트 파일만 직접 분석 가능합니다. "
                "PDF, 이미지 등은 내용을 텍스트로 복사해서 보내주시면 분석해드릴게요."
            )

        await update.message.reply_text(reply, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"⚠️ 파일 처리 오류: {str(e)}")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """이미지를 받아 Claude Vision으로 분석"""
    if not is_authorized(update.effective_user.id):
        return

    caption = update.message.caption or "이 이미지를 분석해줘."

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    try:
        photo = update.message.photo[-1]  # 가장 큰 해상도
        file = await photo.get_file()
        file_bytes = await file.download_as_bytearray()

        import base64
        b64 = base64.b64encode(bytes(file_bytes)).decode("utf-8")

        # Claude Vision API 호출
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": b64,
                            },
                        },
                        {"type": "text", "text": caption},
                    ],
                }
            ],
        )
        reply = response.content[0].text
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"⚠️ 이미지 처리 오류: {str(e)}")


# ─── 메인 ──────────────────────────────────────────────

async def post_init(application: Application):
    """봇 시작 시 명령어 목록 등록 + 매일 아침 알림 스케줄"""
    commands = [
        BotCommand("start", "봇 시작"),
        BotCommand("help", "도움말"),
        BotCommand("task", "태스크 추가"),
        BotCommand("tasks", "태스크 목록"),
        BotCommand("done", "태스크 완료"),
        BotCommand("remind", "시각 알림 설정"),
        BotCommand("remind_after", "N분 후 알림"),
        BotCommand("clear", "대화 초기화"),
    ]
    await application.bot.set_my_commands(commands)

    # 매일 아침 9시에 미완료 태스크 알림 (서버 시간 기준)
    MORNING_HOUR = int(os.environ.get("MORNING_REMINDER_HOUR", "9"))
    application.job_queue.run_daily(
        daily_task_reminder,
        time=datetime.now().replace(
            hour=MORNING_HOUR, minute=0, second=0
        ).time(),
        name="daily_morning_reminder",
    )
    logger.info(f"Daily reminder scheduled at {MORNING_HOUR}:00")


def main():
    app = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .post_init(post_init)
        .build()
    )

    # 명령어 핸들러
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("task", add_task))
    app.add_handler(CommandHandler("tasks", list_tasks))
    app.add_handler(CommandHandler("done", done_task))
    app.add_handler(CommandHandler("remind", remind))
    app.add_handler(CommandHandler("remind_after", remind_after))
    app.add_handler(CommandHandler("clear", clear))

    # 파일/이미지 핸들러
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # 일반 텍스트 핸들러 (맨 마지막에)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🚀 Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
