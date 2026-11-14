"""Run items x models and write a CSV of raw responses and parsed stances.

Refuses to run unless the gold labels are frozen (items/FROZEN matches the
sha256 of items/items.jsonl). Scoring lives in a separate step.

Usage:
  python -m harness.run --model groq:openai/gpt-oss-20b --limit 5
  python -m harness.run --model groq:openai/gpt-oss-20b --ids LIB-01,LIB-03 --sleep 15
"""
import argparse
import csv
import datetime as dt
import sys
import time
from pathlib import Path

from harness.clients import call_model
from harness.items import check_frozen, load_items
from harness.parse import parse_stance
from harness.prompts import build_messages

ROOT = Path(__file__).resolve().parent.parent
FIELDS = ["run_id", "item_id", "provider", "model", "variant", "gold_stance",
          "pred_stance", "parse_ok", "answer", "raw", "finish_reason",
          "prompt_tokens", "completion_tokens", "error", "temperature",
          "max_tokens"]


def _is_success(row):
    """A row is done only if the call itself succeeded. Parse failures are kept;
    error rows are retried on resume so a daily cap or blip can be filled later.
    """
    return not (row.get("error") or "").strip() and (row.get("raw") or "").strip() != ""


def _load_done(path):
    done = set()
    if not path.exists() or path.stat().st_size == 0:
        return done
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if _is_success(row):
                done.add((row["provider"], row["model"], row["item_id"]))
    return done


def _compact_errors(path, models):
    """Drop unsuccessful rows for the models in this run so they can be retried."""
    if not path.exists() or path.stat().st_size == 0:
        return
    want = set()
    for spec in models:
        provider, model = spec.split(":", 1)
        want.add((provider, model))
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    keep, dropped = [], 0
    for row in rows:
        key = (row["provider"], row["model"])
        if key in want and not _is_success(row):
            dropped += 1
            continue
        keep.append(row)
    if not dropped:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for row in keep:
            w.writerow(row)
    print(f"removed {dropped} unsuccessful row(s) from {path.name} for retry")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default=str(ROOT / "items" / "items.jsonl"))
    ap.add_argument("--freeze", default=str(ROOT / "items" / "FROZEN"))
    ap.add_argument("--model", action="append", required=True, help="provider:model, repeatable")
    ap.add_argument("--variant", default="default", choices=["default", "permissive"])
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--ids", default="", help="comma-separated item ids; default is all")
    ap.add_argument("--out", default="")
    ap.add_argument("--sleep", type=float, default=0.0, help="seconds to wait after each call")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--max-tokens", type=int, default=2048, dest="max_tokens")
    ap.add_argument("--run-id", default="", dest="run_id")
    a = ap.parse_args(argv)

    if not check_frozen(a.items, a.freeze):
        sys.exit("REFUSED: gold labels are not frozen (items/FROZEN missing or hash mismatch).")

    items = load_items(a.items)
    if a.ids:
        want = [s.strip() for s in a.ids.split(",") if s.strip()]
        by_id = {it["id"]: it for it in items}
        missing = [i for i in want if i not in by_id]
        if missing:
            sys.exit(f"unknown item ids: {', '.join(missing)}")
        items = [by_id[i] for i in want]
    if a.limit:
        items = items[: a.limit]
    run_id = a.run_id or dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = Path(a.out or ROOT / "results" / f"raw-{run_id}-{a.variant}.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    _compact_errors(out, a.model)
    done = _load_done(out)
    new_file = not out.exists() or out.stat().st_size == 0

    with out.open("a" if not new_file else "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        if new_file:
            w.writeheader()
        for spec in a.model:
            provider, model = spec.split(":", 1)
            rate_limit_streak = 0
            for it in items:
                key = (provider, model, it["id"])
                if key in done:
                    print(f"{provider}:{model} {it['id']} -> SKIP (already in {out.name})")
                    continue
                row = {"run_id": run_id, "item_id": it["id"], "provider": provider,
                       "model": model, "variant": a.variant, "gold_stance": it["gold_stance"],
                       "temperature": a.temperature, "max_tokens": a.max_tokens}
                try:
                    res = call_model(provider, model, build_messages(it, a.variant),
                                     temperature=a.temperature, max_tokens=a.max_tokens)
                    stance, answer = parse_stance(res["content"])
                    row.update(pred_stance=stance or "", parse_ok=stance is not None,
                               answer=answer, raw=res["content"],
                               finish_reason=res.get("finish_reason", ""),
                               prompt_tokens=res["usage"].get("prompt_tokens", ""),
                               completion_tokens=res["usage"].get("completion_tokens", ""),
                               error="")
                except Exception as e:  # keep going; record the failure
                    row.update(pred_stance="", parse_ok=False, answer="", raw="",
                               finish_reason="", prompt_tokens="", completion_tokens="",
                               error=str(e)[:300])
                w.writerow(row)
                f.flush()
                print(f"{provider}:{model} {it['id']} -> {row['pred_stance'] or 'NONE'}"
                      f"{' ERR ' + row['error'][:80] if row['error'] else ''}")
                err = (row.get("error") or "")
                if "HTTP 429" in err or "rate limit" in err.lower():
                    rate_limit_streak += 1
                    if rate_limit_streak >= 2:
                        print(f"{provider}:{model} stopping early after repeated rate limits")
                        break
                else:
                    rate_limit_streak = 0
                if a.sleep:
                    time.sleep(a.sleep)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
