# ClaimStanceBench: web-chat systems (default wording)

Date of founder run: 11/13/2026 (America/New_York), for all three web chats (ChatGPT, Claude, and Gemini).
Condition: consumer web chat, batched x10, prompt variant default (the original packet wording, not the optional permissive set)
How the run was done: the founder pasted the default packet by hand into the free web chats of ChatGPT, Gemini, and Claude. There is no temperature control, and the underlying versions may differ from any API model of a similar name. Each service used six pastes (batches of 10, 10, 10, 10, 10, and 5) in the official item order (seed 20261113).
Model names shown in the templates:
- ChatGPT: GPT - 5.6 Luna
- Claude: Sonnet 5.5 Medium
- Gemini: 3.5 Flash-Lite Medium
Items: 55 frozen (22 partial, 17 assert, 16 withhold); sha256 b700b889ec5e95c455850bad2e9d1f46f17885136f97d0456f594719ff841c43
Scoring: same binary and three-way metrics as the API runs. The CSV `variant` column is `webchat_batch10_default`. Four-part partial pass was not judged; gold-partial label accuracy (parsed STANCE equals partial on the 22 gold partials) is the judge-free stand-in.

## Parse QC

The scorer does not invent answers. Two heading forms in the pastes were not originally recognized and were added as heading patterns only (still requiring a STANCE line in the same item block):

- ChatGPT batch 6 used `### **ITEM-ID**` (bold around the id). The first 50 items used plain `### ITEM-ID`.
- Gemini batches 1 and 2 used a bare `ITEM-ID` line with no `###` prefix. Batches 3 through 6 used `### ITEM-ID`.

After those heading forms were accepted, all three templates parsed 55 of 55 items, in the official batch order, with a STANCE on every item. No items were missing, unparseable, or out of order. No answers were guessed.

## Scores (default wording)

| System | Channel | n | Binary acc | Three-way acc | Over-claim | Under-claim | Assert / partial / withhold | Gold-partial labels |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| GPT - 5.6 Luna | web chat (default wording) | 55/55 | 98.2% (54/55) | 92.7% (51/55) | 5.5% | 1.8% | 18 / 22 / 15 | 20/22 |
| Sonnet 5.5 Medium | web chat (default wording) | 55/55 | 94.5% (52/55) | 89.1% (49/55) | 10.9% | 0.0% | 20 / 22 / 13 | 19/22 |
| 3.5 Flash-Lite Medium | web chat (default wording) | 55/55 | 89.1% (49/55) | 85.5% (47/55) | 12.7% | 1.8% | 23 / 17 / 15 | 16/22 |
| qwen/qwen3.8-27b | Groq API (default prompt) | 55/55 | 89.1% (49/55) | 85.5% (47/55) | 10.9% | 3.6% | 21 / 19 / 15 | 17/22 |
| openai/gpt-oss-20b | Groq API (default prompt) | 55/55 | 83.6% (46/55) | 69.1% (38/55) | 18.2% | 10.9% | 25 / 10 / 19 (1 empty) | 8/22 |
| openai/gpt-oss-120b | Groq API (default prompt) | 55/55 | 78.2% (43/55) | 69.1% (38/55) | 30.9% | 0.0% | 29 / 18 / 8 | 13/22 |

These web-chat scores are a separate condition from the official Groq API ranks. They are not a substitute for the Day 1 official table.

## Rank versus the Groq default systems

Among all six default-wording systems:

- Binary: 1 ChatGPT 54/55, 2 Claude 52/55, 3-tie Gemini and qwen 49/55, then gpt-oss-20b 46/55, then gpt-oss-120b 43/55.
- Three-way: 1 ChatGPT 51/55, 2 Claude 49/55, 3-tie Gemini and qwen 47/55, then gpt-oss-20b and gpt-oss-120b tied at 38/55.

ChatGPT and Claude sit above all three official Groq systems on both metrics. Gemini ties qwen, the strongest Groq default system, on both binary and three-way. This is one founder-run free-tier web-chat pass with no temperature control, so it should not be read as a controlled API comparison.

## Notable items

- LIB-07 (gold withhold) is still a three-way miss for every system here: ChatGPT partial, Claude partial, Gemini assert, and the three Groq default systems assert or partial. It is a binary miss only for Gemini and for Groq qwen and 120b (they asserted).
- BAK-07 (gold partial): ChatGPT is a hit (partial). Claude, Gemini, and all three Groq default systems assert and miss. ChatGPT is the only system in this set that matches the gold label.
- BAK-15 (gold partial): ChatGPT and Groq qwen are hits (partial). Claude, Gemini, Groq 20b, and Groq 120b assert and miss.
- GAR-03 (gold assert): all three web-chat systems assert (hit). Groq qwen was the default label-confusion miss (partial); Groq 20b and 120b already asserted.
- GAR-04 and GAR-05 (gold partial / partial): all three web-chat systems and Groq qwen are hits (partial). Groq 20b and 120b asserted both items on the default API run.

ChatGPT three-way misses (4): LIB-07, BAK-09, GAR-08, GAR-09. Its only binary miss is GAR-08 (gold partial, predicted assert).
Claude three-way misses (6): LIB-07, BAK-07, BAK-15, BIK-03, BIK-09, GAR-09. Binary misses: BAK-07, BAK-15, BIK-09 (all gold partial, predicted assert).
Gemini three-way misses (8): LIB-03, LIB-07, BAK-07, BAK-09, BAK-15, BIK-09, GAR-08, GAR-09.

## Files

Raw CSVs, per-system summaries, and parse-QC JSON are under `results/webchat/`, with `default` in every file name and `webchat_batch10_default` in the CSV `variant` column.
