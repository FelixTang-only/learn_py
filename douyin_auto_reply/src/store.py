"""SQLite store for already-replied comments and messages."""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path


class ReplyStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS replied (
                id TEXT NOT NULL,
                kind TEXT NOT NULL,
                content TEXT,
                reply TEXT,
                ts REAL NOT NULL,
                PRIMARY KEY (id, kind)
            )
            """
        )
        self._conn.commit()

    def has_replied(self, item_id: str, kind: str) -> bool:
        cur = self._conn.execute(
            "SELECT 1 FROM replied WHERE id = ? AND kind = ? LIMIT 1",
            (item_id, kind),
        )
        return cur.fetchone() is not None

    def mark_replied(
        self,
        item_id: str,
        kind: str,
        content: str = "",
        reply: str = "",
    ) -> None:
        self._conn.execute(
            """
            INSERT OR REPLACE INTO replied (id, kind, content, reply, ts)
            VALUES (?, ?, ?, ?, ?)
            """,
            (item_id, kind, content, reply, time.time()),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "ReplyStore":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
