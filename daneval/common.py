"""Shared helpers: config, prompts, lenses, run files and the OpenRouter client."""
import json
import os
import re
import sys
from itertools import combinations
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def load_config(path=None):
    cfg = json.loads(Path(path or ROOT / "config.json").read_text())
    cfg["run_dir"] = ROOT / "runs" / cfg["run_id"]
    cfg["run_dir"].mkdir(parents=True, exist_ok=True)
    return cfg


def read_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def append_jsonl(path, row):
    with open(path, "a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_prompts(cfg):
    return {p["id"]: p for p in read_jsonl(ROOT / cfg["prompts"])}


def load_lenses():
    return {lens["id"]: lens for lens in json.loads((ROOT / "data" / "lenses.json").read_text())}


def pair_id(prompt_id, m1, m2):
    a, b = sorted([m1, m2])
    return f"{prompt_id}::{a}|{b}"


def model_pairs(cfg):
    return list(combinations(cfg["models"], 2))


def responses_by_key(cfg):
    """{(prompt_id, model): response_text} for every successful generation."""
    return {(r["prompt_id"], r["model"]): r["response"]
            for r in read_jsonl(cfg["run_dir"] / "responses.jsonl") if r.get("response")}


def chat(model, messages, max_tokens=8000, json_mode=False):
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        sys.exit("OPENROUTER_API_KEY is not set")
    body = {"model": model, "messages": messages, "max_tokens": max_tokens}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    r = httpx.post(OPENROUTER_URL, json=body, timeout=180,
                   headers={"Authorization": f"Bearer {key}", "X-Title": "Dan-Eval"})
    r.raise_for_status()
    data = r.json()
    choice = data["choices"][0]
    usage = dict(data.get("usage", {}), finish_reason=choice.get("finish_reason"))
    return choice["message"]["content"], usage


def parse_json(text):
    """Judge output as a dict; tolerates a ```json fence around it."""
    m = re.search(r"\{.*\}", text, re.S)
    return json.loads(m.group(0) if m else text)
