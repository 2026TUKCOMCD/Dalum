#!/bin/bash

echo "==============================="
echo "   VIT BACKGROUND START"
echo "==============================="

# 프로젝트 루트로 이동 (본인 경로 맞게 수정)
cd /home/ubuntu/Dalum-AI

# 가상환경 활성화
source .venv/bin/activate

# CPU 메모리 보호 옵션
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export TOKENIZERS_PARALLELISM=false

# 로그 파일
LOG_FILE="vit_$(date +%Y%m%d_%H%M%S).log"

echo "로그 파일: $LOG_FILE"

# nohup으로 백그라운드 실행
nohup python -m vit.runners.run_crawl_vit > $LOG_FILE 2>&1 &

echo "VIT 실행 완료 (백그라운드)"
echo "PID 확인:"
ps aux | grep run_upload_vit