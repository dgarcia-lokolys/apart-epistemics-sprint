"""Fetch official AbstentionBench-linked sources and write a seeded ID sample.

Downloads go to _cache/ (gitignored). This script does not write passages
into sample_ids.json.
"""
from __future__ import annotations

import json
import random
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "_cache"
SAMPLE_PATH = ROOT / "sample_ids.json"

SEED = 20261113
N_PER_CLASS = 25

SQUAD_PARQUET_URL = (
    "https://huggingface.co/datasets/rajpurkar/squad_v2/resolve/main/"
    "squad_v2/validation-00000-of-00001.parquet"
)
SUBSAMPLE_URL = (
    "https://raw.githubusercontent.com/facebookresearch/AbstentionBench/"
    "main/data/subsampling-indices.json"
)
KEYWORDS_URL = (
    "https://raw.githubusercontent.com/facebookresearch/AbstentionBench/"
    "main/recipe/abstention_keywords.py"
)
ICRAFT_URL = "https://raw.githubusercontent.com/stellalisy/mediQ/refs/heads/main/data/all_craft_md.jsonl"
IMEDQA_URL = "https://raw.githubusercontent.com/stellalisy/mediQ/refs/heads/main/data/all_dev_good.jsonl"
IMEDQA_EXCLUDE = {224, 298, 779}

SQUAD_PREPROMPT = "Respond to the question using only information given in the context."
SQUAD_TEMPLATE = "{preprompt}\nContext: {context}\nQuestion: {question}"


