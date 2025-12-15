# パワハラフィルターチャット

パワハラ防止フィルター付きの Slack 風チャットアプリケーションです。FastAPI で API と SSR（Jinja2）を提供し、HTMX でインタラクションを強化しています。JWT 認証でログインし、チャンネルごとのメッセージは WebSocket でリアルタイム同期されます。

## 技術スタック

- **バックエンド**: FastAPI + SQLAlchemy + PostgreSQL
- **フロントエンド**: Jinja2 テンプレート + HTMX + Tailwind CSS
- **認証**: JWT ベースのトークン認証

## 必要条件

- Docker / Docker Compose (推奨)
- または Python 3.11+ / PostgreSQL 15+

## セットアップ手順

### Docker を使用する場合（推奨）

#### 1. リポジトリをクローン

```bash
cd c:\パワハラフィルターチャット
```

#### 2. 環境変数ファイルを作成

```bash
cp .env.example .env
```

`.env` の必須値（最低限）:

- `POSTGRES_PASSWORD` … DB の postgres ユーザー用パスワード
- `DATABASE_URL` … 例: `postgresql://postgres:<POSTGRES_PASSWORD>@db:5432/powerharafilter`
- `SECRET_KEY` … JWT 用の十分に長いランダム文字列（本番は必ず変更）

#### 3. Docker Compose でアプリを起動

```bash
docker compose up --build
```

#### 4. データベースマイグレーション

初回:

```bash
docker compose exec app alembic revision --autogenerate -m "initial"
docker compose exec app alembic upgrade head
```

モデルを変更したときは再度 `revision --autogenerate` と `upgrade head` を実行してください。既存のマイグレーションがある場合は `upgrade head` のみで OK です。

#### 5. アプリにアクセス

- **アプリケーション**: http://localhost:8000
- **API ドキュメント (Swagger UI)**: http://localhost:8000/docs
- **API ドキュメント (ReDoc)**: http://localhost:8000/redoc
- **Adminer (DB GUI)**: http://localhost:8080 （`System=PostgreSQL`, `Server=db`, `Username=postgres`, `Password=<POSTGRES_PASSWORD>`, `Database=powerharafilter`）

---

### ローカル環境で実行する場合

#### 1. Python 仮想環境を作成

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
```

#### 2. 依存関係をインストール

```bash
pip install -r requirements.txt
```

#### 3. PostgreSQL を起動

PostgreSQL がローカルで動作している必要があります。Docker で DB だけ起動する場合:

```bash
docker run -d --name powerharafilter-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=powerharafilter \
  -p 5432:5432 \
  postgres:15-alpine
```

#### 4. 環境変数を設定

`.env` ファイルを編集:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/powerharafilter
POSTGRES_PASSWORD=postgres  # Docker で DB を立てたときの値に合わせる
SECRET_KEY=your-secret-key
```

#### 5. データベースマイグレーション

```bash
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

#### 6. アプリを起動

```bash
uvicorn app.main:app --reload
```

## プロジェクト構成

```
c:\パワハラフィルターチャット/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI アプリケーション
│   ├── config.py            # 設定
│   ├── database.py          # DB 設定
│   ├── models/              # SQLAlchemy モデル
│   │   └── user.py
│   ├── routers/             # API ルーター
│   │   └── auth.py
│   ├── schemas/             # Pydantic スキーマ
│   │   └── user.py
│   ├── services/            # ビジネスロジック
│   │   └── auth.py
│   ├── templates/           # Jinja2 テンプレート
│   │   ├── base.html
│   │   └── index.html
│   └── static/              # 静的ファイル
│       └── css/
│           └── style.css
├── alembic/                 # マイグレーション
├── alembic.ini
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
└── README.md
```

## API エンドポイント

### 認証

| メソッド | パス | 説明 |
|---------|------|------|
| POST | `/auth/register` | ユーザー登録 |
| POST | `/auth/login` | ログイン（JWT 発行）|

### その他

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/` | トップページ |
| GET | `/health` | ヘルスチェック |
| GET | `/docs` | Swagger UI |

## 開発

### コードフォーマット

```bash
pip install black isort
black app/
isort app/
```

### リンター

```bash
pip install ruff
ruff check app/
```

## ライセンス

MIT License
