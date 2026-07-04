import os
import pandas as pd
from sqlalchemy import create_engine

def main():
    CSV_PATH = r"D:\KAIM\medical-telegram-warehouse\data\yolo_detections.csv"
    DB_URL = "postgresql://postgres:my_secret_password@localhost:5433/medical_db"    
    if not os.path.exists(CSV_PATH):
        print(f" Ingestion Error: CSV file not found at {CSV_PATH}")
        return

    print(f" Reading YOLO CSV tracking data from: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)

    print("Connecting to PostgreSQL Docker container...")
    engine = create_engine(DB_URL)
    
    print(" Loading vision analytics into 'raw.yolo_detections'...")
    df.to_sql(
        name="yolo_detections",
        con=engine,
        schema="raw",
        if_exists="replace", 
        index=False
    )
    print("Ingestion complete! Data is now living securely inside the database.")

if __name__ == "__main__":
    main()