"""Offline tests for label scoring. No model calls."""
from harness.score import binary_label, claim_error, format_pct, parse_judge_json, summarize, rankings_changed


def test_binary_and_claim_error():
    assert binary_label("assert") == "answer"
    assert binary_label("partial") == "abstain"
    assert binary_label("withhold") == "abstain"
    assert binary_label("") is None
    assert claim_error("withhold", "assert") == "over_claim"
    assert claim_error("partial", "withhold") == "under_claim"
    assert claim_error("assert", "assert") == ""


def test_summarize_label_metrics():
    rows = [
        {"provider": "groq", "model": "m1", "variant": "default", "gold_stance": "assert",
         "pred_stance": "assert", "parse_ok": "True", "error": "", "item_id": "A"},
        {"provider": "groq", "model": "m1", "variant": "default", "gold_stance": "partial",
         "pred_stance": "assert", "parse_ok": "True", "error": "", "item_id": "B"},
        {"provider": "groq", "model": "m1", "variant": "default", "gold_stance": "withhold",
         "pred_stance": "withhold", "parse_ok": "True", "error": "", "item_id": "C"},
        {"provider": "groq", "model": "m2", "variant": "default", "gold_stance": "assert",
         "pred_stance": "partial", "parse_ok": "True", "error": "", "item_id": "A"},
        {"provider": "groq", "model": "m2", "variant": "default", "gold_stance": "partial",
         "pred_stance": "partial", "parse_ok": "True", "error": "", "item_id": "B"},
        {"provider": "groq", "model": "m2", "variant": "default", "gold_stance": "withhold",
         "pred_stance": "withhold", "parse_ok": "True", "error": "", "item_id": "C"},
    ]
    sums = {s["model"]: s for s in summarize(rows, {})}
    assert sums["m1"]["binary_correct"] == 2
    assert sums["m1"]["three_way_correct"] == 2
    assert sums["m1"]["over_claim"] == 1
    assert sums["m2"]["binary_correct"] == 2  # assert->partial is a binary miss; other two abstain
    assert sums["m2"]["three_way_correct"] == 2
    changed, complete, bin_order, three_order, *rest = rankings_changed(list(sums.values()), n_expected=3)
    # m1 binary 2/3, m2 binary 2/3 (tie, ordered by model name)
    assert changed is False or bin_order != three_order or bin_order == three_order
    # both 2/3 on both metrics, so rankings should not change
    assert changed is False


def test_parse_judge_json():
    obj = parse_judge_json('prefix\n{"actual_stance": "withhold", "partial_pass": null}\n')
    assert obj["actual_stance"] == "withhold"
    assert obj["partial_pass"] is None


def test_format_pct_avoids_double_rounding():
    # 41/55 = 0.7454...; pre-rounding to 4 decimals (0.7455) would print 74.6%.
    assert format_pct(41, 55) == "74.5%"
    assert f"{round(41 / 55, 4):.1%}" == "74.6%"
    assert format_pct(42, 55) == "76.4%"
    assert format_pct(0, 55) == "0.0%"
    assert format_pct(1, 0) == "-"
    assert format_pct(None, 55) == "-"
