"""本地 JSON 存储层"""
import json
import os
from pathlib import Path
from datetime import datetime, timezone


def get_output_dir() -> Path:
    return Path(__file__).parent.parent / "data"


def save_daily(items: list[dict], date_str: str = None) -> Path:
    """保存当天结果到 data/YYYY-MM-DD.json"""
    if date_str is None:
        date_str = datetime.now(timezone.utc).date().isoformat()

    output_dir = get_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    filepath = output_dir / f"{date_str}.json"
    filepath.write_text(json.dumps(items, ensure_ascii=False, indent=2))
    print(f"  [Storage] Saved {len(items)} items → {filepath}")
    return filepath


def load_existing_urls() -> set[str]:
    """加载历史所有 URL（用于去重）"""
    urls = set()
    output_dir = get_output_dir()
    if not output_dir.exists():
        return urls

    for f in sorted(output_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            for item in data:
                if url := item.get("url"):
                    urls.add(url)
        except (json.JSONDecodeError, OSError):
            continue

    return urls


def append_to_feed(items: list[dict]) -> Path:
    """追加到 data/feed.json（全量历史，去重合并）"""
    output_dir = get_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    feed_path = output_dir / "feed.json"
    existing = []
    existing_urls = set()

    if feed_path.exists():
        try:
            existing = json.loads(feed_path.read_text())
            existing_urls = {item.get("url", "") for item in existing}
        except (json.JSONDecodeError, OSError):
            pass

    new_items = [item for item in items if item.get("url") not in existing_urls]
    existing.extend(new_items)

    # 按时间戳倒序排列
    existing.sort(key=lambda x: x.get("timestamp", 0), reverse=True)

    feed_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2))
    print(f"  [Storage] Feed: {len(new_items)} new, {len(existing)} total → {feed_path}")
    return feed_path