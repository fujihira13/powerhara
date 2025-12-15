from typing import Dict, List
from fastapi import WebSocket
import json


class ConnectionManager:
    """WebSocket接続マネージャー"""
    
    def __init__(self):
        # channel_id -> list of (user_id, websocket)
        self.active_connections: Dict[int, List[tuple[int, WebSocket]]] = {}
    
    async def connect(self, websocket: WebSocket, channel_id: int, user_id: int):
        """WebSocket接続を受け入れてチャンネルに参加"""
        await websocket.accept()
        if channel_id not in self.active_connections:
            self.active_connections[channel_id] = []
        self.active_connections[channel_id].append((user_id, websocket))
    
    def disconnect(self, websocket: WebSocket, channel_id: int, user_id: int):
        """WebSocket接続を切断"""
        if channel_id in self.active_connections:
            self.active_connections[channel_id] = [
                (uid, ws) for uid, ws in self.active_connections[channel_id]
                if ws != websocket
            ]
            if not self.active_connections[channel_id]:
                del self.active_connections[channel_id]
    
    async def broadcast_to_channel(self, channel_id: int, message: dict):
        """チャンネル内のすべての接続にメッセージを送信"""
        if channel_id in self.active_connections:
            disconnected = []
            for user_id, websocket in self.active_connections[channel_id]:
                try:
                    await websocket.send_json(message)
                except Exception:
                    disconnected.append((user_id, websocket))
            # 失敗した接続を削除
            for uid, ws in disconnected:
                self.disconnect(ws, channel_id, uid)
    
    def get_channel_user_count(self, channel_id: int) -> int:
        """チャンネル内の接続数を取得"""
        return len(self.active_connections.get(channel_id, []))


# シングルトンインスタンス
manager = ConnectionManager()
