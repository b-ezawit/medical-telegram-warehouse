# api/main.py
from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from api.database import get_db
from api import schemas

app = FastAPI(
    title="Kara Solutions - Ethiopian Medical Businesses Analytics API",
    description="REST API exposing insights from transformed Telegram dbt Marts.",
    version="1.0.0"
)

def get_table_schema(db: Session, table_name: str) -> str:
    """Helper to automatically discover which schema a dbt table lives in."""
    query = text("""
        SELECT table_schema 
        FROM information_schema.tables 
        WHERE table_name = :table_name 
        LIMIT 1
    """)
    result = db.execute(query, {"table_name": table_name}).fetchone()
    if result:
        return f'"{result[0]}".'
    return ""  # Fallback to default if not found

@app.get("/")
def read_root():
    return {"message": "Welcome to the Medical Telegram Warehouse Analytical API. Navigate to /docs for testing."}

# --- Endpoint 1: Top Products ---
@app.get("/api/reports/top-products", response_model=List[schemas.TopProductResponse])
def get_top_products(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    schema = get_table_schema(db, "fct_messages")
    query = text(f"""
        SELECT 
            LOWER(UNNEST(REGEXP_MATCHES(message_text, '(paracetamol|amoxicillin|ibuprofen|cream|vitamin|serum|gel|capsule|pill)', 'g'))) AS product_name,
            COUNT(*) AS mention_count
        FROM {schema}fct_messages
        WHERE message_text IS NOT NULL
        GROUP BY product_name
        ORDER BY mention_count DESC
        LIMIT :limit
    """)
    try:
        result = db.execute(query, {"limit": limit}).fetchall()
        return [{"product_name": row[0], "mention_count": row[1]} for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# --- Endpoint 2: Channel Activity ---
@app.get("/api/channels/{channel_name}/activity", response_model=schemas.ChannelActivityResponse)
def get_channel_activity(channel_name: str, db: Session = Depends(get_db)):
    schema = get_table_schema(db, "dim_channels")
    query = text(f"""
        SELECT channel_name, channel_type, first_post_date, last_post_date, total_posts, avg_views
        FROM {schema}Dim_channels
        WHERE LOWER(channel_name) = LOWER(:channel_name)
    """)
    try:
        result = db.execute(query, {"channel_name": channel_name}).fetchone()
        if not result:
            raise HTTPException(status_code=404, detail=f"Channel '{channel_name}' not found.")
        return {
            "channel_name": result[0], "channel_type": result[1],
            "first_post_date": result[2], "last_post_date": result[3],
            "total_posts": result[4], "avg_views": float(result[5])
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# --- Endpoint 3: Message Search ---
@app.get("/api/search/messages", response_model=List[schemas.MessageSearchResponse])
def search_messages(query: str = Query(..., min_length=2), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    fct_schema = get_table_schema(db, "fct_messages")
    chan_schema = get_table_schema(db, "dim_channels")
    date_schema = get_table_schema(db, "dim_dates")
    
    sql_query = text(f"""
        SELECT f.message_id, c.channel_name, d.full_date, f.message_text, f.view_count, f.forward_count
        FROM {fct_schema}fct_messages f
        JOIN {chan_schema}Dim_channels c ON f.channel_key = c.channel_key
        JOIN {date_schema}Dim_dates d ON f.date_key = d.date_key
        WHERE f.message_text ILIKE :search_param
        ORDER BY f.view_count DESC
        LIMIT :limit
    """)
    try:
        search_param = f"%{query}%"
        result = db.execute(sql_query, {"search_param": search_param, "limit": limit}).fetchall()
        return [
            {"message_id": r[0], "channel_name": r[1], "full_date": r[2], "message_text": r[3], "view_count": r[4], "forward_count": r[5]}
            for r in result
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failure: {str(e)}")

# --- Endpoint 4: Visual Content Stats ---
@app.get("/api/reports/visual-content", response_model=schemas.VisualContentResponse)
def get_visual_content_stats(db: Session = Depends(get_db)):
    img_schema = get_table_schema(db, "fct_image_detections")
    chan_schema = get_table_schema(db, "dim_channels")
    
    query = text(f"""
        SELECT c.channel_name, COUNT(i.message_id) AS total_images,
            COUNT(CASE WHEN i.image_category = 'promotional' THEN 1 END) AS promotional_count,
            COUNT(CASE WHEN i.image_category = 'product_display' THEN 1 END) AS product_display_count,
            COUNT(CASE WHEN i.image_category = 'lifestyle' THEN 1 END) AS lifestyle_count,
            COUNT(CASE WHEN i.image_category = 'other' THEN 1 END) AS other_count
        FROM {img_schema}fct_image_detections i
        JOIN {chan_schema}Dim_channels c ON i.channel_key = c.channel_key
        GROUP BY c.channel_name
    """)
    try:
        result = db.execute(query).fetchall()
        channels_data = [
            {"channel_name": r[0], "total_images": r[1], "promotional_count": r[2], "product_display_count": r[3], "lifestyle_count": r[4], "other_count": r[5]}
            for r in result
        ]
        return {"summary": "YOLOv8 image metrics across medical channels.", "channels": channels_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics breakdown error: {str(e)}")