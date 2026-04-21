# おかスノ LINE Bot 開発ロードマップ

> 最終目標: Git/GitHub でバージョン管理し、Supabase に FAQ・予約データを保存、Vercel で 24/7 本番稼働する LINE Bot
> **2026-04-20 本番稼働開始** — Vercel サーバーレス + Supabase + Gemini で LINE Webhook が 24/7 応答中

## 現在のステータス

- 本番 URL: https://okasuno-line-bot.vercel.app
- LINE Webhook: Vercel に切替済 (cloudflared 停止済)
- Gemini モデル: `gemini-2.5-flash-lite` (有料・前払い残高)
- 稼働中の構成: Vercel (api/index.py) → Flask app → Gemini 2.5 Flash-Lite / Supabase

## 翌日以降に必要なタスク

- [x] Phase 7.6: `pending_handoffs` が本番で保存されないバグの調査・修正
  > 2026-04-21 解決: 原因は (1) pop の無条件削除 (仮説 b) + (2) `set_pending_handoff` の upsert で `created_at` が更新されず TTL が早期に切れる問題 の 2 つ
  > 対応: pop を peek + delete に 2 フェーズ化 + upsert payload に `created_at=now()` を明示追加
  > 本格対応案 (後日、race condition が再度問題化したら): /callback 即時 ACK + push_message 非同期化 + event_id による冪等性担保
- [ ] Vercel トライアル期限 (2026-05-04 頃) 前に Hobby プラン (無料) へダウングレードするか有料継続するか判断
- [ ] Phase 7 の `reservations` テーブル / 予約フローの実装 (スコープが固まったら)

---

## Phase 1: 環境構築と設定ファイルの準備

- [x] Python仮想環境を作成し、有効化する
- [x] 必要なライブラリをインストールする（flask, line-bot-sdk, anthropic, python-dotenv）
- [x] `requirements.txt` を作成する
- [x] `.env` ファイルを作成し、APIキーを設定する
- [x] `config.py` で環境変数を読み込む処理を書く
- [x] `.gitignore` を作成し、`.env` や `__pycache__/` を除外する

## Phase 2: サーバー基盤の作成

- [x] Flaskアプリを作成し、`/callback` エンドポイントを実装する
- [x] `/health` エンドポイントを追加する
- [x] cloudflared でローカルサーバーを外部公開する (開発時のみ使用、Phase 8 で役目終了)
- [x] LINE Developers ConsoleでWebhook URLを設定する
- [x] Webhook署名検証の動作を確認する

## Phase 3: オウム返しBotの実装

- [x] `handle_message` をオウム返しで実装して疎通確認
- [x] LINE ↔ サーバー ↔ LINE の通信フローをログで確認

## Phase 4: Gemini API連携

- [x] `gemini_client.py` を作成し、Gemini API で返答を取得
- [x] `config.py` にシステムプロンプト (おかスノサポート用) を定義
- [x] `handle_message` を Gemini 連携に切替
- [x] 複数パターンで動作確認

## Phase 5: Git / GitHub 導入

- [x] `git init` で初期化
- [x] `.gitignore` で venv/.env/__pycache__ を除外
- [x] 初回コミット
- [x] GitHub Private リポジトリ `okasuno-line-bot` を作成
- [x] remote 登録 + 初回 push
- [x] README.md を作成

## Phase 6: エラーハンドリングとコードの整理

- [x] Gemini API エラー時のフォールバックメッセージを実装 (`app.py` の try/except)
- [x] `logging` モジュールでログ出力
- [x] Webhook 署名検証失敗時のログ・400 レスポンス確認
- [ ] コード全体を見直し、不要なコメント・未使用 import を確認
  > Phase 8 完了後、落ち着いたタイミングで実施

## Phase 7: Supabase 連携（FAQ・商品マスタ＋予約データ）

- [x] Supabase プロジェクトを作成
- [x] `supabase` Python クライアントを requirements.txt に追加
- [x] `.env` / `config.py` に SUPABASE_URL / SUPABASE_KEY を追加
- [x] `faqs` テーブルを作成し、サンプル投入
- [ ] `reservations` テーブルを作成
  > 予約フローの要件が固まってから着手 (現時点では FAQ 対応のみで運用開始)
- [x] `supabase_client.py` で FAQ 取得 + pending_handoff 操作を実装
- [x] `gemini_client.py` で FAQ を system_instruction に注入
- [ ] 予約キーワード検知時の対話フロー (日時・プラン・人数) で `reservations` に INSERT
  > reservations テーブル作成後

## Phase 7.5: スタッフエスカレーション通知（2 段階承認）

- [x] `config.py` で HANDOFF_PHRASE を定数化し SYSTEM_PROMPT を再構成
- [x] `notifier.py` で `notify_staff` を実装
- [x] `pending_handoffs` テーブルを作成
- [x] `app.py` で 2 段階承認フローを実装
- [x] `ADMIN_LINE_TARGET_ID` を `.env` に設定 (2026-04-20 取得: <管理者の LINE user_id>)
- [x] エンドツーエンド検証 (4 ケース全成立)
  > 2026-04-20 実施 (ローカル cloudflared 環境):
  > - [x] 1: FAQ にない質問 → `スタッフにお繋ぎしましょうか？` が返る
  > - [x] 2: 「はい」送信 → 管理者 LINE に `🔔 スタッフ対応依頼` 通知が届く
  >
  > 2026-04-21 実施 (本番 Vercel 環境, gemini-2.5-flash-lite):
  > - [x] 4: FAQ ヒット質問「レンタル料金は？」→ HANDOFF_PHRASE なし、FAQ 回答、通知なし、pending_handoffs 行なし
  > - [x] 3: FAQ ミス質問「猫を連れて行ってもいいですか？」→ HANDOFF_PHRASE 含む返信 + `pending_handoffs` 行保存 → 「いいえ」で固定文言「承知しました。ほかにご質問があればどうぞ。」と行削除、「はい」で 🔔 管理者通知と行削除を本番で確認 (Phase 7.6 の小修正後に成立)

