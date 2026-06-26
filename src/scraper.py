import os
import json
import logging
from datetime import datetime
from telethon import TelegramClient
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Setup logging architecture as required by Task 1
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/scraping.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Safely extract credentials from the environment
API_ID = os.environ.get("TG_API_ID")
API_HASH = os.environ.get("TG_API_HASH")

if not API_ID or not API_HASH:
    raise ValueError("Missing TG_API_ID or TG_API_HASH environment variables. Double check your .env file!")

# Convert API_ID to integer required by Telethon
API_ID = int(API_ID)

# Target list of public channels corrected from your screenshots
CHANNELS = [
    'CheMed123',           # Correct handle from image metadata
    'lobelia4cosmetics',   # Correct handle from image metadata
    'tikvahpharma'         # Confirmed working handle
]

async def scrape_channel_messages(client, channel_username):
    logging.info(f"Starting sweep on channel: {channel_username}")
    print(f"Scraping {channel_username}...")
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # Ensure partitioned data lake directory paths exist
    json_dir = f"data/raw/telegram_messages/{today_str}"
    img_dir = f"data/raw/images/{channel_username}"
    os.makedirs(json_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)
    
    messages_data = []

    try:
        # Fetching the last 100 recent messages for baseline ingestion
        async for message in client.iter_messages(channel_username, limit=100):
            # Track media metadata flags
            has_media = message.media is not None
            image_path = None
            
            # If an image exists, download it into partitioned structure
            if message.photo:
                filename = f"{message.id}.jpg"
                target_path = os.path.join(img_dir, filename)
                # Avoid downloading a file twice if you rerun the script
                if not os.path.exists(target_path):
                    await message.download_media(file=target_path)
                    logging.info(f"Downloaded image for message ID {message.id}")
                image_path = target_path

            # Format the entry exactly to match your requested fields
            msg_entry = {
                "message_id": message.id,
                "channel_name": channel_username,
                "message_date": str(message.date) if message.date else None,
                "message_text": message.text or "",
                "has_media": has_media,
                "image_path": image_path,
                "views": message.views or 0,
                "forwards": message.forwards or 0
            }
            messages_data.append(msg_entry)

        # Write data lake output to a localized JSON file
        output_file = f"{json_dir}/{channel_username}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(messages_data, f, indent=4, ensure_ascii=False)
            
        logging.info(f"Successfully saved {len(messages_data)} records to {output_file}")
        print(f"Successfully saved {len(messages_data)} records for {channel_username}!")

    except Exception as e:
        logging.error(f"Error encountered while scraping {channel_username}: {str(e)}")
        print(f"Error scraping {channel_username}. See logs/scraping.log for details.")

async def main():
    async with TelegramClient('session_buzzy', API_ID, API_HASH) as client:
        for channel in CHANNELS:
            await scrape_channel_messages(client, channel)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
