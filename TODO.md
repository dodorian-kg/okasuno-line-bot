# おかスノ LINE Bot 開発ロードマップ

> 最終目標: Git/GitHub でバージョン管理し、Supabase に FAQ・予約データを保存、Vercel で 24/7 本番稼働する LINE Bot

## Phase 1: 環境構築と設定ファイルの準備

- [x] Python仮想環境を作成し、有効化する
  > ゴール: `python --version` で Python 3.9+ が表示される
- [x] 必要なライブラリをインストールする（flask, line-bot-sdk, anthropic, python-dotenv）
  > ゴール: `pip install -r requirements.txt` がエラーなく完了する
- [x] `requirements.txt` を作成する
  > ゴール: ファイルに4つのライブラリとバージョンが記載されている
- [x] `.env` ファイルを作成し、APIキーを設定する（LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN, GEMINI_API_KEY）
  > ゴール: `.env` に3つのキーが設定され、`config.py` から読み込める
- [x] `config.py` で環境変数を読み込む処理を書く
  > ゴール: `python -c "from config import LINE_CHANNEL_SECRET; print('OK')"` がエラーなく実行できる
- [x] `.gitignore` を作成し、`.env` や `__pycache__/` を除外する
  > ゴール: `git status` で `.env` が追跡対象に表示されない

## Phase 2: サーバー基盤の作成

- [x] Flaskアプリを作成し、`/callback` エンドポイントを実装する
  > ゴール: `python app.py` でサーバーが起動し、ログに「サーバー起動」と表示される
- [x] `/health` エンドポイントを追加する（動作確認用）
  > ゴール: ブラウザで `http://localhost:5000/health` にアクセスし `{"status": "ok"}` が返る
- [x] cloudflared (Cloudflare Tunnel) をインストールし、ローカルサーバーを外部公開する
  > ゴール: `cloudflared tunnel --url http://localhost:5000` で発行されたURLにブラウザからアクセスでき、`/health` が応答する
- [x] LINE Developers ConsoleでWebhook URLを設定する
  > ゴール: ConsoleのWebhook設定に `https://xxxx.trycloudflare.com/callback` を入力し、「検証」ボタンで成功する
- [x] Webhook署名検証の動作を確認する
  > ゴール: LINE ConsoleからのWebhook検証で200が返り、不正なリクエストには400が返る

## Phase 3: オウム返しBotの実装

- [x] `handle_message` をオウム返しに変更して動作確認する（Claude連携を一時的に外す）
  > ゴール: LINEで「こんにちは」と送ると「こんにちは」とそのまま返ってくる
- [x] LINEアプリからメッセージを送り、端末〜サーバー〜LINE間の通信が正常に動くことを確認する
  > ゴール: 送信→受信→返信の一連のフローがエラーなく動作し、サーバーのログにメッセージ内容が記録される

## Phase 4: Gemini API連携

- [x] `gemini_client.py` を作成し、Gemini APIにメッセージを送って返答を受け取る関数を実装する
  > ゴール: `python -c "from gemini_client import get_gemini_response; print(get_gemini_response('こんにちは'))"` でAIの返答が表示される
- [x] `config.py` にシステムプロンプト（おかスノのサポート用）を定義する
  > ゴール: `SYSTEM_PROMPT` にショップの役割・対応範囲が記述されている
- [x] `handle_message` でオウム返しをGemini連携に切り替える
  > ゴール: LINEで質問を送ると、おかスノのサポートBotとしてAIが返答する
- [x] LINEから実際に複数パターンのメッセージを送り、期待通りの返答が返ることを確認する
  > ゴール: 「レンタル料金は？」「予約したい」「営業時間は？」等を送り、それぞれ適切な返答が返る

## Phase 5: Git / GitHub 導入

- [x] `git init` でローカルリポジトリを初期化する
  > ゴール: `git status` でワーキングツリーが表示される
- [x] `.gitignore` が `venv/`・`.env`・`__pycache__/` を除外しているか確認・追記する
  > ゴール: `git status` に `.env` と `venv/` が表示されない
