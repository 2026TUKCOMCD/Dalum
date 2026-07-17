"""
style_output.csv → DB UPDATE

run_style_local.py로 생성된 style_output.csv를 읽어
product 테이블의 style, material_vector, dominant_colors 컬럼을 업데이트한다.

매칭 기준: product_id (정수)

사용법:
    python -m vit.test.run_style_db_upload
    python -m vit.test.run_style_db_upload --dry-run   # DB 미반영, 로그만 출력
    python -m vit.test.run_style_db_upload --batch 500
"""

import os
import sys
import csv
import json
import argparse
import psycopg2
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, BASE_DIR)
load_dotenv()

INPUT_PATH = os.path.join(BASE_DIR, "vit", "outputs", "style_output.csv")


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", 5432),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def run(batch_size: int = 500, dry_run: bool = False):
    if not os.path.exists(INPUT_PATH):
        print(f"style_output.csv 없음: {INPUT_PATH}")
        print("먼저 run_style_local.py를 실행하세요.")
        return

    with open(INPUT_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"총 {len(rows)}개 로드\n")

    if dry_run:
        print("[DRY-RUN] DB 반영 없이 첫 5개 미리보기:\n")
        for row in rows[:5]:
            pid  = row["product_id"]
            styl = row["style"]
            mat  = json.loads(row["material_vector"])[:3]
            col  = json.loads(row["dominant_colors"])[:1]
            print(f"  product_id={pid}  style={styl}  material[:3]={mat}  dominant={col}")
        return

    conn   = get_db_connection()
    cursor = conn.cursor()

    updated = 0
    skipped = 0

    batch = []
    for i, row in enumerate(rows, 1):
        try:
            product_id       = int(row["product_id"])
            style            = row["style"]
            material_vector  = row["material_vector"]   # 이미 JSON 문자열
            dominant_colors  = row["dominant_colors"]   # 이미 JSON 문자열
            batch.append((material_vector, dominant_colors, style, product_id))
        except (ValueError, KeyError):
            skipped += 1
            continue

        if len(batch) >= batch_size:
            cursor.executemany(
                """
                UPDATE product
                SET material_vector = %s::jsonb,
                    dominant_colors = %s::jsonb,
                    style           = %s
                WHERE product_id = %s
                """,
                batch,
            )
            conn.commit()
            updated += len(batch)
            print(f"  → {updated}/{len(rows)} 업데이트 완료")
            batch.clear()

    # 나머지 처리
    if batch:
        cursor.executemany(
            """
            UPDATE product
            SET material_vector = %s::jsonb,
                dominant_colors = %s::jsonb,
                style           = %s
            WHERE product_id = %s
            """,
            batch,
        )
        conn.commit()
        updated += len(batch)

    cursor.close()
    conn.close()

    print(f"\n완료: 업데이트 {updated}개 / 스킵 {skipped}개")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch",   type=int,  default=500,   help="배치 크기 (기본 500)")
    parser.add_argument("--dry-run", action="store_true",      help="DB 반영 없이 미리보기만")
    args = parser.parse_args()
    run(batch_size=args.batch, dry_run=args.dry_run)
