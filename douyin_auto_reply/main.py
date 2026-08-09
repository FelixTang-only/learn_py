#!/usr/bin/env python3
"""Douyin comment & DM auto-reply CLI."""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

# Allow `python main.py` from project root
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.browser import BrowserManager, wait_for_manual_login
from src.comments import CommentService
from src.config import AppConfig, load_config
from src.messages import MessageService
from src.reply_engine import ReplyEngine
from src.store import ReplyStore
from src.utils import setup_logging

logger = logging.getLogger("main")


def cmd_login(config: AppConfig) -> int:
    browser = BrowserManager(config)
    logger.info("启动浏览器（有界面），请扫码登录…")
    with browser.launch(headless=False) as context:
        page = browser.new_page(context)
        wait_for_manual_login(page)
        # Keep browser open briefly so cookies flush to disk
        page.wait_for_timeout(2000)
    logger.info("登录态已写入: %s", config.profile_path)
    return 0


def cmd_run(
    config: AppConfig,
    *,
    dry_run: bool = False,
    comments_only: bool = False,
    messages_only: bool = False,
    once: bool = False,
) -> int:
    do_comments = config.enable_comments and not messages_only
    do_messages = config.enable_messages and not comments_only
    if comments_only:
        do_messages = False
    if messages_only:
        do_comments = False

    if not do_comments and not do_messages:
        logger.error("评论与私信均已禁用，请检查 config.yaml 或命令行参数")
        return 2

    browser = BrowserManager(config)
    engine = ReplyEngine(config)

    with ReplyStore(config.database_path) as store:
        comments = CommentService(config, store, engine, browser)
        messages = MessageService(config, store, engine, browser)

        with browser.launch() as context:
            page = browser.new_page(context)
            round_no = 0
            while True:
                round_no += 1
                logger.info("======== 第 %d 轮 ========", round_no)
                try:
                    if do_comments:
                        n = comments.process(page, dry_run=dry_run)
                        logger.info("本轮评论回复 %d 条", n)
                    if do_messages:
                        n = messages.process(page, dry_run=dry_run)
                        logger.info("本轮私信回复 %d 条", n)
                except RuntimeError as exc:
                    logger.error("%s", exc)
                    return 1
                except Exception:
                    logger.exception("本轮处理异常，将在下一轮重试")

                if once:
                    break
                logger.info(
                    "休眠 %s 秒后继续… (Ctrl+C 退出)",
                    config.poll_interval_seconds,
                )
                try:
                    time.sleep(config.poll_interval_seconds)
                except KeyboardInterrupt:
                    logger.info("已停止")
                    break
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="抖音作品评论 / 新私信自动回复（Playwright + 关键词模板）"
    )
    parser.add_argument(
        "-c",
        "--config",
        default=None,
        help="配置文件路径（默认: ./config.yaml）",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="调试日志")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("login", help="扫码登录并保存会话")

    run = sub.add_parser("run", help="轮询并自动回复")
    run.add_argument(
        "--dry-run",
        action="store_true",
        help="只匹配并打印拟回复内容，不实际发送",
    )
    run.add_argument("--comments-only", action="store_true", help="只处理评论")
    run.add_argument("--messages-only", action="store_true", help="只处理私信")
    run.add_argument("--once", action="store_true", help="只跑一轮后退出")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    setup_logging(verbose=args.verbose)

    try:
        config = load_config(args.config)
    except (FileNotFoundError, ValueError) as exc:
        logger.error("%s", exc)
        return 2

    if args.command == "login":
        return cmd_login(config)
    if args.command == "run":
        return cmd_run(
            config,
            dry_run=args.dry_run,
            comments_only=args.comments_only,
            messages_only=args.messages_only,
            once=args.once,
        )
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
