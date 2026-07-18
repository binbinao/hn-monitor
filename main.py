#!/usr/bin/env python3
"""HN Monitor — 每天抓取 Hacker News，Gemini 评分筛选 AI/创业新闻"""
import os
import sys
from pathlib import Path

# 确保项目根目录在 sys.path
sys.path.insert(0, str(Path(__file__).parent))

from scraper.sources.hackernews import fetch_top_stories, fetch_new_stories
from scraper.filters import pre_filter
from storage.json_sync import save_daily, append_to_feed, load_existing_urls


def ai_enabled() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY"))


def main():
    print("=" * 60)
    print("HN Monitor — AI/创业新闻监控")
    print("=" * 60)

    # Step 1: 抓取
    print("\n[1/4] Fetching HN stories...")
    top = fetch_top_stories(limit=100)
    new = fetch_new_stories(limit=100)
    print(f"  Top: {len(top)}, New: {len(new)}")

    # 合并去重
    seen_ids = set()
    all_items = []
    for item in top + new:
        if item["url"] not in seen_ids:
            seen_ids.add(item["url"])
            all_items.append(item)
    print(f"  Unique: {len(all_items)}")

    # Step 2: 关键词预过滤
    print("\n[2/4] Pre-filtering by keywords...")
    filtered = pre_filter(all_items)
    print(f"  {len(all_items)} → {len(filtered)} after keyword filter")

    if not filtered:
        print("  No matching stories found today.")
        return

    # Step 3: AI 评分+摘要
    print("\n[3/4] AI scoring & summarisation...")
    if ai_enabled():
        from ai.pipeline import analyse_batch

        context_path = Path(__file__).parent / "profile" / "context.md"
        context = context_path.read_text() if context_path.exists() else ""
        enriched = analyse_batch(filtered, context=context)
    else:
        print("  [AI] Skipped — GEMINI_API_KEY not set")
        enriched = filtered

    # 按 AI 评分排序
    enriched.sort(key=lambda x: x.get("ai_score", 0), reverse=True)

    # Step 4: 存储
    print("\n[4/4] Saving results...")
    save_daily(enriched)
    append_to_feed(enriched)

    # 打印摘要
    print("\n" + "=" * 60)
    print(f"Done! {len(enriched)} stories saved.")
    print("=" * 60)

    # 打印 Top 10
    print("\n📊 Top Stories:\n")
    for i, item in enumerate(enriched[:10]):
        score = item.get("ai_score", "?")
        cat = item.get("ai_category", "?")
        summary = item.get("ai_summary", "")
        print(f"  {i+1}. [{score}] [{cat}] {item['name'][:80]}")
        if summary:
            print(f"     {summary[:120]}")
        print(f"     {item.get('hn_url', item.get('url', ''))}")
        print()


if __name__ == "__main__":
    main()