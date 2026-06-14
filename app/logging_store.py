"""Append every request to a jsonl log — the basis for future quality analysis
and for harvesting corrected question->SQL pairs."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from app.config import settings


def log_request(record: dict) -> None:
    record = {"ts": datetime.now(timezone.utc).isoformat(), **record}
    settings.log_path.parent.mkdir(parents=True, exist_ok=True)
    with settings.log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
