# ClaimStanceBench: default vs permissive prompt

Date: Fri Nov 13, 2026 (America/New_York) for the permissive Groq runs; four-part judging completed Sat Nov 14, 2026 (America/New_York)
Condition: permissive prompt variant, scored separately from the default Day 1 run
Items: 55 frozen (22 partial, 17 assert, 16 withhold); sha256 b700b889ec5e95c455850bad2e9d1f46f17885136f97d0456f594719ff841c43
Systems: groq openai/gpt-oss-120b, openai/gpt-oss-20b, and qwen/qwen3.8-27b
Parameters: temperature 0, max tokens 2048, same as the default run
Calls: 165 successful Groq calls (55 items times 3 systems). All 55 items completed for each system, with no recorded errors and no parse failures.
Prompt: the PERMISSIVE harness wording, which adds "Use only what the card supports. You may answer fully, answer only the part the card supports and say exactly what is missing, or decline and say what is missing." before the same STANCE last-line rule as the default prompt.

Four-part partial pass and strict three-way are now complete for all three permissive systems (judge groq:openai/gpt-oss-120b, all 22 gold partials). Gold-partial label accuracy (parsed STANCE equals partial on the 22 gold partials) is still shown as a judge-free companion figure.

One completion-token count for gpt-oss-120b GAR-07 is left blank in the committed CSV (a repo constraint). Scores do not use token counts.

## Default vs permissive

| System | Prompt | n | Binary acc | Three-way acc | Over-claim | Under-claim | Pred assert / partial / withhold | Gold-partial labels | Partial pass | Strict three-way |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen/qwen3.8-27b | default | 55/55 | 89.1% (49/55) | 85.5% (47/55) | 10.9% | 3.6% | 21 / 19 / 15 | 17/22 | 68.2% (15/22) | 81.8% (45/55) |
| qwen/qwen3.8-27b | permissive | 55/55 | 92.7% (51/55) | 89.1% (49/55) | 10.9% | 0.0% | 21 / 20 / 14 | 18/22 | 81.8% (18/22) | 89.1% (49/55) |
| openai/gpt-oss-20b | default | 55/55 | 83.6% (46/55) | 69.1% (38/55) | 18.2% | 10.9% | 25 / 10 / 19 (1 empty) | 8/22 | 45.5% (10/22) | 70.9% (39/55) |
| openai/gpt-oss-20b | permissive | 55/55 | 90.9% (50/55) | 69.1% (38/55) | 30.9% | 0.0% | 22 / 29 / 4 | 17/22 | 68.2% (15/22) | 65.5% (36/55) |
| openai/gpt-oss-120b | default | 55/55 | 78.2% (43/55) | 69.1% (38/55) | 30.9% | 0.0% | 29 / 18 / 8 | 13/22 | 59.1% (13/22) | 76.4% (42/55) |
| openai/gpt-oss-120b | permissive | 55/55 | 92.7% (51/55) | 78.2% (43/55) | 21.8% | 0.0% | 21 / 27 / 7 | 19/22 | 77.3% (17/22) | 74.5% (41/55) |

Deltas (permissive minus default):

- qwen: binary +2 (49 to 51), three-way +2 (47 to 49). Partial pass +3 (15 to 18), strict three-way +4 (45 to 49). Stance usage is almost unchanged (partial 19 to 20, withhold 15 to 14, assert 21 unchanged). Under-claim goes to 0.
- gpt-oss-20b: binary +4 (46 to 50), three-way unchanged at 38/55. Partial pass +5 (10 to 15), but strict three-way falls (39 to 36) because many gold-withhold items are now labeled partial. Partial labels jump from 10 to 29; withhold falls from 19 to 4; assert 25 to 22. Under-claim goes to 0; over-claim rises (18.2% to 30.9%).
- gpt-oss-120b: binary +8 (43 to 51), three-way +5 (38 to 43). Partial pass +4 (13 to 17), while strict three-way falls by one item (42 to 41) for the same withhold-to-partial reason. Assert falls from 29 to 21; partial rises from 18 to 27; withhold 8 to 7. Over-claim falls (30.9% to 21.8%). Gold-partial labels rise from 13/22 to 19/22.

Partial usage increased clearly for 20b and 120b. Combined partial plus withhold usage rose for 120b (26 to 34) and slightly for 20b (29 plus one empty, to 33), and stayed flat for qwen (34 to 34). Withhold usage itself did not increase; 20b in particular moved withhold answers to partial.

