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


@app.get("/auth/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """ログインページ"""
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "title": "ログイン - パワハラフィルターチャット",
        }
    )


@app.get("/auth/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """登録ページ"""
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "title": "新規登録 - パワハラフィルターチャット",
        }
    )
