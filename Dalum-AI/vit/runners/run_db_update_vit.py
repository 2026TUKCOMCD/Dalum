import json
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", 5432),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def update_style_color_material(cursor, conn, purchase_link, material_vector, dominant_colors, style):
    dominant_color_list = [
        {"hex": hex_color, "ratio": float(round(ratio, 4))}
        for hex_color, ratio in dominant_colors
    ]

    cursor.execute(
        """
        UPDATE product
        SET material_vector = %s,
            dominant_colors = %s,
            style = %s
        WHERE purchase_link = %s
        """,
        (
            json.dumps(material_vector),
            json.dumps(dominant_color_list),
            style,
            purchase_link,
        ),
    )

    conn.commit()
