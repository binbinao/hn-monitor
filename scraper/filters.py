"""规则预过滤器 — 快速关键词匹配，在 AI 评分前过滤"""
import re
from pathlib import Path
import yaml


def load_config():
    config_path = Path(__file__).parent.parent / "config.yaml"
    return yaml.safe_load(config_path.read_text())


def is_relevant(title: str) -> bool:
    """检查标题是否包含至少一个目标关键词"""
    config = load_config()
    required = config.get("filters", {}).get("required_keywords", [])
    blocked = config.get("filters", {}).get("blocked_keywords", [])

    # 检查屏蔽词
    for kw in blocked:
        if kw.lower() in title.lower():
            return False

    # 检查目标关键词
    for kw in required:
        if kw.lower() in title.lower():
            return True

    return False


def pre_filter(items: list[dict]) -> list[dict]:
    """预过滤：只保留标题包含目标关键词的条目"""
    filtered = []
    for item in items:
        title = item.get("name", "")
        if is_relevant(title):
            filtered.append(item)
    return filtered