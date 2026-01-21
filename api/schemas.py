from pydantic import BaseModel
from typing import Optional, List


class ProductReport(BaseModel):
    term: str
    count: int


class ChannelActivity(BaseModel):
    date: str
    message_count: int
    total_views: int


class MessageItem(BaseModel):
    message_id: int
    channel_name: str
    message_date: str
    message_text: str
    view_count: int
    forward_count: int
    has_image: bool


class VisualContentStats(BaseModel):
    channel_name: str
    total_messages: int
    messages_with_images: int
    promotional: int
    product_display: int
    lifestyle: int
    other: int
