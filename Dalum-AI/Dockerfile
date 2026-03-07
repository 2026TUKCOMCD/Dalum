# Python 베이스 이미지
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# requirements 먼저 복사 - 변경 사항 있을 때 실행
COPY requirements.txt .

# pip 업그레이드
RUN pip install --upgrade pip

# 의존성 설치
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

# 전체 프로젝트 복사
COPY . .

# 포트 오픈
EXPOSE 8000

# FastAPI 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]