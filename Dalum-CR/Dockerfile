FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Seoul

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libxshmfence1 \
    libx11-xcb1 \
    libgtk-3-0 \
    libdrm2 \
    libxcb-dri3-0 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright 브라우저 설치
RUN python -m playwright install chromium

COPY . .

CMD ["python", "runners/run_musinsa.py"]