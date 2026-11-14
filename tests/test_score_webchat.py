"""Offline tests for the web-chat packet and scorer. No model calls."""
from pathlib import Path

from harness.items import load_items
from harness.parse import parse_stance
from harness.webchat_packet import (
    SEED,
    VARIANT,
    VARIANT_PERMISSIVE,
    PERMISSIVE_PERMISSION,
    assign_batches,
    batch_preamble,
    build_packet_markdown,
    format_batch,
    leak_check,
    pair_groups,
    reply_template,
)
from harness.score_webchat import parse_template, rows_from_template, variant_label
from harness.score import summarize
from harness.prompts import SYSTEM, PERMISSIVE, DEFAULT

ROOT = Path(__file__).resolve().parent.parent


def test_batches_separate_pairs_and_hide_gold():
    items = load_items(ROOT / "items" / "items.jsonl")
    batches, conflicts = assign_batches(items, seed=SEED)
    assert [len(b) for b in batches] == [10, 10, 10, 10, 10, 5]
    assert conflicts == []
    loc = {item_id: i for i, batch in enumerate(batches) for item_id in batch}
    for a, b in pair_groups(items)[0]:
        assert loc[a] != loc[b]
    by_id = {it["id"]: it for it in items}
    text = format_batch([by_id[i] for i in batches[0]])
    assert leak_check(text) == []
    assert "gold" not in text.lower()
    assert "missing_facts" not in text
    assert "pair_id" not in text
    pre = batch_preamble(10)
    assert pre.startswith(SYSTEM + "\n")
    assert "Answer the question. Then, on the last line, write exactly one of:" in pre
    assert PERMISSIVE_PERMISSION not in pre
    assert PERMISSIVE_PERMISSION in PERMISSIVE
    assert "Answer the question. Then, on the last line, write exactly one of:" in DEFAULT


def test_parse_template_last_block_wins():
    text = (
        "# ClaimStanceBench web-chat replies: ChatGPT\n\n"
        "Model name shown: test-model\n\n"
        "Date (America/New_York): 2026-11-13\n\n"
        "## Batch 1 (10 items)\n\n"
        "### LIB-01\n"
        "This is the prompt card pasted by mistake.\n"
        "STANCE: withhold\n\n"
        "### LIB-01\n"
        "The real answer.\n"
        "STANCE: assert\n"
    )
    parsed = parse_template(text, known_ids={"LIB-01"})
    assert parsed["model_name"] == "test-model"
    stance, answer = parse_stance(parsed["items"]["LIB-01"])
    assert stance == "assert"
    assert "real answer" in answer


def test_fake_template_from_groq_qwen_matches_official_scores():
    """A filled template built from the official Groq qwen outputs should match those scores."""
    import csv

    items = load_items(ROOT / "items" / "items.jsonl")
    items_by_id = {it["id"]: it for it in items}
    raw_path = ROOT / "results" / "raw-20261113-groq-default.csv"
    by_item = {}
    for row in csv.DictReader(raw_path.open()):
        if row["model"] != "qwen/qwen3.8-27b":
            continue
        by_item[row["item_id"]] = row
    assert len(by_item) == 55

    batches, _ = assign_batches(items, seed=SEED)
    lines = [reply_template("ChatGPT")]
    # Fill the model/date lines in a copy
    header = (
        "# ClaimStanceBench web-chat replies: ChatGPT\n\n"
        "Model name shown: groq-qwen-fake\n\n"
        "Date (America/New_York): 2026-11-13\n\n"
        "Paste only the model's full reply for each batch, including any `continue` text. "
        "Do not paste the batch prompt.\n"
    )
    parts = [header]
    for i, ids in enumerate(batches, 1):
        n = len(ids)
        parts.append(f"## Batch {i} ({n} items)\n")
        for item_id in ids:
            raw = by_item[item_id]["raw"] or by_item[item_id].get("answer") or ""
            parts.append(f"### {item_id}\n{raw.strip()}\n")
        parts.append("")
    text = "\n".join(parts)
    parsed = parse_template(text, known_ids=set(items_by_id))
    assert len(parsed["items"]) == 55
    rows = rows_from_template(parsed, items_by_id, "chatgpt", "", "webchat-fake-qwen")
    sums = summarize(rows, items_by_id)
    assert len(sums) == 1
    s = sums[0]
    assert s["n_success"] == 55
    assert s["binary_correct"] == 49
    assert s["three_way_correct"] == 47
    assert s["variant"] == VARIANT
    assert s["model"] == "groq-qwen-fake"


