import csv
from pathlib import Path
from db_utils import get_connection

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "yolo_detections.csv"


def load_csv_to_db():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # create schema/table if not exists
            cur.execute("""
                CREATE SCHEMA IF NOT EXISTS raw;

                CREATE TABLE IF NOT EXISTS raw.image_detections (
                    message_id BIGINT,
                    channel_name TEXT,
                    detected_class TEXT,
                    confidence_score DOUBLE PRECISION
                );
            """)

            with open(CSV_PATH, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            for row in rows:
                cur.execute(
                    """
                    INSERT INTO raw.image_detections (
                        message_id,
                        channel_name,
                        detected_class,
                        confidence_score
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        int(row["message_id"]),
                        row["channel_name"],
                        row["detected_class"],
                        float(row["confidence_score"]),
                    ),
                )

            conn.commit()
            print(f"Inserted {len(rows)} rows into raw.image_detections")
    finally:
        conn.close()


if __name__ == "__main__":
    load_csv_to_db()
