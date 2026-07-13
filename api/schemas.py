# api/schemas.py
from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional

# --- Endpoint 1: Top Products Response ---
class TopProductResponse(BaseModel):
    product_name: str
    mention_count: int

    class Config:
        from_attributes = True

# --- Endpoint 2: Channel Activity Response ---
class ChannelActivityResponse(BaseModel):
    channel_name: str
    channel_type: str
    total_posts: int
    avg_views: float
    first_post_date: Optional[datetime] = None
    last_post_date: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Endpoint 3: Message Search Response ---
class MessageSearchResponse(BaseModel):
    message_id: int
    channel_name: str
    full_date: date
    message_text: Optional[str] = None
    view_count: int
    forward_count: int

    class Config:
        from_attributes = True

# --- Endpoint 4: Visual Content Stats Response ---
class VisualContentStat(BaseModel):
    channel_name: str
    total_images: int
    promotional_count: int
    product_display_count: int
    lifestyle_count: int
    other_count: int

class VisualContentResponse(BaseModel):
    summary: str
    channels: List[VisualContentStat]

    class Config:
        from_attributes = True