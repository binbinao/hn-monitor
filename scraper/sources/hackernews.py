"""
Hacker News 数据源 — 抓取首页 + /newest 页面
使用官方 Firebase API（免费、无限制、结构化 JSON）
"""
import requests
from datetime import datetime, timezone

HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
HN_WEB_BASE = "https://news.ycombinator.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; hn-monitor/1.0)",
}


def fetch_top_stories(limit: int = 100) -> list[dict]:
    """抓取 HN 首页热门故事"""
    return _fetch_stories("topstories", limit)


def fetch_new_stories(limit: int = 100) -> list[dict]:
    """抓取 HN /newest 最新故事"""
    return _fetch_stories("newstories", limit)


def _fetch_stories(endpoint: str, limit: int) -> list[dict]:
    """通用抓取逻辑"""
    try:
        # 获取 ID 列表
        ids_resp = requests.get(f"{HN_API_BASE}/{endpoint}.json", headers=HEADERS, timeout=15)
        ids_resp.raise_for_status()
        ids = ids_resp.json()[:limit]

        # 批量获取详情
        items = []
        for item_id in ids:
            try:
                item_resp = requests.get(
                    f"{HN_API_BASE}/item/{item_id}.json", headers=HEADERS, timeout=10
                )
                item_resp.raise_for_status()
                item = item_resp.json()
                if item and item.get("type") == "story":
                    items.append(_normalise(item, endpoint))
            except Exception:
                continue

        return items
    except Exception as e:
        print(f"[HN] Failed to fetch {endpoint}: {e}")
        return []


def _normalise(raw: dict, source: str) -> dict:
    """标准化为统一 schema"""
    source_name = "HN Top" if "top" in source else "HN New"
    return {
        "name": raw.get("title", ""),
        "url": raw.get("url", f"{HN_WEB_BASE}/item?id={raw.get('id')}"),
        "hn_url": f"{HN_WEB_BASE}/item?id={raw.get('id')}",
        "source": source_name,
        "score": raw.get("score", 0),
        "comments": raw.get("descendants", 0),
        "author": raw.get("by", ""),
        "date_found": datetime.now(timezone.utc).date().isoformat(),
        "timestamp": raw.get("time", 0),
    }