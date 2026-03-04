import os
import csv
import psycopg2

from dotenv import load_dotenv
from psycopg2.extras import execute_batch


# ENV 로드
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINAL_DIR = os.path.join(BASE_DIR, "final")

CSV_FILE = os.path.join(FINAL_DIR, "musinsa_products.csv")


# DB Insert

def insert_to_db(rows):
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

    cur = conn.cursor()

    insert_query = """
        INSERT INTO products (
            product_id,
            shopping_mall,
            large_category,
            medium_category,
            small_category,
            brand,
            product_name,
            price,
            discount_price,
            discount_rate,
            purchase_link,
            image_url
        )
        VALUES (
            %(product_id)s,
            %(shopping_mall)s,
            %(large_category)s,
            %(medium_category)s,
            %(small_category)s,
            %(brand)s,
            %(product_name)s,
            %(price)s,
            %(discount_price)s,
            %(discount_rate)s,
            %(purchase_link)s,
            %(image_url)s
        )
        ON CONFLICT (product_id) DO NOTHING;
    """

    execute_batch(cur, insert_query, rows)

    conn.commit()
    cur.close()
    conn.close()

    print(f"DB insert 완료: {len(rows)}개")


# CSV 읽기

def read_csv():
    if not os.path.exists(CSV_FILE):
        print("CSV 파일 없음:", CSV_FILE)
        return []

    rows = []

    with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            rows.append({
                "product_id": row["product_id"],
                "shopping_mall": row["shopping_mall"],
                "large_category": row["large_category"],
                "medium_category": row["medium_category"],
                "small_category": row["small_category"],
                "brand": row["brand"],
                "product_name": row["product_name"],
                "price": row["price"],
                "discount_price": row["discount_price"],
                "discount_rate": row["discount_rate"],
                "purchase_link": row["purchase_link"],
                "image_url": row["image_url"],
            })

    return rows


# MAIN

def main():

    print("DB Insert 시작")

    rows = read_csv()

    if not rows:
        print("Insert할 데이터 없음")
        return

    insert_to_db(rows)


if __name__ == "__main__":
    main()