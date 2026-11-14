# AbstentionBench comparison (proposal approved 2026-11-13, 12:40 PM America/New_York)

This folder contains a small, passage-grounded comparison against AbstentionBench (Kirichenko, Ibrahim, Chaudhuri, and Bell, 2025; Meta / FAIR).

## License and what is stored here

- AbstentionBench code and packaged benchmark: [CC BY-NC 4.0](https://github.com/facebookresearch/AbstentionBench/blob/main/LICENSE). Official sources: [GitHub](https://github.com/facebookresearch/AbstentionBench), [Hugging Face](https://huggingface.co/datasets/facebook/AbstentionBench), [paper](https://arxiv.org/abs/2506.09038).
- SQuAD 2.0 (the `squad2` subset, loaded from the same validation parquet AbstentionBench uses): [CC BY-SA 4.0](https://huggingface.co/datasets/rajpurkar/squad_v2).
- MediQ (patient-context questions, used as a second context-grounded subset): [CC BY 4.0](https://github.com/stellalisy/mediQ/blob/main/LICENSE).

Because AbstentionBench is non-commercial, this folder does **not** redistribute dataset passages, questions, or the official keyword list. It stores item IDs, a fetch-and-sample script, run metrics, and model answers without the source context. To rebuild the prompts, run `fetch_and_sample.py`, which downloads from the official sources into `_cache/` (gitignored).

## Sample

- Seed: `20261113`
- Subsets: AbstentionBench `squad2` (SQuAD 2.0 validation, first restricted to the official 3,500-index subsample in `data/subsampling-indices.json`) and MediQ (iCRAFT-MD and iMEDQA, with the same three iMEDQA exclusions as AbstentionBench).
- Size: 50 items per subset, 25 should-abstain and 25 should-answer, 100 items total.
- MediQ answerable and unanswerable items use disjoint source IDs, so the same patient question is not tested twice.
- QASPER was not used: official prompts can run up to about 29k tokens, which does not fit this free-tier budget. Musique was not used: the official AbstentionBench download path is a Google Drive zip, and two passage-grounded subsets already fill the call budget.

## Systems and scoring

- Systems: groq `openai/gpt-oss-120b`, `openai/gpt-oss-20b`, and `qwen/qwen3.8-27b`. Temperature 0. `max_tokens` 2048. For the two gpt-oss systems, `reasoning_effort=low` was set to stay inside Groq token-per-minute limits; that is a documented difference from the ClaimStanceBench day 1 default (medium).
- Prompts follow the official AbstentionBench templates for each subset (no ClaimStanceBench STANCE line).
- Abstention is scored with AbstentionBench's rule-based `ContainsAbstentionKeywordAbstentionDetector`: a case-insensitive substring match against `recipe/abstention_keywords.py`. The keyword list is fetched from the official repo at run time and is not copied into this folder. The paper's headline metric uses an LLM judge; this official keyword detector is the method that can be run without a paid judge. It is a known-limited string matcher and may miss abstentions that do not use those phrases.
- Budget: 100 items times 3 systems = 300 Groq calls, under the 400-call cap and inside Groq's about 1,000/day limit.

## Attribution

AbstentionBench (c) Meta Platforms, Inc. and affiliates, CC BY-NC 4.0. SQuAD 2.0 (Rajpurkar et al.), CC BY-SA 4.0. MediQ (Li et al.), CC BY 4.0.

## Day 1 run status (Fri Nov 13, 2026, America/New_York)

The comparison was approved at 12:40 PM and started the same afternoon. gpt-oss-20b and qwen3.8-27b finished all 100 items. gpt-oss-120b completed 45 of 100 (AB-001 through AB-045, all SQuAD 2.0) before the runner was stopped at about 2:23 PM. A Groq header probe at about 2:21 PM showed this was not a daily cap (884 of 1000 requests remaining for that system; 8000 tokens per minute). At about 2 rows per 6 minutes, the rest would not have finished within 30 minutes. The leftover IDs can be resumed from `raw-20261113-groq-compare.csv`. Official three-system ranks use only the 45-item shared subset.

The committed `raw-20261113-groq-compare.csv` stores IDs, labels, and detector outputs only. Raw model answers and token counts stay in the gitignored `_cache/` copy on the machine that ran the job, and are not redistributed.
