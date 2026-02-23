# Python 베이스 이미지
FROM python:3.10-slim
# 작업 디렉토리 설정
WORKDIR /app
# 시스템 패키지 설치 (opencv용)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
# requirements 먼저 복사
COPY requirements.txt .
# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt
# 전체 프로젝트 복사
COPY . .
# 포트 오픈
EXPOSE 8000
# FastAPI 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]