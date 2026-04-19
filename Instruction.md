# おかスノ LINE Bot 開発ガイド

---

## Phase 1: 環境構築と設定ファイルの準備

「アプリを動かすための土台」を作るフェーズです。

### Python仮想環境の作成
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
```
仮想環境とは「このプロジェクト専用のPython環境」です。他のプロジェクトのライブラリと混ざらないように隔離します。

### ライブラリのインストール
```bash
pip install -r requirements.txt
```
`requirements.txt` には4つのライブラリが書いてあります：
- **flask** — Webサーバーを作るフレームワーク
- **line-bot-sdk** — LINE公式のPythonライブラリ
- **google-genai** — Gemini AIのPythonライブラリ
- **python-dotenv** — `.env`ファイルを読み込む

### `.env`ファイルの作成
```
LINE_CHANNEL_SECRET=xxxx
LINE_CHANNEL_ACCESS_TOKEN=xxxx
GEMINI_API_KEY=xxxx
```
APIキーをコードに直書きせず、このファイルに分離します。Gitに上げると漏洩するので厳禁。

### `config.py`の役割（既に完成）
`config.py` が`.env`を読み込み、どこからでも`from config import LINE_CHANNEL_SECRET`と書けるようにしています。キーが未設定なら即エラーを出す安全機構付き。

### `.gitignore`の作成
```
.env
__pycache__/
```
Gitが`.env`を「追跡しないファイル」として無視するように設定します。

---

## Phase 2: サーバー基盤の作成

「LINEからのメッセージを受け取る窓口」を作るフェーズです。

### `app.py`の作成 — Flaskサーバー
```
[LINE公式サーバー] → POST /callback → [あなたのFlaskサーバー]
```
LINEはメッセージが来るたびに、設定したURLに自動でHTTPリクエストを送ってきます（Webhook）。このリクエストを受け取る`/callback`エンドポイントを作ります。

### `/health`エンドポイント
```
ブラウザ → http://localhost:5000/health → {"status": "ok"}
```
「サーバーが生きているか」を確認するだけの簡単なページ。デバッグに便利。

### ngrokの設定
```
[LINE公式サーバー] → https://xxxx.ngrok-free.app → [あなたのPC]
```
LINEのWebhookはHTTPS（インターネット上のURL）が必要です。しかしあなたのPCはインターネットから直接アクセスできません。ngrokは「トンネル」を掘って、外部URLをあなたのPC（localhost:5000）に転送してくれるツールです。

### LINE DevelopersでWebhook URLを設定
LINE Developers Consoleで「Webhook URL」に`https://xxxx.ngrok-free.app/callback`を登録します。これでLINEがあなたのサーバーにメッセージを送れるようになります。

### 署名検証の確認
LINEは送るリクエストに「署名（ハッシュ）」を付けます。line-bot-sdkが自動で検証し、偽物のリクエストは400エラーで拒否します。

---

## Phase 3: オウム返しBotの実装

「通信経路が正しく動くか」を確認するフェーズです。

### なぜGeminiを一時的に外すのか
Gemini連携を入れた状態でテストすると、問題が起きたとき「LINEとの通信の問題か、Gemini APIの問題か」が分かりません。まずシンプルなオウム返しで通信経路だけを確認します。

### 通信の流れ
```
あなた（LINE）
  ↓ 「こんにちは」を送信
LINE公式サーバー
  ↓ Webhookでapp.pyに転送
handle_message関数
  ↓ 受け取ったテキストをそのまま返す
LINE公式サーバー
  ↓
あなた（LINE）に「こんにちは」が届く
```
この全経路がエラーなく動けばPhase 3完了です。

---

## Phase 4: Gemini API連携

「オウム返し → AI返答」に切り替えるフェーズです。

### `gemini_client.py`の作成
```python
def get_gemini_response(user_message):
    # Gemini APIにメッセージを送って返答を受け取る
    ...
```
Gemini APIとのやり取りを**専用ファイルに分離**します。`app.py`に全部書かないことで、コードが読みやすくなります。

### `config.py`にシステムプロンプトを追加
```python
SYSTEM_PROMPT = "あなたはおかスノのサポートBotです。..."
```
「このBotはどんな役割か」をGeminiに事前に伝える指示文です。「レンタル料金を答える」「予約の案内をする」など、おかスノ専用の応答をさせます。

