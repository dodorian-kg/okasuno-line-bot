# おかスノ LINE Bot

スノーボードグッズレンタルショップ「おかスノ」のカスタマーサポート LINE Bot。お客様からのレンタル料金・予約・営業時間に関する問い合わせに、Gemini API で自動応答し、FAQ に無い質問はスタッフへエスカレーションします。

## アーキテクチャ

- **Flask** — Webhook 受信サーバー (`/callback`, `/health`)
- **LINE Messaging API (v3 SDK)** — メッセージ送受信
- **Gemini 2.5 Flash Lite** — 回答生成（Supabase から取得した FAQ を system_instruction に注入）
- **Supabase** — FAQ マスタ (`faqs`) と エスカレーション保留ステート (`pending_handoffs`) の永続化
- **スタッフエスカレーション通知** — FAQ に無い質問にはユーザー承認後に管理者 LINE へ push 通知
- **cloudflared** — ローカル開発時に外部公開（将来は Vercel へ移行予定）

## セットアップ

### 1. 仮想環境の作成と有効化

```bash
python -m venv venv
source venv/Scripts/activate   # Windows (Git Bash)
# venv\Scripts\activate         # Windows (PowerShell / cmd)
```

### 2. 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

### 3. `.env` の作成

`.env.example` をコピーして `.env` を作成し、以下のキーを設定します。

```
LINE_CHANNEL_SECRET=<LINE Developers Console の Channel secret>
LINE_CHANNEL_ACCESS_TOKEN=<LINE Developers Console で発行した長期アクセストークン>
GEMINI_API_KEY=<Google AI Studio で発行した API キー>
SUPABASE_URL=<Supabase プロジェクトの URL>
SUPABASE_KEY=<Supabase anon key もしくは service_role key>
ADMIN_LINE_TARGET_ID=<管理者 LINE の user_id または group_id（未設定時は通知 no-op）>
```

### 4. Supabase テーブル準備

Supabase SQL Editor で以下を作成:

- `faqs` (`id`, `question`, `answer`, `category`, `updated_at`) — RLS: anon に SELECT のみ許可
- `pending_handoffs` (`user_id` PK, `original_question`, `bot_reply`, `created_at`) — SUPABASE_KEY に service_role を使うか、anon に INSERT/SELECT/DELETE を許可

### 5. サーバー起動

```bash
python app.py
```

`http://localhost:5000/health` にアクセスして `{"status": "ok"}` が返れば OK。

### 6. cloudflared で外部公開 & LINE Webhook 設定

```bash
cloudflared tunnel --url http://localhost:5000
```

発行された `https://xxxx.trycloudflare.com` を LINE Developers Console の Webhook URL に `/callback` を付けて登録します（例: `https://xxxx.trycloudflare.com/callback`）。

## 環境変数

| 変数名 | 用途 |
|---|---|
| `LINE_CHANNEL_SECRET` | Webhook 署名検証 |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Messaging API への返信・push |
| `GEMINI_API_KEY` | Gemini API 呼び出し |
| `SUPABASE_URL` | Supabase プロジェクト URL |
| `SUPABASE_KEY` | Supabase API キー (anon または service_role) |
| `ADMIN_LINE_TARGET_ID` | エスカレーション通知先の LINE user_id / group_id |

## ファイル構成

| ファイル | 役割 |
|---|---|
| `app.py` | Flask アプリ本体、Webhook ハンドラ、2 段階承認フロー |
| `config.py` | `.env` 読み込み、起動時検証、システムプロンプト、定型文定数 |
| `gemini_client.py` | Gemini API クライアント (FAQ 注入) |
| `supabase_client.py` | Supabase クライアント (FAQ 取得、pending_handoffs 操作) |
| `notifier.py` | 管理者 LINE への push 通知ラッパ |
| `requirements.txt` | Python 依存ライブラリ |
| `TODO.md` | 開発ロードマップ |
| `Instruction.md` | 構築手順書 |
