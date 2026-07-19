#!/bin/bash

echo "==============================="
echo "   DALUM-CR DB INSERT START"
echo "==============================="

# 현재 파일 위치 기준으로 Dalum-CR 루트 이동
cd "$(dirname "$0")"

# 가상환경 활성화
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "가상환경 활성화 완료"
else
    echo "⚠️  .venv 가상환경 없음"
fi

# 로그 파일 생성
LOG_FILE="db_insert_$(date +%Y%m%d_%H%M%S).log"
echo "로그 파일: $LOG_FILE"

# 서버 보호 옵션
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

# 백그라운드 실행
nohup python runners/run_db_insert.py > $LOG_FILE 2>&1 &

echo "DB Insert 백그라운드 실행 완료"
echo "PID 확인:"
ps aux | grep run_db_insert.py