from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
from app.routers import auth
from app.config import get_settings

settings = get_settings()

# FastAPIアプリケーション
app = FastAPI(
    title="パワハラフィルターチャット",
    description="パワハラ防止フィルター付きSlack風チャットアプリケーション",
    version="1.0.0",
)

# 静的ファイルのマウント
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Jinja2テンプレート設定
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# ルーター登録
app.include_router(auth.router)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """トップページ"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "パワハラフィルターチャット",
        }
    )


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy"}
