import os
from dotenv import load_dotenv
from telethon import TelegramClient

# Load .env file
load_dotenv()

api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
session_name = os.getenv("TELEGRAM_SESSION_NAME", "medical_telegram_session")

async def main():
    me = await client.get_me()
    print("Logged in as:", me.username or me.first_name)

if __name__ == "__main__":
    client = TelegramClient(session_name, api_id, api_hash)
    with client:
        client.loop.run_until_complete(main())
