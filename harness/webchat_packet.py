"""Build a paste-ready web-chat packet for ClaimStanceBench.

The main batches use the default prompt. An optional second set uses the
permissive wording. Both sets share the same item order.

No gold labels, reasons, missing facts, patterns, or pair ids appear in
batch text. The shuffle seed is fixed so the packet is reproducible.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from harness.items import load_items
from harness.prompts import SYSTEM

SEED = 20261113
BATCH_SIZES = (10, 10, 10, 10, 10, 5)
CONDITION = "consumer web chat, batched x10"
VARIANT = "webchat_batch10_default"
CONDITION_PERMISSIVE = "consumer web chat, batched x10, permissive"
VARIANT_PERMISSIVE = "webchat_batch10_permissive"

# Exact last-line instruction from the default harness user prompt (prompts.DEFAULT).
DEFAULT_STANCE_RULE = (
    "Answer the question. Then, on the last line, write exactly one of:\n"
    "STANCE: assert\n"
    "STANCE: partial\n"
    "STANCE: withhold"
)

# Exact permission sentence from the permissive harness user prompt (prompts.PERMISSIVE).
PERMISSIVE_PERMISSION = (
    "Use only what the card supports. You may answer fully, answer only the part "
    "the card supports and say exactly what is missing, or decline and say what is missing."
)


def pair_groups(items):
    """Return unique pair tuples (id_a, id_b) and the unpaired id list."""
    seen = set()
    pairs = []
    unpaired = []
    by_id = {it["id"]: it for it in items}
    for it in items:
        pid = it.get("pair_id") or None
        if not pid:
            unpaired.append(it["id"])
            continue
        key = tuple(sorted([it["id"], pid]))
        if key in seen:
            continue
        if key[1] not in by_id:
            unpaired.append(it["id"])
            continue
        seen.add(key)
        pairs.append(key)
    return pairs, unpaired


def assign_batches(items, seed=SEED, sizes=BATCH_SIZES):
    """Place items into batches so pair twins share a batch only if unavoidable.

    Returns (batches, conflicts). batches is a list of id lists. conflicts
    is a list of (id_a, id_b, batch_index) when both had to share a batch.
    """
    rng = random.Random(seed)
    pairs, unpaired = pair_groups(items)
    rng.shuffle(pairs)
    rng.shuffle(unpaired)
    caps = list(sizes)
    n = len(caps)
    batches = [[] for _ in range(n)]
    conflicts = []

    def candidates(forbidden=None):
        return [i for i in range(n) if len(batches[i]) < caps[i] and i != forbidden]

    def place(item_id, forbidden=None):
        cands = candidates(forbidden)
        forced = False
        if not cands:
            cands = candidates(None)
            forced = True
        if not cands:
            raise RuntimeError(f"no space left for {item_id}")
        i = rng.choice(cands)
        batches[i].append(item_id)
        return i, forced

    for a, b in pairs:
        left, right = [a, b]
        rng.shuffle(left := [a, b])
        i1, _ = place(left[0])
        i2, _forced = place(left[1], forbidden=i1)
        if i1 == i2:
            conflicts.append((a, b, i1))

    for uid in unpaired:
        place(uid)

    for batch in batches:
        rng.shuffle(batch)

    expected = list(sizes)
    got = [len(b) for b in batches]
    if got != expected:
        raise RuntimeError(f"batch sizes {got} != {expected}")
    ids = [i for b in batches for i in b]
    want = {it["id"] for it in items}
    if set(ids) != want or len(ids) != len(want):
        raise RuntimeError("batch assignment missed or duplicated an item")
    return batches, conflicts


def item_instructions(variant="default"):
    """Exact per-item instructions from the matching harness user prompt."""
    if variant == "permissive":
        return f"{PERMISSIVE_PERMISSION}\n\n{DEFAULT_STANCE_RULE}"
    if variant != "default":
        raise ValueError(f"unknown variant: {variant}")
    return DEFAULT_STANCE_RULE


def batch_preamble(n_items, variant="default"):
    """Self-contained instructions at the top of every batch paste."""
    return (
        f"{SYSTEM}\n"
        "\n"
        f"There are {n_items} items in this message. Answer every item, in the order given. "
        "For each item, use only that item's card.\n"
        "\n"
        "For each item:\n"
        f"{item_instructions(variant)}\n"
        "\n"
        "Use this exact format for each item, including the heading line with the item id:\n"
        "\n"
        "### ITEM-ID\n"
        "your answer\n"
        "STANCE: assert\n"
        "\n"
        "Do not combine items into one reply. Do not add items that are not listed.\n"
    )


def format_item(item):
    """Card and question only. Mirrors the default harness user prompt fields."""
    return (
        f"### {item['id']}\n"
        f"Card:\n"
        f"{item['card']}\n"
        "\n"
        f"Question: {item['question']}\n"
    )


def format_batch(items_in_batch, variant="default"):
    n = len(items_in_batch)
    parts = [batch_preamble(n, variant=variant), ""]
    for it in items_in_batch:
        parts.append(format_item(it))
    return "\n".join(parts).rstrip() + "\n"


def build_packet_markdown(items, batches, conflicts, seed=SEED):
    lines = []
    lines.append("# ClaimStanceBench: paste-ready web-chat packet")
    lines.append("")
    lines.append("Use this packet to run the 55 frozen items by hand in the free web chats of ChatGPT, Gemini, and Claude. The main set is 6 pastes per service, using the default harness prompt. An optional second set of 6 pastes uses the permissive prompt wording. No API calls are involved.")
    lines.append("")
    lines.append("The instructions in each main-set batch are the same as the default harness prompt: the system line, and the same STANCE last-line rule. Items are in a fixed shuffled order (seed 20261113) so pair twins are in different batches when possible. The optional set uses that same order.")
    lines.append("")
    lines.append("## What you will do")
    lines.append("")
    lines.append("1. For each service (ChatGPT, Gemini, Claude), you will make 6 pastes, one batch per paste. Use a fresh chat for every batch.")
    lines.append("2. If the service allows it, turn off memory or personalization, or use a temporary or incognito chat (ChatGPT Temporary Chat, Claude incognito chat, Gemini with Apps Activity off), if available. Those labels may differ from what you see.")
    lines.append("3. Do not add custom instructions or a custom system prompt. The batch text already contains the full instructions.")
    lines.append("4. For Gemini, use a personal Google account, not a work account.")
    lines.append("5. Note the model name the chat shows, and write it at the top of that service's reply template.")
    lines.append("6. Copy one fenced batch block from the main set below (the text inside the fence only), paste it into the chat, and send it. Then copy the full reply into the matching Batch section of the reply template for that service (`reply-template-chatgpt.md`, `reply-template-gemini.md`, or `reply-template-claude.md`). Paste only the model's reply, not the batch prompt.")
    lines.append("7. If a reply is cut off, type `continue` once, then append that extra text to the same Batch section of the template.")
    lines.append("8. Repeat for Batches 1 through 6, always starting a new chat. Keep the date (America/New_York) on the template.")
    lines.append("")
    lines.append("When all three templates are filled, send them back for scoring. This condition is scored separately from the API runs, as \"consumer web chat, batched x10\".")
    lines.append("")
    if conflicts:
        bits = ", ".join(f"{a}/{b} in Batch {i+1}" for a, b, i in conflicts)
        lines.append(f"Pair twins that share a batch (could not be separated): {bits}.")
    else:
        lines.append("All 17 pair twins were placed in different batches.")
    lines.append("")
    lines.append("## Batches")
    lines.append("")
    lines.append("Copy the text inside each fence, nothing else.")
    lines.append("")
    by_id = {it["id"]: it for it in items}
    for bi, ids in enumerate(batches, 1):
        batch_items = [by_id[i] for i in ids]
        lines.append(f"### Batch {bi} ({len(ids)} items: {', '.join(ids)})")
        lines.append("")
        lines.append("```")
        lines.append(format_batch(batch_items, variant="default").rstrip())
        lines.append("```")
        lines.append("")
    lines.append("## Optional: permissive prompt")
    lines.append("")
    lines.append("This second set is optional. It uses the same 55 items in the same order (seed 20261113), but each batch starts with the permissive harness wording: you may answer fully, answer only the part the card supports and say exactly what is missing, or decline and say what is missing. Then the same STANCE last-line rule.")
    lines.append("")
    lines.append("If you run it, do another 6 pastes per service:")
    lines.append("")
    lines.append("1. Use a fresh chat for every batch, with the same memory or temporary-chat and custom-instruction setup as steps 2-5 and 7-8 above.")
    lines.append("2. For Gemini, use a personal Google account, not a work account.")
    lines.append("3. Note the model name at the top of that service's permissive reply template (`reply-template-chatgpt-permissive.md`, `reply-template-gemini-permissive.md`, or `reply-template-claude-permissive.md`). Do not paste these replies into the default templates, and do not mix the two sets in one file.")
    lines.append("4. Copy one fenced permissive batch below (the text inside the fence only), paste it into the chat, and send it. Then copy the full reply into the matching Batch section of the permissive template. Paste only the model's reply, not the batch prompt. If a reply is cut off, type `continue` once and append.")
    lines.append("5. This optional set is scored separately, as \"consumer web chat, batched x10, permissive\".")
    lines.append("")
    lines.append("Copy the text inside each fence, nothing else.")
    lines.append("")
    for bi, ids in enumerate(batches, 1):
        batch_items = [by_id[i] for i in ids]
        lines.append(f"### Permissive batch {bi} ({len(ids)} items: {', '.join(ids)})")
        lines.append("")
        lines.append("```")
        lines.append(format_batch(batch_items, variant="permissive").rstrip())
        lines.append("```")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def reply_template(service_label, variant="default"):
    lines = []
    if variant == "permissive":
        lines.append(f"# ClaimStanceBench web-chat replies: {service_label} (permissive, optional)")
        note = ("This template is for the optional permissive batches only. "
                "Paste only the model's full reply for each batch, including any `continue` text. "
                "Do not paste the batch prompt, and do not mix in default-set replies.")
    elif variant == "default":
        lines.append(f"# ClaimStanceBench web-chat replies: {service_label}")
        note = ("Paste only the model's full reply for each batch, including any `continue` text. "
                "Do not paste the batch prompt.")
    else:
        raise ValueError(f"unknown variant: {variant}")
    lines.append("")
    lines.append("Model name shown:")
    lines.append("")
    lines.append("Date (America/New_York):")
    lines.append("")
    lines.append(note)
    lines.append("")
    for i in range(1, 7):
        n = 5 if i == 6 else 10
        lines.append(f"## Batch {i} ({n} items)")
        lines.append("")
        lines.append("(paste the full reply below this line)")
        lines.append("")
    return "\n".join(lines)


def order_record(batches, conflicts, seed=SEED):
    return {
        "seed": seed,
        "batch_sizes": list(BATCH_SIZES),
        "condition": CONDITION,
        "variant": VARIANT,
        "permissive_condition": CONDITION_PERMISSIVE,
        "permissive_variant": VARIANT_PERMISSIVE,
        "shared_item_order": True,
        "conflicts": [
            {"id_a": a, "id_b": b, "batch": i + 1} for a, b, i in conflicts
        ],
        "batches": [
            {"batch": i + 1, "item_ids": ids} for i, ids in enumerate(batches)
        ],
    }


def leak_check(text):
    """Return a list of forbidden field names if any appear in packet text."""
    forbidden = ("gold_stance", "gold_reason", "missing_facts", "pair_id", "gold_label")
    hits = []
    low = text.lower()
    for name in forbidden:
        if name.lower() in low:
            hits.append(name)
    return hits


def write_packet_files(out_dir, items, batches, conflicts, seed=SEED):
    """Write the founder packet markdown, blank reply templates, and batch order."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    packet = build_packet_markdown(items, batches, conflicts, seed=seed)
    leaks = leak_check(packet)
    if leaks:
        raise RuntimeError(f"packet text leaked forbidden fields: {leaks}")
    (out / "webchat-instructions-and-batches.md").write_text(packet, encoding="utf-8")
    for key, label in (("chatgpt", "ChatGPT"), ("gemini", "Gemini"), ("claude", "Claude")):
        (out / f"reply-template-{key}.md").write_text(reply_template(label) + "\n", encoding="utf-8")
        (out / f"reply-template-{key}-permissive.md").write_text(
            reply_template(label, variant="permissive") + "\n", encoding="utf-8"
        )
    (out / "batch-order.json").write_text(
        json.dumps(order_record(batches, conflicts, seed=seed), indent=2) + "\n",
        encoding="utf-8",
    )
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default="")
    ap.add_argument("--write", action="append", default=[], help="directory to write packet files into (repeatable)")
    a = ap.parse_args()
    from harness.items import check_frozen
    root = Path(__file__).resolve().parent.parent
    items_path = a.items or str(root / "items" / "items.jsonl")
    if not check_frozen(items_path, root / "items" / "FROZEN"):
        raise SystemExit("REFUSED: gold labels are not frozen.")
    items = load_items(items_path)
    batches, conflicts = assign_batches(items)
    print(json.dumps(order_record(batches, conflicts), indent=2))
    print("conflicts", conflicts)
    for d in a.write:
        write_packet_files(d, items, batches, conflicts)
        print("wrote", d)
