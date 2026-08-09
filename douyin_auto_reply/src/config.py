"""Load and validate config.yaml."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class Rule:
    keywords: list[str]
    replies: list[str]


@dataclass
class AppConfig:
    poll_interval_seconds: int = 60
    action_delay_ms: list[int] = field(default_factory=lambda: [800, 2000])
    headless: bool = False
    enable_comments: bool = True
    enable_messages: bool = True
    skip_own_replies: bool = True
    profile_dir: str = ".playwright/douyin-profile"
    db_path: str = "data/replies.db"
    urls: dict[str, str] = field(default_factory=dict)
    rules: list[Rule] = field(default_factory=list)
    default_replies: list[str] = field(default_factory=list)
    blacklist_keywords: list[str] = field(default_factory=list)
    root: Path = field(default_factory=Path.cwd)

    @property
    def profile_path(self) -> Path:
        path = Path(self.profile_dir)
        if not path.is_absolute():
            path = self.root / path
        return path

    @property
    def database_path(self) -> Path:
        path = Path(self.db_path)
        if not path.is_absolute():
            path = self.root / path
        return path

    def url(self, key: str, default: str = "") -> str:
        return self.urls.get(key, default)


def load_config(path: Path | str | None = None) -> AppConfig:
    root = Path(__file__).resolve().parent.parent
    config_path = Path(path) if path else root / "config.yaml"
    if not config_path.exists():
        example = root / "config.example.yaml"
        raise FileNotFoundError(
            f"缺少配置文件: {config_path}\n"
            f"请先执行: cp {example.name} config.yaml 并按需修改"
        )

    with config_path.open("r", encoding="utf-8") as fh:
        raw: dict[str, Any] = yaml.safe_load(fh) or {}

    rules: list[Rule] = []
    for item in raw.get("rules") or []:
        keywords = [str(k).strip() for k in (item.get("keywords") or []) if str(k).strip()]
        replies = [str(r).strip() for r in (item.get("replies") or []) if str(r).strip()]
        if keywords and replies:
            rules.append(Rule(keywords=keywords, replies=replies))

    default_replies = [
        str(r).strip() for r in (raw.get("default_replies") or []) if str(r).strip()
    ]
    if not default_replies:
        raise ValueError("config.yaml 中 default_replies 不能为空")

    delay = raw.get("action_delay_ms") or [800, 2000]
    if not isinstance(delay, list) or len(delay) < 2:
        delay = [800, 2000]

    urls = raw.get("urls") or {}
    if not isinstance(urls, dict):
        urls = {}

    return AppConfig(
        poll_interval_seconds=int(raw.get("poll_interval_seconds") or 60),
        action_delay_ms=[int(delay[0]), int(delay[1])],
        headless=bool(raw.get("headless", False)),
        enable_comments=bool(raw.get("enable_comments", True)),
        enable_messages=bool(raw.get("enable_messages", True)),
        skip_own_replies=bool(raw.get("skip_own_replies", True)),
        profile_dir=str(raw.get("profile_dir") or ".playwright/douyin-profile"),
        db_path=str(raw.get("db_path") or "data/replies.db"),
        urls={str(k): str(v) for k, v in urls.items()},
        rules=rules,
        default_replies=default_replies,
        blacklist_keywords=[
            str(k).strip()
            for k in (raw.get("blacklist_keywords") or [])
            if str(k).strip()
        ],
        root=root,
    )
