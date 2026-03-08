#!/bin/bash

set -e  # 에러 발생 시 중단

echo "==============================="
echo "   VIT BACKGROUND START"
echo "==============================="

APP_DIR="/home/ubuntu/Dalum/Dalum-AI"
LOG_FILE="vit.log"
MAX_SIZE_MB=100
RETENTION_DAYS=7

cd "$APP_DIR" || exit 1

source .venv/bin/activate

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export TOKENIZERS_PARALLELISM=false

echo "로그 파일: $LOG_FILE"

# 중복 실행 방지
if pgrep -f "vit.runners.run_crawl_vit" > /dev/null; then
    echo "이미 실행 중입니다. 종료합니다."
    exit 1
fi

# 로그 파일 크기 체크 (100MB 이상이면 롤링)
if [ -f "$LOG_FILE" ]; then
    FILE_SIZE_MB=$(du -m "$LOG_FILE" | cut -f1)

    if [ "$FILE_SIZE_MB" -ge "$MAX_SIZE_MB" ]; then
        echo "로그 파일이 ${MAX_SIZE_MB}MB 초과 → 롤링"
        mv "$LOG_FILE" "vit_$(date +%Y%m%d_%H%M%S).log"
    fi
fi

# 오래된 로그 자동 삭제
find . -name "vit_*.log" -mtime +$RETENTION_DAYS -delete


# 백그라운드 실행
nohup python -u -m vit.runners.run_crawl_vit >> $LOG_FILE 2>&1 &

sleep 1

echo "VIT 실행 완료 (백그라운드)"
echo "PID:"
pgrep -f "vit.runners.run_crawl_vit"

echo "==============================="