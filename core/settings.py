"""サーバーごとの設定(使えるチャンネルと反応確率)を JSON に保存する。"""

import json
import os
import tempfile
from dataclasses import dataclass, field


@dataclass
class GuildSettings:
    channels: set[int] = field(default_factory=set)
    rate: float = 0.2  # 0.0〜1.0。普通の発言に反応する確率


class SettingsStore:
    def __init__(self, path: str, default_rate: float = 0.2) -> None:
        self.path = path
        self.default_rate = clamp_rate(default_rate)
        self._guilds: dict[int, GuildSettings] = {}
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.path):
            return
        with open(self.path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        for gid, g in raw.items():
            self._guilds[int(gid)] = GuildSettings(
                channels={int(c) for c in g.get("channels", [])},
                rate=clamp_rate(g.get("rate", self.default_rate)),
            )

    def _save(self) -> None:
        raw = {
            str(gid): {"channels": sorted(g.channels), "rate": g.rate} for gid, g in self._guilds.items()
        }
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        # 書き込み途中で落ちても設定が壊れないよう、一時ファイルに書いてから置き換える
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(self.path) or ".", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(raw, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)

    def get(self, guild_id: int) -> GuildSettings:
        if guild_id not in self._guilds:
            self._guilds[guild_id] = GuildSettings(rate=self.default_rate)
        return self._guilds[guild_id]

    def is_enabled(self, guild_id: int, channel_id: int) -> bool:
        g = self._guilds.get(guild_id)
        return g is not None and channel_id in g.channels

    def add_channel(self, guild_id: int, channel_id: int) -> bool:
        g = self.get(guild_id)
        if channel_id in g.channels:
            return False
        g.channels.add(channel_id)
        self._save()
        return True

    def remove_channel(self, guild_id: int, channel_id: int) -> bool:
        g = self.get(guild_id)
        if channel_id not in g.channels:
            return False
        g.channels.discard(channel_id)
        self._save()
        return True

    def set_rate(self, guild_id: int, rate: float) -> float:
        g = self.get(guild_id)
        g.rate = clamp_rate(rate)
        self._save()
        return g.rate


def clamp_rate(rate: float) -> float:
    return min(1.0, max(0.0, float(rate)))
