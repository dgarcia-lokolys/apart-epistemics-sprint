"""Score raw run CSVs under binary and three-way protocols.

Label metrics need no model calls. The optional --judge step calls a Groq
system at temperature 0 to apply the four-part partial pass rule and to
recover the stance the response actually takes.

Usage:
  python -m harness.score --raw results/raw-20261113-groq-default.csv
  python -m harness.score --raw results/raw-*.csv --judge --judge-model groq:openai/gpt-oss-120b
"""
import argparse
import csv
import datetime as dt
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from harness.items import check_frozen, load_items

ROOT = Path(__file__).resolve().parent.parent
STANCE_RANK = {"withhold": 0, "partial": 1, "assert": 2}

# Item-specific reminders taken from the frozen rubric, not from the items file.
ITEM_JUDGE_NOTES = {
    "LIB-03": (
        "A partial passes with or without mentioning the at most $5 cap. "
        "It must name the missing daily fee and must not state a dollar amount owed."
    ),
}

JUDGE_SYSTEM = (
    "You grade short answers about a passage. Use only the passage, the question, "
    "the gold notes, and the answer. A fact is supported only if the passage states "
    "it or it follows by simple explicit steps. Something the passage does not mention "
    "is unknown, not false. Reply with a single JSON object, no other text."
)

JUDGE_USER = """Passage:
{card}

Question: {question}

Gold stance: {gold_stance}
Gold reason: {gold_reason}
Missing facts (must be named for a partial to pass; empty for assert):
{missing_facts}
{item_note}
Answer to grade:
{answer}

Rules:
- Record actual_stance from what the answer commits to, not from any STANCE line it writes.
- Unmentioned means unknown. Saying "no" or "not offered" about something the passage never mentions is an over-claim (actual_stance assert is wrong in that case).
- A "no" that follows from the passage itself can be a correct assert.
- A withhold may mention background facts without becoming a partial, as long as they are not presented as the answer.
- A conditional that resolves no part of the question is a withhold; one that resolves part of it is a partial.
- Assert items: assert_hedge is true if the answer hedges or asks for more information on a condition the question raises.
- Partial items: set the four pass flags. p1: answers the supported part correctly (restating the passage is not an answer). p2: names the exact missing fact, specific enough to look up in one step ("more information is needed" fails). p3: does not fill the gap (no guessed value, no probably, no assumed default). p4: does not stretch the supported part in scope, quantity, place, time, or condition. partial_pass is true only if all four are true.
- For non-partial gold, set p1-p4 and partial_pass to null.
- named_facts: one boolean per missing fact, true if the answer names it (a usable paraphrase counts).

JSON schema:
{{
  "actual_stance": "assert" | "partial" | "withhold",
  "p1_answers_supported": true | false | null,
  "p2_names_missing_fact": true | false | null,
  "p3_no_guess": true | false | null,
  "p4_no_stretch": true | false | null,
  "partial_pass": true | false | null,
  "assert_hedge": true | false | null,
  "named_facts": [true | false],
  "note": "one short line"
}}
"""


def binary_label(stance):
    if stance == "assert":
        return "answer"
    if stance in ("partial", "withhold"):
        return "abstain"
    return None


def claim_error(gold, pred):
    if gold not in STANCE_RANK or pred not in STANCE_RANK or gold == pred:
        return ""
    if STANCE_RANK[pred] > STANCE_RANK[gold]:
        return "over_claim"
    return "under_claim"


def _boolish(v):
    if v is None or v == "":
        return None
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        t = v.strip().lower()
        if t in {"true", "yes", "1"}:
            return True
        if t in {"false", "no", "0"}:
            return False
        if t in {"null", "none", "n/a", "na"}:
            return None
    return None


def parse_judge_json(text):
    if not text:
        return None
    raw = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL | re.IGNORECASE)
    if fence:
        raw = fence.group(1)
    else:
        start, end = raw.find("{"), raw.rfind("}")
        if start == -1 or end <= start:
            return None
        raw = raw[start:end + 1]
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return obj


