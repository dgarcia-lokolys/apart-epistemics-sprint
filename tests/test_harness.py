"""Offline tests. No model calls. Fixtures are synthetic placeholders, not benchmark items."""
import json
import tempfile
from pathlib import Path

from harness.items import check_frozen, load_items, sha256_file
from harness.parse import parse_stance
from harness.prompts import build_messages

FIXTURE = {"id": "fixture-1", "card": "PLACEHOLDER CARD TEXT.", "question": "PLACEHOLDER QUESTION?",
           "gold_stance": "assert", "gold_reason": "placeholder", "missing_facts": []}


def test_parse_basic():
    assert parse_stance("Yes.\nSTANCE: assert")[0] == "assert"
    assert parse_stance("stance - Partial")[0] == "partial"
    assert parse_stance("STANCE: **withhold**")[0] == "withhold"


def test_parse_last_label_wins():
    s, _ = parse_stance("I could say STANCE: assert but\nSTANCE: partial")
    assert s == "partial"


def test_parse_missing():
    assert parse_stance("no label here")[0] is None
    assert parse_stance("")[0] is None


def test_load_and_freeze_gate():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "items.jsonl"
        p.write_text(json.dumps(FIXTURE) + "\n")
        items = load_items(p)
        assert items[0]["id"] == "fixture-1"
        fz = Path(d) / "FROZEN"
        assert not check_frozen(p, fz)
        fz.write_text(sha256_file(p) + "\n")
        assert check_frozen(p, fz)
        p.write_text(json.dumps({**FIXTURE, "gold_stance": "partial"}) + "\n")
        assert not check_frozen(p, fz)


def test_prompt_build():
    m = build_messages(FIXTURE)
    assert "PLACEHOLDER CARD TEXT." in m[1]["content"]
    assert m[1]["content"].rstrip().endswith("STANCE: withhold")
