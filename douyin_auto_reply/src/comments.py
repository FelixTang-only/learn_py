"""Creator-center comment polling and reply."""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass

from playwright.sync_api import Locator, Page

from .browser import BrowserManager
from .config import AppConfig
from .reply_engine import ReplyEngine
from .store import ReplyStore
from .utils import human_delay

logger = logging.getLogger(__name__)

# Selectors are fragile — Douyin DOM changes often. Adjust here when pages break.
SELECTORS = {
    "unreplied_tab": 'text=未回复',
    "comment_items": [
        "[class*='comment-item']",
        "[class*='CommentItem']",
        "[class*='commentItem']",
        "div[class*='list'] > div[class*='item']",
    ],
    "username": [
        "[class*='user-name']",
        "[class*='nickname']",
        "[class*='NickName']",
        "a[href*='/user/']",
    ],
    "content": [
        "[class*='comment-content']",
        "[class*='content']",
        "[class*='CommentContent']",
    ],
    "reply_button": [
        "text=回复",
        "button:has-text('回复')",
        "[class*='reply']",
    ],
    "reply_input": [
        "textarea",
        "div[contenteditable='true']",
        "input[type='text']",
    ],
    "send_button": [
        "button:has-text('发送')",
        "text=发送",
        "[class*='submit']",
    ],
}


@dataclass
class CommentItem:
    item_id: str
    username: str
    content: str
    locator: Locator


class CommentService:
    KIND = "comment"

    def __init__(
        self,
        config: AppConfig,
        store: ReplyStore,
        engine: ReplyEngine,
        browser: BrowserManager,
    ) -> None:
        self.config = config
        self.store = store
        self.engine = engine
        self.browser = browser

    def process(self, page: Page, *, dry_run: bool = False) -> int:
        url = self.config.url(
            "comments",
            "https://creator.douyin.com/creator-micro/interactive/comment",
        )
        logger.info("打开评论管理: %s", url)
        self.browser.require_logged_in(page, url)
        human_delay(self.config.action_delay_ms)

        self._try_click_unreplied(page)
        human_delay(self.config.action_delay_ms)

        comments = self._collect_comments(page)
        logger.info("本轮可见评论 %d 条", len(comments))
        replied = 0

        for item in comments:
            if self.store.has_replied(item.item_id, self.KIND):
                continue

            match = self.engine.match(item.content)
            if match.skipped:
                self.store.mark_replied(item.item_id, self.KIND, item.content, "")
                continue
            if not match.reply:
                continue

            logger.info(
                "[评论] @%s | %s | 回复: %s%s",
                item.username or "?",
                item.content[:60],
                match.reply,
                " (dry-run)" if dry_run else "",
            )

            if dry_run:
                self.store.mark_replied(
                    item.item_id, self.KIND, item.content, f"[dry-run]{match.reply}"
                )
                replied += 1
                continue

            ok = self._reply_one(page, item, match.reply)
            if ok:
                self.store.mark_replied(
                    item.item_id, self.KIND, item.content, match.reply
                )
                replied += 1
                human_delay(self.config.action_delay_ms)
            else:
                logger.warning("回复失败，稍后重试: %s", item.content[:60])

        return replied

    def _try_click_unreplied(self, page: Page) -> None:
        try:
            tab = page.locator(SELECTORS["unreplied_tab"]).first
            if tab.count() and tab.is_visible():
                tab.click(timeout=5000)
                page.wait_for_timeout(1500)
                logger.info("已切换到「未回复」筛选")
        except Exception as exc:
            logger.debug("未找到「未回复」筛选项: %s", exc)

    def _first_locator(self, root: Page | Locator, selectors: list[str]) -> Locator | None:
        for sel in selectors:
            loc = root.locator(sel)
            try:
                if loc.count() > 0:
                    return loc
            except Exception:
                continue
        return None

    def _collect_comments(self, page: Page) -> list[CommentItem]:
        items_loc = None
        for sel in SELECTORS["comment_items"]:
            loc = page.locator(sel)
            try:
                if loc.count() > 0:
                    items_loc = loc
                    break
            except Exception:
                continue

        if items_loc is None:
            logger.warning(
                "未匹配到评论列表节点。页面可能已改版，请更新 comments.py 中 SELECTORS。"
            )
            return []

        results: list[CommentItem] = []
        count = min(items_loc.count(), 50)
        for i in range(count):
            row = items_loc.nth(i)
            try:
                text = row.inner_text(timeout=3000).strip()
            except Exception:
                continue
            if not text:
                continue

            username = self._extract_field(row, SELECTORS["username"]) or ""
            content = self._extract_field(row, SELECTORS["content"]) or text
            content = self._clean_content(content, username)
            if not content:
                continue

            item_id = hashlib.sha1(
                f"{username}|{content}".encode("utf-8")
            ).hexdigest()[:24]
            results.append(
                CommentItem(
                    item_id=item_id,
                    username=username,
                    content=content,
                    locator=row,
                )
            )
        return results

    def _extract_field(self, row: Locator, selectors: list[str]) -> str:
        for sel in selectors:
            try:
                loc = row.locator(sel).first
                if loc.count() > 0:
                    return loc.inner_text(timeout=1000).strip()
            except Exception:
                continue
        return ""

    def _clean_content(self, content: str, username: str) -> str:
        text = content.strip()
        if username and text.startswith(username):
            text = text[len(username) :].strip()
        text = re.sub(r"\s+", " ", text)
        # Drop trailing action labels often present in scraped blocks
        for noise in ("回复", "展开", "点赞", "举报"):
            if text.endswith(noise):
                text = text[: -len(noise)].strip()
        return text

    def _reply_one(self, page: Page, item: CommentItem, reply: str) -> bool:
        try:
            btn = self._first_locator(item.locator, SELECTORS["reply_button"])
            if btn is None:
                btn = self._first_locator(page, SELECTORS["reply_button"])
            if btn is None:
                logger.error("找不到回复按钮")
                return False
            btn.first.click(timeout=5000)
            human_delay(self.config.action_delay_ms)

            input_box = self._first_locator(page, SELECTORS["reply_input"])
            if input_box is None:
                logger.error("找不到回复输入框")
                return False

            target = input_box.first
            target.click(timeout=3000)
            tag = target.evaluate("el => el.tagName.toLowerCase()")
            if tag in ("textarea", "input"):
                target.fill(reply)
            else:
                target.fill("")
                page.keyboard.type(reply, delay=30)

            human_delay(self.config.action_delay_ms)
            send = self._first_locator(page, SELECTORS["send_button"])
            if send is None:
                page.keyboard.press("Enter")
            else:
                send.first.click(timeout=5000)
            page.wait_for_timeout(1000)
            return True
        except Exception as exc:
            logger.exception("回复评论异常: %s", exc)
            return False
