import os
import csv
import subprocess
import sys

# ===============================
# 경로 설정
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CRAWLERS_DIR = os.path.join(BASE_DIR, "crawlers")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
MERGED_DIR = os.path.join(BASE_DIR, "merged")
FINAL_DIR = os.path.join(BASE_DIR, "final")

# ===============================
# 실행할 크롤러 목록
# ===============================
CRAWLERS = [
    "musinsa.py",
    "musinsa_empty.py",
    "cm29.py",
    "fruitsfamily.py",
    # "kream.py",
]

SHOP_MALLS = [
    "musinsa",
    "musinsa_empty",
    "29cm",
    "fruitsfamily",
    # "kream",
]

CATEGORIES = [
    "OUTER",
    "TOP",
    "BOTTOM",
    "SHOES",
    "BAG",
    "ACC",
    "DRESS",
]

FINAL_HEADER = [
    "쇼핑몰",
    "대분류",
    "중분류",
    "카테고리",
    "브랜드",
    "상품명",
    "정가",
    "판매가",
    "할인율(%)",
    "상품 URL",
    "이미지 URL",
]

# ===============================
# 디렉토리 보장
# ===============================
def ensure_dirs():
    os.makedirs(MERGED_DIR, exist_ok=True)
    os.makedirs(FINAL_DIR, exist_ok=True)

# ===============================
# 크롤러 실행
# ===============================
def run_crawlers():
    print("\n🚀 [1/3] 크롤링 단계 시작")

    for crawler in CRAWLERS:
        crawler_path = os.path.join(CRAWLERS_DIR, crawler)
        print(f"\n▶ 실행 중: {crawler}")

        try:
            result = subprocess.run(
                [sys.executable, crawler_path],
                check=False
            )

            if result.returncode != 0:
                print(f"⚠ 크롤러 실패: {crawler} (continue)")
            else:
                print(f"✅ 완료: {crawler}")

        except Exception as e:
            print(f"❌ 실행 오류: {crawler} | {e}")

    print("\n🚀 크롤링 단계 종료")

# ===============================
def read_csv_no_header(path):
    if not os.path.exists(path):
        return []

    rows = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                rows.append(row)
    return rows

# ===============================
# output → merged
# ===============================
def merge_by_category():
    print("\n📦 [2/3] 2차 결과물 생성 (output → merged)")

    for category in CATEGORIES:
        merged_rows = []

        for mall in SHOP_MALLS:
            path = os.path.join(OUTPUT_DIR, mall, f"{category}.csv")
            rows = read_csv_no_header(path)

            for r in rows:
                merged_rows.append([mall] + r)

        if not merged_rows:
            print(f"⚠ {category}: 병합 데이터 없음 (skip)")
            continue

        merged_path = os.path.join(MERGED_DIR, f"{category}.csv")
        with open(merged_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerows(merged_rows)

        print(f"✅ merged/{category}.csv ({len(merged_rows)}개)")

# ===============================
# merged → final
# ===============================
def merge_all():
    print("\n⭐ [3/3] 최종 결과물 생성 (merged → final)")

    final_rows = []

    for category in CATEGORIES:
        path = os.path.join(MERGED_DIR, f"{category}.csv")
        rows = read_csv_no_header(path)
        final_rows.extend(rows)

    if not final_rows:
        print("❌ 최종 병합 데이터 없음")
        return

    final_path = os.path.join(FINAL_DIR, "all_products.csv")
    with open(final_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(FINAL_HEADER)
        writer.writerows(final_rows)

    print(f"🎉 final/all_products.csv 생성 완료 ({len(final_rows)}개)")

# ===============================
def main():
    ensure_dirs()
    run_crawlers()
    merge_by_category()
    merge_all()

# ===============================
if __name__ == "__main__":
    main()
