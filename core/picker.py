"""発言内容からカテゴリを選び、最近使っていない定型文を返す。"""

import random
import re
from collections import deque

from core.lines import GENERAL, KEYWORD_CATEGORIES, LINES, Category

# 同じチャンネルで、直近この件数に使った台詞は避ける
RECENT_SIZE = 40
# 長文とみなす文字数
LONG_LEN = 80
# 短文とみなす文字数
SHORT_LEN = 4

URL_RE = re.compile(r"https?://\S+")
MENTION_RE = re.compile(r"<(?:@[!&]?|#)\d+>|<a?:\w+:\d+>")


def normalize(text: str) -> str:
    """メンション・カスタム絵文字・URL を除き、判定用に小文字へそろえる。"""
    text = MENTION_RE.sub("", text)
    text = URL_RE.sub(" ", text)
    return text.strip().lower()


def classify(text: str, has_attachment: bool = False, to_bot: bool = False) -> str:
    """発言にいちばん合うカテゴリ名を返す。合うものがなければ GENERAL。"""
    body = normalize(text)
    if to_bot:
        return "to_bot"
    if not body and has_attachment:
        return "image"
    for cat in KEYWORD_CATEGORIES:
        if any(k in body for k in cat.keywords):
            return cat.name
    if has_attachment:
        return "image"
    if URL_RE.search(text):
        return "link"
    if len(body) >= LONG_LEN:
        return "long"
    if len(body) <= SHORT_LEN:
        return "short"
    if body.endswith(("?", "？")):
        return "question"
    return GENERAL


class Picker:
    def __init__(self, rng: random.Random | None = None) -> None:
        self.rng = rng or random.Random()
        self._recent: dict[int, deque[str]] = {}

    def pick(self, channel_id: int, category: str, name: str) -> str:
        recent = self._recent.setdefault(channel_id, deque(maxlen=RECENT_SIZE))
        # カテゴリ専用の台詞を主に、ときどき汎用の台詞も混ぜて単調さを減らす
        pool = list(LINES.get(category, LINES[GENERAL]))
        if category != GENERAL and self.rng.random() < 0.25:
            pool = list(LINES[GENERAL])
        fresh = [line for line in pool if line not in recent] or pool
        line = self.rng.choice(fresh)
        recent.append(line)
        return line.replace("{name}", name)


__all__ = ["Category", "Picker", "classify", "normalize"]
