import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# توکن ربات رو اینجا موقت وارد کن، بعداً از env می‌گیریم
BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک اینستاگرام یا ویدیو رو بفرست.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("⏳ در حال پردازش...")

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'force_generic_extractor': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get("formats", [])
            if not formats:
                raise Exception("هیچ فرمتی پیدا نشد.")

            best = formats[-1]  # یا یک فیلتر برای بهترین کیفیت بزن
            video_url = best.get("url")
            title = info.get("title", "بدون عنوان")
            duration = info.get("duration", "نامشخص")

            await update.message.reply_text(
                f"🎬 عنوان: {title}\n⏱ مدت: {duration} ثانیه\n🔗 لینک: {video_url}"
            )
    except Exception as e:
        await update.message.reply_text(f"❌ خطا:\n{str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
