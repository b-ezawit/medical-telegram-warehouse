import os
import json
import glob
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 1. Load configuration from your .env file
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "medical_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Create connection engine string
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

def run_data_pipeline():
    base_directory = "data/raw/telegram_messages"
    processed_records = []

    search_path = os.path.join(base_directory, "**/*.json")
    target_files = glob.glob(search_path, recursive=True)
    
    if not target_files:
        print(f"⚠️ No raw JSON files found under {base_directory}. Double check your pathing.")
        return

    print(f"Found {len(target_files)} target JSON partition files. Parsing content...")

    for file_path in target_files:
        filename = os.path.basename(file_path)
        channel_fallback = filename.replace(".json", "")

        with open(file_path, "r", encoding="utf-8") as raw_file:
            try:
                content = json.load(raw_file)
                
                messages_list = content if isinstance(content, list) else [content]
                
                for msg in messages_list:
                    extracted_row = {
                        "message_id": msg.get("message_id"),
                        "channel_name": msg.get("channel_name", channel_fallback),
                        "message_date": msg.get("message_date"),
                        "message_text": msg.get("message_text"),
                        "has_media": msg.get("has_media", False),
                        "image_path": msg.get("image_path"),
                        "views": msg.get("views", 0),
                        "forwards": msg.get("forwards", 0)
                    }
                    processed_records.append(extracted_row)
            except Exception as error:
                print(f"Failed to parse file {file_path}. Reason: {error}")

    # 4. Ship compiled rows into Postgres
    if processed_records:
        df = pd.DataFrame(processed_records)
        
        with engine.connect() as connection:
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
            connection.commit()
            
        print(f"Streaming {len(df)} records into PostgreSQL table 'raw.telegram_messages'...")
        
        df.to_sql(
            name="telegram_messages",
            con=engine,
            schema="raw",
            if_exists="append",
            index=False
        )
        print("Data Lake migration completely finalized successfully!")
    else:
        print("Zero records loaded.")

if __name__ == "__main__":
    run_data_pipeline()
