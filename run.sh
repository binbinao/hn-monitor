#!/bin/bash
# hn-monitor 一键运行：抓取 → AI评分 → 发布到 GitHub
set -e

cd "$(dirname "$0")"

echo "🚀 HN Monitor — 开始每日运行..."
echo ""

# Step 1: 抓取 + AI 评分
echo "📥 Step 1: 抓取 & AI 评分..."
export GEMINI_API_KEY="${GEMINI_API_KEY:-}"
python3 main.py

echo ""

# Step 2: 发布到 GitHub
echo "📤 Step 2: 发布到 GitHub..."
bash publish.sh

echo ""
echo "✅ 全部完成！"
echo "🌐 在线浏览: https://binbinao.github.io/hn-monitor/"