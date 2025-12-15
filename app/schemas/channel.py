from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ChannelBase(BaseModel):
    """チャンネル基本スキーマ"""
    name: str
    description: Optional[str] = None


class ChannelCreate(ChannelBase):
    """チャンネル作成スキーマ"""
    pass


class ChannelResponse(ChannelBase):
    """チャンネルレスポンススキーマ"""
    id: int
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True
