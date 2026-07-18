"""AI Pipeline — 批量调用 Gemini 评分+摘要"""
import json
import yaml
from pathlib import Path
from ai.client import generate


def analyse_batch(items: list[dict], context: str = "", preference_prompt: str = "") -> list[dict]:
    """批量分析条目，返回带 AI 评分和摘要的结果"""
    config_path = Path(__file__).parent.parent / "config.yaml"
    config = yaml.safe_load(config_path.read_text())

    model = config.get("ai", {}).get("model", "gemini-2.5-flash")
    rate_limit = config.get("ai", {}).get("rate_limit_seconds", 2.0)
    min_score = config.get("ai", {}).get("min_score", 50)
    batch_size = config.get("ai", {}).get("batch_size", 5)

    batches = [items[i : i + batch_size] for i in range(0, len(items), batch_size)]
    print(f"  [AI] {len(items)} items → {len(batches)} API calls (batch size={batch_size})")

    enriched = []
    for i, batch in enumerate(batches):
        print(f"  [AI] Batch {i + 1}/{len(batches)}...")
        prompt = _build_prompt(batch, context, preference_prompt, config)
        result = generate(prompt, model=model, rate_limit=rate_limit)

        analyses = result.get("analyses", [])
        for j, item in enumerate(batch):
            ai = analyses[j] if j < len(analyses) else {}
            if ai:
                score = max(0, min(100, int(ai.get("score", 0))))
                if min_score and score < min_score:
                    continue
                enriched.append(
                    {
                        **item,
                        "ai_score": score,
                        "ai_summary": ai.get("summary", ""),
                        "ai_category": ai.get("category", ""),
                        "ai_notes": ai.get("notes", ""),
                    }
                )
            else:
                enriched.append(item)

    return enriched


def _build_prompt(batch, context, preference_prompt, config):
    priorities = config.get("priorities", [])
    items_text = "\n\n".join(
        f"Item {i+1}: {json.dumps({k: v for k, v in item.items() if not k.startswith('_')}, ensure_ascii=False)}"
        for i, item in enumerate(batch)
    )

    return f"""Analyse these {len(batch)} Hacker News stories and return a JSON object.

# Stories
{items_text}

# User Context
{context[:800] if context else "Not provided"}

# User Priorities (higher = more relevant)
{chr(10).join(f"- {p}" for p in priorities)}

{preference_prompt}

# Instructions
For each story, score relevance (0-100) and categorise. Return:
{{"analyses": [
  {{
    "score": <0-100>,
    "category": "<LLM|Funding|Agent|Infra|OpenSource|Other>",
    "summary": "<1-2 sentence Chinese summary of what this is about>",
    "notes": "<why this is relevant or not, in Chinese>"
  }}
  for each story in order
]}}

Scoring guide:
- 90-100: Major LLM release, $100M+ funding, breakthrough
- 70-89: Interesting AI startup, new model, significant launch
- 50-69: Related but not core (general tech with AI angle)
- <50: Tangentially related, skip

Be concise. Use Chinese for summary and notes."""