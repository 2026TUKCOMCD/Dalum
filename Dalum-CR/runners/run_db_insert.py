import os
import csv
import psycopg2
import boto3
from io import StringIO
from datetime import datetime

from dotenv import load_dotenv
from psycopg2.extras import execute_batch

load_dotenv()

S3_BUCKET = os.getenv("S3_BUCKET_NAME")
S3_KEY = "crawling/musinsa_products.csv"
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")


CHUNK_SIZE = 10000


def insert_to_db(rows):

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=60,
    )

    cur = conn.cursor()

    insert_query = """
        INSERT INTO product (
            product_id,
            shopping_mall,
            large_category,
            medium_category,
            small_category,
            product_name,
            brand,
            price,
            discount_price,
            discount_rate,
            purchase_link,
            image_url,
            created_at
        )
        VALUES (
            %(product_id)s,
            %(shopping_mall)s,
            %(large_category)s,
            %(medium_category)s,
            %(small_category)s,
            %(product_name)s,
            %(brand)s,
            %(price)s,
            %(discount_price)s,
            %(discount_rate)s,
            %(purchase_link)s,
            %(image_url)s,
            %(created_at)s
        )
        ON CONFLICT (product_id) DO NOTHING;
    """

    total = len(rows)
    inserted = 0
    for i in range(0, total, CHUNK_SIZE):
        chunk = rows[i:i + CHUNK_SIZE]
        execute_batch(cur, insert_query, chunk, page_size=1000)
        conn.commit()
        inserted += len(chunk)
        print(f"  진행: {inserted}/{total}")

    cur.close()
    conn.close()

    print(f"DB insert 완료: {total}개")


def read_csv_from_s3():

    s3 = boto3.client("s3", region_name=AWS_REGION)

    response = s3.get_object(
        Bucket=S3_BUCKET,
        Key=S3_KEY
    )

    csv_content = response["Body"].read().decode("utf-8-sig")

    f = StringIO(csv_content)
    reader = csv.DictReader(f)

    rows = []

    for idx, row in enumerate(reader, start=1):

        rows.append({
            "product_id": idx,   # 자동 증가 대신 코드에서 생성
            "shopping_mall": row["shopping_mall"],
            "large_category": row["large_category"],
            "medium_category": row["medium_category"],
            "small_category": row["small_category"],
            "product_name": row["product_name"],
            "brand": row["brand"],
            "price": int(row["price"]) if row["price"] else 0,
            "discount_price": int(row["discount_price"]) if row["discount_price"] else 0,
            "discount_rate": int(row["discount_rate"]) if row["discount_rate"] else 0,
            "purchase_link": row["purchase_link"],
            "image_url": row["image_url"],
            "created_at": datetime.now()
        })

    return rows


def main():

    print("S3 CSV 읽는 중...")

    rows = read_csv_from_s3()

    if not rows:
        print("Insert할 데이터 없음")
        return

    print(f"총 {len(rows)}개 데이터 insert 시작")

    insert_to_db(rows)


if __name__ == "__main__":
    main()