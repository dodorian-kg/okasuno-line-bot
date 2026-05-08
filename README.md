# Okasuno LINE Bot

スノーボードグッズレンタルショップ「おかスノ」のカスタマーサポート LINE Bot。FAQ をもとに自動回答し、FAQ に無い質問は誤回答を避けるためスタッフ対応へ誘導します。

- 本番 URL: <https://okasuno-line-bot.vercel.app>
- ヘルスチェック: <https://okasuno-line-bot.vercel.app/health> （`{"status": "ok"}` を返します）

## 友だち追加して試す

実機で動作を確認したい場合は、以下から LINE 公式アカウントを友だち追加してメッセージを送ってください。

- 友だち追加 URL: `<https://lin.ee/u7E2h5Y>`

<!-- QR 画像配置時に有効化: ![LINE 友だち追加 QR](assets/line-qr.png) -->

## 概要

友人と行っているレンタル事業向けに作成した LINE Bot です。ユーザーからの問い合わせに対して、FAQ データベースをもとに自動回答し、FAQ にない質問については誤回答を避けるためスタッフ対応へ誘導します。

## 作成背景

レンタル事業では、料金、予約方法、受け取り方法、返却方法など、同じような問い合わせが繰り返し発生します。これらの問い合わせ対応を効率化し、ユーザーが LINE 上で簡単に情報を確認できるようにするために開発しました。

## 主な機能

- **LINE メッセージの受信**: Webhook で受信し、署名検証 (`X-Line-Signature`) を行ったうえで処理します。
- **FAQ データベースを参照した自動回答**: Supabase 上の `faqs` テーブルを Gemini の `system_instruction` に注入し、FAQ 範囲内の事実のみで回答します。
- **FAQ にない質問へのスタッフ対応誘導**: FAQ 外の質問には推測で答えず、「スタッフにお繋ぎしましょうか？」と確認します。
- **2 段階のエスカレーション**: ユーザーが「はい」と承認した時点で初めてスタッフへ通知し、誤通知を防ぎます。保留状態は Supabase に 10 分 TTL で永続化します。
- **スタッフへの LINE 通知**: 管理者の LINE（個人 / グループ）へ Push メッセージで「ユーザーの質問」と「Bot の暫定回答」を送信します。
- **環境変数による API キー管理**: LINE / Gemini / Supabase の認証情報はすべて `.env`（ローカル）または Vercel 環境変数（本番）で管理し、コード内ハードコードはありません。
- **Vercel での 24/7 稼働**: Serverless Python（`@vercel/python`）でデプロイし、GitHub への push で自動更新されます。

## 使用技術

### ランタイム

| 種類 | 採用技術 |
|---|---|
| 言語 | Python 3.9+ |
| Web フレームワーク | Flask |
| LINE 連携 | `line-bot-sdk` v3（Messaging API v3） |
| 生成 AI | Google Gemini API（`google-genai` / `gemini-2.5-flash-lite`） |
| データベース | Supabase（PostgreSQL + REST） |
| 設定管理 | `python-dotenv` |

### インフラ

- **Vercel (Serverless Python)** — `api/index.py` を entry に Flask app をラップして 24/7 稼働。
- **Supabase** — `faqs`（FAQ マスタ）と `pending_handoffs`（エスカレーション保留）を保持。
- **cloudflared** — ローカル開発時に LINE Webhook を一時的に外部公開する用途のみ。

### 開発支援

- **ChatGPT** — 要件整理・設計の壁打ち。
- **Claude Code** — 実装補助・エラー調査・コード改善。

> Bot がユーザーへ返信する回答そのものは Gemini API が生成します。Claude Code はあくまで開発時に使用したアシスタントであり、ランタイムには含まれません。

## システム構成

```
ユーザー
  ↓ LINE
LINE Messaging API
  ↓ Webhook (署名検証)
Vercel Serverless / Flask (/callback)
  ↓
Supabase (faqs を取得) ─→ Gemini API (system_instruction に FAQ を注入して回答生成)
  ↓
  ├─ FAQ で回答可能 → そのまま自動返信
  └─ FAQ で回答不可 → 「スタッフにお繋ぎしましょうか？」と確認
                        ↓ ユーザーが「はい」
                      Supabase pending_handoffs を確認
                        ↓
                      管理者 LINE へ Push 通知（ADMIN_LINE_TARGET_ID）
                        ↓
                      ユーザーへ「スタッフに連絡しました」と返信
```

## 工夫した点

- **FAQ に存在しない質問は推測で回答しない**。誤情報による信用失墜を避けるため、Gemini への `system_instruction` で「FAQ にない事項はスタッフ誘導文を返す」と明示しています。
- **エスカレーションを 2 段階に分離**。Bot が一方的に通知すると誤通知が増えるため、ユーザーの承認を挟むことでスタッフ側の負荷を抑えました。
- **保留状態を Supabase に永続化（10 分 TTL）**。Vercel の Serverless 環境ではプロセスメモリが揮発するため、`pending_handoffs` テーブルに保存して再起動でも保持されるようにしました。
- **LINE 上で完結する UX**。ユーザーがアプリや Web を切り替えずに、友だち追加した LINE 内で問い合わせから連絡までを完了できるよう設計しました。
- **API キーは環境変数で一元管理**。`.env` はリポジトリにコミットせず、`.env.example` のみ配置。本番では Vercel の環境変数として登録しています。
- **AI を活用しつつ、判断は自分で行う**。仕様判断・動作確認・修正方針の決定は自分で行い、AI はあくまで作業を加速させるパートナーとして位置づけました。

