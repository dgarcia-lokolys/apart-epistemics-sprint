# ClaimStanceBench item changelog

## 2026-11-13, 12:40 PM (America/New_York)

Post-run gold-label correction, made before founder blind grading. No system outputs were re-run.

- GAR-05 relabeled from withhold to partial. The question asks "when" without asking for a date, so "every spring" partly answers it.
- New gold_reason: "Supported: the swap happens every spring (answers 'when' at the level asked); missing: where it is held and whether seedlings may be sold for cash."
- New missing_facts: where the plant swap is held; whether seedlings may be sold for cash at the swap.
- Set counts are now 22 partial, 17 assert, and 16 withhold (still 55 items).
- Previous freeze: sha256 1eb761483d5f911ec45e2d2799bc42ad3c107933e9f9dc93f0fc0daf63523252 (commit e2abc2b). New freeze: sha256 b700b889ec5e95c455850bad2e9d1f46f17885136f97d0456f594719ff841c43.

The raw model outputs in `results/` are unchanged. After this freeze, those runs were rescored against the corrected gold, and the GAR-05 judge annotations were regenerated under the four-part partial rule.

