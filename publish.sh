#!/bin/bash
# hn-monitor 自动发布脚本
# 在 main.py 运行后执行，将最新数据推送到 GitHub
set -e

cd "$(dirname "$0")"

# 检查是否有变更
if git diff --quiet && git diff --cached --quiet; then
    echo "No changes to publish."
    exit 0
fi

# 添加所有变更
git add data/*.json index.html

# 提交
DATE=$(date +%Y-%m-%d)
git commit -m "📊 Daily update: $DATE" || echo "Nothing to commit"

# 推送
git push origin main

echo "✅ Published to GitHub: https://github.com/binbinao/hn-monitor"