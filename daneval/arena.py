"""Step 3: the human A/B arena. A local page that shows one prompt and two blinded answers
in random left/right order. Choices go to runs/<run_id>/human_prefs.jsonl.

    uv run daneval/arena.py            # then open http://localhost:8765
"""
import json
import random
import secrets
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from common import append_jsonl, load_config, load_prompts, model_pairs, pair_id, read_jsonl, responses_by_key

PORT = 8765
cfg = load_config()
prompts = load_prompts(cfg)
responses = responses_by_key(cfg)
prefs_path = cfg["run_dir"] / "human_prefs.jsonl"
PAGE = (Path(__file__).parent / "arena.html").read_bytes()
pending = {}  # token -> (pid, left_model, right_model); models stay server-side so the page is blind


def all_pairs():
    return [(pid, m1, m2) for pid in prompts for m1, m2 in model_pairs(cfg)
            if (pid, m1) in responses and (pid, m2) in responses]


def next_pair():
    done = {r["pair_id"] for r in read_jsonl(prefs_path)}
    pairs = all_pairs()
    todo = [p for p in pairs if pair_id(*p) not in done]
    if not todo:
        return {"done": True, "total": len(pairs)}
    pid, m1, m2 = random.choice(todo)
    left, right = random.sample([m1, m2], 2)
    token = secrets.token_hex(8)
    pending[token] = (pid, left, right)
    return {"token": token, "prompt": prompts[pid]["prompt"], "left": responses[(pid, left)],
            "right": responses[(pid, right)], "rated": len(pairs) - len(todo), "total": len(pairs)}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.end_headers()
        self.wfile.write(body if isinstance(body, bytes) else json.dumps(body).encode())

    def do_GET(self):
        if self.path == "/":
            self._send(200, PAGE, "text/html; charset=utf-8")
        elif self.path == "/api/next":
            self._send(200, next_pair())
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/api/rate":
            return self._send(404, {"error": "not found"})
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if body.get("token") not in pending or body.get("choice") not in ("left", "right", "tie", "both_bad"):
            return self._send(400, {"error": "unknown token or choice"})
        pid, left, right = pending.pop(body["token"])
        winner = {"left": left, "right": right}.get(body["choice"])
        append_jsonl(prefs_path, {
            "pair_id": pair_id(pid, left, right), "prompt_id": pid, "shown_left": left, "shown_right": right,
            "winner": winner, "outcome": "win" if winner else body["choice"],
            "note": body.get("note") or None, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
        self._send(200, {"ok": True})

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print(f"Arena for run {cfg['run_id']}: http://localhost:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