## Rank changes

Default official ranks (complete Groq set):

- Binary: 1 qwen (89.1%), 2 gpt-oss-20b (83.6%), 3 gpt-oss-120b (78.2%).
- Three-way: 1 qwen (85.5%), 2-tie gpt-oss-20b and gpt-oss-120b (both 69.1%, 38/55).
- Partial pass: 1 qwen (68.2%, 15/22), 2 gpt-oss-120b (59.1%, 13/22), 3 gpt-oss-20b (45.5%, 10/22).
- Strict three-way: 1 qwen (81.8%, 45/55), 2 gpt-oss-120b (76.4%, 42/55), 3 gpt-oss-20b (70.9%, 39/55).

Permissive ranks:

- Binary: 1-tie qwen and gpt-oss-120b (both 92.7%, 51/55); gpt-oss-20b is third by one item (90.9%, 50/55).
- Three-way: 1 qwen (89.1%, 49/55), 2 gpt-oss-120b (78.2%, 43/55), 3 gpt-oss-20b (69.1%, 38/55).
- Partial pass: 1 qwen (81.8%, 18/22), 2 gpt-oss-120b (77.3%, 17/22), 3 gpt-oss-20b (68.2%, 15/22). The order matches default, and all three rates rise.
- Strict three-way: 1 qwen (89.1%, 49/55), 2 gpt-oss-120b (74.5%, 41/55), 3 gpt-oss-20b (65.5%, 36/55). qwen stays first and rises; 120b and 20b each drop versus their default strict scores.

What changed:

- qwen remains first on three-way, partial pass, and strict three-way, and is tied for first on binary.
- gpt-oss-120b is the most prompt-sensitive system here on the label metrics. It moves from last on default binary to a first-place tie, and it breaks the default three-way tie to take sole second. Its four-part partial pass also rises (13/22 to 17/22), but strict three-way falls by one item.
- gpt-oss-20b improves on binary (to 50/55) and on partial pass (10/22 to 15/22) but stays at 38/55 on three-way and drops on strict three-way (39/55 to 36/55), so it remains third under the permissive rankings.

The default 20b-vs-120b binary order (20b ahead) reverses under the permissive prompt (120b ahead, tied with qwen). The default three-way tie is also broken in 120b's favor.

## Notable item flips

qwen, 5 flips:

- GAR-03 (gold assert): default partial, permissive assert. This was the only default gold-assert / predicted-partial case, a label-confusion miss on a complete answer. It is gone under the permissive prompt.
- LIB-07 (gold withhold): default assert, permissive partial. Still a three-way miss, but no longer an over-claim by assert. Binary becomes a hit.
- BAK-09 and BIK-05 (gold partial): default withhold or assert, permissive partial (both now three-way hits).
- GAR-08 (gold partial): default partial, permissive assert. The one qwen regression.

gpt-oss-20b, 23 flips, mostly withhold to partial. Gold partials that improve include LIB-04, LIB-11, LIB-13, BAK-09, BAK-15, BIK-07, GAR-04, GAR-05, and GAR-08. BAK-15, GAR-04, and GAR-05 all move from assert to partial. BIK-05 (empty on default) becomes assert and is still a miss. Many gold-withhold items move from a correct withhold to partial, which is why three-way accuracy does not rise with the binary gain.

gpt-oss-120b, 14 flips. Improvements include LIB-03, LIB-06, BAK-15, BIK-05, GAR-04, and GAR-05 (all gold partial, default assert, permissive partial), plus BAK-13, BIK-12, and GAR-13 (gold withhold, now correctly withhold). GAR-04/GAR-05 is a both-items hit for 120b on the permissive prompt; on default it was neither (both asserted).

Shared highlights:

- GAR-03 label confusion is resolved for qwen. 20b and 120b were already assert on default and stay assert.
- LIB-07 remains a three-way miss for all three Groq systems (qwen partial, 20b partial, 120b assert). It is no longer a unanimous assert.
- BAK-15 (gold partial): qwen was already partial; 20b and 120b move from assert to partial, so all three Groq systems match the gold label under the permissive prompt.
- GAR-04 and GAR-05 (gold partial / partial pair): qwen already had both; 20b and 120b move from neither (both asserted) to both.

BAK-07 (gold partial) is still asserted by all three systems under both prompts.
