# ClaimStanceBench run summary

Date: 2026-11-14
Variant: default
Temperature: 0.0
Max tokens: 2048 for all runs, with one gpt-oss-20b retry at 8192 on BIK-05 (still empty)
Items: 55 (frozen sha256 b700b889ec5e95c455850bad2e9d1f46f17885136f97d0456f594719ff841c43)
Prompt: default (permissive variant not run in this pass)

## Systems
- groq:openai/gpt-oss-120b
- groq:openai/gpt-oss-20b
- groq:qwen/qwen3.8-27b
- openrouter:baidu/ernie-5.5-flash-preview:free

## Notes
- ERNIE default is 55/55. Four-part partial-pass judge annotations (judge groq:openai/gpt-oss-120b) are complete for all four default systems on all 22 gold partials, finished Sat Nov 14 2026 after the Groq daily reset. gpt-oss-20b BIK-05 is unscorable (empty output) and counts as a non-pass in the 22-item denominator.

## Scores

| System | n | parse ok | binary acc (answer vs abstain) | three-way stance acc | over-claim | under-claim | partial pass | strict three-way |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| openai/gpt-oss-120b | 55/55 | 100.0% | 78.2% (43/55) | 69.1% (38/55) | 30.9% | 0.0% | 59.1% | 76.4% |
| openai/gpt-oss-20b | 55/55 | 98.2% | 83.6% (46/55) | 69.1% (38/55) | 18.2% | 10.9% | 45.5% | 70.9% |
| qwen/qwen3.8-27b | 55/55 | 100.0% | 89.1% (49/55) | 85.5% (47/55) | 10.9% | 3.6% | 68.2% | 81.8% |
| baidu/ernie-5.5-flash-preview:free | 55/55 | 100.0% | 96.4% (53/55) | 89.1% (49/55) | 5.5% | 5.5% | 81.8% | 87.3% |

Binary scoring maps assert to answer and maps partial and withhold to abstain.
Three-way stance accuracy is a match on the parsed STANCE label.
Partial pass and strict three-way use the automated judge when that step has been run.
Strict three-way requires a four-part pass on gold partials, a matching stance on gold withhold items,
and a matching unhedged assert on gold asserts.

## Rankings

Binary order: baidu/ernie-5.5-flash-preview:free, qwen/qwen3.8-27b, openai/gpt-oss-20b, openai/gpt-oss-120b
Three-way order: baidu/ernie-5.5-flash-preview:free, qwen/qwen3.8-27b, openai/gpt-oss-120b, openai/gpt-oss-20b
Three-way ties: openai/gpt-oss-120b and openai/gpt-oss-20b
Rankings changed between binary and three-way scoring.

