"""Step 1: get every model's answer to every prompt. Resumable: done pairs are skipped."""
import time
from concurrent.futures import ThreadPoolExecutor

from common import append_jsonl, chat, load_config, load_prompts, responses_by_key


def main():
    cfg = load_config()
    prompts = load_prompts(cfg)
    done = responses_by_key(cfg)
    todo = [(p, m) for p in prompts.values() for m in cfg["models"] if (p["id"], m) not in done]
    out = cfg["run_dir"] / "responses.jsonl"
    print(f"{len(todo)} generations to run ({len(done)} already done)")

    def run(job):
        p, model = job
        # No system prompt: the eval measures the model's defaults.
        try:
            text, usage = chat(model, [{"role": "user", "content": p["prompt"]}], cfg["max_tokens"])
            row = {"prompt_id": p["id"], "model": model, "response": text, "usage": usage}
        except Exception as e:
            row = {"prompt_id": p["id"], "model": model, "response": None, "error": str(e)}
        row["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        append_jsonl(out, row)
        print(("ok  " if row["response"] else "ERR ") + f"{p['id']} {model}")

    with ThreadPoolExecutor(8) as pool:
        list(pool.map(run, todo))


if __name__ == "__main__":
    main()
