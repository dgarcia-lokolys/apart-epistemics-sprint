"""Score a filled web-chat reply template against frozen gold labels.

No model calls. Parses item blocks with the same stance parser as the API
runs, then uses the same binary, three-way, and judge-hook scoring.

Usage:
  python -m harness.score_webchat --template path/to/reply-template-chatgpt.md --service chatgpt
  python -m harness.score_webchat --template path/to/reply-template-chatgpt-permissive.md --service chatgpt --variant permissive
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import sys
from pathlib import Path

from harness.items import check_frozen, load_items
from harness.parse import parse_stance
from harness.score import rankings_changed, summarize, write_summary_md
from harness.webchat_packet import (
    CONDITION, CONDITION_PERMISSIVE, VARIANT, VARIANT_PERMISSIVE,
)
from harness.run import FIELDS

ROOT = Path(__file__).resolve().parent.parent

ITEM_HEAD = re.compile(
    r"^#{0,3}\s*\**\s*((?:LIB|BAK|BIK|GAR)-\d+)\s*\**\s*$",
    re.MULTILINE,
)
BATCH_HEAD = re.compile(r"^##\s*Batch\s+(\d+)\b.*$", re.MULTILINE | re.IGNORECASE)
MODEL_LINE = re.compile(r"^Model name shown:[ \t]*([^\n]*)$", re.MULTILINE | re.IGNORECASE)
DATE_LINE = re.compile(r"^Date(?:[ \t]*\(America/New_York\))?:[ \t]*([^\n]*)$", re.MULTILINE | re.IGNORECASE)

SERVICE_PROVIDERS = {
    "chatgpt": "webchat-chatgpt",
    "gemini": "webchat-gemini",
    "claude": "webchat-claude",
}


def variant_label(cli_variant):
    if cli_variant == "permissive":
        return VARIANT_PERMISSIVE
    if cli_variant == "default":
        return VARIANT
    raise ValueError(f"unknown variant: {cli_variant}")


def condition_label(cli_variant):
    if cli_variant == "permissive":
        return CONDITION_PERMISSIVE
    if cli_variant == "default":
        return CONDITION
    raise ValueError(f"unknown variant: {cli_variant}")


def parse_header_fields(text):
    model = ""
    date = ""
    m = MODEL_LINE.search(text)
    if m:
        model = (m.group(1) or "").strip()
    d = DATE_LINE.search(text)
    if d:
        date = (d.group(1) or "").strip()
    return model, date


def split_batches(text):
    """Return a list of (batch_number, body) in file order."""
    matches = list(BATCH_HEAD.finditer(text))
    if not matches:
        return [(None, text)]
    out = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[m.end():end]
        out.append((int(m.group(1)), body))
    return out


def split_item_blocks(text):
    """Map item_id -> reply body. If an id appears more than once, the last block wins."""
    matches = list(ITEM_HEAD.finditer(text))
    blocks = {}
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[m.end():end].strip()
        blocks[m.group(1)] = body
    return blocks


def parse_template(text, known_ids=None):
    """Parse a filled reply template into header fields and item replies."""
    model, date = parse_header_fields(text)
    # Last occurrence of each id across the whole file (reply should follow any accidental prompt paste).
    blocks = split_item_blocks(text)
    if known_ids is not None:
        blocks = {k: v for k, v in blocks.items() if k in known_ids}
    return {"model_name": model, "date": date, "items": blocks}


def item_id_order(text, known_ids=None):
    """First-occurrence item id order from heading lines (not last-wins)."""
    ids = []
    seen = set()
    for m in ITEM_HEAD.finditer(text):
        item_id = m.group(1)
        if known_ids is not None and item_id not in known_ids:
            continue
        if item_id not in seen:
            ids.append(item_id)
            seen.add(item_id)
    return ids


def template_qc(text, known_ids, official_order):
    """Report missing, unparseable, or out-of-order items. Does not invent answers."""
    parsed = parse_template(text, known_ids=known_ids)
    appearing = item_id_order(text, known_ids=known_ids)
    missing = [i for i in official_order if i not in parsed["items"]]
    extra = [i for i in appearing if i not in known_ids]
    unparseable = []
    for item_id, body in parsed["items"].items():
        stance, _answer = parse_stance(body)
        if not stance:
            unparseable.append(item_id)
    # Also count headings whose body is empty
    empty = [i for i, body in parsed["items"].items() if not (body or "").strip()]
    order_ok = appearing == official_order
    diverge = None
    if not order_ok:
        diverge_at = None
        for k, (got, want) in enumerate(zip(appearing, official_order)):
            if got != want:
                diverge_at = k
                diverge = {"index": k, "got": got, "expected": official_order[k]}
                break
        if diverge is None and len(appearing) != len(official_order):
            diverge = {
                "index": min(len(appearing), len(official_order)),
                "got": appearing[len(official_order):] if len(appearing) > len(official_order) else None,
                "expected": official_order[len(appearing):] if len(official_order) > len(appearing) else None,
            }
    return {
        "model_name": parsed["model_name"],
        "date": parsed["date"],
        "n_found": len(parsed["items"]),
        "n_expected": len(known_ids),
        "missing": missing,
        "extra": extra,
        "unparseable": unparseable,
        "empty_body": empty,
        "order_ok": order_ok,
        "order_diverge": diverge,
        "first_occurrence_ids": appearing,
    }


def rows_from_template(parsed, items_by_id, service, model_name, run_id, variant=VARIANT):
    provider = SERVICE_PROVIDERS.get(service, f"webchat-{service}")
    model = model_name or parsed.get("model_name") or service
    rows = []
    for item_id, item in items_by_id.items():
        raw = parsed["items"].get(item_id, "")
        row = {
            "run_id": run_id,
            "item_id": item_id,
            "provider": provider,
            "model": model,
            "variant": variant,
            "gold_stance": item["gold_stance"],
            "pred_stance": "",
            "parse_ok": "False",
            "answer": "",
            "raw": raw,
            "finish_reason": "webchat",
            "prompt_tokens": "",
            "completion_tokens": "",
            "error": "",
            "temperature": "",
            "max_tokens": "",
        }
        if not (raw or "").strip():
            row["error"] = "missing reply for this item"
            rows.append(row)
            continue
        stance, answer = parse_stance(raw)
        if stance:
            row["pred_stance"] = stance
            row["parse_ok"] = "True"
            row["answer"] = answer
        else:
            row["pred_stance"] = ""
            row["parse_ok"] = "False"
            row["answer"] = answer or raw.strip()
        rows.append(row)
    return rows


def write_raw_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True, help="filled reply template markdown")
    ap.add_argument("--service", required=True, choices=sorted(SERVICE_PROVIDERS),
                    help="chatgpt, gemini, or claude")
    ap.add_argument("--model", default="", help="override the model name shown in the template")
    ap.add_argument("--items", default=str(ROOT / "items" / "items.jsonl"))
    ap.add_argument("--freeze", default=str(ROOT / "items" / "FROZEN"))
    ap.add_argument("--out-csv", default="", dest="out_csv")
    ap.add_argument("--out-json", default="", dest="out_json")
    ap.add_argument("--out-md", default="", dest="out_md")
    ap.add_argument("--judge-out", default="", dest="judge_out",
                    help="optional existing judge annotations to merge (no new API calls)")
    ap.add_argument("--variant", default="default", choices=["default", "permissive"],
                    help="default or permissive (matches the template set)")
    ap.add_argument("--run-id", default="", dest="run_id")
    ap.add_argument("--notes", action="append", default=[])
    ap.add_argument("--qc-out", default="", dest="qc_out",
                    help="optional path for a parse-QC JSON report")
    a = ap.parse_args(argv)

    if not check_frozen(a.items, a.freeze):
        sys.exit("REFUSED: gold labels are not frozen (items/FROZEN missing or hash mismatch).")
    items = load_items(a.items)
    items_by_id = {it["id"]: it for it in items}
    text = Path(a.template).read_text(encoding="utf-8")
    from harness.webchat_packet import assign_batches, SEED
    official_order = [i for b in assign_batches(items, seed=SEED)[0] for i in b]
    qc = template_qc(text, set(items_by_id), official_order)
    parsed = parse_template(text, known_ids=set(items_by_id))
    variant = variant_label(a.variant)
    condition = condition_label(a.variant)
    run_id = a.run_id or f"webchat-{a.service}-{a.variant}-{dt.date.today().isoformat()}"
    rows = rows_from_template(parsed, items_by_id, a.service, a.model, run_id, variant=variant)

    out_csv = Path(a.out_csv or (ROOT / "results" / f"raw-{run_id}.csv"))
    write_raw_csv(out_csv, rows)

    # Merge judge annotations if a file already exists; this entry point does not call a judge.
    judge_path = Path(a.judge_out) if a.judge_out else None
    if judge_path and judge_path.exists() and judge_path.stat().st_size:
        anns = {}
        with judge_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if (row.get("error") or "").strip():
                    continue
                anns[(row["provider"], row["model"], row["item_id"], row.get("variant") or "default")] = row
        for r in rows:
            key = (r["provider"], r["model"], r["item_id"], r.get("variant") or "default")
            if key in anns:
                arow = anns[key]
                for k in ("actual_stance", "p1_answers_supported", "p2_names_missing_fact",
                          "p3_no_guess", "p4_no_stretch", "partial_pass", "assert_hedge",
                          "named_facts"):
                    r[k] = arow.get(k, "")

    summaries = summarize(rows, items_by_id)
    frozen_hash = Path(a.freeze).read_text(encoding="utf-8").split()[0].strip()
    meta = {
        "date": parsed.get("date") or dt.date.today().isoformat(),
        "timezone": "America/New_York",
        "n_items": len(items),
        "frozen_hash": frozen_hash,
        "temperature": "n/a (consumer web chat)",
        "max_tokens": "n/a (consumer web chat)",
        "variant": variant,
        "systems": [f"{s['provider']}:{s['model']}" for s in summaries],
        "notes": [condition] + list(a.notes or []),
        "raw_files": [str(out_csv)],
        "judge_file": str(judge_path) if judge_path and judge_path.exists() else "",
        "judge_model": "",
        "condition": condition,
        "service": a.service,
        "template": str(a.template),
        "prompt_variant": a.variant,
        "parse_qc": {
            "missing": qc["missing"],
            "extra": qc["extra"],
            "unparseable": qc["unparseable"],
            "empty_body": qc["empty_body"],
            "order_ok": qc["order_ok"],
            "order_diverge": qc["order_diverge"],
            "model_name": qc["model_name"],
            "date": qc["date"],
            "n_found": qc["n_found"],
            "n_expected": qc["n_expected"],
        },
    }
    rank_info = rankings_changed(summaries, n_expected=len(items))
    if rank_info[0] is not None:
        meta["rankings_changed"] = rank_info[0]
        meta["binary_order"] = rank_info[2]
        meta["three_way_order"] = rank_info[3]
    else:
        meta["rankings_changed"] = None

    out_json = Path(a.out_json or (ROOT / "results" / f"summary-{run_id}.json"))
    out_md = Path(a.out_md or (ROOT / "results" / f"summary-{run_id}.md"))
    out_json.write_text(json.dumps({"meta": meta, "systems": summaries}, indent=2) + "\n", encoding="utf-8")
    write_summary_md(out_md, meta, summaries, rank_info)
    print(f"wrote {out_csv}")
    print(f"wrote {out_json}")
    print(f"wrote {out_md}")
    for s in summaries:
        print(f"{s['provider']}:{s['model']} n={s['n_success']}/{s['n_rows']} "
              f"bin={s['binary_accuracy']} three={s['three_way_accuracy']} "
              f"partial_pass={s['partial_pass_rate']}")
    n_missing = sum(1 for r in rows if (r.get("error") or "").startswith("missing"))
    n_parse_fail = sum(1 for r in rows if not (r.get("error") or "").strip() and r.get("parse_ok") != "True")
    if n_missing or n_parse_fail:
        print(f"missing items: {n_missing}; unparsed stance on successful items: {n_parse_fail}")
    print(
        f"parse QC: found {qc['n_found']}/{qc['n_expected']}; "
        f"missing={qc['missing'] or '[]'}; unparseable={qc['unparseable'] or '[]'}; "
        f"order_ok={qc['order_ok']}; date={qc['date']!r}; model={qc['model_name']!r}"
    )
    if a.qc_out:
        qc_path = Path(a.qc_out)
        qc_path.parent.mkdir(parents=True, exist_ok=True)
        qc_path.write_text(json.dumps(qc, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {qc_path}")


if __name__ == "__main__":
    main()