def test_permissive_batches_use_exact_wording_and_same_order():
    items = load_items(ROOT / "items" / "items.jsonl")
    batches, conflicts = assign_batches(items, seed=SEED)
    assert conflicts == []
    by_id = {it["id"]: it for it in items}
    default_text = format_batch([by_id[i] for i in batches[0]], variant="default")
    perm_text = format_batch([by_id[i] for i in batches[0]], variant="permissive")
    assert leak_check(perm_text) == []
    assert PERMISSIVE_PERMISSION not in default_text
    assert PERMISSIVE_PERMISSION in perm_text
    assert perm_text.startswith(SYSTEM + "\n")
    # same items, same order; only the preamble permission line differs
    assert default_text.split("### ")[1:] == perm_text.split("### ")[1:]
    packet = build_packet_markdown(items, batches, conflicts)
    assert leak_check(packet) == []
    assert "## Optional: permissive prompt" in packet
    assert packet.count("```") == 24  # 6 default + 6 permissive fences
    assert PERMISSIVE_PERMISSION in packet
    tpl = reply_template("ChatGPT", variant="permissive")
    assert "(permissive, optional)" in tpl


def test_score_variant_label_permissive():
    assert variant_label("default") == VARIANT
    assert variant_label("permissive") == VARIANT_PERMISSIVE
    items = load_items(ROOT / "items" / "items.jsonl")
    items_by_id = {it["id"]: it for it in items}
    text = (
        "# ClaimStanceBench web-chat replies: ChatGPT (permissive, optional)\n\n"
        "Model name shown: test-perm\n\n"
        "Date (America/New_York): 2026-11-13\n\n"
        "## Batch 1 (10 items)\n\n"
        "### LIB-01\n"
        "A full answer.\n"
        "STANCE: assert\n"
    )
    parsed = parse_template(text, known_ids=set(items_by_id))
    rows = rows_from_template(
        parsed, items_by_id, "chatgpt", "", "webchat-fake-perm",
        variant=VARIANT_PERMISSIVE,
    )
    assert all(r["variant"] == VARIANT_PERMISSIVE for r in rows)
    lib = next(r for r in rows if r["item_id"] == "LIB-01")
    assert lib["pred_stance"] == "assert"
    missing = [r for r in rows if r["item_id"] != "LIB-01"]
    assert all(r["error"] == "missing reply for this item" for r in missing)


def test_parse_bold_and_bare_headings_and_qc():
    """Founder pastes may use ### **ID** or a bare ID line; those are headings, not guesses."""
    from harness.score_webchat import template_qc, item_id_order

    items = load_items(ROOT / "items" / "items.jsonl")
    known = {it["id"] for it in items}
    official = ["GAR-08", "BAK-15", "BAK-08"]
    text = (
        "# ClaimStanceBench web-chat replies: Gemini\n\n"
        "Model name shown: 3.5 Flash-Lite Medium\n\n"
        "Date (America/New_York):\n\n"
        "## Batch 1 (10 items)\n\n"
        "GAR-08\n"
        "An answer about the picnic.\n"
        "STANCE: assert\n\n"
        "### **BAK-15**\n"
        "Lemon bars only.\n"
        "STANCE: partial\n\n"
        "### BAK-08\n"
        "The total is $25.\n"
        "STANCE: assert\n"
    )
    parsed = parse_template(text, known_ids=known)
    assert set(parsed["items"]) == {"GAR-08", "BAK-15", "BAK-08"}
    assert parsed["model_name"] == "3.5 Flash-Lite Medium"
    assert parsed["date"] == ""
    stance, answer = parse_stance(parsed["items"]["BAK-15"])
    assert stance == "partial"
    assert "Lemon bars" in answer
    assert item_id_order(text, known_ids=known) == official
    qc = template_qc(text, known, official)
    assert qc["missing"] == []
    assert qc["unparseable"] == []
    assert qc["order_ok"] is True
    # If an official item is absent, report it; do not invent a stance.
    qc2 = template_qc(text, known, official + ["GAR-01"])
    assert qc2["missing"] == ["GAR-01"]
    assert "GAR-01" not in parsed["items"]


def test_default_variant_label_includes_default():
    assert variant_label("default") == "webchat_batch10_default"
    assert "default" in variant_label("default")
    assert "permissive" in variant_label("permissive")