### `handle_message`の切り替え
```
オウム返し: return user_message
     ↓ 変更
Gemini連携: return get_gemini_response(user_message)
```
Phase 3で動作確認したオウム返しをGemini呼び出しに差し替えます。

### 動作確認
「レンタル料金は？」「予約したい」「営業時間は？」などを実際に送って、適切な返答が来るか確認します。

---

## Phase 5: Git / GitHub 導入

「コードをバージョン管理下に置く」フェーズです。Phase 4 までの成果物が動いているうちに、早めにバージョン管理を始めます。

### なぜここでGit/GitHubを入れるのか
- **コード消失リスク潰し**: PC故障・誤削除の保険。OneDrive 上にあっても、履歴までは残らない
- **就活時のアピール材料**: 後からコミット履歴を遡って「何を考えて作ったか」を語れる
- **次のPhase以降の土台**: Vercel は GitHub と連携してデプロイするので、先に GitHub リポを用意しておく必要がある

### `git init` → 初回コミットの流れ
```bash
cd /path/to/line-bot
git init                  # ローカルに .git ディレクトリを作成
git status                # 追跡対象ファイルを確認
git add .                 # 全ファイルをステージ（.gitignore 除外分は入らない）
git commit -m "Initial commit: Phase 1-4 implementation"
```
**重要**: `.gitignore` に `.env` と `venv/` と `__pycache__/` が入っているか必ず確認してから `git add .` する。APIキー（`.env` の中身）を誤ってコミットすると、後から削除しても履歴には残り、漏洩扱いになる。

### GitHub で Private リポジトリを作る
GitHub Web で「New repository」→ 名前を `okasuno-line-bot` 等にして **Private** を選ぶ。お店の業務データ・FAQ・予約ロジックが含まれるので、就活ポートフォリオとして見せたい場合は別途整理したPublic版を後から作る方が安全。

### リモート登録と初回 push
```bash
git remote add origin https://github.com/<your-name>/okasuno-line-bot.git
git branch -M main
git push -u origin main
```
これで GitHub にファイルが上がります。以降は「変更 → `git add` → `git commit` → `git push`」のサイクルを回す。

### README.md の作成
リポジトリトップに以下を書いた `README.md` を置きます：
- Bot の概要（何をするBotか）
- セットアップ手順（仮想環境・依存インストール・`.env` 設定）
- 必要な環境変数の一覧

---

## Phase 6: エラーハンドリングとコードの整理

「本番運用に耐えられるコード」にするフェーズです。

### エラーハンドリング
Gemini APIは以下のエラーを起こすことがあります：
- **接続エラー** — ネットワーク障害
- **レート制限** — API呼び出しが多すぎる
- **その他の例外** — 予期せぬバグ

エラーが起きてもサーバーがクラッシュしないよう、`try/except`でエラーを捕まえ「しばらくお待ちください」などのメッセージを返します。

### ロギングの導入
```
2026-04-18 12:00:01 INFO  メッセージ受信: 「レンタル料金は？」
2026-04-18 12:00:02 INFO  返信送信完了
2026-04-18 12:00:05 ERROR Gemini API接続エラー
```
`logging`モジュールでタイムスタンプ付きログを出力します。問題が起きたときに「いつ・何が起きたか」を追跡できます。

### コードの最終整理
不要なコメントや使っていない`import`を削除し、警告なく起動できる状態にします。

---

## Phase 7: Supabase 連携（FAQ・商品マスタ＋予約データ）

「Bot に永続的な知識と記憶を持たせる」フェーズです。

### Supabase とは
**マネージド PostgreSQL + 管理画面 + REST API** がまとまったサービス。自前でDBサーバーを立てなくても、Web画面からテーブルを作り、Python クライアントから読み書きできる。無料枠が広いので個人開発に向く。

### なぜ FAQ を DB に入れるのか
現在はシステムプロンプト（`config.py` 内の文字列）にお店の情報を埋め込んでいるが、料金変更や新プラン追加のたびに**コードを書き換えて再デプロイ**する必要がある。FAQ を Supabase に移せば、管理画面から行を追加・編集するだけで Bot の回答が更新される。