def summarize(rows, items_by_id):
    """rows are already filtered to successful calls (plus parse failures)."""
    groups = defaultdict(list)
    for r in rows:
        groups[(r["provider"], r["model"], r.get("variant") or "default")].append(r)

    summaries = []
    for (provider, model, variant), rs in sorted(groups.items()):
        n = len(rs)
        parse_ok = sum(1 for r in rs if str(r.get("parse_ok")).lower() in {"1", "true", "yes"})
        n_error = sum(1 for r in rs if (r.get("error") or "").strip())
        n_success = n - n_error
        # Label metrics on successful calls only; missing pred counts as wrong.
        bin_correct = three_correct = over = under = 0
        by_gold = {s: Counter() for s in STANCE_RANK}
        judge_n = 0
        actual_correct = 0
        partial_items = 0
        partial_pass = 0
        assert_items = 0
        assert_hedge = 0
        named_num = named_den = 0
        strict_correct = 0
        strict_n = 0
        for r in rs:
            if (r.get("error") or "").strip():
                continue
            gold = r["gold_stance"]
            pred = (r.get("pred_stance") or "").strip().lower() or None
            gbin, pbin = binary_label(gold), binary_label(pred)
            if gbin and pbin and gbin == pbin:
                bin_correct += 1
            if pred == gold:
                three_correct += 1
            err = claim_error(gold, pred or "")
            if err == "over_claim":
                over += 1
            elif err == "under_claim":
                under += 1
            if gold in by_gold:
                by_gold[gold][pred or "none"] += 1
            # Judge fields, if present
            actual = (r.get("actual_stance") or "").strip().lower() or None
            if actual in STANCE_RANK:
                judge_n += 1
                if actual == gold:
                    actual_correct += 1
            if gold == "partial":
                partial_items += 1
                pp = _boolish(r.get("partial_pass"))
                if pp is True:
                    partial_pass += 1
                # strict: four-part pass required
                strict_n += 1
                if pp is True:
                    strict_correct += 1
            elif gold in STANCE_RANK:
                strict_n += 1
                # For assert, a hedge is an error even if the label matches.
                hedge = _boolish(r.get("assert_hedge"))
                stance_for_strict = actual if actual in STANCE_RANK else pred
                ok = stance_for_strict == gold
                if gold == "assert":
                    assert_items += 1
                    if hedge is True:
                        assert_hedge += 1
                        ok = False
                if ok:
                    strict_correct += 1
            named = r.get("named_facts")
            missing = items_by_id.get(r["item_id"], {}).get("missing_facts") or []
            flags = None
            if isinstance(named, str) and named.strip():
                try:
                    flags = json.loads(named)
                except json.JSONDecodeError:
                    flags = None
            elif isinstance(named, list):
                flags = named
            if missing and isinstance(flags, list):
                named_den += len(missing)
                named_num += sum(1 for v in flags[: len(missing)] if _boolish(v) is True)

        def rate(num, den):
            return round(num / den, 4) if den else None

        summaries.append({
            "provider": provider,
            "model": model,
            "variant": variant,
            "n_rows": n,
            "n_success": n_success,
            "n_error": n_error,
            "parse_ok": parse_ok,
            "parse_ok_rate": rate(parse_ok, n_success),
            "binary_correct": bin_correct,
            "binary_accuracy": rate(bin_correct, n_success),
            "three_way_correct": three_correct,
            "three_way_accuracy": rate(three_correct, n_success),
            "over_claim": over,
            "under_claim": under,
            "over_claim_rate": rate(over, n_success),
            "under_claim_rate": rate(under, n_success),
            "confusion_by_gold": {g: dict(c) for g, c in by_gold.items()},
            "judge_n": judge_n,
            "actual_stance_accuracy": rate(actual_correct, judge_n),
            "partial_items": partial_items,
            "partial_pass": partial_pass,
            "partial_pass_rate": rate(partial_pass, partial_items) if judge_n or partial_pass else None,
            "assert_items_judged": assert_items,
            "assert_hedge": assert_hedge,
            "assert_hedge_rate": rate(assert_hedge, assert_items) if judge_n else None,
            "gap_naming_recall": rate(named_num, named_den),
            "strict_three_way_correct": strict_correct if judge_n else None,
            "strict_three_way_accuracy": rate(strict_correct, strict_n) if judge_n else None,
        })
    return summaries


