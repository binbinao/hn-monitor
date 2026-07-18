# HN Monitor — AI/创业新闻监控

每天抓取 Hacker News 首页 + /newest，用 Gemini 筛选 AI/创业相关内容，评分+摘要，输出到本地 JSON。

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key
export GEMINI_API_KEY="your-key"

# 3. 运行
python main.py
```

## 输出

- `data/YYYY-MM-DD.json` — 当天筛选结果（评分+摘要）
- `data/feed.json` — 全量历史（去重合并）

## 自定义

编辑 `config.yaml` 修改关键词、优先级、评分阈值。