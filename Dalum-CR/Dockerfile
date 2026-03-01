FROM python:3.10-slim

WORKDIR /app

# 시스템 패키지 (필요 시)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# uv 설치
RUN pip install --upgrade pip
RUN pip install uv

# 프로젝트 복사
COPY . .

# 의존성 설치
RUN uv sync --frozen

# 배치 실행
CMD ["python", "runners/run_main.py"]