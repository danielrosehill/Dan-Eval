"""Step 4: the scorecard. Three views of the same pairs, plus the judge's lens scores:

- judge view:     win rate from the judge's pairwise verdicts
- human view:     win rate from the arena
- composite:      human_weight * human + (1 - human_weight) * judge, per model
- divergence:     agreement rate on pairs both rated, and every pair where they disagree

Writes runs/<run_id>/report.json and report.md.
"""
import json
from collections import defaultdict
from statistics import mean

from common import load_config, load_lenses, load_prompts, read_jsonl


def win_rates(rows, models, prompts, lens=None):
    """{model: (win_rate, n_pairs)}. A tie or 'both bad' counts as half a win to each side."""
    pts, n = defaultdict(float), defaultdict(int)
    for r in rows:
        if lens and lens not in prompts[r["prompt_id"]]["lenses"]:
            continue
        pair = r["pair_id"].split("::", 1)[1].split("|")
        for m in pair:
            n[m] += 1
            pts[m] += 1.0 if r["winner"] == m else 0.5 if r["winner"] is None else 0.0
    return {m: (round(pts[m] / n[m], 3) if n[m] else None, n[m]) for m in models}


def fmt(x):
    return "–" if x is None else f"{x:.2f}"


def main():
    cfg = load_config()
    prompts, lenses, models, rd = load_prompts(cfg), load_lenses(), cfg["models"], cfg["run_dir"]
    w = cfg["human_weight"]
    judge_pairs, human = read_jsonl(rd / "judge_pairs.jsonl"), read_jsonl(rd / "human_prefs.jsonl")
    scores = read_jsonl(rd / "judge_scores.jsonl")

    # Lens severity from the judge's absolute scores (0-3, lower is better)
    sev = defaultdict(list)
    for r in scores:
        for lid, s in r["scores"].items():
            if isinstance(s, dict) and isinstance(s.get("score"), (int, float)):
                sev[(r["model"], lid)].append(s["score"])
    lens_ids = [l for l in lenses if any((m, l) in sev for m in models)]

    views = {}
    for lens in [None] + lens_ids:
        j, h = win_rates(judge_pairs, models, prompts, lens), win_rates(human, models, prompts, lens)
        comp = {}
        for m in models:
            jw, hw = j[m][0], h[m][0]
            comp[m] = None if jw is None and hw is None else jw if hw is None else hw if jw is None else round(w * hw + (1 - w) * jw, 3)
        views[lens or "all"] = {"judge": j, "human": h, "composite": comp}

    # Divergence: pairs rated by both
    jmap = {r["pair_id"]: r for r in judge_pairs}
    both = [(jmap[h["pair_id"]], h) for h in human if h["pair_id"] in jmap]
    agree = [jr for jr, hr in both if jr["winner"] == hr["winner"]]
    disagreements = [{"pair_id": hr["pair_id"], "prompt": prompts[hr["prompt_id"]]["prompt"],
                      "judge_winner": jr["winner"] or "tie", "human_winner": hr["winner"] or hr["outcome"],
                      "judge_rationale": jr.get("rationale"), "human_note": hr.get("note")}
                     for jr, hr in both if jr["winner"] != hr["winner"]]

    report = {
        "run_id": cfg["run_id"], "models": models, "judge": cfg["judge"], "human_weight": w,
        "views": views,
        "lens_severity": {m: {l: round(mean(sev[(m, l)]), 2) for l in lens_ids if sev[(m, l)]} for m in models},
        "agreement": {"pairs_rated_by_both": len(both), "agree": len(agree),
                      "rate": round(len(agree) / len(both), 3) if both else None},
        "disagreements": disagreements,
    }
    (rd / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))

    md = [f"# Dan-Eval report: {cfg['run_id']}", "",
          f"Judge: `{cfg['judge']}` · human weight in composite: {w}", "",
          "## Win rates (pairwise, ties count half)", "",
          "| Lens | Model | Judge | Human | Composite | Human − Judge |", "|---|---|---|---|---|---|"]
    for lens, v in views.items():
        for m in models:
            jw, hw = v["judge"][m][0], v["human"][m][0]
            gap = fmt(hw - jw) if jw is not None and hw is not None else "–"
            md.append(f"| {lens} | `{m}` | {fmt(jw)} (n={v['judge'][m][1]}) | {fmt(hw)} (n={v['human'][m][1]}) "
                      f"| {fmt(v['composite'][m])} | {gap} |")
    md += ["", "## Judge lens severity (0 = clean, 3 = severe)", "",
           "| Model | " + " | ".join(lens_ids) + " |", "|---|" + "---|" * len(lens_ids)]
    for m in models:
        md.append(f"| `{m}` | " + " | ".join(fmt(report["lens_severity"][m].get(l)) for l in lens_ids) + " |")
    a = report["agreement"]
    md += ["", "## Judge vs human", "",
           f"Agreement on {a['pairs_rated_by_both']} pairs rated by both: {fmt(a['rate'])}", ""]
    for d in disagreements:
        md += [f"- **{d['prompt']}** — judge: `{d['judge_winner']}`, you: `{d['human_winner']}`",
               f"  - judge: {d['judge_rationale']}"] + ([f"  - you: {d['human_note']}"] if d["human_note"] else [])
    (rd / "report.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
