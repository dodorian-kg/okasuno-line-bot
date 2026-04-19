# おかスノ LINE Bot

スノーボードグッズレンタルショップ「おかスノ」のカスタマーサポート LINE Bot。お客様からのレンタル料金・予約・営業時間に関する問い合わせに、Gemini API で自動応答します。

## アーキテクチャ

- **Flask** — Webhook 受信サーバー (`/callback`, `/health`)
- **LINE Messaging API (v3 SDK)** — メッセージ送受信
- **Gemini 2.5 Flash Lite** — 回答生成
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
```

### 4. サーバー起動

```bash
python app.py
```

`http://localhost:5000/health` にアクセスして `{"status": "ok"}` が返れば OK。

### 5. cloudflared で外部公開 & LINE Webhook 設定

```bash
cloudflared tunnel --url http://localhost:5000
```

発行された `https://xxxx.trycloudflare.com` を LINE Developers Console の Webhook URL に `/callback` を付けて登録します（例: `https://xxxx.trycloudflare.com/callback`）。

## 環境変数

| 変数名 | 用途 |
|---|---|
| `LINE_CHANNEL_SECRET` | Webhook 署名検証 |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Messaging API への返信 |
| `GEMINI_API_KEY` | Gemini API 呼び出し |

## ファイル構成

| ファイル | 役割 |
|---|---|
| `app.py` | Flask アプリ本体、Webhook ハンドラ |
| `config.py` | `.env` 読み込み & システムプロンプト定義 |
| `gemini_client.py` | Gemini API クライアント |
| `requirements.txt` | Python 依存ライブラリ |
| `TODO.md` | 開発ロードマップ |
| `Instruction.md` | 構築手順書 |
