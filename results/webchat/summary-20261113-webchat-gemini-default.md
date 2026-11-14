# ClaimStanceBench run summary

Date: 2026-11-13
Variant: webchat_batch10_default
Temperature: n/a (consumer web chat)
Max tokens: n/a (consumer web chat)
Items: 55 (frozen sha256 b700b889ec5e95c455850bad2e9d1f46f17885136f97d0456f594719ff841c43)
Prompt: default (permissive variant not run in this pass)

## Systems
- webchat-gemini:3.5 Flash-Lite Medium

## Notes
- consumer web chat, batched x10
- Founder-run free-tier web chat, default packet wording, batched x10. No temperature control. Prompt variant: default.

## Scores

| System | n | parse ok | binary acc (answer vs abstain) | three-way stance acc | over-claim | under-claim | partial pass | strict three-way |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 3.5 Flash-Lite Medium | 55/55 | 100.0% | 89.1% (49/55) | 85.5% (47/55) | 12.7% | 1.8% | - | - |

Binary scoring maps assert to answer and maps partial and withhold to abstain.
Three-way stance accuracy is a match on the parsed STANCE label.
Partial pass and strict three-way use the automated judge when that step has been run.
Strict three-way requires a four-part pass on gold partials, a matching stance on gold withhold items,
and a matching unhedged assert on gold asserts.