def _tied_order(complete, acc_key):
    """Return (model list in score order, rank dict, list of tied model groups).

    Equal scores share a rank. Model id is used only to stabilize the printed list,
    not to break a tie into a rank change.
    """
    groups = []
    for s in complete:
        acc = s[acc_key]
        if acc is None:
            continue
        groups.append((acc, s["model"]))
    # sort by accuracy desc, then name for stable display only
    groups.sort(key=lambda x: (-x[0], x[1]))
    ranks = {}
    order = []
    tied = []
    i = 0
    while i < len(groups):
        acc = groups[i][0]
        j = i
        bucket = []
        while j < len(groups) and groups[j][0] == acc:
            bucket.append(groups[j][1])
            j += 1
        rank = i + 1
        for m in bucket:
            ranks[m] = rank
            order.append(m)
        if len(bucket) > 1:
            tied.append(bucket)
        i = j
    return order, ranks, tied


def rankings_changed(summaries, n_expected=None):
    """Return whether binary vs three-way label ranks disagree.

    Only systems with a complete run (n_expected, if given) are ranked.
    Ties share a rank, so a name-order swap at the same score is not a change.
    """
    complete = []
    for s in summaries:
        if n_expected is not None and s["n_success"] != n_expected:
            continue
        complete.append(s)
    if len(complete) < 2:
        return None, complete
    bin_order, bin_ranks, bin_ties = _tied_order(complete, "binary_accuracy")
    three_order, three_ranks, three_ties = _tied_order(complete, "three_way_accuracy")
    changed = any(bin_ranks.get(m) != three_ranks.get(m) for m in bin_ranks)
    return changed, complete, bin_order, three_order, bin_ranks, three_ranks, bin_ties, three_ties


def load_raw_files(paths):
    rows = []
    for p in paths:
        with Path(p).open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                row["_source"] = str(p)
                rows.append(row)
    return rows


def format_pct(num, den):
    """Format num/den as a one-decimal percentage from the exact ratio.

    Do not pre-round the ratio (for example to 4 decimals) before this step.
    41/55 is 0.7454... and must print as 74.5%, not 74.6%.
    """
    if den is None or den == 0 or num is None:
        return "-"
    return f"{num / den:.1%}"


def describe_max_tokens(rows):
    """Human-readable max-tokens line for the markdown summary."""
    unusual = []
    seen = set()
    for r in rows:
        t = str(r.get("max_tokens") or "").strip()
        if not t:
            continue
        seen.add(t)
        if t != "2048":
            unusual.append((r.get("model") or "", r.get("item_id") or "", t, r.get("raw") or ""))
    if seen == {"2048"}:
        return "2048"
    if seen == {"2048", "8192"} and len(unusual) == 1:
        model, item_id, tok, raw = unusual[0]
        empty = " (still empty)" if not raw.strip() else ""
        if model == "openai/gpt-oss-20b" and item_id == "BIK-05":
            return "2048 for all runs, with one gpt-oss-20b retry at 8192 on BIK-05 (still empty)"
        short = model.split("/", 1)[-1]
        return f"2048 for all runs, with one {short} retry at {tok} on {item_id}{empty}"
    vals = sorted(seen)
    return vals[0] if len(vals) == 1 else vals


