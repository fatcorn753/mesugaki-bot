"""メスガキ bot — エントリポイント。

有効にしたチャンネルでの発言に、設定した確率でメンション付きの定型文を返す。
bot へのメンションと、bot の発言への返信には必ず返す。
設定は config.json(トークン)と data/settings.json(チャンネルと確率)に保存する。
"""

import json
import logging
import os
import random
import re

import discord
from discord import app_commands
from discord.ext import commands

from core.picker import Picker, classify
from core.settings import SettingsStore

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
SETTINGS_PATH = os.path.join(BASE_DIR, "data", "settings.json")

log = logging.getLogger("mesugaki")


def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        raise SystemExit("config.json が見つかりません。config.example.json をコピーしてトークンを設定してください。")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_token(token: str) -> str:
    token = (token or "").strip()
    if not re.fullmatch(r"[\w-]{20,}\.[\w-]{4,}\.[\w-]{20,}", token):
        raise SystemExit("config.json の token が未設定、または Bot トークンの形式ではありません。")
    return token


def is_to_bot(message: discord.Message, bot_user: discord.ClientUser) -> bool:
    """bot へのメンション、または bot の発言への返信なら True。"""
    if bot_user in message.mentions:
        return True
    ref = message.reference
    resolved = ref.resolved if ref else None
    return isinstance(resolved, discord.Message) and resolved.author.id == bot_user.id


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    config = load_config()
    token = validate_token(config.get("token", ""))
    store = SettingsStore(SETTINGS_PATH, default_rate=float(config.get("default_rate", 0.2)))
    picker = Picker()

    intents = discord.Intents.default()
    intents.message_content = True  # 特権インテント。Developer Portal で ON が必要
    bot = commands.Bot(
        command_prefix=commands.when_mentioned,
        intents=intents,
        # 発言者本人へのメンションだけ通す。@everyone やロールは台詞に入っても鳴らさない
        allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True, replied_user=True),
    )

    @bot.event
    async def on_ready() -> None:
        await bot.tree.sync()
        log.info("ログイン: %s (%s)", bot.user, bot.user.id if bot.user else "?")

    @bot.event
    async def on_message(message: discord.Message) -> None:
        if message.author.bot or message.guild is None or bot.user is None:
            return
        if not store.is_enabled(message.guild.id, message.channel.id):
            return
        to_bot = is_to_bot(message, bot.user)
        if not to_bot and random.random() >= store.get(message.guild.id).rate:
            return
        category = classify(message.content, has_attachment=bool(message.attachments), to_bot=to_bot)
        line = picker.pick(message.channel.id, category, message.author.display_name)
        try:
            await message.reply(f"{message.author.mention} {line}", mention_author=True)
        except discord.HTTPException as e:
            log.warning("送信に失敗: %s", e)

    group = app_commands.Group(
        name="mesugaki",
        description="メスガキ bot の設定",
        guild_only=True,
        default_permissions=discord.Permissions(manage_guild=True),
    )

    @group.command(name="on", description="このチャンネルで反応するようにする")
    async def cmd_on(interaction: discord.Interaction) -> None:
        added = store.add_channel(interaction.guild_id, interaction.channel_id)
        msg = "このチャンネルで反応するようにしたよ♡" if added else "このチャンネルはもう有効だよ♡"
        await interaction.response.send_message(msg, ephemeral=True)

    @group.command(name="off", description="このチャンネルで反応しないようにする")
    async def cmd_off(interaction: discord.Interaction) -> None:
        removed = store.remove_channel(interaction.guild_id, interaction.channel_id)
        msg = "このチャンネルでは黙っててあげる♡" if removed else "このチャンネルはもともと無効だよ♡"
        await interaction.response.send_message(msg, ephemeral=True)

    @group.command(name="rate", description="普通の発言に反応する確率(%)を設定する")
    @app_commands.describe(percent="0〜100。100 で全発言に反応。メンションには常に反応する")
    async def cmd_rate(interaction: discord.Interaction, percent: app_commands.Range[float, 0.0, 100.0]) -> None:
        rate = store.set_rate(interaction.guild_id, percent / 100)
        await interaction.response.send_message(f"反応する確率を {rate * 100:g}% にしたよ♡", ephemeral=True)

    @group.command(name="status", description="有効なチャンネルと確率を見る")
    async def cmd_status(interaction: discord.Interaction) -> None:
        g = store.get(interaction.guild_id)
        chans = " ".join(f"<#{c}>" for c in sorted(g.channels)) or "なし"
        await interaction.response.send_message(
            f"有効なチャンネル: {chans}\n反応する確率: {g.rate * 100:g}%", ephemeral=True
        )

    bot.tree.add_command(group)
    bot.run(token, log_handler=None)


if __name__ == "__main__":
    main()