- [x] 初回コミット（Phase 1〜4 の成果を一括コミット）を行う
  > ゴール: `git log` に初回コミットが記録される
- [ ] GitHub で Private リポジトリを作成する（例: `okasuno-line-bot`）
  > ゴール: GitHub Web 上で空のリポジトリが存在する
- [ ] リモート登録と初回 push（`git remote add origin ...` → `git push -u origin main`）を行う
  > ゴール: GitHub Web 上に全ファイル（`.env` 以外）が表示される
- [x] `README.md` を作成する（Bot の概要・セットアップ手順・環境変数一覧）
  > ゴール: リポジトリトップで概要が読める

## Phase 6: エラーハンドリングとコードの整理

- [x] Gemini APIのエラー（接続エラー、レート制限、その他例外）にフォールバックメッセージを返す処理を追加する
  > ゴール: APIエラー時にユーザーへ「しばらくお待ちください」等のメッセージが返り、サーバーがクラッシュしない
- [x] `app.py` にロギング（`logging`モジュール）を導入する
  > ゴール: メッセージの受信・返信・エラーがタイムスタンプ付きでコンソールに出力される
- [x] Webhook署名検証失敗時のログとエラーレスポンスを確認する
  > ゴール: 不正リクエスト受信時に警告ログが出力され、400が返ることをテストで確認する
- [ ] コード全体を見直し、不要なコメント・未使用importがないことを確認する
  > ゴール: 各ファイルが整理され、`python app.py` で警告なく起動する

## Phase 7: Supabase 連携（FAQ・商品マスタ＋予約データ）

> 2026-04-20 方針決定: 店舗情報 (料金・営業時間など) は Supabase `faqs` に保存。デプロイ後は Supabase ダッシュボードから編集すれば再デプロイ不要で即反映される運用にする。

- [x] Supabase プロジェクトを作成し、URL と anon key を控える
  > ゴール: Supabase ダッシュボードでプロジェクトが開ける
- [x] `supabase` Python クライアントを `requirements.txt` に追加する
  > ゴール: `pip install -r requirements.txt` で `supabase-py` が入る
- [x] `.env` に `SUPABASE_URL` / `SUPABASE_KEY` を追加し、`config.py` で読み込む
  > ゴール: `python -c "from config import SUPABASE_URL; print('OK')"` がエラーなく動く
- [x] Supabase SQL Editor で `faqs` テーブルを作成する（`id`, `question`, `answer`, `category`, `updated_at`）
  > ゴール: Table Editor に `faqs` が存在し、サンプルFAQを挿入できる
  > スキーマ: `id bigint generated always as identity pk, question text not null, answer text not null, category text not null, updated_at timestamptz default now()`
  > RLS: anon に SELECT のみ許可（書き込みは拒否）
  > シード category 案: 料金 / 営業時間 / 予約方法 / キャンセルポリシー / アクセス / 持ち物 / サイズ展開 / 支払い / その他
- [ ] Supabase SQL Editor で `reservations` テーブルを作成する（`id`, `line_user_id`, `plan`, `reserved_at`, `party_size`, `status`, `created_at`）
  > ゴール: Table Editor に `reservations` が存在する
- [x] `supabase_client.py` を作成し、FAQ 取得関数を実装する
  > ゴール: `python -c "from supabase_client import get_all_faqs; print(get_all_faqs())"` でサンプルFAQが返る
  > 実装済: `get_all_faqs()` / `format_faqs_for_prompt()` / `set_pending_handoff()` / `pop_pending_handoff()`
- [x] `gemini_client.py` を改修し、回答前に FAQ を取得して Gemini のプロンプトに組み込む
  > ゴール: 「レンタル料金は？」と送ると Supabase 上の FAQ に基づいた回答が返る
  > 毎リクエストで FAQ を取得 → `## 店舗情報(最新)` として system_instruction に注入
- [ ] 予約キーワード検知時、対話フローで日時・プラン・人数を聞き取り `reservations` に INSERT する
  > ゴール: LINE から予約を実行すると Supabase にレコードが追加され、確認メッセージが返る

## Phase 7.5: スタッフエスカレーション通知（2 段階承認）

