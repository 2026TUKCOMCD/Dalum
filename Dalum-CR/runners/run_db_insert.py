import os
import csv
import psycopg2
import boto3
from io import StringIO

from dotenv import load_dotenv
from psycopg2.extras import execute_batch

# ENV 로드
load_dotenv()

# S3 설정
S3_BUCKET = os.getenv("S3_BUCKET_NAME")
S3_KEY = "crawling/musinsa_products.csv"
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")

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
        INSERT INTO product (
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


# S3에서 CSV 읽기
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

    print("S3 CSV 읽는 중...")

    rows = read_csv_from_s3()

    if not rows:
        print("Insert할 데이터 없음")
        return

    print(f"총 {len(rows)}개 데이터 insert 시작")

    insert_to_db(rows)


if __name__ == "__main__":
    main()