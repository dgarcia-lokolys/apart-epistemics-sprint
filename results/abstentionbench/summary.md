# AbstentionBench comparison (Day 1)

Date: 2026-11-13 (America/New_York)
Subsets: squad2 (SQuAD 2.0, official AbstentionBench subsample then seed 20261113 25/25) and MediQ (25/25, disjoint source IDs).
Detector: official ContainsAbstentionKeywordAbstentionDetector. Temperature 0, max_tokens 2048. gpt-oss reasoning_effort=low.

All three systems finished all 100 items (300 of 300 planned calls, zero recorded errors). The head-to-head below uses the full set. gpt-oss-120b was resumed after an earlier stop at 45 items and completed AB-046 through AB-100 later the same day.

| System | n | Accuracy | Rank (acc) | Abstention recall | Abstention precision | F1 |
|---|---:|---:|---:|---:|---:|---:|
| openai/gpt-oss-120b | 100 | 51.0% | 2 | 2.0% | 100.0% | 3.9% |
| openai/gpt-oss-20b | 100 | 50.0% | 3 | 0.0% | - | - |
| qwen/qwen3.8-27b | 100 | 57.0% | 1 | 14.0% | 100.0% | 24.6% |

All three systems answered the 50 should-answer items correctly (no official-detector false abstentions). Rank is driven by abstention recall on the 50 should-abstain items: qwen 7/50, 120b 1/50 (AB-021, squad2), 20b 0/50.

By subset (accuracy / recall / precision):

| System | squad2 acc | squad2 rec | squad2 prec | mediq acc | mediq rec | mediq prec |
|---|---:|---:|---:|---:|---:|---:|
| openai/gpt-oss-120b | 52.0% | 4.0% | 100.0% | 50.0% | 0.0% | - |
| openai/gpt-oss-20b | 50.0% | 0.0% | - | 50.0% | 0.0% | - |
| qwen/qwen3.8-27b | 60.0% | 20.0% | 100.0% | 54.0% | 8.0% | 100.0% |

## Rank agreement with ClaimStanceBench

On this 100-item head-to-head, accuracy order is qwen3.8-27b, then gpt-oss-120b, then gpt-oss-20b.
ClaimStanceBench default binary order among the same three Groq systems is qwen, then 20b, then 120b. That does not match: 20b and 120b swap.
ClaimStanceBench default three-way order is qwen first, with 20b and 120b tied. First place matches; the 20b/120b tie does not appear here.
ClaimStanceBench four-part partial pass (complete Groq default run only: 120b 13/22, 20b 10/22) has 120b ahead of 20b, which matches this comparison's 120b-over-20b accuracy and recall gap, but the gap here is a single official-detector abstention (1 vs 0) and should not be over-read.
ERNIE leads ClaimStanceBench default binary and three-way (55/55 items) and was not included in this AbstentionBench comparison.

## Keyword-detector hand-check

Ten outputs were reviewed against the official keyword list: 120b AB-021 (the only 120b official abstention), qwen AB-004, AB-006, and AB-059 (official abstentions), 120b AB-001 and AB-051 (should-abstain, official non-abstain), 120b AB-026 and 20b AB-076 (should-answer, official non-abstain), and qwen AB-001 and AB-002 (should-abstain, official non-abstain).

A fresh run of the official detector agreed with every stored label on all 300 rows, including these ten.

On the ten hand-checked rows, the official substring rule was applied correctly in all ten cases. Human judgment of whether the answer actually withheld agreed in 7 of 10. The three exceptions:
- qwen AB-059 (MediQ, official abstain): the hit is incidental clinical wording ("location is unclear", "clinical picture is ambiguous") in a long workup that is trying to pick a test. The stored row is truncated at 4000 characters (finish_reason=length). This is a keyword false positive relative to human intent, and a lucky true positive on the gold label.
- qwen AB-001 and AB-002 (SQuAD 2.0) clearly withhold in paraphrase ("the information required to answer the question is not present in the context"; "does not contain information") but do not contain an official keyword, so the detector labels them as answers. These are official-rule true negatives and human-intent false negatives.

Calls used: 300 of 300 planned. Zero recorded errors.
