<p align="center">
  <img src="assets/icon.png" width="160" alt="メスガキ bot のアイコン">
</p>

<h1 align="center">メスガキ bot</h1>

<p align="center">指定したチャンネルでの発言に、ときどきメンションしてからかってくる Discord bot</p>

---

```
あなた    : 課題やっと終わった〜
メスガキbot: @あなた ふ〜ん、できたんだ♡ たまたまだよね？♡

あなた    : ガチャ爆死した
メスガキbot: @あなた ガチャ爆死してそ〜♡

あなた    : @メスガキbot おはよ
メスガキbot: @あなた 呼んだ？ ざこが私に何の用？♡
```

## 特徴

- **定型文が約 350 本**。発言内容を 21 種類(あいさつ・疲れた・眠い・ご飯・ゲーム・課題・質問・長文・画像・リンクなど)に分けて、合う台詞を選ぶ
- **反応するチャンネルを指定できる**。指定していないチャンネルでは一切喋らない
- **反応する確率を 0〜100% で設定できる**。100% にすると全発言に返す
- bot へのメンションと、bot の発言への返信には**必ず返す**
- 同じチャンネルで直近 40 回に使った台詞は使わないので、同じ台詞が続きにくい
- LLM や外部 API を使わない。動かすのに必要なのは Bot トークンだけ

台詞は生意気なからかいだけにしています。性的な台詞、容姿や属性への中傷、本気の暴言は入れていません。

## 必要なもの

- Python 3.11 以上
- Discord の Bot アプリケーション

## セットアップ

### 1. Bot を作る

1. [Discord Developer Portal](https://discord.com/developers/applications) でアプリケーションを作る
2. **Bot** ページで次を設定する
   - **Message Content Intent** を ON(発言の内容を読むのに必要)
   - 「トークンをリセット」でトークンを発行し、控えておく
3. **インストール** ページで次を設定する
   - インストールのコンテキスト: **ギルドのインストール**
   - スコープ: `bot`、`applications.commands`
   - 権限: **チャンネルを表示**、**メッセージを送る**、**メッセージ履歴を読む**
4. 表示されたインストールリンクから、bot をサーバーに招待する

### 2. 動かす

```bash
git clone https://github.com/fatcorn753/mesugaki-bot.git
cd mesugaki-bot
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp config.example.json config.json   # token にトークンを書く
.venv/bin/python main.py
```

ログに `ログイン: <bot の名前>` と出れば起動しています。

### 3. チャンネルで有効にする

反応させたいチャンネルで次を実行します。

```
/mesugaki on
/mesugaki rate 30
```

スラッシュコマンドは、初回の起動から表示されるまで数分かかることがあります。

## コマンド

サーバーの管理権限(サーバー管理)を持つ人だけが使えます。返事は実行した本人にだけ見えます。

| コマンド | 内容 |
|---|---|
| `/mesugaki on` | 今いるチャンネルで反応するようにする |
| `/mesugaki off` | 今いるチャンネルで反応しないようにする |
| `/mesugaki rate <0〜100>` | 普通の発言に反応する確率(%)。100 で全発言 |
| `/mesugaki status` | 有効なチャンネルと確率を見る |

## 設定ファイル

`config.json`

| キー | 内容 |
|---|---|
| `token` | Bot トークン |
| `default_rate` | 確率の初期値(0〜1)。`/mesugaki rate` を使う前のサーバーに使う |

チャンネルと確率は `data/settings.json` に保存されます。`config.json` と `data/` は `.gitignore` 済みです。

## 常駐させる(Linux + systemd)

`deploy/mesugaki-bot.service` が unit ファイルの例です。ユーザー名とパスを自分の環境に合わせてから登録します。

```bash
sudo cp deploy/mesugaki-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now mesugaki-bot
journalctl -u mesugaki-bot -f   # ログを見る
```

## 台詞を足す・変える

台詞は [`core/lines.py`](core/lines.py) にあります。

- `LINES` の各カテゴリに文字列を足すだけで使われます
- `{name}` は発言者の表示名に置き換わります
- カテゴリを増やすときは、`KEYWORD_CATEGORIES` に判定用のキーワードも足します。上から順に判定し、先に当たったものを使います

## 構成

```
main.py            bot 本体とスラッシュコマンド
core/lines.py      定型文とカテゴリのキーワード
core/picker.py     発言の分類と台詞の選択
core/settings.py   チャンネルと確率の保存
assets/            アイコン画像と、それを描くスクリプト
deploy/            systemd の unit ファイルの例
tests/             テスト
```

## テスト

```bash
.venv/bin/pip install pytest
.venv/bin/python -m pytest -q
```

## ライセンス

[MIT](LICENSE)