### テーブル設計（最小構成）
```
faqs
  id (uuid, PK)
  question    (text)  -- 「レンタル料金は？」
  answer      (text)  -- 「半日3,000円、1日5,000円です」
  category    (text)  -- 「料金」「営業時間」など
  updated_at  (timestamptz)

reservations
  id           (uuid, PK)
  line_user_id (text)    -- LINE の userId
  plan         (text)    -- 「半日」「1日」など
  reserved_at  (timestamptz)
  party_size   (int)
  status       (text)    -- 「pending」「confirmed」「cancelled」
  created_at   (timestamptz)
```

### FAQ を Gemini に渡す簡易 RAG
```
ユーザーメッセージ
    ↓
Supabase から faqs 全件取得（件数少なければ全件でOK）
    ↓
Gemini への system prompt に「以下の FAQ を参考に回答してください」と FAQ を添えて送信
    ↓
Gemini が FAQ に基づいた回答を返す
```
件数が増えてきたら pgvector で類似検索に切り替える、という段階的アプローチで良い。最初は全件渡しで十分。

### 予約フローの簡易設計
複雑な状態管理は避け、まずは**1メッセージで完結する形式**から始めるのがおすすめ：
```
ユーザー: 「予約したい 2026-05-10 半日 2人」
    ↓
Bot: パース → reservations に INSERT → 「予約を承りました」
```
段階的に「対話で1問ずつ聞く」方式へ発展させる。最初から凝ると挫折しやすい。

---

## Phase 8: Vercel デプロイ

「cloudflared を卒業して本番環境に乗せる」フェーズです。

### Vercel とは
**GitHub にpushするだけでアプリが公開される** サービス。Next.js で有名だが、Python Flask も serverless function として動かせる。無料枠で個人プロジェクトには十分。

### なぜ cloudflared から乗り換えるか
- **PC 起動依存**: cloudflared は自分のPCで動かすので、PC を落とすと Bot が死ぬ
- **URL 不安定**: `cloudflared tunnel --url ...` の一時URLは再起動で変わる。LINE Developers の Webhook URL を毎回貼り替えるのは現実的でない
- **24/7 稼働**: Vercel 側でサーバーレスなので、常時立ち上がっている

### ディレクトリ構成
Vercel の Python serverless は `api/` 配下の Python ファイルをエンドポイントとして認識する。Flask アプリを少し書き換える：
```
line-bot/
├── api/
│   └── index.py      ← ここに Flask アプリ本体
├── vercel.json       ← ルーティング設定
├── requirements.txt
├── config.py
└── ...
```
`vercel.json` でルーティングを一括で `api/index.py` に流す設定を書く。

### デプロイの流れ
1. Vercel アカウント作成・GitHub 連携（Phase 5 の Private リポを import）
2. Project Settings → Environment Variables に `.env` の中身を全部登録（`LINE_CHANNEL_SECRET` / `LINE_CHANNEL_ACCESS_TOKEN` / `GEMINI_API_KEY` / `SUPABASE_URL` / `SUPABASE_KEY`）
3. `git push` → Vercel が自動でビルド・デプロイ
4. 発行された `https://xxx.vercel.app` を LINE Developers の Webhook URL に設定

以降は **`git push` するだけで本番環境が更新される**。

### Vercel Python の制約
- **10秒タイムアウト**（Hobby プラン）: Gemini の応答が遅いと切れる可能性がある。基本は問題ないが、長文プロンプトには注意
- **リクエスト単位の実行**: サーバーが常駐しているわけではないので、インメモリの状態管理（グローバル変数で予約の途中状態を持つ、等）は使えない。状態は Supabase に保存する
- **コールドスタート**: しばらくアクセスがないと初回応答が数秒遅れる。LINE Bot なら許容範囲

---

## 全体の流れまとめ

```
Phase 1: ライブラリ・APIキーの準備（土台）
    ↓
Phase 2: Flaskサーバー + cloudflared で外部公開（窓口）
    ↓
Phase 3: オウム返しで通信経路を確認（疎通テスト）
    ↓
Phase 4: Geminiに接続してAI返答（本機能）
    ↓
Phase 5: Git/GitHub でバージョン管理（保険）
    ↓
Phase 6: エラー対策・ログ整備（仕上げ）
    ↓
Phase 7: Supabase で FAQ・予約を永続化（DB）
    ↓
Phase 8: Vercel にデプロイし 24/7 稼働（本番）
```
