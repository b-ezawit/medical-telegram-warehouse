from pydantic import BaseModel
from typing import Optional, List

class TopProductResponse(BaseModel):
    product_name: str
    mention_count: int

    class Config:
        from_attributes = True

class ChannelActivityResponse(BaseModel):
    channel_name: str
    total_messages: int
    latest_post_date: Optional[str] = None

    class Config:
        from_attributes = True

class MessageSearchResponse(BaseModel):
    message_id: int
    channel_name: Optional[str] = None
    message_text: Optional[str] = None
    views: Optional[int] = None

    class Config:
        from_attributes = True

class VisualContentStatsResponse(BaseModel):
    channel_name: str
    total_images_analyzed: int
    promotional_count: int
    product_display_count: int
    lifestyle_count: int
    other_count: int

    class Config:
        from_attributes = True