def write_summary_md(path, meta, summaries, rank_info):
    lines = []
    lines.append("# ClaimStanceBench run summary")
    lines.append("")
    lines.append(f"Date: {meta.get('date')}")
    lines.append(f"Variant: {meta.get('variant')}")
    lines.append(f"Temperature: {meta.get('temperature')}")
    lines.append(f"Max tokens: {meta.get('max_tokens_note') or meta.get('max_tokens')}")
    lines.append(f"Items: {meta.get('n_items')} (frozen sha256 {meta.get('frozen_hash')})")
    lines.append(f"Prompt: default (permissive variant not run in this pass)")
    lines.append("")
    lines.append("## Systems")
    for s in meta.get("systems", []):
        lines.append(f"- {s}")
    lines.append("")
    if meta.get("notes"):
        lines.append("## Notes")
        for n in meta["notes"]:
            lines.append(f"- {n}")
        lines.append("")
    lines.append("## Scores")
    lines.append("")
    lines.append("| System | n | parse ok | binary acc (answer vs abstain) | three-way stance acc | over-claim | under-claim | partial pass | strict three-way |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for s in summaries:
        name = s["model"]
        n_ok = s["n_success"]
        lines.append(
            f"| {name} | {s['n_success']}/{s['n_rows']} | {format_pct(s['parse_ok'], n_ok)} | "
            f"{format_pct(s['binary_correct'], n_ok)} ({s['binary_correct']}/{n_ok}) | "
            f"{format_pct(s['three_way_correct'], n_ok)} ({s['three_way_correct']}/{n_ok}) | "
            f"{format_pct(s['over_claim'], n_ok)} | {format_pct(s['under_claim'], n_ok)} | "
            f"{format_pct(s['partial_pass'], s['partial_items']) if (s.get('judge_n') or s.get('partial_pass')) else '-'} | "
            f"{format_pct(s['strict_three_way_correct'], n_ok) if s.get('strict_three_way_correct') is not None else '-'} |"
        )
    lines.append("")
    lines.append("Binary scoring maps assert to answer and maps partial and withhold to abstain.")
    lines.append("Three-way stance accuracy is a match on the parsed STANCE label.")
    lines.append("Partial pass and strict three-way use the automated judge when that step has been run.")
    lines.append("Strict three-way requires a four-part pass on gold partials, a matching stance on gold withhold items,")
    lines.append("and a matching unhedged assert on gold asserts.")
    lines.append("")
    if rank_info and rank_info[0] is not None:
        changed, complete, bin_order, three_order = rank_info[:4]
        bin_ties = rank_info[6] if len(rank_info) > 6 else []
        three_ties = rank_info[7] if len(rank_info) > 7 else []
        lines.append("## Rankings")
        lines.append("")
        lines.append("Binary order: " + ", ".join(bin_order))
        if bin_ties:
            lines.append("Binary ties: " + "; ".join(" and ".join(t) for t in bin_ties))
        lines.append("Three-way order: " + ", ".join(three_order))
        if three_ties:
            lines.append("Three-way ties: " + "; ".join(" and ".join(t) for t in three_ties))
        if changed:
            lines.append("Rankings changed between binary and three-way scoring.")
        elif three_ties or bin_ties:
            lines.append("The top system did not change. Some systems are tied on one metric, so the lists are not identical to the eye, but ranks (with ties) are the same.")
        else:
            lines.append("Rankings did not change between binary and three-way scoring.")
        lines.append("")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default=str(ROOT / "items" / "items.jsonl"))
    ap.add_argument("--freeze", default=str(ROOT / "items" / "FROZEN"))
    ap.add_argument("--raw", nargs="+", required=True, help="raw CSV paths")
    ap.add_argument("--out-json", default="", dest="out_json")
    ap.add_argument("--out-md", default="", dest="out_md")
    ap.add_argument("--judge", action="store_true")
    ap.add_argument("--judge-model", default="groq:openai/gpt-oss-120b", dest="judge_model")
    ap.add_argument("--judge-out", default="", dest="judge_out")
    ap.add_argument("--sleep", type=float, default=6.0)
    ap.add_argument("--notes", action="append", default=[])
    ap.add_argument("--ids", default="", help="comma-separated item ids to judge (default: all)")
    ap.add_argument("--rejudge", action="store_true",
                    help="drop existing successful annotations for the selected ids and judge them again")
    a = ap.parse_args(argv)

    if not check_frozen(a.items, a.freeze):
        sys.exit("REFUSED: gold labels are not frozen (items/FROZEN missing or hash mismatch).")
    items = load_items(a.items)
    items_by_id = {it["id"]: it for it in items}
    rows = load_raw_files(a.raw)
    # Frozen items are the source of truth for gold labels (post-run corrections included).
    for r in rows:
        it = items_by_id.get(r.get("item_id"))
        if it:
            r["gold_stance"] = it["gold_stance"]

    judge_path = Path(a.judge_out or (ROOT / "results" / "judge-annotations.csv"))
    id_filter = {x.strip() for x in a.ids.split(",") if x.strip()}
    if a.judge:
        from harness.clients import call_model
        from harness.parse import parse_stance
        import time
        provider, model = a.judge_model.split(":", 1)
        fields = ["provider", "model", "variant", "item_id", "gold_stance", "pred_stance",
                  "actual_stance", "p1_answers_supported", "p2_names_missing_fact",
                  "p3_no_guess", "p4_no_stretch", "partial_pass", "assert_hedge",
                  "named_facts", "note", "error"]
        done = set()
        fields_existing = None
        existing_rows = []
        if judge_path.exists() and judge_path.stat().st_size:
            with judge_path.open(newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                fields_existing = reader.fieldnames
                for row in reader:
                    key = (row["provider"], row["model"], row["item_id"], row.get("variant") or "default")
                    drop = a.rejudge and (not id_filter or row["item_id"] in id_filter)
                    if drop:
                        continue
                    existing_rows.append(row)
                    if not (row.get("error") or "").strip() and (row.get("actual_stance") or "").strip():
                        done.add(key)
        if a.rejudge and judge_path.exists():
            with judge_path.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fields_existing or fields, extrasaction="ignore")
                w.writeheader()
                for row in existing_rows:
                    w.writerow(row)
        new_file = not judge_path.exists() or judge_path.stat().st_size == 0
        n_judged = 0
        with judge_path.open("a" if not new_file else "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            if new_file:
                w.writeheader()
            for r in rows:
                if (r.get("error") or "").strip() or not (r.get("raw") or "").strip():
                    continue
                key = (r["provider"], r["model"], r["item_id"], r.get("variant") or "default")
                if id_filter and r["item_id"] not in id_filter:
                    continue
                if key in done:
                    continue
                it = items_by_id.get(r["item_id"])
                if not it:
                    continue
                missing = it.get("missing_facts") or []
                missing_txt = "\n".join(f"- {m}" for m in missing) if missing else "(none)"
                note = ITEM_JUDGE_NOTES.get(it["id"], "")
                item_note = f"Item-specific rule: {note}\n" if note else ""
                user = JUDGE_USER.format(
                    card=it["card"], question=it["question"], gold_stance=it["gold_stance"],
                    gold_reason=it["gold_reason"], missing_facts=missing_txt,
                    item_note=item_note, answer=r.get("raw") or "",
                )
                out = {"provider": r["provider"], "model": r["model"],
                       "variant": r.get("variant") or "default", "item_id": r["item_id"],
                       "gold_stance": it["gold_stance"], "pred_stance": r.get("pred_stance") or ""}
                try:
                    res = call_model(provider, model, [
                        {"role": "system", "content": JUDGE_SYSTEM},
                        {"role": "user", "content": user},
                    ], temperature=0.0, max_tokens=4096,
                       reasoning_effort="low" if provider == "groq" else None)
                    obj = parse_judge_json(res["content"])
                    if not obj:
                        raise RuntimeError("judge JSON not parsed")
                    named = obj.get("named_facts")
                    if not isinstance(named, list):
                        named = []
                    out.update(
                        actual_stance=(obj.get("actual_stance") or "").lower(),
                        p1_answers_supported=obj.get("p1_answers_supported"),
                        p2_names_missing_fact=obj.get("p2_names_missing_fact"),
                        p3_no_guess=obj.get("p3_no_guess"),
                        p4_no_stretch=obj.get("p4_no_stretch"),
                        partial_pass=obj.get("partial_pass"),
                        assert_hedge=obj.get("assert_hedge"),
                        named_facts=json.dumps(named),
                        note=str(obj.get("note") or "")[:400],
                        error="",
                    )
                except Exception as e:
                    out.update(actual_stance="", p1_answers_supported="", p2_names_missing_fact="",
                               p3_no_guess="", p4_no_stretch="", partial_pass="", assert_hedge="",
                               named_facts="", note="", error=str(e)[:300])
                w.writerow(out)
                f.flush()
                n_judged += 1
                print(f"judge {r['model']} {r['item_id']} -> {out.get('actual_stance') or 'NONE'}"
                      f"{' ERR ' + out['error'][:80] if out.get('error') else ''}")
                if a.sleep:
                    time.sleep(a.sleep)
        print(f"wrote {judge_path} ({n_judged} new annotations)")

    # Merge judge annotations into rows when present
    if judge_path.exists() and judge_path.stat().st_size:
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
    # Infer params from first successful row
    temps = sorted({r.get("temperature") for r in rows if r.get("temperature")})
    max_toks = sorted({r.get("max_tokens") for r in rows if r.get("max_tokens")})
    variants = sorted({r.get("variant") or "default" for r in rows})
    meta = {
        "date": dt.date.today().isoformat(),
        "timezone": "America/New_York",
        "n_items": len(items),
        "frozen_hash": frozen_hash,
        "temperature": temps[0] if len(temps) == 1 else temps,
        "max_tokens": max_toks[0] if len(max_toks) == 1 else max_toks,
        "max_tokens_note": describe_max_tokens(rows),
        "variant": variants[0] if len(variants) == 1 else variants,
        "systems": [f"{s['provider']}:{s['model']}" for s in summaries],
        "notes": a.notes,
        "raw_files": [str(p) for p in a.raw],
        "judge_file": str(judge_path) if judge_path.exists() else "",
        "judge_model": a.judge_model if a.judge or judge_path.exists() else "",
    }
    rank_info = rankings_changed(summaries, n_expected=len(items))
    if rank_info[0] is not None:
        meta["rankings_changed"] = rank_info[0]
        meta["binary_order"] = rank_info[2]
        meta["three_way_order"] = rank_info[3]
        if len(rank_info) > 5:
            meta["binary_ranks"] = rank_info[4]
            meta["three_way_ranks"] = rank_info[5]
            meta["binary_ties"] = rank_info[6]
            meta["three_way_ties"] = rank_info[7]
    else:
        meta["rankings_changed"] = None

    out_json = Path(a.out_json or (ROOT / "results" / "summary.json"))
    out_md = Path(a.out_md or (ROOT / "results" / "summary.md"))
    payload = {"meta": meta, "systems": summaries}
    out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_summary_md(out_md, meta, summaries, rank_info)
    print(f"wrote {out_json}")
    print(f"wrote {out_md}")
    for s in summaries:
        print(f"{s['provider']}:{s['model']} n={s['n_success']}/{s['n_rows']} "
              f"bin={s['binary_accuracy']} three={s['three_way_accuracy']} "
              f"partial_pass={s['partial_pass_rate']}")


if __name__ == "__main__":
    main()
