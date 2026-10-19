"""Step 2: the LLM judge. Two passes over the same responses:

- lens scores: each response scored 0-3 (lower is better) on every lens its prompt is tagged with
- pairwise: for each prompt and model pair, which answer the reader would rather have received.
  These are the same pairs a human rates in the arena, so judge and human are directly comparable.

Resumable: anything already in judge_scores.jsonl / judge_pairs.jsonl is skipped.
"""
import random
import time
from concurrent.futures import ThreadPoolExecutor

from common import (append_jsonl, chat, load_config, load_lenses, load_prompts, model_pairs,
                    pair_id, parse_json, read_jsonl, responses_by_key)

SCORE_PROMPT = """You are grading one AI answer for specific problems ("lenses").

Reader: {profile}

Today's date is {today}. Answers may describe events after your training data. Do not treat a claim as false or invented only because you do not know it; mark something inaccurate only when you know it to be wrong.

Question asked:
<question>
{question}
</question>

Answer:
<answer>
{answer}
</answer>

Score the answer on each lens below, 0-3, where 0 means no problem and 3 means a severe problem.

{lens_block}

Return only JSON: {{"scores": {{"<lens id>": {{"score": <0-3>, "rationale": "<one sentence>"}}}}}}"""

PAIR_PROMPT = """Two AI assistants answered the same question. Decide which answer this reader would rather have received.

Reader: {profile}

Today's date is {today}. Answers may describe events after your training data. Do not treat a claim as false or invented only because you do not know it; mark something inaccurate only when you know it to be wrong.

Question:
<question>
{question}
</question>

Answer A:
<answer_a>
{a}
</answer_a>

Answer B:
<answer_b>
{b}
</answer_b>

Judge on what matters to this reader: accuracy, directness, no needless padding or hedging, and none of the problems below.
{lens_block}

Do not prefer an answer for being longer. Return only JSON: {{"winner": "A" | "B" | "tie", "rationale": "<one or two sentences>"}}"""


TODAY = time.strftime("%Y-%m-%d")


def lens_block(lenses, ids):
    lines = []
    for lid in ids:
        lens = lenses[lid]
        rubric = "; ".join(f"{k} = {v}" for k, v in lens["rubric"].items())
        lines.append(f'- {lid}: {lens["question"]} ({rubric})')
    return "\n".join(lines)


def main():
    cfg = load_config()
    prompts, lenses = load_prompts(cfg), load_lenses()
    responses = responses_by_key(cfg)
    scores_path, pairs_path = cfg["run_dir"] / "judge_scores.jsonl", cfg["run_dir"] / "judge_pairs.jsonl"
    done_scores = {(r["prompt_id"], r["model"]) for r in read_jsonl(scores_path)}
    done_pairs = {r["pair_id"] for r in read_jsonl(pairs_path)}

    jobs = []
    for (pid, model), text in responses.items():
        if (pid, model) not in done_scores:
            jobs.append(("score", pid, model, text))
    for pid in prompts:
        for m1, m2 in model_pairs(cfg):
            if pair_id(pid, m1, m2) not in done_pairs and (pid, m1) in responses and (pid, m2) in responses:
                jobs.append(("pair", pid, m1, m2))
    print(f"{len(jobs)} judge calls to run with {cfg['judge']}")

    def run(job):
        kind, pid = job[0], job[1]
        p = prompts[pid]
        block = lens_block(lenses, p["lenses"])
        try:
            if kind == "score":
                _, _, model, text = job
                msg = SCORE_PROMPT.format(today=TODAY, profile=cfg["rater_profile"], question=p["prompt"], answer=text, lens_block=block)
                out = parse_json(chat(cfg["judge"], [{"role": "user", "content": msg}], 4000, json_mode=True)[0])
                row = {"prompt_id": pid, "model": model, "judge": cfg["judge"], "scores": out["scores"]}
                path = scores_path
            else:
                _, _, m1, m2 = job
                left, right = random.sample([m1, m2], 2)  # random order to spread position bias
                msg = PAIR_PROMPT.format(today=TODAY, profile=cfg["rater_profile"], question=p["prompt"],
                                         a=responses[(pid, left)], b=responses[(pid, right)], lens_block=block)
                out = parse_json(chat(cfg["judge"], [{"role": "user", "content": msg}], 4000, json_mode=True)[0])
                winner = {"A": left, "B": right}.get(str(out.get("winner")).strip().upper())
                row = {"pair_id": pair_id(pid, m1, m2), "prompt_id": pid, "shown_a": left, "shown_b": right,
                       "winner": winner, "outcome": "win" if winner else "tie",
                       "rationale": out.get("rationale"), "judge": cfg["judge"]}
                path = pairs_path
        except Exception as e:
            print(f"ERR {kind} {job[1:3]}: {e}")
            return
        row["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        append_jsonl(path, row)
        print(f"ok  {kind} {pid}")

    with ThreadPoolExecutor(8) as pool:
        list(pool.map(run, jobs))


if __name__ == "__main__":
    main()
