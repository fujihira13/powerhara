from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from typing import Optional
from app.database import get_db
from app.models.channel import Channel
from app.models.user import User
from app.schemas.channel import ChannelCreate, ChannelResponse
from app.services.auth import get_current_user_required

router = APIRouter(prefix="/channels", tags=["チャンネル"])

# テンプレート設定
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Cookieからトークンを取得してユーザーを返す"""
    from app.services.auth import decode_token
    token = request.cookies.get("access_token")
    if not token:
        return None
    # "Bearer "を削除
    if token.startswith("Bearer "):
        token = token[7:]
    token_data = decode_token(token)
    if not token_data:
        return None
    return db.query(User).filter(User.id == token_data.user_id).first()


def require_login(request: Request, db: Session = Depends(get_db)) -> User:
    """ログイン必須"""
    user = get_current_user_from_cookie(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/auth/login"}
        )
    return user


@router.get("", response_class=HTMLResponse)
async def channels_list(
    request: Request,
    db: Session = Depends(get_db)
):
    """チャンネル一覧ページ"""
    user = get_current_user_from_cookie(request, db)
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/auth/login", status_code=303)
    
    channels = db.query(Channel).order_by(Channel.created_at.desc()).all()
    return templates.TemplateResponse(
        "channels/list.html",
        {
            "request": request,
            "channels": channels,
            "user": user,
            "title": "チャンネル一覧",
        }
    )


@router.post("", response_class=HTMLResponse)
async def create_channel(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db)
):
    """チャンネル作成（HTMX対応）"""
    user = get_current_user_from_cookie(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="ログインが必要です")
    
    # 重複チェック
    existing = db.query(Channel).filter(Channel.name == name).first()
    if existing:
        return templates.TemplateResponse(
            "partials/channel_error.html",
            {
                "request": request,
                "error": "このチャンネル名は既に使用されています",
            }
        )
    
    # 新規チャンネル作成
    new_channel = Channel(
        name=name,
        description=description,
        created_by=user.id,
    )
    db.add(new_channel)
    db.commit()
    db.refresh(new_channel)
    
    # チャンネル一覧の部分テンプレートを返す
    channels = db.query(Channel).order_by(Channel.created_at.desc()).all()
    return templates.TemplateResponse(
        "partials/channel_list.html",
        {
            "request": request,
            "channels": channels,
        }
    )


@router.get("/{channel_id}", response_class=HTMLResponse)
async def channel_detail(
    request: Request,
    channel_id: int,
    db: Session = Depends(get_db)
):
    """チャンネル詳細（メッセージ一覧）ページ"""
    user = get_current_user_from_cookie(request, db)
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/auth/login", status_code=303)
    
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="チャンネルが見つかりません")
    
    # メッセージとユーザー情報を取得
    from app.models.message import Message
    messages = (
        db.query(Message, User)
        .join(User, Message.user_id == User.id)
        .filter(Message.channel_id == channel_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    
    # メッセージリストを整形
    message_list = []
    for msg, msg_user in messages:
        message_list.append({
            "id": msg.id,
            "text": msg.text,
            "user_id": msg.user_id,
            "username": msg_user.username,
            "is_edited": msg.is_edited,
            "created_at": msg.created_at,
        })
    
    return templates.TemplateResponse(
        "channels/detail.html",
        {
            "request": request,
            "channel": channel,
            "messages": message_list,
            "user": user,
            "title": f"#{channel.name}",
        }
    )