> FAQ に無い質問が来たとき、Bot が「スタッフにお繋ぎしましょうか？」と尋ね、ユーザーが肯定したら管理者 LINE に通知する 2 段階フロー。状態は Supabase に保持し、Vercel サーバーレスでも成立するようにする。

- [x] `config.py` で `HANDOFF_PHRASE = "スタッフにお繋ぎしましょうか？"` を定数化し、SYSTEM_PROMPT をペルソナ + 注入ルール + 定型質問文に再構成
  > ゴール: FAQ に無い内容への回答末尾に必ず HANDOFF_PHRASE が付く
- [x] `notifier.py` を作成し `notify_staff(user_text, bot_text)` で LINE `push_message` を送るラッパを実装
  > ゴール: ADMIN_LINE_TARGET_ID 未設定時は警告ログで no-op、送信失敗も握り潰してログのみ
- [x] Supabase SQL Editor で `pending_handoffs` テーブルを作成する
  > ```sql
  > create table pending_handoffs (
  >   user_id text primary key,
  >   original_question text not null,
  >   bot_reply text not null,
  >   created_at timestamptz default now()
  > );
  > alter table pending_handoffs enable row level security;
  > ```
  > RLS: SUPABASE_KEY に service_role を使うか、このテーブルは anon に INSERT/SELECT/DELETE を許可する専用ポリシーを設定
- [x] `app.py` で 2 段階承認フローを実装
  > ゴール:
  > 1. 毎受信で `pop_pending_handoff(user_id)` を実行
  > 2. 保留中 + 肯定語 (yes/はい/お願い/ok/了解 等) → `notify_staff` + 「スタッフに連絡しました」
  > 3. 保留中 + 否定語 (no/いいえ/結構/大丈夫 等) → 「承知しました」で終了
  > 4. 保留なし → Gemini 応答 → 返答に HANDOFF_PHRASE が含まれれば `set_pending_handoff` で保留登録
  > 5. 保留は 10 分で失効
- [ ] `ADMIN_LINE_TARGET_ID` を `.env` に設定する
  > 取得手順: 管理者 LINE で Bot に一度メッセージ送信 → `app.py` のログ `source=...` から `user_id` をコピー → `.env` に貼り付け → 再起動
  > グループ通知にしたい場合は Bot をグループに招待 → グループで発言 → `group_id` を取得して貼り付け
- [ ] エンドツーエンド検証
  > 1. FAQ に無い質問を送る → Bot が `スタッフにお繋ぎしましょうか？` と返す
  > 2. 続けて「はい」と送る → 管理者 LINE に「🔔 スタッフ対応依頼」通知が届く
  > 3. 再度 FAQ に無い質問 → 「いいえ」で返す → 通知が飛ばないこと
  > 4. FAQ にヒットする質問 (例: 営業時間) では通知が発生しないこと

## Phase 8: Vercel デプロイ

- [ ] `vercel.json` を作成し、Flask アプリを serverless function として配置する（`api/index.py` 等）
  > ゴール: `vercel dev` でローカル起動し、`/health` が応答する
- [ ] Vercel アカウントを作成し、Phase 5 で作成した GitHub Private リポを import する
  > ゴール: Vercel ダッシュボードにプロジェクトが表示される
- [ ] Vercel 環境変数に `LINE_CHANNEL_SECRET` / `LINE_CHANNEL_ACCESS_TOKEN` / `GEMINI_API_KEY` / `SUPABASE_URL` / `SUPABASE_KEY` を設定する
  > ゴール: Vercel Project Settings → Environment Variables に5件登録済み
- [ ] GitHub へ push し、Vercel の自動デプロイが成功することを確認する
  > ゴール: `https://xxx.vercel.app/health` がブラウザで `{"status": "ok"}` を返す
- [ ] LINE Developers Console の Webhook URL を `https://xxx.vercel.app/callback` に変更する
  > ゴール: LINE からメッセージを送ると Vercel 経由で応答が返る（PC を落としても稼働）
- [ ] cloudflared を停止し、Vercel 本番運用に切り替える
  > ゴール: `cloudflared` プロセスを起動せずに Bot が動作し続ける