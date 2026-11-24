import random

import pytest

from core.lines import GENERAL, KEYWORD_CATEGORIES, LINES
from core.picker import RECENT_SIZE, Picker, classify
from core.settings import SettingsStore

BANNED = ("死ね", "しね", "消えろ", "殺す")


def test_every_category_has_lines():
    names = {c.name for c in KEYWORD_CATEGORIES} | {GENERAL, "to_bot", "short", "long", "question", "image", "link"}
    for n in names:
        assert len(LINES[n]) >= 6, n


def test_no_duplicate_or_banned_lines():
    all_lines = [l for ls in LINES.values() for l in ls]
    assert len(all_lines) == len(set(all_lines))
    assert not [l for l in all_lines if any(b in l for b in BANNED)]


@pytest.mark.parametrize(
    "text,expected",
    [
        ("おはよう〜", "morning"),
        ("そろそろ寝るわ", "night"),
        ("課題が終わらん", "study"),
        ("ガチャ爆死した", "game"),
        ("まじ草", "laugh"),
        ("今日のご飯なにがいいかな", "hungry"),
        ("w", "short"),
        ("これってどういう意味なんですか？", "question"),
        ("https://example.com", "link"),
        ("あ" * 90, "long"),
        ("今日は天気がいいね", GENERAL),
    ],
)
def test_classify(text, expected):
    assert classify(text) == expected


def test_classify_attachment_and_bot():
    assert classify("", has_attachment=True) == "image"
    assert classify("おはよう", to_bot=True) == "to_bot"
    assert classify("<@123> おはよう") == "morning"


def test_picker_avoids_recent_and_fills_name():
    p = Picker(random.Random(0))
    seen = [p.pick(1, GENERAL, "たろう") for _ in range(RECENT_SIZE)]
    assert len(set(seen)) == RECENT_SIZE
    assert all("{name}" not in s for s in seen)


def test_picker_small_pool_does_not_crash():
    p = Picker(random.Random(0))
    for _ in range(50):
        assert p.pick(1, "short", "x")


def test_settings_roundtrip(tmp_path):
    path = tmp_path / "s.json"
    s = SettingsStore(str(path), default_rate=0.3)
    assert not s.is_enabled(1, 10)
    assert s.add_channel(1, 10) and not s.add_channel(1, 10)
    assert s.set_rate(1, 1.5) == 1.0
    s2 = SettingsStore(str(path))
    assert s2.is_enabled(1, 10) and s2.get(1).rate == 1.0
    assert s2.remove_channel(1, 10) and not s2.is_enabled(1, 10)
    assert s2.get(2).rate == 0.2
