"""Load benchmark items and enforce the gold-label freeze gate.

Item format (one JSON object per line in items/items.jsonl):
  id            str   unique item id
  card          str   short free-prose fact card
  question      str   the question asked about the card
  gold_stance   str   one of: assert, partial, withhold
  gold_reason   str   one-line reason for the gold label
  missing_facts list  facts the card does not support (empty for assert)
  pattern       str   item pattern tag (optional)
  pair_id       str   id of the paired item with/without the deciding fact (optional)
"""
import hashlib
import json
from pathlib import Path

STANCES = ("assert", "partial", "withhold")
REQUIRED = ("id", "card", "question", "gold_stance", "gold_reason", "missing_facts")


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_items(path):
    items, seen = [], set()
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        obj = json.loads(line)
        missing = [k for k in REQUIRED if k not in obj]
        if missing:
            raise ValueError(f"line {n}: missing fields {missing}")
        if obj["gold_stance"] not in STANCES:
            raise ValueError(f"line {n}: bad gold_stance {obj['gold_stance']!r}")
        if obj["id"] in seen:
            raise ValueError(f"line {n}: duplicate id {obj['id']}")
        seen.add(obj["id"])
        items.append(obj)
    return items


def check_frozen(items_path, freeze_path):
    """Return True only if the freeze file exists and matches the items file hash.

    The freeze file is written only after the founder approves the gold labels.
    Format: first line is the sha256 of items.jsonl at freeze time.
    """
    fp = Path(freeze_path)
    if not fp.exists():
        return False
    want = fp.read_text(encoding="utf-8").split()[0].strip()
    return want == sha256_file(items_path)
