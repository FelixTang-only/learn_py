"""Web private-message polling and reply."""

from __future__ import annotations

import hashlib
import logging

from playwright.sync_api import Locator, Page

from .browser import BrowserManager
from .config import AppConfig
from .reply_engine import ReplyEngine
from .store import ReplyStore
from .utils import human_delay

logger = logging.getLogger(__name__)

# Selectors for Douyin web IM — adjust when DOM changes.
SELECTORS = {
    "message_entry": [
        "text=私信",
        "text=消息",
        "[data-e2e='message-icon']",
        "a[href*='message']",
        "[class*='message']",
    ],
    "conversation_items": [
        "[class*='conversation-item']",
        "[class*='ConversationItem']",
        "[class*='session-item']",
        "[class*='chat-item']",
        "div[role='listitem']",
    ],
    "unread_badge": [
        "[class*='badge']",
        "[class*='unread']",
        "[class*='red-dot']",
    ],
    "peer_name": [
        "[class*='name']",
        "[class*='nickname']",
        "[class*='title']",
    ],
    "message_bubbles": [
        "[class*='message-item']",
        "[class*='MessageItem']",
        "[class*='chat-message']",
        "[class*='bubble']",
    ],
    "incoming_hint": [
        "[class*='left']",
        "[class*='other']",
        "[class*='receive']",
        "[class*='peer']",
    ],
    "reply_input": [
        "textarea",
        "div[contenteditable='true']",
        "input[placeholder*='发送']",
        "input[placeholder*='输入']",
    ],
    "send_button": [
        "button:has-text('发送')",
        "text=发送",
    ],
}


class MessageService:
    KIND = "message"

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
        url = self.config.url("messages", "https://www.douyin.com/")
        logger.info("打开私信入口: %s", url)
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60_000)
            page.wait_for_timeout(2000)
        except Exception as exc:
            logger.error("打开私信页失败: %s", exc)
            return 0

        if self.browser.looks_like_login_page(page):
            raise RuntimeError(
                "私信页检测到未登录。请先运行: python main.py login"
            )

        self._open_message_panel(page)
        human_delay(self.config.action_delay_ms)

        conversations = self._list_conversations(page)
        logger.info("本轮可见会话 %d 个", len(conversations))
        replied = 0

        for conv in conversations[:20]:
            try:
                peer = self._peer_name(conv) or "unknown"
                conv.click(timeout=5000)
                page.wait_for_timeout(1200)
                human_delay(self.config.action_delay_ms)

                latest = self._latest_incoming(page)
                if not latest:
                    continue

                item_id = hashlib.sha1(
                    f"{peer}|{latest}".encode("utf-8")
                ).hexdigest()[:24]
                if self.store.has_replied(item_id, self.KIND):
                    continue

                match = self.engine.match(latest)
                if match.skipped:
                    self.store.mark_replied(item_id, self.KIND, latest, "")
                    continue
                if not match.reply:
                    continue

                logger.info(
                    "[私信] %s | %s | 回复: %s%s",
                    peer,
                    latest[:60],
                    match.reply,
                    " (dry-run)" if dry_run else "",
                )

                if dry_run:
                    self.store.mark_replied(
                        item_id, self.KIND, latest, f"[dry-run]{match.reply}"
                    )
                    replied += 1
                    continue

                ok = self._send_reply(page, match.reply)
                if ok:
                    self.store.mark_replied(item_id, self.KIND, latest, match.reply)
                    replied += 1
                    human_delay(self.config.action_delay_ms)
                else:
                    logger.warning("私信发送失败: %s", peer)
            except Exception as exc:
                logger.warning("处理会话失败，跳过: %s", exc)
                continue

        return replied

    def _first_locator(self, root: Page | Locator, selectors: list[str]) -> Locator | None:
        for sel in selectors:
            loc = root.locator(sel)
            try:
                if loc.count() > 0:
                    return loc
            except Exception:
                continue
        return None

    def _open_message_panel(self, page: Page) -> None:
        entry = self._first_locator(page, SELECTORS["message_entry"])
        if entry is None:
            logger.warning(
                "未找到私信/消息入口。可在浏览器中手动打开消息面板，"
                "或更新 messages.py 中 SELECTORS / config urls.messages"
            )
            return
        try:
            entry.first.click(timeout=5000)
            page.wait_for_timeout(2000)
            logger.info("已点击消息入口")
        except Exception as exc:
            logger.debug("点击消息入口失败: %s", exc)

    def _list_conversations(self, page: Page) -> list[Locator]:
        for sel in SELECTORS["conversation_items"]:
            loc = page.locator(sel)
            try:
                n = loc.count()
                if n > 0:
                    return [loc.nth(i) for i in range(min(n, 30))]
            except Exception:
                continue
        logger.warning(
            "未匹配到会话列表。页面可能已改版，请更新 messages.py 中 SELECTORS。"
        )
        return []

    def _peer_name(self, conv: Locator) -> str:
        for sel in SELECTORS["peer_name"]:
            try:
                loc = conv.locator(sel).first
                if loc.count() > 0:
                    return loc.inner_text(timeout=1000).strip()
            except Exception:
                continue
        try:
            return conv.inner_text(timeout=1000).strip().split("\n")[0][:40]
        except Exception:
            return ""

    def _latest_incoming(self, page: Page) -> str:
        bubbles = self._first_locator(page, SELECTORS["message_bubbles"])
        if bubbles is None:
            return ""
        try:
            count = bubbles.count()
            if count == 0:
                return ""
            # Prefer last bubble that looks incoming; fallback to last bubble.
            for i in range(count - 1, max(-1, count - 8), -1):
                bubble = bubbles.nth(i)
                text = bubble.inner_text(timeout=1000).strip()
                if not text:
                    continue
                cls = ""
                try:
                    cls = bubble.get_attribute("class") or ""
                except Exception:
                    pass
                incoming = any(
                    hint.replace("[class*='", "").replace("']", "") in cls
                    for hint in ["left", "other", "receive", "peer"]
                )
                if incoming or i == count - 1:
                    return text.split("\n")[0].strip()
        except Exception as exc:
            logger.debug("读取消息气泡失败: %s", exc)
        return ""

    def _send_reply(self, page: Page, reply: str) -> bool:
        try:
            input_box = self._first_locator(page, SELECTORS["reply_input"])
            if input_box is None:
                logger.error("找不到私信输入框")
                return False
            target = input_box.first
            target.click(timeout=3000)
            tag = target.evaluate("el => el.tagName.toLowerCase()")
            if tag in ("textarea", "input"):
                target.fill(reply)
            else:
                page.keyboard.type(reply, delay=30)

            human_delay(self.config.action_delay_ms)
            send = self._first_locator(page, SELECTORS["send_button"])
            if send is None:
                page.keyboard.press("Enter")
            else:
                send.first.click(timeout=5000)
            page.wait_for_timeout(800)
            return True
        except Exception as exc:
            logger.exception("发送私信异常: %s", exc)
            return False
