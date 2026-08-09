"""Keyword-based reply matching."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from .config import AppConfig
from .utils import pick_one

logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    reply: str
    matched_keyword: str | None
    skipped: bool = False
    skip_reason: str = ""


class ReplyEngine:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def match(self, text: str) -> MatchResult:
        content = (text or "").strip()
        if not content:
            return MatchResult(
                reply="",
                matched_keyword=None,
                skipped=True,
                skip_reason="empty_content",
            )

        lowered = content.casefold()
        for bad in self.config.blacklist_keywords:
            if bad.casefold() in lowered:
                logger.info("命中黑名单关键词「%s」，跳过: %s", bad, content[:80])
                return MatchResult(
                    reply="",
                    matched_keyword=bad,
                    skipped=True,
                    skip_reason="blacklist",
                )

        for rule in self.config.rules:
            for keyword in rule.keywords:
                if keyword.casefold() in lowered:
                    reply = pick_one(rule.replies)
                    logger.debug("关键词「%s」命中 -> %s", keyword, reply)
                    return MatchResult(reply=reply, matched_keyword=keyword)

        reply = pick_one(self.config.default_replies)
        logger.debug("未命中关键词，使用默认话术: %s", reply)
        return MatchResult(reply=reply, matched_keyword=None)
