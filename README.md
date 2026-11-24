# メスガキ bot

有効にしたチャンネルでの発言に、設定した確率でメンション付きのメスガキ口調の定型文を返す Discord bot。

- 定型文は約 350 本(`core/lines.py`)。発言内容(あいさつ・疲れた・ゲーム・質問・長文など 21 種)から合うものを選ぶ
- 同じチャンネルで直近 40 回に使った台詞は避ける
- bot へのメンションと、bot の発言への返信には確率に関係なく必ず返す
- クールダウンはなし
- 台詞は生意気なからかいだけにしている。性的な台詞や本気の暴言は入れない

## セットアップ

1. Developer Portal で bot を作り、**Message Content Intent を ON** にする
2. 招待時の権限: メッセージの送信・メッセージ履歴を読む。スコープは `bot` と `applications.commands`
3. 起動

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp config.example.json config.json   # token を書く
.venv/bin/python main.py
```

## コマンド(サーバー管理権限のある人だけ)

| コマンド | 内容 |
|---|---|
| `/mesugaki on` | 今いるチャンネルで反応するようにする |
| `/mesugaki off` | 今いるチャンネルで反応しないようにする |
| `/mesugaki rate <0〜100>` | 普通の発言に反応する確率(%)。100 で全発言 |
| `/mesugaki status` | 有効なチャンネルと確率を見る |

設定は `data/settings.json` に保存する。確率の初期値は `config.json` の `default_rate`(0〜1)。

## 定型文を足す

`core/lines.py` の `LINES` に追記する。`{name}` は発言者の表示名に置き換わる。
カテゴリを増やすときは `KEYWORD_CATEGORIES` にキーワードも足す(上から順に判定)。

## テスト

```bash
.venv/bin/pip install pytest
.venv/bin/python -m pytest -q
```