## Phase 8: Vercel デプロイ

- [x] `api/index.py` + `vercel.json` を作成 (Flask app を serverless 化)
- [x] Vercel アカウント作成 (dodorian-kg / Pro Trial, 2026-05-04 頃まで)
- [x] GitHub リポジトリ `okasuno-line-bot` を Vercel に import
- [x] 環境変数 6 件を登録 (LINE_CHANNEL_SECRET / LINE_CHANNEL_ACCESS_TOKEN / GEMINI_API_KEY / SUPABASE_URL / SUPABASE_KEY / ADMIN_LINE_TARGET_ID)
- [x] Deploy 成功 (https://okasuno-line-bot.vercel.app/health が 200 OK)
- [x] LINE Webhook URL を `https://okasuno-line-bot.vercel.app/callback` に切替 (検証成功)
- [x] cloudflared プロセスを停止

---

## 本日 (2026-04-20) の出来事メモ

- Phase 7.5 E2E をローカル (cloudflared) で着手したが、Gemini 無料枠 20 RPD を連続でヒット
- モデル切替を 4 パターン試行: `gemini-2.5-flash-lite` → `gemini-2.0-flash` (limit:0) → `gemini-2.5-flash` → `gemini-1.5-flash` (404) → `gemini-2.0-flash-lite` (limit:0)
- 新プロジェクトで Gemini API キーを再発行しても枠がリセットされなかった (Google アカウント横断で制限される模様)
- シナリオ 3/4 は翌日持ち越しとし、Phase 8 (Vercel デプロイ) を先行実施
- Vercel トライアル登録 → GitHub import → 環境変数設定 → デプロイ → LINE Webhook 切替までを完了し、本番稼働開始

## 2026-04-21 の出来事メモ

- Google Cloud の Gemini API に前払いで 2000 円チャージ (従量課金の buffer)
- 当初予定した `gemini-1.5-flash-8b` は 2026 時点で deprecation 済み (ListModels に含まれず 404) のため `gemini-2.5-flash-lite` を採用
  > 安定版 GA は 2026-02-19、$0.10/1M input・$0.40/1M output で 2.5 系最安
- `gemini_client.py` のモデルを `gemini-2.5-flash` → `gemini-2.5-flash-lite` へ変更
- API キーは同一プロジェクトのため `.env` / Vercel 環境変数の変更は不要
- ローカルで `get_gemini_response("営業時間は何時から？")` を実行 → FAQ ベースの正しい応答を確認
- 本番 Vercel で Phase 7.5 E2E 残り 2 ケースを検証
  - シナリオ 4「レンタル料金は？」: 成立 (FAQ 回答、HANDOFF_PHRASE なし、通知なし、pending_handoffs 行なし)
  - シナリオ 3「猫を連れて行ってもいいですか？」: Step 1 の HANDOFF_PHRASE 含む返信は成立。ただし Supabase `pending_handoffs` に行が保存されず Step 2「いいえ」の検証に進めず
    - 併発していた事象: Vercel ログに `POST 500 Exception on /callback` が 10 数件、合間に `POST 200` 数件
    - `pending_handoff set for` / `pending_handoff保存失敗` のログが**一切出ていない**点から、`set_pending_handoff` 呼び出しに到達する前に lambda が終了している疑い
    - 仮説: Gemini の応答遅延 → LINE Webhook 1 秒タイムアウト → 同一イベント再送 → Vercel で複数 lambda 並行 → 先着 lambda が reply 後 `set_pending_handoff` 到達前に request cancellation で kill / 後続 lambda は reply_token 再利用で 500
    - 対応: Phase 7.6 として新設し、まず小修正 (set_pending_handoff を _reply 前へ、pop_pending_handoff を yes/no 合致時のみ) を試行する方針
- Phase 7.6 小修正を実装: supabase_client.py の pop_pending_handoff を peek_pending_handoff + delete_pending_handoff に 2 フェーズ化
  - peek: 読み出しのみ (TTL 切れ行は掃除)
  - delete: app.py で yes/no 合致 & pending 発見時に明示的に呼ぶ
  - app.py の import とハンドラ内呼び出しも差替え (set_pending_handoff は既に _reply 前配置)
- 追加修正: set_pending_handoff の upsert payload に `created_at=now()` を明示追加
  - 背景: `created_at` カラムの `DEFAULT now()` は INSERT 時のみ発火し、UPDATE (upsert の UPDATE パス) では更新されないため、同一 user_id で 2 回目以降の質問でも初回の `created_at` が残り、TTL(10 分) が誤って早期に切れる
  - 症状: 21:37 の「いいえ」送信で peek が `expired` 判定 → 行削除 + None 返却 → Gemini 経路にフォールスルー → 固定文言ではなく Gemini 生成文が返る
  - 修正: `datetime.now(timezone.utc).isoformat()` を upsert に同梱し、質問のたびに TTL をリセット
- Phase 7.5 E2E シナリオ 3 を本番で再検証 → 「いいえ」で固定文言 + 行削除、「はい」で 🔔 通知 + 行削除、ともに成立 → Phase 7.5 / Phase 7.6 をクローズ
