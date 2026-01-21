import os
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto

# Load environment variables
load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION_NAME = os.getenv("TELEGRAM_SESSION_NAME", "medical_telegram_session")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"
MESSAGES_DIR = DATA_DIR / "telegram_messages"
IMAGES_DIR = DATA_DIR / "images"
LOGS_DIR = BASE_DIR / "logs"

CHANNELS = [
    "lobelia4cosmetics",
    "tikvahpharma",
    # Add more later from et.tgstat.com/medicine
]

# Ensure directories exist
for d in [MESSAGES_DIR, IMAGES_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Logging setup
log_file = LOGS_DIR / "scraper.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


async def scrape_channel(client, username: str, limit: int = 200):
    """Scrape recent messages from one channel."""
    print(f"\n=== Scraping channel: {username} ===")
    logger.info(f"Scraping channel: {username}")

    entity = await client.get_entity(username)
    channel_name = username.lower()

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    channel_date_dir = MESSAGES_DIR / today_str
    channel_date_dir.mkdir(parents=True, exist_ok=True)

    json_path = channel_date_dir / f"{channel_name}.json"

    messages_data = []

    async for message in client.iter_messages(entity, limit=limit):
        if not message:
            continue

        message_id = message.id
        message_date = message.date.isoformat() if message.date else None
        message_text = message.message or ""

        views = getattr(message, "views", None)
        forwards = getattr(message, "forwards", None)

        has_media = isinstance(message.media, MessageMediaPhoto)
        image_path = None

        if has_media:
            channel_image_dir = IMAGES_DIR / channel_name
            channel_image_dir.mkdir(parents=True, exist_ok=True)
            image_filename = f"{message_id}.jpg"
            image_full_path = channel_image_dir / image_filename

            try:
                await client.download_media(
                    message,
                    file=str(image_full_path),
                )
                image_path = str(image_full_path)
            except Exception as e:
                print(f"Failed to download image for message {message_id}: {e}")
                logger.error(f"Failed to download image for message {message_id}: {e}")

        messages_data.append(
            {
                "message_id": message_id,
                "channel_name": channel_name,
                "message_date": message_date,
                "message_text": message_text,
                "has_media": has_media,
                "image_path": image_path,
                "views": views,
                "forwards": forwards,
            }
        )

    # Save to JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(messages_data, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(messages_data)} messages to {json_path}")
    logger.info(f"Saved {len(messages_data)} messages to {json_path}")


async def main():
    print("Starting full scrape at", datetime.now(timezone.utc).isoformat())
    logger.info("Starting full scrape")
    for username in CHANNELS:
        try:
            await scrape_channel(client, username, limit=200)
        except Exception as e:
            print(f"Error scraping {username}: {e}")
            logger.error(f"Error scraping {username}: {e}")
    print("Done scraping.")
    logger.info("Done scraping.")


if __name__ == "__main__":
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    with client:
        client.loop.run_until_complete(main())
