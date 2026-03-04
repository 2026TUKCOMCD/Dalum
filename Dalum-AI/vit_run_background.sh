#!/bin/bash

echo "==============================="
echo "   VIT BACKGROUND START"
echo "==============================="

cd /home/ubuntu/Dalum-AI

source .venv/bin/activate

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export TOKENIZERS_PARALLELISM=false

LOG_FILE="vit_$(date +%Y%m%d_%H%M%S).log"

echo "로그 파일: $LOG_FILE"

nohup python -m vit.runners.run_crawl_vit > $LOG_FILE 2>&1 &

sleep 1
echo "VIT 실행 완료 (백그라운드)"
echo "PID 확인:"
ps aux | grep run_crawl_vit | grep -v grep