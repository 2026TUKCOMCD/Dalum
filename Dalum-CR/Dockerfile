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

# playwright 브라우저 설치
RUN playwright install --with-deps

CMD ["python", "runners/run_kream.py"]