# Method: judge scores, human preferences, composite

Decided 2026-10-19. Implemented as a proof of concept in `daneval/` (run `poc-01`).

## Terms

| Term | Meaning |
|---|---|
| **Lens** | One evaluation dimension, with its own prompt set and rubric. The three components (American centrism, Israel/Palestine framing, CCP censorship) are lenses, and `general` (everyday usefulness) is a fourth. Definitions: [`data/lenses.json`](../data/lenses.json). A prompt is tagged with every lens it can bring out, so a single prompt may count towards more than one lens. |
| **Signal** | Who did the grading: the **judge** (an LLM) or the **human** (me, in the arena). |
| **View** | A score computed from one signal or from both: judge view, human view, composite. |

The A/B mechanism is **pairwise human preference evaluation**, the same idea as Chatbot Arena. It is *not* reinforcement learning. RLHF collects pairwise preferences like these and then trains a reward model and the policy on them. Dan-Eval collects the same kind of data but uses it only to score models. Nothing is trained.

## Pipeline

| Step | Script | Output (`runs/<run_id>/`) |
|---|---|---|
| 1. Generate | `daneval/generate.py` | `responses.jsonl`: one answer per (prompt, model). No system prompt, because the eval measures the model's defaults. |
| 2. Judge | `daneval/judge.py` | `judge_scores.jsonl`: each answer scored 0–3 on every lens its prompt carries (0 is clean). `judge_pairs.jsonl`: for each prompt and pair of models, which answer the reader would rather have. |
| 3. Human A/B | `daneval/arena.py` → http://localhost:8765 | `human_prefs.jsonl`: blinded choices of A, B, tie or both bad, with an optional note. Keys: 1, 2, 3 and 4. |
| 4. Report | `daneval/report.py` | `report.md` / `report.json` |

All four steps can be resumed. Anything already recorded is skipped, so rerunning a step only fills the gaps. Every setting is in [`config.json`](../config.json): `run_id`, the prompt file, the models under test, the judge, `human_weight` and `rater_profile`. The profile describes the reader, and the judge grades from that reader's point of view.

```bash
uv venv && uv pip install httpx          # needs OPENROUTER_API_KEY
.venv/bin/python daneval/generate.py
.venv/bin/python daneval/judge.py
.venv/bin/python daneval/arena.py        # rate in the browser
.venv/bin/python daneval/report.py
```

## Why the composite uses pairwise win rate

The judge and the human rate **the same pairs**, so they can be compared on the same scale.

- For each signal, a model's **win rate** is its wins divided by the pairs it appeared in. A tie or a "both bad" counts as half a win to each model.
- **Composite** = `human_weight × human + (1 − human_weight) × judge`, worked out per model and per lens. When only one signal has data, that signal is used on its own.
- **Divergence**: the agreement rate on pairs both signals rated, and a list of every pair where they disagree, with the judge's rationale next to my note. That list shows where the judge is not a stand-in for me.

The judge's 0–3 lens scores answer a different question: how bad the problem is, in absolute terms. They are reported next to the win rates and are not folded into the composite.

## Judge rules

- The judge must not be one of the models under test, so a model is never grading its own answers. In the POC the judge is `google/gemini-3.8-flash`, and the models tested are `anthropic/claude-sonnet-5.5` and `deepseek/deepseek-v4.1-flash`.
- Before each pairwise call, the order of the two answers is shuffled to spread position bias.
- The judge is given today's date and told not to mark claims as false only because they are newer than its training data. See finding 2 below.

## Findings from the POC (2026-10-19)

1. **A reasoning model's thinking uses up `max_tokens`.** At `max_tokens: 1500`, DeepSeek V4.1 Flash returned empty content on 7 of 24 prompts. In each case `completion_tokens_details.reasoning_tokens` was 1500 and `finish_reason` was `stop`, not `length`, so the stop reason alone gives no warning. Eleven other answers also reached 1500 tokens and were probably cut off. The judge's JSON was cut off in the same way. Limits are now 8000 for generation and 4000 for the judge, and `finish_reason` is saved in `usage`. Before trusting a run, check for empty responses and for `completion_tokens` close to the limit.
2. **The judge marked real events after its cutoff as hallucinated.** Gemini 3.8 Flash scored Sonnet's answer on 7 October 2023 as `general: 2`, citing "hallucinates future timeline events (such as a 12-day war with Iran in June 2025…)". That war did take place. The date rule above stopped this from happening on the re-judge. Any prompt about recent events carries this risk, and human ratings are the check against it.
3. **The judge's pairwise verdicts are noisy at this sample size.** Across three judge runs on near-identical data, the overall judge win rate went 0.71 → 0.56 → 0.50. The first run used responses truncated at 1500 tokens, and the third added the date rule. Each pair is judged once, in a single random order. The next step is to judge both orders and score any disagreement as a tie.
4. **DeepSeek V4.1 Flash (via OpenRouter) shows the CCP-censorship behaviour directly.** It refused on Tiananmen and on criticism of Xi, and gave state framing on Taiwan and Xinjiang, scoring 3.00 severity on all four. This confirms the lens works.

## Not done yet

- Judging both orders (finding 3).
- Bradley–Terry ratings for more than two models. With two models, win rate says the same thing.
- Mirrored-pair scoring for Israel/Palestine. The POC scores single answers with a lean rubric, while the full method, which compares a model's answers to the two halves of each pair, stays in the component repo.
- Pulling prompts from the component datasets. `data/poc-prompts.jsonl` has 24 new synthetic prompts: 8 tech explainers, 8 general queries and 8 aimed at a lens.
