FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install uv

COPY . .

RUN uv sync --frozen

# 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# playwright 브라우저 설치
RUN python -m playwright install --with-deps

CMD ["python", "runners/run_kream.py"]