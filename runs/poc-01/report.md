# Dan-Eval report: poc-01

Judge: `google/gemini-3.8-flash` · human weight in composite: 0.5

## Win rates (pairwise, ties count half)

| Lens | Model | Judge | Human | Composite | Human − Judge |
|---|---|---|---|---|---|
| all | `anthropic/claude-sonnet-5.5` | 0.50 (n=24) | – (n=0) | 0.50 | – |
| all | `deepseek/deepseek-v4.1-flash` | 0.50 (n=24) | – (n=0) | 0.50 | – |
| general | `anthropic/claude-sonnet-5.5` | 0.50 (n=24) | – (n=0) | 0.50 | – |
| general | `deepseek/deepseek-v4.1-flash` | 0.50 (n=24) | – (n=0) | 0.50 | – |
| american-centrism | `anthropic/claude-sonnet-5.5` | 0.50 (n=10) | – (n=0) | 0.50 | – |
| american-centrism | `deepseek/deepseek-v4.1-flash` | 0.50 (n=10) | – (n=0) | 0.50 | – |
| israel-palestine | `anthropic/claude-sonnet-5.5` | 0.25 (n=4) | – (n=0) | 0.25 | – |
| israel-palestine | `deepseek/deepseek-v4.1-flash` | 0.75 (n=4) | – (n=0) | 0.75 | – |
| ccp-censorship | `anthropic/claude-sonnet-5.5` | 1.00 (n=4) | – (n=0) | 1.00 | – |
| ccp-censorship | `deepseek/deepseek-v4.1-flash` | 0.00 (n=4) | – (n=0) | 0.00 | – |

## Judge lens severity (0 = clean, 3 = severe)

| Model | general | american-centrism | israel-palestine | ccp-censorship |
|---|---|---|---|---|
| `anthropic/claude-sonnet-5.5` | 0.08 | 1.00 | 0.00 | 0.00 |
| `deepseek/deepseek-v4.1-flash` | 0.67 | 1.10 | 0.25 | 3.00 |

## Judge vs human

Agreement on 0 pairs rated by both: –

