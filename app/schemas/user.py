from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """ユーザー基本スキーマ"""
    email: EmailStr
    username: str


class UserCreate(UserBase):
    """ユーザー作成スキーマ"""
    password: str


class UserLogin(BaseModel):
    """ログインスキーマ"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """ユーザーレスポンススキーマ"""
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWTトークンスキーマ"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """トークンデータスキーマ"""
    user_id: Optional[int] = None
    email: Optional[str] = None
