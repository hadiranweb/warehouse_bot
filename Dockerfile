# استفاده از تصویر پایه Python 3.9-slim برای کاهش حجم
FROM python:3.9-slim

# تنظیم متغیرهای محیطی برای جلوگیری از مشکلات بافر و نصب
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# نصب وابستگی‌های سیستمی مورد نیاز برای pillow و سایر پکیج‌ها
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# به‌روزرسانی pip به آخرین نسخه
RUN pip install --upgrade pip

# کپی و نصب وابستگی‌های Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# کپی کد پروژه
COPY . .

# تنظیم دایرکتوری کاری
WORKDIR /app
COPY ./src /app

# اجرای برنامه
CMD ["python", "main.py"]
