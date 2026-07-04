from fastapi import FastAPI, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from .database import get_db
from .schemas import (
    TopProductResponse, 
    ChannelActivityResponse, 
    MessageSearchResponse, 
    VisualContentStatsResponse
)

app = FastAPI(
    title="Medical Telegram Warehouse Analytical API",
    description=(
        "Operational REST API Gateway\n"
        "This API provides programmatic access to the data warehouse data mart layers. "
        "It exposes transformed metrics, message text analytics, and computer vision "
        "object detection classifications generated during the extraction pipelines."
    ),
    version="1.0.0"
)

@app.get("/", tags=["System Health"])
def read_root():
    return {
        "status": "healthy",
        "message": "Welcome to the Medical Warehouse REST API. Go to /docs for interactive Swagger documentation."
    }

@app.get(
    "/api/reports/top-products", 
    response_model=List[TopProductResponse],
    tags=["Analytical Reports"],
    summary="Retrieve most frequently mentioned terms or products"
)
def get_top_products(
    limit: int = Query(
        default=10, 
        ge=1, 
        le=100, 
        description="The maximum number of top mentioned product items to return. Must be between 1 and 100."
    ), 
    db: Session = Depends(get_db)
):
    query = text("""
        select 
            message_text as product_name, 
            count(*) as mention_count
        from raw.telegram_messages
        where message_text is not null and length(message_text) < 50
        group by message_text
        order by mention_count desc
        limit :limit
    """)
    try:
        results = db.execute(query, {"limit": limit}).fetchall()
        return [{"product_name": r[0], "mention_count": r[1]} for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failure: {str(e)}")

@app.get(
    "/api/channels/{channel_name}/activity", 
    response_model=ChannelActivityResponse,
    tags=["Channel Metrics"],
    summary="Get posting volume and timelines for a specific channel"
)
def get_channel_activity(
    channel_name: str = Path(
        ..., 
        description="The exact identifier directory name of the Telegram channel (e.g., 'CheMed123'). Case-insensitive."
    ), 
    db: Session = Depends(get_db)
):
    query = text("""
        select 
            channel_name,
            count(*) as total_messages,
            max(date_key::text) as latest_post_date
        from raw.yolo_detections
        where lower(channel_name) = lower(:channel_name)
        group by channel_name
    """)
    result = db.execute(query, {"channel_name": channel_name}).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Channel '{channel_name}' not found or contains no recorded activity.")
        
    return {
        "channel_name": result[0],
        "total_messages": result[1],
        "latest_post_date": result[2]
    }

@app.get(
    "/api/search/messages", 
    response_model=List[MessageSearchResponse],
    tags=["Search Engine"],
    summary="Search historic text contents for explicit keywords"
)
def search_messages(
    query: str = Query(
        ..., 
        min_length=2, 
        description="The alphanumeric keyword search string to match inside message bodies (e.g., 'paracetamol')."
    ), 
    limit: int = Query(
        default=20, 
        ge=1, 
        le=50, 
        description="Maximum matching message records to return. Default is 20 rows."
    ), 
    db: Session = Depends(get_db)
):
    sql = text("""
        select 
            id as message_id,
            channel as channel_name,
            message_text,
            coalesce(views, 0) as views
        from raw.telegram_messages
        where message_text ilike :search_query
        order by views desc
        limit :limit
    """)
    try:
        results = db.execute(sql, {"search_query": f"%{query}%", "limit": limit}).fetchall()
        return [
            {
                "message_id": r[0],
                "channel_name": r[1],
                "message_text": r[2],
                "views": r[3]
            } for r in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search execution failed: {str(e)}")

@app.get(
    "/api/reports/visual-content", 
    response_model=List[VisualContentStatsResponse],
    tags=["Analytical Reports"],
    summary="Fetch object classification statistics across all channels"
)
def get_visual_content_stats(db: Session = Depends(get_db)):
    query = text("""
        select 
            channel_name,
            count(*) as total_images_analyzed,
            count(case when image_category = 'promotional' then 1 end) as promotional_count,
            count(case when image_category = 'product_display' then 1 end) as product_display_count,
            count(case when image_category = 'lifestyle' then 1 end) as lifestyle_count,
            count(case when image_category = 'other' then 1 end) as other_count
        from raw.yolo_detections
        group by channel_name
        order by total_images_analyzed desc
    """)
    try:
        results = db.execute(query).fetchall()
        return [
            {
                "channel_name": r[0],
                "total_images_analyzed": r[1],
                "promotional_count": r[2],
                "product_display_count": r[3],
                "lifestyle_count": r[4],
                "other_count": r[5]
            } for r in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed fetching visualization stats: {str(e)}")