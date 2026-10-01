"""Playwright browser helpers with persistent login profile."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from playwright.sync_api import BrowserContext, Page, sync_playwright

from .config import AppConfig

logger = logging.getLogger(__name__)

LOGIN_HINTS = ("登录", "扫码", "手机号登录", "验证码登录")


class BrowserManager:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def ensure_profile_dir(self) -> Path:
        path = self.config.profile_path
        path.mkdir(parents=True, exist_ok=True)
        return path

    @contextmanager
    def launch(self, headless: bool | None = None) -> Generator[BrowserContext, None, None]:
        profile = self.ensure_profile_dir()
        use_headless = self.config.headless if headless is None else headless
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(profile),
                headless=use_headless,
                viewport={"width": 1440, "height": 900},
                locale="zh-CN",
                args=["--disable-blink-features=AutomationControlled"],
            )
            try:
                yield context
            finally:
                context.close()

    def new_page(self, context: BrowserContext) -> Page:
        if context.pages:
            return context.pages[0]
        return context.new_page()

    def looks_like_login_page(self, page: Page) -> bool:
        url = (page.url or "").lower()
        if "login" in url or "passport" in url:
            return True
        try:
            title = page.title()
            body_text = page.locator("body").inner_text(timeout=3000)
        except Exception:
            return False
        blob = f"{title}\n{body_text}"[:2000]
        return any(hint in blob for hint in LOGIN_HINTS) and (
            "创作者中心" not in blob and "作品" not in blob
        )

    def require_logged_in(self, page: Page, target_url: str) -> None:
        page.goto(target_url, wait_until="domcontentloaded", timeout=60_000)
        page.wait_for_timeout(2000)
        if self.looks_like_login_page(page):
            raise RuntimeError(
                "检测到未登录或登录已失效。请先运行: python main.py login"
            )


def wait_for_manual_login(page: Page, timeout_ms: int = 300_000) -> None:
    """Block until user finishes QR login in the opened browser."""
    logger.info("请在打开的浏览器中扫码登录抖音创作者中心…（最多等待 %ss）", timeout_ms // 1000)
    page.goto("https://creator.douyin.com/", wait_until="domcontentloaded")
    deadline = timeout_ms
    elapsed = 0
    step = 3000
    while elapsed < deadline:
        page.wait_for_timeout(step)
        elapsed += step
        url = page.url.lower()
        if "login" not in url and "passport" not in url:
            try:
                text = page.locator("body").inner_text(timeout=2000)
            except Exception:
                text = ""
            if "创作者中心" in text or "作品管理" in text or "数据中心" in text:
                logger.info("登录成功，会话已保存到本地 profile")
                return
            if "creator.douyin.com" in url and "login" not in url:
                logger.info("已进入创作者中心，视为登录成功")
                return
    raise TimeoutError("等待扫码登录超时，请重试 python main.py login")