def _download(url: str, dest: Path, timeout: int = 120) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size:
        return dest
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    req = urllib.request.Request(url, headers={"User-Agent": "ClaimStanceBench-comparison/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp, tmp.open("wb") as f:
        while True:
            chunk = resp.read(1024 * 256)
            if not chunk:
                break
            f.write(chunk)
    tmp.replace(dest)
    return dest


def load_keywords() -> list[str]:
    """Load official keyword list by executing only the upstream assignment file in isolation."""
    path = _download(KEYWORDS_URL, CACHE / "abstention_keywords.py")
    ns: dict = {}
    # The official file builds ABSTENTION_KEYWORDS from string lists. No network in that file.
    exec(path.read_text(encoding="utf-8"), ns)
    keys = ns.get("ABSTENTION_KEYWORDS")
    if not isinstance(keys, list) or not keys:
        raise RuntimeError("official ABSTENTION_KEYWORDS not found")
    return [str(k) for k in keys]


def detect_abstention(text: str, keywords: list[str]) -> bool:
    """Official ContainsAbstentionKeywordAbstentionDetector (substring, case-insensitive)."""
    low = (text or "").lower()
    for keyword in keywords:
        if keyword.lower() in low:
            return True
    return False


def load_squad_pool() -> list[dict]:
    import pandas as pd

    parquet = _download(SQUAD_PARQUET_URL, CACHE / "squad_v2_validation.parquet")
    idx_path = _download(SUBSAMPLE_URL, CACHE / "subsampling-indices.json")
    df = pd.read_parquet(parquet)
    indices = json.loads(idx_path.read_text(encoding="utf-8"))["Squad2Dataset"]
    pool = []
    for i in indices:
        row = df.iloc[int(i)]
        answers = row["answers"]
        # answers is a dict-like with "text" list; empty text means unanswerable
        texts = list(answers["text"]) if answers is not None else []
        if hasattr(texts, "tolist"):
            texts = list(texts.tolist())
        should_abstain = len(texts) == 0
        context = str(row["context"])
        question = str(row["question"])
        prompt = SQUAD_TEMPLATE.format(
            preprompt=SQUAD_PREPROMPT, context=context, question=question
        )
        pool.append({
            "subset": "squad2",
            "source_id": str(row["id"]),
            "official_index": int(i),
            "should_abstain": bool(should_abstain),
            "prompt": prompt,
            "reference_answers": None if should_abstain else [str(t) for t in texts],
        })
    return pool


def _load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _mediq_prompt(item: dict, should_abstain: bool) -> str:
    context_sents = [(c + "." if not str(c).endswith(".") else str(c)) for c in item["context"]]
    if should_abstain:
        context = context_sents[0]
    else:
        context = " ".join(context_sents)
    question = item["question"]
    choices = "\n".join(item["options"].values())
    return f"Context: {context}\nQuestion: {question}\nChoices:\n{choices}\nAnswer: "


def load_mediq_pool() -> list[dict]:
    icraft = _load_jsonl(_download(ICRAFT_URL, CACHE / "all_craft_md.jsonl"))
    imed = _load_jsonl(_download(IMEDQA_URL, CACHE / "all_dev_good.jsonl"))
    imed = [r for r in imed if r.get("id") not in IMEDQA_EXCLUDE]
    pool = []
    for source, rows in (("iCRAFT-MD", icraft), ("iMEDQA", imed)):
        for item in rows:
            if not item.get("context"):
                continue
            for should_abstain in (False, True):
                pool.append({
                    "subset": "mediq",
                    "source": source,
                    "source_id": f"{source}:{item['id']}",
                    "should_abstain": should_abstain,
                    "prompt": _mediq_prompt(item, should_abstain),
                    "reference_answers": None if should_abstain else [item.get("answer")],
                })
    return pool


def _balanced_sample(pool: list[dict], rng: random.Random, n_per_class: int, unique_ids: bool) -> list[dict]:
    yes = [x for x in pool if x["should_abstain"]]
    no = [x for x in pool if not x["should_abstain"]]
    rng.shuffle(yes)
    rng.shuffle(no)
    if not unique_ids:
        if len(yes) < n_per_class or len(no) < n_per_class:
            raise RuntimeError(f"not enough items: abstain={len(yes)} answer={len(no)}")
        return yes[:n_per_class] + no[:n_per_class]
    # Disjoint source IDs across the two classes (MediQ).
    picked_ids: set[str] = set()
    picked_yes, picked_no = [], []
    for row in yes:
        if row["source_id"] in picked_ids:
            continue
        picked_yes.append(row)
        picked_ids.add(row["source_id"])
        if len(picked_yes) == n_per_class:
            break
    for row in no:
        if row["source_id"] in picked_ids:
            continue
        picked_no.append(row)
        picked_ids.add(row["source_id"])
        if len(picked_no) == n_per_class:
            break
    if len(picked_yes) < n_per_class or len(picked_no) < n_per_class:
        raise RuntimeError(
            f"not enough disjoint MediQ ids: abstain={len(picked_yes)} answer={len(picked_no)}"
        )
    return picked_yes + picked_no


def sample_items() -> list[dict]:
    rng = random.Random(SEED)
    squad = _balanced_sample(load_squad_pool(), rng, N_PER_CLASS, unique_ids=False)
    mediq = _balanced_sample(load_mediq_pool(), rng, N_PER_CLASS, unique_ids=True)
    # Assign stable sample ids in a documented order: squad2 then mediq, abstain then answer,
    # as returned by the class-wise draws above (already shuffled with the seed).
    items = []
    for i, row in enumerate(squad + mediq, 1):
        items.append({
            "sample_id": f"AB-{i:03d}",
            "subset": row["subset"],
            "source_id": row["source_id"],
            "official_index": row.get("official_index"),
            "source": row.get("source"),
            "should_abstain": row["should_abstain"],
            "prompt": row["prompt"],
            "reference_answers": row.get("reference_answers"),
        })
    return items


def write_sample_ids(items: list[dict]) -> None:
    public = {
        "seed": SEED,
        "n_per_subset": 50,
        "n_per_class": N_PER_CLASS,
        "subsets": ["squad2", "mediq"],
        "license_note": (
            "IDs and sampling metadata only. Passages are not stored. "
            "Rebuild prompts with fetch_and_sample.py. "
            "AbstentionBench CC BY-NC 4.0; SQuAD 2.0 CC BY-SA 4.0; MediQ CC BY 4.0."
        ),
        "items": [
            {
                "sample_id": it["sample_id"],
                "subset": it["subset"],
                "source_id": it["source_id"],
                "official_index": it.get("official_index"),
                "source": it.get("source"),
                "should_abstain": it["should_abstain"],
            }
            for it in items
        ],
    }
    SAMPLE_PATH.write_text(json.dumps(public, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    items = sample_items()
    write_sample_ids(items)
    # Cache full prompts locally for the runner; never commit this file.
    cache_prompts = CACHE / "sampled_prompts.json"
    CACHE.mkdir(parents=True, exist_ok=True)
    cache_prompts.write_text(json.dumps(items, indent=2) + "\n", encoding="utf-8")
    by = {}
    for it in items:
        by.setdefault(it["subset"], {True: 0, False: 0})
        by[it["subset"]][it["should_abstain"]] += 1
    print(f"wrote {SAMPLE_PATH} ({len(items)} ids)")
    print(f"wrote {cache_prompts} (gitignored prompts)")
    print("counts", {k: {"abstain": v[True], "answer": v[False]} for k, v in by.items()})


if __name__ == "__main__":
    main()
