import os
import csv
import subprocess
import sys
import hashlib

# 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CRAWLERS_DIR = os.path.join(BASE_DIR, "crawlers")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
MERGED_DIR = os.path.join(BASE_DIR, "merged")
FINAL_DIR = os.path.join(BASE_DIR, "final")

# KREAM만 실행
CRAWLERS = [
    "kream.py",
]

SHOP_MALLS = [
    "kream",
]

CATEGORIES = [
    "OUTER",
    "TOP",
    "BOTTOM",
    "SHOES",
    "BAG",
    "HAT",
    "DRESS",
]

FINAL_HEADER = [
    "product_id",
    "shopping_mall",
    "large_category",
    "medium_category",
    "small_category",
    "brand",
    "product_name",
    "price",
    "discount_price",
    "discount_rate",
    "purchase_link",
    "image_url",
]


def ensure_dirs():
    os.makedirs(MERGED_DIR, exist_ok=True)
    os.makedirs(FINAL_DIR, exist_ok=True)


def run_crawlers():
    print("\n[KREAM 전용 크롤링 시작]")

    for crawler in CRAWLERS:
        crawler_path = os.path.join(CRAWLERS_DIR, crawler)
        print(f"\n실행 중: {crawler}")

        try:
            result = subprocess.run(
                [sys.executable, crawler_path],
                check=False
            )

            if result.returncode != 0:
                print(f"크롤러 실패: {crawler}")
            else:
                print(f"완료: {crawler}")

        except Exception as e:
            print(f"실행 오류: {crawler} | {e}")

    print("\n크롤링 단계 종료")


def read_csv_dict(path):
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def generate_product_id(product_url: str) -> str:
    return hashlib.md5(product_url.strip().encode()).hexdigest()


def merge_by_category():
    print("\n[KREAM] output → merged")

    for category in CATEGORIES:
        merged_rows = []

        for mall in SHOP_MALLS:
            path = os.path.join(OUTPUT_DIR, mall, f"{category}.csv")
            rows = read_csv_dict(path)

            for r in rows:
                r["shopping_mall"] = mall
                merged_rows.append(r)

        if not merged_rows:
            continue

        merged_path = os.path.join(MERGED_DIR, f"{category}.csv")
        with open(merged_path, "w", newline="", encoding="utf-8-sig") as f:
            fieldnames = merged_rows[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(merged_rows)

        print(f"merged/{category}.csv ({len(merged_rows)}개)")


def merge_all():
    print("\n[KREAM] merged → final")

    final_rows = []

    for category in CATEGORIES:
        path = os.path.join(MERGED_DIR, f"{category}.csv")
        rows = read_csv_dict(path)

        for row in rows:
            product_url = row.get("상품 URL", "")
            product_id = generate_product_id(product_url)

            final_row = {
                "product_id": product_id,
                "shopping_mall": row.get("shopping_mall", ""),
                "large_category": row.get("대분류", ""),
                "medium_category": row.get("중분류", ""),
                "small_category": row.get("카테고리", ""),
                "brand": row.get("브랜드", ""),
                "product_name": row.get("상품명", ""),
                "price": row.get("정가", ""),
                "discount_price": row.get("판매가", ""),
                "discount_rate": row.get("할인율(%)", ""),
                "purchase_link": product_url,
                "image_url": row.get("이미지 URL", ""),
            }

            final_rows.append(final_row)

    if not final_rows:
        print("최종 병합 데이터 없음")
        return

    final_path = os.path.join(FINAL_DIR, "kream_products.csv")
    with open(final_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FINAL_HEADER)
        writer.writeheader()
        writer.writerows(final_rows)

    print(f"kream_products.csv 생성 완료 ({len(final_rows)}개)")


def main():
    ensure_dirs()
    run_crawlers()
    merge_by_category()
    merge_all()


if __name__ == "__main__":
    main()