import json
from datetime import datetime
from pathlib import Path

from db_utils import get_connection

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_MESSAGES_DIR = BASE_DIR / "data" / "raw" / "telegram_messages"


def parse_iso_datetime(dt_str):
    if not dt_str:
        return None
    # message_date is ISO string from scraper
    return datetime.fromisoformat(dt_str)


def load_json_file(json_path: Path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_all_json_to_db():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for date_dir in RAW_MESSAGES_DIR.iterdir():
                if not date_dir.is_dir():
                    continue

                for json_path in date_dir.glob("*.json"):
                    print(f"Loading file: {json_path}")
                    records = load_json_file(json_path)

                    for rec in records:
                        cur.execute(
                            """
                            INSERT INTO raw.telegram_messages (
                                message_id,
                                channel_name,
                                message_date,
                                message_text,
                                has_media,
                                image_path,
                                views,
                                forwards
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                rec.get("message_id"),
                                rec.get("channel_name"),
                                parse_iso_datetime(rec.get("message_date")),
                                rec.get("message_text"),
                                rec.get("has_media"),
                                rec.get("image_path"),
                                rec.get("views"),
                                rec.get("forwards"),
                            ),
                        )

            conn.commit()
            print("Finished loading all JSON files into raw.telegram_messages")
    finally:
        conn.close()


if __name__ == "__main__":
    load_all_json_to_db()
