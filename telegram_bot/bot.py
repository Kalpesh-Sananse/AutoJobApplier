import os
import asyncio
import httpx
from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from telegram.error import BadRequest, NetworkError

# ================== CONFIG ==================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_BASE = os.getenv("API_BASE")

ROLE, COUNTRY, LIMIT = range(3)

COUNTRIES = [
    "India", "USA", "UK", "Canada",
    "Germany", "Australia", "Singapore", "Netherlands"
]

LIMITS = [20, 30, 50]   # keep fast & safe

# ================== SAFE HELPERS ==================
async def safe_edit_message(query, text, reply_markup=None, parse_mode=None):
    """Safely edit message (ignore 'Message is not modified')."""
    try:
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
    except BadRequest as e:
        if "Message is not modified" in str(e):
            return
        raise


async def safe_send_message(bot, chat_id, text, **kwargs):
    """Safely send message (ignore network glitches)."""
    try:
        await bot.send_message(chat_id=chat_id, text=text, **kwargs)
    except NetworkError:
        pass


# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["state"] = ROLE

    await update.message.reply_text(
        "👋 *Welcome to AutoJobApplier Bot*\n\n"
        "💼 Please enter the job role you are looking for:",
        parse_mode="Markdown"
    )


# ================== TEXT HANDLER ==================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") != ROLE:
        return

    context.user_data["role"] = update.message.text.strip()

    keyboard = [
        [InlineKeyboardButton(country, callback_data=country)]
        for country in COUNTRIES
    ]

    await update.message.reply_text(
        "🌍 *Select country:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

    context.user_data["state"] = COUNTRY


# ================== COUNTRY HANDLER ==================
async def handle_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["country"] = query.data

    keyboard = [
        [InlineKeyboardButton(f"{n} jobs", callback_data=str(n))]
        for n in LIMITS
    ]

    await safe_edit_message(
        query,
        "📊 *How many jobs do you want?*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

    context.user_data["state"] = LIMIT


# ================== LIMIT HANDLER ==================
async def handle_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    role = context.user_data.get("role")
    country = context.user_data.get("country")
    limit = int(query.data)

    await safe_edit_message(
        query,
        "⏳ *Job search started*\n\n"
        "This may take 30–90 seconds.\n"
        "You will receive results shortly.",
        parse_mode="Markdown"
    )

    # Background fetch (non-blocking)
    asyncio.create_task(
        fetch_and_send_jobs(
            chat_id=query.message.chat_id,
            role=role,
            country=country,
            limit=limit,
            context=context
        )
    )


# ================== BACKGROUND JOB FETCH ==================
async def fetch_and_send_jobs(chat_id, role, country, limit, context):
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(90),
            limits=httpx.Limits(max_connections=5)
        ) as client:
            response = await client.get(
                f"{API_BASE}/jobs",
                params={
                    "role": role,
                    "country": country,
                    "limit": limit
                }
            )
            response.raise_for_status()

        data = response.json()

        if not data or "results" not in data or not data["results"]:
            await safe_send_message(
                context.bot,
                chat_id,
                "❌ No jobs found for this search."
            )
            return

        # Send jobs gradually (Telegram-safe)
        for job in data["results"][:10]:
            msg = (
                f"💼 *{job.get('title', 'N/A')}*\n"
                f"🏢 {job.get('company', 'Unknown')}\n"
                f"🌐 {job.get('site', '')}\n"
                f"📍 {'Remote' if job.get('is_remote') else 'Onsite'}\n"
                f"📅 {job.get('date_posted', '')}\n"
                f"🔗 [Apply Here]({job.get('job_url')})"
            )

            await safe_send_message(
                context.bot,
                chat_id,
                msg,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )

            await asyncio.sleep(0.7)

        await safe_send_message(
            context.bot,
            chat_id,
            "✅ *Search complete!*\n\nType /start to search again.",
            parse_mode="Markdown"
        )

    except httpx.RequestError:
        await safe_send_message(
            context.bot,
            chat_id,
            "⚠️ Job service is currently unavailable. Please try again later."
        )

    except Exception as e:
        print("UNEXPECTED ERROR:", e)
        await safe_send_message(
            context.bot,
            chat_id,
            "⚠️ Something went wrong. Please try again."
        )


# ================== GLOBAL ERROR HANDLER ==================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    error = context.error
    print("⚠️ BOT ERROR:", repr(error))

    if isinstance(error, NetworkError):
        return

    if update and hasattr(update, "effective_chat"):
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ Temporary network issue. Please try again."
            )
        except Exception:
            pass


# ================== MAIN ==================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(
        CallbackQueryHandler(
            handle_country,
            pattern="^(India|USA|UK|Canada|Germany|Australia|Singapore|Netherlands)$"
        )
    )
    app.add_handler(
        CallbackQueryHandler(handle_limit, pattern="^(20|30|50)$")
    )

    app.add_error_handler(error_handler)

    print("🤖 Telegram bot running safely...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
