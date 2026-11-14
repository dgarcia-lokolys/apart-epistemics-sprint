"""Run the seeded AbstentionBench sample on three Groq systems and score it.

Resumes from results CSV. Does not write source passages into the results file.
"""
from __future__ import annotations

import argparse
import threading
import csv
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
CACHE = ROOT / "_cache"
RESULTS_CSV = ROOT / "raw-20261113-groq-compare.csv"
METRICS_JSON = ROOT / "metrics.json"
METRICS_MD = ROOT / "summary.md"

# Make the repo importable when run as a file.
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(REPO))

from fetch_and_sample import (  # noqa: E402
    CACHE as FETCH_CACHE,
    detect_abstention,
    load_keywords,
    sample_items,
    write_sample_ids,
)

SYSTEMS = [
    ("groq", "openai/gpt-oss-120b", "low"),
    ("groq", "openai/gpt-oss-20b", "low"),
    ("groq", "qwen/qwen3.8-27b", None),
]

FIELDS = [
    "run_id", "sample_id", "subset", "source_id", "should_abstain",
    "provider", "model", "pred_abstain",
    "answer", "finish_reason", "prompt_tokens", "completion_tokens",
    "error", "temperature", "max_tokens", "reasoning_effort",
]


def load_or_build_items():
    cache_prompts = FETCH_CACHE / "sampled_prompts.json"
    if cache_prompts.exists() and cache_prompts.stat().st_size:
        return json.loads(cache_prompts.read_text(encoding="utf-8"))
    items = sample_items()
    write_sample_ids(items)
    FETCH_CACHE.mkdir(parents=True, exist_ok=True)
    cache_prompts.write_text(json.dumps(items, indent=2) + "\n", encoding="utf-8")
    return items


def load_done(path: Path) -> set[tuple[str, str]]:
    done = set()
    if not path.exists() or path.stat().st_size == 0:
        return done
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if (row.get("error") or "").strip():
                continue
            if (row.get("answer") or "").strip() or row.get("pred_abstain") in {"True", "False", "true", "false"}:
                # A successful call can legally have empty content; treat no error + tokens as done
                if not (row.get("error") or "").strip():
                    done.add((row["model"], row["sample_id"]))
    return done


def first_keyword(text: str, keywords: list[str]) -> str:
    low = (text or "").lower()
    for keyword in keywords:
        if keyword.lower() in low:
            return keyword
    return ""


def metrics_for(rows: list[dict]) -> dict:
    # Successful scored rows only
    ok = [r for r in rows if not (r.get("error") or "").strip()]
    should = [r for r in ok if str(r["should_abstain"]).lower() in {"1", "true", "yes"}]
    should_not = [r for r in ok if str(r["should_abstain"]).lower() not in {"1", "true", "yes"}]
    pred_yes = [r for r in ok if str(r["pred_abstain"]).lower() in {"1", "true", "yes"}]
    tp = [r for r in should if str(r["pred_abstain"]).lower() in {"1", "true", "yes"}]
    tn = [r for r in should_not if str(r["pred_abstain"]).lower() not in {"1", "true", "yes"}]
    fp = [r for r in pred_yes if str(r["should_abstain"]).lower() not in {"1", "true", "yes"}]
    fn = [r for r in should if str(r["pred_abstain"]).lower() not in {"1", "true", "yes"}]
    recall = (len(tp) / len(should)) if should else None
    prec = (len(tp) / len(pred_yes)) if pred_yes else (1.0 if not should else 0.0)
    # If no predicted abstentions and no should-abstain, precision is undefined; treat as None
    if not pred_yes:
        prec = None if should else 1.0
    acc = ((len(tp) + len(tn)) / len(ok)) if ok else None
    f1 = None
    if recall is not None and prec is not None and (prec + recall) > 0:
        f1 = 2 * prec * recall / (prec + recall)
    return {
        "n": len(ok),
        "n_should_abstain": len(should),
        "n_should_answer": len(should_not),
        "tp": len(tp),
        "tn": len(tn),
        "fp": len(fp),
        "fn": len(fn),
        "abstention_recall": None if recall is None else round(recall, 4),
        "abstention_precision": None if prec is None else round(prec, 4),
        "abstention_f1": None if f1 is None else round(f1, 4),
        "accuracy": None if acc is None else round(acc, 4),
    }


