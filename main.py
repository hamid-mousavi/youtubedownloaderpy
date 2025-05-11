import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک اینستاگرام یا ویدیو رو بفرست.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("⏳ در حال دانلود ویدیو...")

    ydl_opts = {
        'quiet': True,
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'video.%(ext)s',
        'merge_output_format': 'mp4'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get("title", "بدون عنوان")

        # await update.message.reply_video(video=open(filename, 'rb'), caption=title)

        # حذف فایل بعد از ارسال
        with open(filename, 'rb') as video_file:
            await update.message.reply_video(video=video_file, caption=title)

        try:
            os.remove(filename)
            print(f"🧹 فایل حذف شد: {filename}")
        except Exception as e:
            print(f"⚠️ خطا در حذف فایل: {e}")


    except Exception as e:
        await update.message.reply_text(f"❌ خطا:\n{str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
