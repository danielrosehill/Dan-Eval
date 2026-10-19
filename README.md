# Dan-Eval

> **Status: proof of concept (2026-10-19).** The harness runs from start to finish on a 24-prompt POC set (run `poc-01`): two models, judge scores, the A/B arena and the report. Human ratings for `poc-01` have not been collected yet. Method: [docs/method.md](docs/method.md).

A composite of my pet-peeve evaluations: the behaviours I check before adopting a new model. It is not a capability benchmark. It asks whether a model carries the biases and blind spots that make it annoying, or unusable, for someone in my position: Israel-based, English-speaking and non-American.

Each component is **atomic**. It lives in its own repository with its own prompts, rubric and results, and can be run and cited on its own. Dan-Eval runs them together and reports one scorecard per model.

## Scoring: judge, human, composite

Each lens is scored by two signals:

- **LLM-as-judge.** A judge model that is not one of the models under test scores each answer 0–3 on each of its prompt's lenses. It also picks the better answer of each pair.
- **Human A/B.** An arena (`daneval/arena.py`, run locally or on the private HF Space `Dan-Eval-Arena`) shows the same pairs to me blind, in random left/right order. This is pairwise preference evaluation, as in Chatbot Arena. It is not reinforcement learning, since nothing is trained on the choices.

The report shows a judge view, a human view and a weighted composite, per model and per lens. It also shows where the judge and I disagree. Details and run commands: [docs/method.md](docs/method.md).

## Components

| # | Component | Question | Where it lives | Status |
|---|---|---|---|---|
| 1 | Israel/Palestine framing | Does the model affirm misinformation or contested allegations as fact about the conflict, and does it lean pro-Israel or pro-Palestinian on mirrored and open-neutral prompts? | [Israel-Palestine-Framing-Eval](https://github.com/danielrosehill/Israel-Palestine-Framing-Eval) · [prompts](https://huggingface.co/datasets/danielrosehill/Israel-Palestine-Framing-Eval) | v0.2 prompts (70), not yet run |
| 2 | Chinese state censorship | Does the model refuse, deflect or adopt state framing on topics sensitive to the CCP? | Existing public datasets (see below). No repo of my own | Not yet run |
| 3 | American centrism | Does the model assume the user is in the US when nothing says so? | [American-Centrism-Eval](https://github.com/danielrosehill/American-Centrism-Eval) · [prompts](https://huggingface.co/datasets/danielrosehill/American-Centrism-Eval) | v0.1 prompts, not yet run |

Each component's test prompts are published as their own Hugging Face dataset, linked in the table above, so they can be used without the rest of Dan-Eval.

### Component 2: use an existing benchmark

Chinese-censorship evaluation is already well covered, so Dan-Eval reuses published prompt sets rather than building its own:

- **[promptfoo/CCP-sensitive-prompts](https://huggingface.co/datasets/promptfoo/CCP-sensitive-prompts)** is the primary set. It contains about 20 prompts for each CCP-sensitive topic, such as Taiwan, Tiananmen and Xi Jinping, and can be run with promptfoo's own eval tool. The licence is CC BY-NC 4.0. Promptfoo's [write-up](https://promptfoo.dev/blog/deepseek-censorship/) describes the method.
- **[augmxnt/deccp](https://huggingface.co/datasets/augmxnt/deccp)** is a secondary set, licensed Apache-2.0.

Caveat: the [R1dacted paper](https://arxiv.org/abs/2505.12625) found that a large share of the CCP-sensitive prompts are unsafe in their own right. A refusal on one of those may be ordinary safety filtering rather than state censorship. Use a filtered subset, or score general-safety prompts separately.

## Noted for later (not yet components)

- **US political persuasion.** Whether the model aligns more with US Democratic or Republican positions. This now has its own repo, [US-Partisan-Framing-Eval](https://github.com/danielrosehill/US-Partisan-Framing-Eval) (prompts only, 2026-10-19), which asks neutral questions and reads the lean from the answer. It is not yet a component.
- **Political correctness generally.** Whether the model hedges, moralises or refuses on contested topics beyond what the question needs. Scoped on 2026-10-19 as its own repo, [The PC Bench](https://github.com/danielrosehill/The-PC-Bench) (prompts only, no harness yet). Not yet a component.

## Prior work

- [Bias-Censorship-Eval-Tests](https://github.com/danielrosehill/Bias-Censorship-Eval-Tests): early loose notes on the same themes, including US-centricity, China censorship and progressive-versus-conservative lean.
- [My-Benchmarks](https://github.com/danielrosehill/My-Benchmarks): the index of my benchmarks, which lists these repos.

## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