def write_metrics(all_rows: list[dict]) -> dict:
    by_model = defaultdict(list)
    by_model_subset = defaultdict(list)
    for r in all_rows:
        if (r.get("error") or "").strip():
            continue
        by_model[r["model"]].append(r)
        by_model_subset[(r["model"], r["subset"])].append(r)
    systems = []
    for model in [s[1] for s in SYSTEMS]:
        overall = metrics_for(by_model.get(model, []))
        overall["model"] = model
        overall["by_subset"] = {}
        for subset in ("squad2", "mediq"):
            overall["by_subset"][subset] = metrics_for(by_model_subset.get((model, subset), []))
        systems.append(overall)

    # Ranks by accuracy (ties share a rank); also list recall ranks
    def ranks(key):
        scored = [(s["model"], s[key]) for s in systems if s.get(key) is not None]
        scored.sort(key=lambda x: (-x[1], x[0]))
        out = {}
        i = 0
        while i < len(scored):
            val = scored[i][1]
            j = i
            bucket = []
            while j < len(scored) and scored[j][1] == val:
                bucket.append(scored[j][0])
                j += 1
            for m in bucket:
                out[m] = i + 1
            i = j
        return out

    acc_ranks = ranks("accuracy")
    rec_ranks = ranks("abstention_recall")
    for s in systems:
        s["rank_accuracy"] = acc_ranks.get(s["model"])
        s["rank_recall"] = rec_ranks.get(s["model"])

    payload = {
        "date": "2026-11-13",
        "timezone": "America/New_York",
        "n_items": 100,
        "subsets": ["squad2", "mediq"],
        "seed": 20261113,
        "temperature": 0.0,
        "max_tokens": 1024,
        "detector": "ContainsAbstentionKeywordAbstentionDetector (official keyword substring match)",
        "gpt_oss_reasoning_effort": "low",
        "systems": systems,
        "calls_planned": 300,
    }
    METRICS_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def write_metrics_md(payload: dict) -> None:
    lines = []
    lines.append("# AbstentionBench comparison (Day 1)")
    lines.append("")
    lines.append(f"Date: {payload['date']} ({payload['timezone']})")
    lines.append("Subsets: squad2 (SQuAD 2.0, official AbstentionBench subsample then seed 20261113 25/25) and MediQ (25/25, disjoint source IDs).")
    lines.append("Detector: official ContainsAbstentionKeywordAbstentionDetector. Temperature 0, max_tokens 2048. gpt-oss reasoning_effort=low.")
    lines.append("")
    lines.append("| System | n | Accuracy | Rank (acc) | Abstention recall | Abstention precision | F1 |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for s in payload["systems"]:
        def fmt(v):
            return "-" if v is None else (f"{v:.1%}" if isinstance(v, float) else str(v))
        lines.append(
            f"| {s['model']} | {s['n']} | {fmt(s['accuracy'])} | {s.get('rank_accuracy') or '-'} | "
            f"{fmt(s['abstention_recall'])} | {fmt(s['abstention_precision'])} | {fmt(s['abstention_f1'])} |"
        )
    lines.append("")
    lines.append("By subset (accuracy / recall / precision):")
    lines.append("")
    lines.append("| System | squad2 acc | squad2 rec | squad2 prec | mediq acc | mediq rec | mediq prec |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for s in payload["systems"]:
        def fmt(v):
            return "-" if v is None else f"{v:.1%}"
        a = s["by_subset"]["squad2"]
        b = s["by_subset"]["mediq"]
        lines.append(
            f"| {s['model']} | {fmt(a['accuracy'])} | {fmt(a['abstention_recall'])} | {fmt(a['abstention_precision'])} | "
            f"{fmt(b['accuracy'])} | {fmt(b['abstention_recall'])} | {fmt(b['abstention_precision'])} |"
        )
    lines.append("")
    METRICS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--sleep", type=float, default=6.0)
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--ids", default="", help="optional comma-separated sample_id filter (for smoke tests)")
    ap.add_argument("--dry-fetch-only", action="store_true")
    ap.add_argument("--parallel", action="store_true",
                    help="run the three systems concurrently (separate Groq TPM pools)")
    a = ap.parse_args(argv)

    items = load_or_build_items()
    if a.ids:
        want = {x.strip() for x in a.ids.split(",") if x.strip()}
        items = [it for it in items if it["sample_id"] in want]
    if a.dry_fetch_only:
        print(f"fetched {len(items)} items")
        return

    from harness.clients import call_model

    keywords = load_keywords()
    done = load_done(RESULTS_CSV)
    new_file = not RESULTS_CSV.exists() or RESULTS_CSV.stat().st_size == 0
    n_new = 0
    with RESULTS_CSV.open("a" if not new_file else "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        if new_file:
            w.writeheader()
        jobs = []
        for it in items:
            for provider, model, effort in SYSTEMS:
                if (model, it["sample_id"]) in done:
                    continue
                jobs.append((it, provider, model, effort))
        print(f"planned new calls: {len(jobs)} (already done: {len(done)})", flush=True)
        write_lock = threading.Lock()
        n_new_box = [0]

        def run_one(it, provider, model, effort):
            out = {
                "run_id": "20261113-ab-compare",
                "sample_id": it["sample_id"],
                "subset": it["subset"],
                "source_id": it["source_id"],
                "should_abstain": it["should_abstain"],
                "provider": provider,
                "model": model,
                "temperature": "0.0",
                "max_tokens": str(a.max_tokens),
                "reasoning_effort": effort or "",
            }
            try:
                res = call_model(
                    provider, model,
                    [{"role": "user", "content": it["prompt"]}],
                    temperature=0.0, max_tokens=a.max_tokens,
                    reasoning_effort=effort,
                )
                text = res.get("content") or ""
                usage = res.get("usage") or {}
                pred = detect_abstention(text, keywords)
                out.update(
                    pred_abstain=str(bool(pred)),
                    
                    answer=(text or "")[:4000],
                    finish_reason=res.get("finish_reason") or "",
                    prompt_tokens=usage.get("prompt_tokens") or "",
                    completion_tokens=usage.get("completion_tokens") or "",
                    error="",
                )
            except Exception as e:
                out.update(
                    pred_abstain="", answer="",
                    finish_reason="", prompt_tokens="", completion_tokens="",
                    error=str(e)[:300],
                )
            with write_lock:
                w.writerow(out)
                f.flush()
                n_new_box[0] += 1
                status = out.get("error") or f"abstain={out.get('pred_abstain')}"
                print(f"{model} {it['sample_id']} {it['subset']} -> {status}", flush=True)
            if a.sleep:
                time.sleep(a.sleep)

        if a.parallel:
            from collections import defaultdict
            buckets = defaultdict(list)
            for job in jobs:
                buckets[job[2]].append(job)
            threads = []
            for model, model_jobs in buckets.items():
                def _worker(mjs=model_jobs):
                    for it, provider, m, effort in mjs:
                        run_one(it, provider, m, effort)
                th = threading.Thread(target=_worker, name=f"ab-{model}", daemon=False)
                threads.append(th)
                th.start()
            for th in threads:
                th.join()
        else:
            for it, provider, model, effort in jobs:
                run_one(it, provider, model, effort)
        n_new = n_new_box[0]

    # Reload all successful+all rows for metrics
    all_rows = list(csv.DictReader(RESULTS_CSV.open(newline="", encoding="utf-8"))) if RESULTS_CSV.exists() else []
    payload = write_metrics(all_rows)
    write_metrics_md(payload)
    print(f"wrote {RESULTS_CSV} ({n_new} new rows)")
    print(f"wrote {METRICS_JSON}")
    for s in payload["systems"]:
        print(f"{s['model']} n={s['n']} acc={s['accuracy']} rec={s['abstention_recall']} prec={s['abstention_precision']}")


if __name__ == "__main__":
    main()
