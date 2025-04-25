# استفاده از تصویر پایه Python 3.9-slim
FROM python:3.9-slim

# تنظیم متغیرهای محیطی
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# نصب وابستگی‌های سیستمی
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# به‌روزرسانی pip
RUN pip install --upgrade pip

# کپی و نصب وابستگی‌ها
COPY requirements.txt .
RUN pip install --root-user-action=ignore -r requirements.txt

# تنظیم دایرکتوری کاری
WORKDIR /app

# کپی فایل‌های پروژه
COPY src/ .

# اجرای برنامه
CMD ["python", "main.py"]
