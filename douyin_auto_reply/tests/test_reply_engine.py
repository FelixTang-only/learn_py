"""Unit tests for reply engine, store, and TOML config."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import AppConfig, Rule, load_config
from src.reply_engine import ReplyEngine
from src.store import ReplyStore


def _config(**kwargs) -> AppConfig:
    base = AppConfig(
        rules=[
            Rule(keywords=["价格", "多少钱"], replies=["看置顶"]),
            Rule(keywords=["谢谢"], replies=["不客气"]),
        ],
        default_replies=["默认回复"],
        blacklist_keywords=["加微信"],
    )
    for k, v in kwargs.items():
        setattr(base, k, v)
    return base


class ReplyEngineTests(unittest.TestCase):
    def test_keyword_match(self) -> None:
        engine = ReplyEngine(_config())
        result = engine.match("这个多少钱啊")
        self.assertFalse(result.skipped)
        self.assertEqual(result.matched_keyword, "多少钱")
        self.assertEqual(result.reply, "看置顶")

    def test_default_reply(self) -> None:
        engine = ReplyEngine(_config())
        result = engine.match("今天天气不错")
        self.assertFalse(result.skipped)
        self.assertIsNone(result.matched_keyword)
        self.assertEqual(result.reply, "默认回复")

    def test_blacklist(self) -> None:
        engine = ReplyEngine(_config())
        result = engine.match("加微信详聊")
        self.assertTrue(result.skipped)
        self.assertEqual(result.skip_reason, "blacklist")

    def test_empty(self) -> None:
        engine = ReplyEngine(_config())
        result = engine.match("   ")
        self.assertTrue(result.skipped)
        self.assertEqual(result.skip_reason, "empty_content")

    def test_first_rule_wins(self) -> None:
        engine = ReplyEngine(_config())
        result = engine.match("谢谢，多少钱")
        self.assertEqual(result.matched_keyword, "多少钱")


class ReplyStoreTests(unittest.TestCase):
    def test_mark_and_has(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = ReplyStore(Path(tmp) / "t.db")
            self.assertFalse(store.has_replied("a1", "comment"))
            store.mark_replied("a1", "comment", "hi", "yo")
            self.assertTrue(store.has_replied("a1", "comment"))
            self.assertFalse(store.has_replied("a1", "message"))
            store.close()


class ConfigLoadTests(unittest.TestCase):
    def test_load_example_toml(self) -> None:
        cfg = load_config(ROOT / "config.example.toml")
        self.assertGreaterEqual(len(cfg.rules), 1)
        self.assertTrue(cfg.default_replies)
        self.assertIn("comments", cfg.urls)


if __name__ == "__main__":
    unittest.main()
