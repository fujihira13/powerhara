from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session
from pathlib import Path
from typing import Optional
import json
from datetime import datetime
from app.database import get_db
from app.models.message import Message
from app.models.channel import Channel
from app.models.user import User
from app.models.message_report import MessageReport
from app.schemas.message import MessageCreate, MessageUpdate, MessageReportSummary
from app.services.auth import decode_token
from app.services.websocket_manager import manager

router = APIRouter(tags=["メッセージ"])

# テンプレート設定
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

ALLOWED_REPORT_LABELS = {"uncomfortable", "harassment_suspected"}


def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Cookieからトークンを取得してユーザーを返す"""
    token = request.cookies.get("access_token")
    if not token:
        return None
    if token.startswith("Bearer "):
        token = token[7:]
    token_data = decode_token(token)
    if not token_data:
        return None
    return db.query(User).filter(User.id == token_data.user_id).first()


def get_messages_with_reports(db: Session, channel_id: int, current_user: Optional[User]):
    """メッセージ一覧に通報情報を付与して返す"""
    messages = (
        db.query(Message, User)
        .join(User, Message.user_id == User.id)
        .filter(Message.channel_id == channel_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    message_ids = [msg.id for msg, _ in messages]
    report_counts = defaultdict(dict)
    user_report_map = {}

    if message_ids:
        counts = (
            db.query(
                MessageReport.message_id,
                MessageReport.label,
                func.count(MessageReport.id).label("count"),
            )
            .filter(MessageReport.message_id.in_(message_ids))
            .group_by(MessageReport.message_id, MessageReport.label)
            .all()
        )
        for row in counts:
            report_counts[row.message_id][row.label] = row.count

        if current_user:
            user_reports = (
                db.query(MessageReport.message_id, MessageReport.label)
                .filter(
                    MessageReport.message_id.in_(message_ids),
                    MessageReport.reporter_user_id == current_user.id,
                )
                .all()
            )
            for row in user_reports:
                user_report_map[row.message_id] = row.label

    message_list = []
    for msg, msg_user in messages:
        message_list.append({
            "id": msg.id,
            "text": msg.text,
            "user_id": msg.user_id,
            "username": msg_user.username,
            "is_edited": msg.is_edited,
            "created_at": msg.created_at,
            "report_counts": report_counts.get(msg.id, {}),
            "user_report_label": user_report_map.get(msg.id),
        })

    return message_list


def render_messages_partial(request: Request, db: Session, channel_id: int, user: User):
    """メッセージリスト部分テンプレートを返す"""
    message_list = get_messages_with_reports(db, channel_id, user)
    return templates.TemplateResponse(
        "partials/messages_list.html",
        {
            "request": request,
            "messages": message_list,
            "user": user,
            "channel_id": channel_id,
        }
    )


@router.post("/channels/{channel_id}/messages", response_class=HTMLResponse)
async def create_message(
    request: Request,
    channel_id: int,
    text: str = Form(...),
    db: Session = Depends(get_db)
):
    """メッセージ投稿（HTMX対応）"""
    user = get_current_user_from_cookie(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="ログインが必要です")
    
    # チャンネル存在確認
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="チャンネルが見つかりません")
    
    # メッセージ作成
    new_message = Message(
        channel_id=channel_id,
        user_id=user.id,
        text=text,
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    # WebSocketで新規メッセージを配信
    await manager.broadcast_to_channel(channel_id, {
        "type": "new_message",
        "message": {
            "id": new_message.id,
            "text": new_message.text,
            "user_id": user.id,
            "username": user.username,
            "is_edited": False,
            "created_at": new_message.created_at.isoformat() if new_message.created_at else None,
        }
    })
    
    return render_messages_partial(request, db, channel_id, user)


@router.put("/channels/{channel_id}/messages/{message_id}", response_class=HTMLResponse)
async def update_message(
    request: Request,
    channel_id: int,
    message_id: int,
    text: str = Form(...),
    db: Session = Depends(get_db)
):
    """メッセージ編集"""
    user = get_current_user_from_cookie(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="ログインが必要です")
    
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.channel_id == channel_id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="メッセージが見つかりません")
    
    if message.user_id != user.id:
        raise HTTPException(status_code=403, detail="編集権限がありません")
    
    message.text = text
    message.is_edited = True
    db.commit()
    db.refresh(message)
    
    # WebSocketで更新を配信
    await manager.broadcast_to_channel(channel_id, {
        "type": "update_message",
        "message": {
            "id": message.id,
            "text": message.text,
            "is_edited": True,
        }
    })
    
    return render_messages_partial(request, db, channel_id, user)


@router.delete("/channels/{channel_id}/messages/{message_id}", response_class=HTMLResponse)
async def delete_message(
    request: Request,
    channel_id: int,
    message_id: int,
    db: Session = Depends(get_db)
):
    """メッセージ削除"""
    user = get_current_user_from_cookie(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="ログインが必要です")
    
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.channel_id == channel_id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="メッセージが見つかりません")
    
    if message.user_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="削除権限がありません")
    
    db.delete(message)
    db.commit()
    
    # WebSocketで削除を配信
    await manager.broadcast_to_channel(channel_id, {
        "type": "delete_message",
        "message_id": message_id,
    })
    
    return render_messages_partial(request, db, channel_id, user)


@router.post("/messages/{message_id}/report", response_class=HTMLResponse)
async def report_message(
    request: Request,
    message_id: int,
    label: str = Form(...),
    db: Session = Depends(get_db)
):
    """メッセージ通報（HTMX対応）"""
    user = get_current_user_from_cookie(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="ログインが必要です")
    
    if label not in ALLOWED_REPORT_LABELS:
        raise HTTPException(status_code=400, detail="不正なラベルです")
    
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="メッセージが見つかりません")
    
    existing = (
        db.query(MessageReport)
        .filter(
            MessageReport.message_id == message_id,
            MessageReport.reporter_user_id == user.id,
        )
        .first()
    )
    if not existing:
        report = MessageReport(
            message_id=message_id,
            reporter_user_id=user.id,
            label=label,
        )
        db.add(report)
        db.commit()
    
    return render_messages_partial(request, db, message.channel_id, user)


@router.get("/messages/{message_id}/report_summary", response_model=MessageReportSummary)
async def report_summary(
    message_id: int,
    db: Session = Depends(get_db)
):
    """メッセージ通報の集計を返す"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="メッセージが見つかりません")
    
    counts = {label: 0 for label in ALLOWED_REPORT_LABELS}
    rows = (
        db.query(
            MessageReport.label,
            func.count(MessageReport.id).label("count"),
        )
        .filter(MessageReport.message_id == message_id)
        .group_by(MessageReport.label)
        .all()
    )
    for row in rows:
        counts[row.label] = row.count
    
    return MessageReportSummary(message_id=message_id, counts=counts)


@router.websocket("/ws/channels/{channel_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    channel_id: int,
    db: Session = Depends(get_db)
):
    """WebSocketエンドポイント"""
    # クエリパラメータからトークンを取得
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001)
        return
    
    token_data = decode_token(token)
    if not token_data:
        await websocket.close(code=4001)
        return
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        await websocket.close(code=4001)
        return
    
    # 接続を登録
    await manager.connect(websocket, channel_id, user.id)
    
    try:
        while True:
            # クライアントからのメッセージを待機
            data = await websocket.receive_text()
            # ここで受信したメッセージを処理することも可能
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel_id, user.id)
