FROM python:3.11-slim

WORKDIR /app

# ----------------------------------------------
# 1. تنظیم میرور Debian برای بسته‌های سیستمی (اختیاری)
# ----------------------------------------------
# اگر به بسته‌های سیستمی مانند curl، ca-certificates و fonts نیاز دارید
# این بخش را فعال کنید. در پروژه فعلی شما، با وجود فونت‌های محلی در پوشه fonts/
# لزومی به نصب fonts-dejavu-core نیست. اما برای اطمینان از نصب curl و ca-certificates
# (که ممکن است در دانلود فونت از GitHub به کار آیند) این بخش را نگه می‌دارم.
RUN rm -f /etc/apt/sources.list.d/debian.sources && \
    echo "deb https://linux-mirror.liara.ir/repository/debian bookworm main non-free-firmware" > /etc/apt/sources.list && \
    echo "deb https://linux-mirror.liara.ir/repository/debian-security bookworm-security main non-free-firmware" >> /etc/apt/sources.list && \
    echo "deb https://linux-mirror.liara.ir/repository/debian bookworm-updates main non-free-firmware" >> /etc/apt/sources.list

# نصب بسته‌های سیستمی مورد نیاز
# (اختیاری: اگر نیازی ندارید، می‌توانید این خطوط را حذف کنید)
#RUN apt-get update && apt-get install -y --no-install-recommends \
   # curl \
   # ca-certificates \
   # && rm -rf /var/lib/apt/lists/*

# ----------------------------------------------
# 2. تنظیم میرور PyPI برای کتابخانه‌های پایتون
# ----------------------------------------------
ENV PIP_INDEX_URL=https://package-mirror.liara.ir/repository/pypi/simple

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------------------------
# 3. کپی بقیه فایل‌های پروژه
# ----------------------------------------------
COPY . .

# ----------------------------------------------
# 4. تنظیم پورت و اجرای برنامه
# ----------------------------------------------
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]