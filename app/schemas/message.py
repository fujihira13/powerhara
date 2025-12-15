from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal, Dict


class MessageBase(BaseModel):
    """メッセージ基本スキーマ"""
    text: str


class MessageCreate(MessageBase):
    """メッセージ作成スキーマ"""
    pass


class MessageUpdate(BaseModel):
    """メッセージ更新スキーマ"""
    text: str


class MessageResponse(MessageBase):
    """メッセージレスポンススキーマ"""
    id: int
    channel_id: int
    user_id: int
    is_edited: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MessageWithUser(MessageResponse):
    """ユーザー情報付きメッセージ"""
    username: str


class MessageReportCreate(BaseModel):
    """メッセージ通報作成スキーマ"""
    label: Literal["uncomfortable", "harassment_suspected"]


class MessageReportSummary(BaseModel):
    """メッセージ通報集計スキーマ"""
    message_id: int
    counts: Dict[str, int]