## 苦労した点

- 未経験に近い状態から、LINE Messaging API / Webhook 署名検証 / Supabase / Vercel Serverless の接続関係を 1 つずつ理解しながら統合していく工程。
- ローカルでは再現しなかった本番特有の不具合（`pending_handoffs` の `created_at` が UPSERT 時に更新されず、2 回目以降の保留が即時失効してしまう問題）に遭遇し、UPSERT で `created_at=now()` を明示することで解消した経験。
- Gemini API のレート制限・コスト感の把握、および Vercel Hobby tier の 10 秒タイムアウト制約を踏まえた処理設計。

## AI 活用について

本プロジェクトでは、AI を開発を加速させるパートナーとして活用しました。

- **要件整理・設計の壁打ち**: ChatGPT
- **実装補助・エラー調査・コード改善**: Claude Code
- **仕様判断・動作確認・修正方針の最終決定**: 自分
- **Bot のランタイム回答生成（ユーザーへの返信）**: Gemini API

AI を単なるコード生成ツールとしてではなく、思考の壁打ち相手・実装の補助役として使うことで、未経験領域の学習速度と実装スピードの両立を意識しました。

## セットアップ手順

### 前提

- Python 3.9+
- LINE Developers アカウント（Messaging API チャネル作成済み）
- Supabase プロジェクト
- Google AI Studio で発行した Gemini API キー

### 1. リポジトリ取得と仮想環境の作成

```bash
git clone <このリポジトリの URL>
cd line-bot

python -m venv venv
venv\Scripts\activate            # Windows (PowerShell / cmd)
# source venv/Scripts/activate   # Windows (Git Bash)
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

| 変数名 | 用途 |
|---|---|
| `LINE_CHANNEL_SECRET` | Webhook 署名検証 |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Messaging API への返信・push |
| `GEMINI_API_KEY` | Gemini API 呼び出し |
| `SUPABASE_URL` | Supabase プロジェクト URL |
| `SUPABASE_KEY` | Supabase API キー（anon または service_role） |
| `ADMIN_LINE_TARGET_ID` | エスカレーション通知先の LINE user_id / group_id |

### 4. Supabase テーブルの準備

Supabase の SQL Editor で以下のテーブルを作成します。

- `faqs` (`id`, `question`, `answer`, `category`, `updated_at`) — RLS は anon に SELECT のみ許可。
- `pending_handoffs` (`user_id` PK, `original_question`, `bot_reply`, `created_at`) — `SUPABASE_KEY` に service_role を使うか、anon に INSERT / SELECT / DELETE を許可。

### 5. ローカルサーバーの起動と疎通確認

```bash
python app.py
```

`http://localhost:5000/health` にアクセスして `{"status": "ok"}` が返れば起動成功です。

### 6. cloudflared で LINE Webhook を一時受信（ローカル検証時のみ）

本番は Vercel が常時稼働しているため、ローカルで LINE からの Webhook を受けたい時だけ cloudflared を起動します。

```bash
cloudflared tunnel --url http://localhost:5000
```

発行された `https://xxxx.trycloudflare.com/callback` を LINE Developers Console の Webhook URL に一時登録します。

### 7. 本番デプロイ（Vercel）

GitHub への push で Vercel が自動デプロイします。

- Entry: `api/index.py` が `app.py` の Flask app を import し、`@vercel/python` で serverless 関数化（[vercel.json](vercel.json) 参照）。
- 本番 URL: `https://okasuno-line-bot.vercel.app`
- LINE Webhook URL: `https://okasuno-line-bot.vercel.app/callback` を LINE Developers Console に登録。
- 環境変数: 上記 6 件を Vercel プロジェクト設定に同名で登録。

## ファイル構成

| ファイル | 役割 |
|---|---|
| [app.py](app.py) | Flask アプリ本体、Webhook ハンドラ、2 段階承認フロー |
| [config.py](config.py) | `.env` 読み込み、起動時検証、システムプロンプト、定型文定数 |
| [gemini_client.py](gemini_client.py) | Gemini API クライアント（FAQ 注入） |
| [supabase_client.py](supabase_client.py) | Supabase クライアント（FAQ 取得、`pending_handoffs` 操作） |
| [notifier.py](notifier.py) | 管理者 LINE への push 通知ラッパ |
| [api/index.py](api/index.py) | Vercel serverless entry（Flask app の re-export） |
| [vercel.json](vercel.json) | Vercel ビルド設定（`@vercel/python`） |
| [requirements.txt](requirements.txt) | Python 依存ライブラリ |
| [TODO.md](TODO.md) | 開発ロードマップと進捗記録 |
| [Instruction.md](Instruction.md) | 構築手順・学習メモ |
