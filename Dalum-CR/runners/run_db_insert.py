from psycopg2.extras import execute_batch

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