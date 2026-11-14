# ClaimStanceBench

ClaimStanceBench is a 55-item, passage-grounded evaluation of whether a system asserts a complete answer, answers only the supported part and names what is missing (partial), or withholds when the passage does not support an answer. It was built for the Apart Research AI x Epistemics Research Sprint (Nov 13 to 15, 2026).

Frozen item file: `items/items.jsonl`. Frozen sha256: `b700b889ec5e95c455850bad2e9d1f46f17885136f97d0456f594719ff841c43`. Gold split after a post-run label correction on GAR-05: 17 assert, 22 partial, 16 withhold. See `items/CHANGELOG.md` and `items/FROZEN`.

## License

- Harness, scoring, and other code: Apache License 2.0 (`LICENSE`).
- The 55 author-written items (passages, questions, and gold labels): Creative Commons Attribution 4.0 International (`LICENSE-DATA.md`).
- AbstentionBench (CC BY-NC 4.0), SQuAD 2.0 (CC BY-SA 4.0), and MediQ (CC BY 4.0) source passages and the AbstentionBench keyword list are not redistributed. `results/abstentionbench/` stores item IDs, metrics, and a fetch script. See that folder's README.

## What's in this repository

- `harness/`: load items, call a free-tier system (Groq or OpenRouter `:free`), parse the declared stance, score binary and three-way metrics, and optionally apply the four-part partial pass judge.
- `items/`: frozen items and changelog.
- `results/`: official run CSVs, summaries, judge annotations, and a small AbstentionBench comparison (IDs and metrics only).
- `webchat/`: paste-ready packet and reply templates for the free ChatGPT, Gemini, and Claude web chats.
- `scripts/plot_report_figures.py`: rebuilds the report figures from the committed results.
- `tests/`: offline tests with placeholder fixtures only. No system calls.

## Official API runs

All four default systems completed 55 of 55 items, including OpenRouter `baidu/ernie-5.5-flash-preview:free`. The ERNIE default run stopped at 51 of 55 when OpenRouter returned HTTP 429 for its free-models-per-day cap (GAR-11, GAR-12, GAR-13, and BAK-15 outstanding). Those four items were collected later the same day, Friday, Nov 13, 2026, after the daily reset. gpt-oss-20b produced one empty output on the default prompt (BIK-05), counted as incorrect. See `results/summary.md` and `results/summary-permissive.md`.

## Reproducing the work

Use Python 3.10 or later. From the repository root:

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q tests
```

Scoring the committed CSVs needs no API keys:

```
python -m harness.score --raw results/raw-20261113-groq-default.csv results/raw-20261113-openrouter-ernie-default.csv
python -m harness.score --raw results/raw-20261113-groq-permissive.csv
```

To call systems yourself, set `GROQ_API_KEY` and/or `OPENROUTER_API_KEY` in the environment. Do not put keys in this repository. All API use in the official runs stayed on the providers' free tiers. The harness accepts only OpenRouter models whose ids end in `:free`. Groq was used for `openai/gpt-oss-120b`, `openai/gpt-oss-20b`, and `qwen/qwen3.8-27b`. Free tiers have daily request caps; a 429 means wait for the daily reset or slow the run with `--sleep`.

```
python -m harness.run --model groq:openai/gpt-oss-20b --variant default
python -m harness.score --raw path/to/raw.csv --judge --judge-model groq:openai/gpt-oss-120b
```

The harness refuses to run unless `items/FROZEN` matches the sha256 of `items/items.jsonl`.

Web-chat replies, with no API calls:

```
python -m harness.score_webchat --template path/to/filled-template.md --service chatgpt
```

To rebuild the AbstentionBench comparison prompts, run `python results/abstentionbench/fetch_and_sample.py`, which downloads official sources into `results/abstentionbench/_cache/` (gitignored).

To rebuild figures 1 through 4:

```
python scripts/plot_report_figures.py --outdir figures
```

Figure 5 also needs the blind-grade agreement JSON, passed with `--agreement`.

## Preexisting work

All work in this repository was done during the sprint (Nov 13 to 15, 2026). Nothing is preexisting except the initial README stub and `.gitignore` (Nov 12).
