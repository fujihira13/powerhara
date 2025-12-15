---
description: Docker開発ワークフロー（初心者向け）
---

# Docker開発ワークフロー

このファイルは、ファイルを修正してDockerで確認するための手順をまとめたものです。

## 🚀 基本的な開発フロー

### ステップ1: Dockerが起動しているか確認

```powershell
docker compose ps
```

起動していない場合:
```powershell
$env:COMPOSE_PROJECT_NAME='powerharafilter'; docker compose up -d
```

---

### ステップ2: ファイルを修正

VS Codeでファイルを編集して保存（Ctrl + S）

---

### ステップ3: 変更の反映方法

#### パターンA: Pythonファイルを修正した場合（自動反映）

- 保存するだけで自動的に再読み込みされます
- ログで確認:
```powershell
docker compose logs -f app
```

#### パターンB: HTML/CSS/JSファイルを修正した場合（自動反映）

- ブラウザでスーパーリロード（Ctrl + Shift + R）

#### パターンC: requirements.txtを修正した場合（再ビルド必要）

```powershell
docker compose down
$env:COMPOSE_PROJECT_NAME='powerharafilter'; docker compose up --build -d
```

#### パターンD: データベースモデルを修正した場合（マイグレーション必要）

```powershell
docker compose exec app alembic revision --autogenerate -m "変更内容"
docker compose exec app alembic upgrade head
```

---

### ステップ4: ブラウザで動作確認

http://localhost:8000 にアクセス

---

## 🔧 よく使うコマンド

### Dockerの起動・停止

```powershell
# 起動
$env:COMPOSE_PROJECT_NAME='powerharafilter'; docker compose up -d

# 停止
docker compose down

# 再起動
docker compose restart
```

### ログ確認

```powershell
# リアルタイムでログを表示
docker compose logs -f

# appサービスのログだけ表示
docker compose logs -f app

# 最新50行を表示
docker compose logs app --tail 50
```

### トラブルシューティング

```powershell
# エラーが出た場合、コンテナを完全に再起動
docker compose down
$env:COMPOSE_PROJECT_NAME='powerharafilter'; docker compose up --build -d

# データベースも含めて完全クリーンアップ（注意！データが消えます）
docker compose down -v
$env:COMPOSE_PROJECT_NAME='powerharafilter'; docker compose up --build -d
```

---

## 📋 チェックリスト

ファイル修正後、以下を確認してください:

- [ ] ファイルを保存した（Ctrl + S）
- [ ] 必要に応じて再ビルドした
- [ ] `docker compose ps` でコンテナが起動していることを確認
- [ ] `docker compose logs app --tail 20` でエラーがないか確認
- [ ] ブラウザで http://localhost:8000 にアクセスして動作確認
- [ ] ブラウザをスーパーリロード（Ctrl + Shift + R）した

---

## ⚠️ 重要な注意点

1. **プロジェクトパスに日本語が含まれているため**、Dockerを起動する際は必ず以下のコマンドを使用してください:
   ```powershell
   $env:COMPOSE_PROJECT_NAME='powerharafilter'; docker compose up -d
   ```

2. **ホットリロード**が有効になっているため、Pythonファイルの変更は自動的に反映されます（保存するだけでOK）

3. **データベースマイグレーション**は手動で実行する必要があります

4. **ブラウザのキャッシュ**が原因で変更が反映されない場合は、スーパーリロード（Ctrl + Shift + R）を試してください
