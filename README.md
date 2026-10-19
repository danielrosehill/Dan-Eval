# Dan-Eval

> **Status: placeholder (2026-10-19).** No harness, prompts or results yet. This README records the scope and where each component lives.

A composite of my pet-peeve evaluations: the behaviours I check before adopting a new model. It is not a capability benchmark. It asks whether a model carries the biases and blind spots that make it annoying, or unusable, for someone in my position: Israel-based, English-speaking and non-American.

Each component is **atomic**. It lives in its own repository with its own prompts, rubric and results, and can be run and cited on its own. Dan-Eval runs them together and reports one scorecard per model.

## Components

| # | Component | Question | Where it lives | Status |
|---|---|---|---|---|
| 1 | Israel/Palestine framing | Does the model lean pro-Israel or pro-Palestinian, or does it treat mirrored framings of the same events evenly? | [Israel-Palestine-Framing-Eval](https://github.com/danielrosehill/Israel-Palestine-Framing-Eval) | Placeholder |
| 2 | Chinese state censorship | Does the model refuse, deflect or adopt state framing on topics sensitive to the CCP? | Existing public datasets (see below). No repo of my own | Not yet run |
| 3 | American centrism | Does the model assume the user is in the US when nothing says so? | [American-Centrism-Eval](https://github.com/danielrosehill/American-Centrism-Eval) | Placeholder |

### Component 2: use an existing benchmark

Chinese-censorship evaluation is already well covered, so Dan-Eval reuses published prompt sets rather than building its own:

- **[promptfoo/CCP-sensitive-prompts](https://huggingface.co/datasets/promptfoo/CCP-sensitive-prompts)** is the primary set. It contains about 20 prompts for each CCP-sensitive topic, such as Taiwan, Tiananmen and Xi Jinping, and can be run with promptfoo's own eval tool. The licence is CC BY-NC 4.0. Promptfoo's [write-up](https://promptfoo.dev/blog/deepseek-censorship/) describes the method.
- **[augmxnt/deccp](https://huggingface.co/datasets/augmxnt/deccp)** is a secondary set, licensed Apache-2.0.

Caveat: the [R1dacted paper](https://arxiv.org/abs/2505.12625) found that a large share of the CCP-sensitive prompts are unsafe in their own right. A refusal on one of those may be ordinary safety filtering rather than state censorship. Use a filtered subset, or score general-safety prompts separately.

## Noted for later (not yet components)

- **US political persuasion.** Whether the model aligns more with US Democratic or Republican positions, and whether it refuses to argue one side more often than the other. A detailed plan already exists: [My-Benchmarks/benchmark-plans/us-democrat-vs-republican-alignment.md](https://github.com/danielrosehill/My-Benchmarks/blob/main/benchmark-plans/us-democrat-vs-republican-alignment.md).
- **Political correctness generally.** Whether the model hedges, moralises or refuses on contested topics beyond what the question needs. This is not yet scoped. It overlaps with the asymmetric-refusal measure in the plan above.

## Prior work

- [Bias-Censorship-Eval-Tests](https://github.com/danielrosehill/Bias-Censorship-Eval-Tests): early loose notes on the same themes, including US-centricity, China censorship and progressive-versus-conservative lean.
- [My-Benchmarks](https://github.com/danielrosehill/My-Benchmarks): the index of my benchmarks, which lists these repos.

## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
