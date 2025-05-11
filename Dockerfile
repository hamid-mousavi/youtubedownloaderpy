# از ایمیج پایتون رسمی استفاده کن
FROM python:3.10-slim

# نصب ffmpeg و سایر وابستگی‌ها
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# تنظیم دایرکتوری کاری
WORKDIR /app

# کپی کردن فایل‌ها به داخل کانتینر
COPY . /app

# نصب پکیج‌های پایتون
RUN pip install --no-cache-dir -r requirements.txt

# تنظیم متغیر محیطی (اختیاری)
ENV PORT=8080

# اجرای اپلیکیشن
CMD ["python", "main.py"]
