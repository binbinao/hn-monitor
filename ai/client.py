"""Gemini REST API 客户端 — 带模型回退链"""
import os
import json
import time
import requests

_last_call = 0.0

MODEL_FALLBACK = [
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-lite-latest",
]


def generate(prompt: str, model: str = "", rate_limit: float = 2.0) -> dict:
    """调用 Gemini，429 时自动回退。返回解析后的 JSON dict 或 {}"""
    global _last_call

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("[Gemini] GEMINI_API_KEY not set")
        return {}

    # 速率限制
    elapsed = time.time() - _last_call
    if elapsed < rate_limit:
        time.sleep(rate_limit - elapsed)

    models = [model] + [m for m in MODEL_FALLBACK if m != model] if model else MODEL_FALLBACK
    _last_call = time.time()

    for m in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.3,
                "maxOutputTokens": 2048,
            },
        }
        try:
            resp = requests.post(url, json=payload, timeout=30)
            if resp.status_code == 200:
                return _parse(resp)
            if resp.status_code in (429, 404):
                print(f"[Gemini] {m} returned {resp.status_code}, trying next...")
                time.sleep(1)
                continue
            print(f"[Gemini] {m} error {resp.status_code}: {resp.text[:200]}")
            return {}
        except requests.RequestException as e:
            print(f"[Gemini] {m} request failed: {e}")
            return {}

    print("[Gemini] All models exhausted")
    return {}


def _parse(resp) -> dict:
    """解析 Gemini JSON 响应"""
    try:
        text = (
            resp.json()
            .get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
            .strip()
        )
        if text.startswith("```"):
            text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
        return json.loads(text)
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"[Gemini] Parse error: {e}")
        return {}