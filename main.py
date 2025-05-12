from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import os
import yt_dlp
import uuid

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# منوی اصلی
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📥 دانلود ویدیو", callback_data='download')],
        [InlineKeyboardButton("ℹ️ درباره ربات", callback_data='about')],
        [InlineKeyboardButton("❌ لغو", callback_data='cancel')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! چطور می‌تونم کمکت کنم؟👇", reply_markup=reply_markup)

# هندلر کلیک روی دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data

    if choice == 'download':
        await query.edit_message_text("لینک ویدیوی مورد نظرت رو بفرست.")
        context.user_data['awaiting_link'] = True

    elif choice == 'about':
        await query.edit_message_text("این ربات برای دانلود ویدیو از لینک‌هایی مثل اینستاگرام ساخته شده ✅")

    elif choice == 'cancel':
        await query.edit_message_text("❌ عملیات لغو شد.")

# دریافت لینک و دانلود
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_link'):
        url = update.message.text
        await update.message.reply_text("⏳ در حال دانلود ویدیو...")

        unique_id = str(uuid.uuid4())
        filename = f"{unique_id}.mp4"

        ydl_opts = {
            'quiet': True,
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': filename,
            'merge_output_format': 'mp4'
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get("title", "بدون عنوان")

            with open(filename, 'rb') as f:
                await update.message.reply_video(video=f, caption=title)

            os.remove(filename)
            print(f"🧹 فایل حذف شد: {filename}")
        except Exception as e:
            await update.message.reply_text(f"❌ خطا:\n{e}")
        
        context.user_data['awaiting_link'] = False
    else:
        await update.message.reply_text("لطفاً اول از منو گزینه مورد نظر رو انتخاب کن.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
