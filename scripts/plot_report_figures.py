#!/usr/bin/env python3
"""Publication figures for the ClaimStanceBench Apart report.

Every plotted number is recomputed from the frozen items file, the raw run
CSVs, and judge-annotations.csv in this repository. The script does not
call any API and does not read credentials.

Usage (from the repo root):

  python scripts/plot_report_figures.py --outdir figures
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch, Patch, Rectangle
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness.items import check_frozen, load_items  # noqa: E402
from harness.score import load_raw_files, summarize  # noqa: E402

FONT_DIR = Path("/usr/share/fonts/truetype/sand-box/custom/Source Sans Pro")
FONT_FILES = [
    "SourceSansPro-Regular.ttf",
    "SourceSansPro-Semibold.ttf",
    "SourceSansPro-Bold.ttf",
    "SourceSansPro-It.ttf",
]

# Restrained, colorblind-safer palette.
INK = "#1C1917"
MUTED = "#57534E"
RULE = "#D6D3D1"
GRID = "#E7E5E4"
PAPER = "#FFFFFF"
ACCENT_TEAL = "#215C6E"
ACCENT_SLATE = "#6A89A3"
ACCENT_RUST = "#C06A3A"
ACCENT_FOREST = "#3E6B50"
ACCENT_PLUM = "#5C4D7A"
STONE = "#8A847A"
STONE_DARK = "#5E5954"
HIGHLIGHT = "#B4532A"

METRIC_COLORS = {
    "binary": ACCENT_TEAL,
    "three_way": ACCENT_SLATE,
    "partial_pass": ACCENT_RUST,
    "strict": ACCENT_FOREST,
}
METRIC_LABELS = {
    "binary": "Binary",
    "three_way": "Three-way",
    "partial_pass": "Partial pass",
    "strict": "Strict three-way",
}

# Display order matches the default-prompt binary ranking.
SYSTEMS = [
    {
        "key": ("openrouter", "baidu/ernie-5.5-flash-preview:free"),
        "label": "ERNIE 5.5 Flash",
        "short": "ERNIE 5.5 Flash",
    },
    {
        "key": ("groq", "qwen/qwen3.8-27b"),
        "label": "Qwen3.8-27B",
        "short": "Qwen3.8-27B",
    },
    {
        "key": ("groq", "openai/gpt-oss-20b"),
        "label": "gpt-oss-20b",
        "short": "20b",
    },
    {
        "key": ("groq", "openai/gpt-oss-120b"),
        "label": "gpt-oss-120b",
        "short": "120b",
    },
]

STANCES = ("assert", "partial", "withhold")
STANCE_LABELS = {"assert": "Assert", "partial": "Partial", "withhold": "Withhold"}

RAW_DEFAULT = [
    ROOT / "results" / "raw-20261113-groq-default.csv",
    ROOT / "results" / "raw-20261113-openrouter-ernie-default.csv",
]
RAW_PERMISSIVE = [ROOT / "results" / "raw-20261113-groq-permissive.csv"]
JUDGE_PATH = ROOT / "results" / "judge-annotations.csv"
ITEMS_PATH = ROOT / "items" / "items.jsonl"
FREEZE_PATH = ROOT / "items" / "FROZEN"
def apply_style():
    for fname in FONT_FILES:
        path = FONT_DIR / fname
        if path.exists():
            font_manager.fontManager.addfont(str(path))
    mpl.rcParams.update({
        "font.family": "Source Sans Pro",
        "font.size": 9,
        "axes.titlesize": 11,
        "axes.titleweight": "semibold",
        "axes.labelsize": 9,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "legend.fontsize": 8.5,
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "axes.titlecolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "text.color": INK,
        "axes.linewidth": 0.7,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
        "figure.facecolor": PAPER,
        "axes.facecolor": PAPER,
        "savefig.facecolor": PAPER,
        "savefig.edgecolor": PAPER,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "axes.unicode_minus": False,
        "hatch.linewidth": 0.5,
    })


def wilson_ci(k, n, z=1.96):
    if n is None or n <= 0 or k is None:
        return None, None
    p = k / n
    z2 = z * z
    denom = 1 + z2 / n
    center = (p + z2 / (2 * n)) / denom
    rad = z * math.sqrt((p * (1 - p) + z2 / (4 * n)) / n) / denom
    return max(0.0, center - rad), min(1.0, center + rad)


def merge_judge(rows, judge_path, items_by_id):
    for r in rows:
        it = items_by_id.get(r.get("item_id"))
        if it:
            r["gold_stance"] = it["gold_stance"]
    if not judge_path.exists() or judge_path.stat().st_size == 0:
        return rows
    anns = {}
    with judge_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if (row.get("error") or "").strip():
                continue
            key = (
                row["provider"],
                row["model"],
                row["item_id"],
                row.get("variant") or "default",
            )
            anns[key] = row
    for r in rows:
        key = (
            r["provider"],
            r["model"],
            r["item_id"],
            r.get("variant") or "default",
        )
        if key in anns:
            arow = anns[key]
            for k in (
                "actual_stance",
                "p1_answers_supported",
                "p2_names_missing_fact",
                "p3_no_guess",
                "p4_no_stretch",
                "partial_pass",
                "assert_hedge",
                "named_facts",
            ):
                r[k] = arow.get(k, "")
    return rows


def load_scored(raw_paths, items_by_id):
    rows = load_raw_files(raw_paths)
    rows = merge_judge(rows, JUDGE_PATH, items_by_id)
    summaries = summarize(rows, items_by_id)
    by_key = {}
    for s in summaries:
        by_key[(s["provider"], s["model"], s["variant"])] = s
    return rows, by_key


def confusion(rows, provider, model, variant):
    """Gold x predicted counts from the parsed STANCE line."""
    counts = {g: Counter() for g in STANCES}
    empty = []
    for r in rows:
        if (r.get("provider"), r.get("model"), r.get("variant") or "default") != (
            provider,
            model,
            variant,
        ):
            continue
        gold = (r.get("gold_stance") or "").strip().lower()
        pred = (r.get("pred_stance") or "").strip().lower()
        if not pred:
            empty.append(r.get("item_id"))
            if gold in counts:
                counts[gold]["none"] += 1
            continue
        if gold in counts:
            counts[gold][pred] += 1
    return counts, empty


def metric_pack(summary):
    """k, n, rate for the four official metrics."""
    n = summary["n_success"]
    out = {
        "binary": (summary["binary_correct"], n, summary["binary_accuracy"]),
        "three_way": (summary["three_way_correct"], n, summary["three_way_accuracy"]),
        "partial_pass": (
            summary["partial_pass"],
            summary["partial_items"],
            summary["partial_pass_rate"],
        ),
        "strict": (
            summary["strict_three_way_correct"],
            n,
            summary["strict_three_way_accuracy"],
        ),
    }
    return out


def baselines(n_assert, n_partial, n_withhold):
    n = n_assert + n_partial + n_withhold
    return {
        "Always answer": {
            "binary": (n_assert, n),
            "three_way": (n_assert, n),
        },
        "Always withhold": {
            "binary": (n_partial + n_withhold, n),
            "three_way": (n_withhold, n),
        },
        "Always partial": {
            "binary": (n_partial + n_withhold, n),
            "three_way": (n_partial, n),
        },
    }


def restyle_axes(ax, ylabel=None):
    ax.spines["left"].set_color(RULE)
    ax.spines["bottom"].set_color(RULE)
    ax.tick_params(length=0)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GRID, linewidth=0.7)
    if ylabel:
        ax.set_ylabel(ylabel, color=MUTED)


def bar_with_ci(ax, x, k, n, color, width=0.18, zorder=3, alpha=1.0, hatch=None):
    rate = k / n if n else 0
    lo, hi = wilson_ci(k, n)
    bar = ax.bar(
        x,
        rate * 100,
        width=width,
        color=color,
        edgecolor="none",
        zorder=zorder,
        alpha=alpha,
        hatch=hatch,
    )
    if lo is not None:
        yerr = np.array([[rate - lo], [hi - rate]]) * 100
        ax.errorbar(
            x,
            rate * 100,
            yerr=yerr,
            fmt="none",
            ecolor=INK,
            elinewidth=0.8,
            capsize=2.2,
            capthick=0.8,
            zorder=zorder + 1,
        )
    return bar, rate, lo, hi


def save_figure(fig, outdir: Path, stem: str):
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for ext, kwargs in (
        (".png", {"dpi": 300}),
        (".pdf", {}),
        (".svg", {}),
    ):
        path = outdir / f"{stem}{ext}"
        fig.savefig(path, bbox_inches="tight", pad_inches=0.08, **kwargs)
        paths[ext] = path
    return paths


# ---------------------------------------------------------------------------
# Figure 1
# ---------------------------------------------------------------------------
def plot_fig1(outdir, default_sum, perm_sum):
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.15), sharey=True)
    metrics = ["binary", "three_way", "partial_pass", "strict"]
    width = 0.17
    offsets = (np.arange(len(metrics)) - (len(metrics) - 1) / 2) * (width + 0.02)

    panel_defs = [
        (axes[0], "A  Default prompt", default_sum, "default", True),
        (axes[1], "B  Permissive prompt", perm_sum, "permissive", False),
    ]
    handles = None
    for ax, title, sums, variant, include_ernie in panel_defs:
        labels = []
        xs = []
        xi = 0
        for sys in SYSTEMS:
            provider, model = sys["key"]
            s = sums.get((provider, model, variant))
            labels.append(sys["label"])
            xs.append(xi)
            if s is None:
                ax.text(
                    xi,
                    50,
                    "Not run",
                    ha="center",
                    va="center",
                    color=MUTED,
                    fontsize=8.5,
                    style="italic",
                )
                xi += 1
                continue
            pack = metric_pack(s)
            bars = []
            for off, m in zip(offsets, metrics):
                k, n, _ = pack[m]
                h, _, _, _ = bar_with_ci(
                    ax, xi + off, k, n, METRIC_COLORS[m], width=width
                )
                bars.append(h)
            if handles is None:
                handles = bars
            xi += 1
        ax.set_xticks(xs)
        ax.set_xticklabels(labels)
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 20, 40, 60, 80, 100])
        ax.set_title(title, loc="left", pad=8)
        restyle_axes(ax, ylabel="Accuracy (%)" if ax is axes[0] else None)
        ax.set_xlim(-0.55, len(SYSTEMS) - 0.45)

    legend = fig.legend(
        handles,
        [METRIC_LABELS[m] for m in metrics],
        loc="upper center",
        ncol=4,
        frameon=False,
        bbox_to_anchor=(0.5, 1.02),
        handlelength=1.1,
        columnspacing=1.4,
    )
    fig.text(
        0.5,
        -0.02,
        "Partial pass uses the 22 gold-partial items. The other three metrics use all 55 items. "
        "Error bars are Wilson 95% intervals.",
        ha="center",
        va="top",
        color=MUTED,
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    return save_figure(fig, outdir, "fig1-metrics-default-permissive"), fig


# ---------------------------------------------------------------------------
# Figure 2
# ---------------------------------------------------------------------------
def plot_fig2(outdir, default_sum, n_assert, n_partial, n_withhold):
    fig, ax = plt.subplots(figsize=(9.6, 5.0))
    base = baselines(n_assert, n_partial, n_withhold)
    groups = list(base.keys()) + [sys["label"] for sys in SYSTEMS]
    # visual gap between baselines and systems via an extra half-step
    x = np.array([0, 1, 2, 3.35, 4.35, 5.35, 6.35])
    width = 0.34
    # 69.1% reference line first (behind bars)
    abstain_k = n_partial + n_withhold
    abstain_n = n_assert + n_partial + n_withhold
    abstain_pct = 100 * abstain_k / abstain_n
    ax.plot(
        [-0.55, x[-1] + 0.48],
        [abstain_pct, abstain_pct],
        color=STONE,
        linewidth=0.9,
        linestyle=(0, (3.2, 2.2)),
        zorder=1,
        clip_on=False,
    )
    ax.text(
        x[-1] + 0.58,
        abstain_pct,
        f"Always abstain,\n{abstain_pct:.1f}% binary",
        ha="left",
        va="center",
        color=STONE_DARK,
        fontsize=8,
        linespacing=1.15,
        clip_on=False,
    )

    for i, name in enumerate(groups):
        if name in base:
            bin_k, bin_n = base[name]["binary"]
            tw_k, tw_n = base[name]["three_way"]
        else:
            sys = next(s for s in SYSTEMS if s["label"] == name)
            pack = metric_pack(default_sum[(*sys["key"], "default")])
            bin_k, bin_n, _ = pack["binary"]
            tw_k, tw_n, _ = pack["three_way"]
        bar_with_ci(ax, x[i] - width / 2, bin_k, bin_n, METRIC_COLORS["binary"], width=width)
        bar_with_ci(ax, x[i] + width / 2, tw_k, tw_n, METRIC_COLORS["three_way"], width=width)

    # light divider
    ax.axvline(2.675, color=RULE, linewidth=0.7, zorder=0)

    ax.set_xticks(x)
    ax.set_xticklabels(groups)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    restyle_axes(ax, ylabel="Accuracy (%)")
    ax.set_xlim(-0.55, x[-1] + 1.85)
    ax.legend(
        handles=[
            Patch(facecolor=METRIC_COLORS["binary"], edgecolor="none", label="Binary"),
            Patch(facecolor=METRIC_COLORS["three_way"], edgecolor="none", label="Three-way"),
        ],
        loc="upper left",
        frameon=False,
        handlelength=1.1,
    )
    ax.text(1.0, -18, "Trivial baselines", ha="center", color=MUTED, fontsize=8)
    ax.text(4.85, -18, "Default prompt", ha="center", color=MUTED, fontsize=8)
    fig.tight_layout()
    return save_figure(fig, outdir, "fig2-baselines-binary-threeway"), fig


# ---------------------------------------------------------------------------
# Figure 3
# ---------------------------------------------------------------------------
CMAP = LinearSegmentedColormap.from_list(
    "teal_seq", ["#F4F1EC", "#C5D4D6", "#6A9AA3", "#215C6E", "#143B46"]
)


def draw_matrix(ax, counts, title, highlight=None, show_xlabel=True, show_ylabel=True):
    data = np.zeros((3, 3))
    raw = np.zeros((3, 3), dtype=int)
    for i, g in enumerate(STANCES):
        total = sum(counts[g].values())  # includes 'none' in the denominator
        for j, p in enumerate(STANCES):
            raw[i, j] = counts[g].get(p, 0)
            data[i, j] = (raw[i, j] / total) if total else 0
    im = ax.imshow(data, cmap=CMAP, vmin=0, vmax=1, aspect="equal")
    for i in range(3):
        for j in range(3):
            val = raw[i, j]
            # Darker cells get white type.
            color = PAPER if data[i, j] >= 0.45 else INK
            weight = "bold" if i == j else "regular"
            ax.text(
                j,
                i,
                str(val),
                ha="center",
                va="center",
                color=color,
                fontsize=10,
                fontweight=weight,
            )
            if highlight == (i, j):
                ax.add_patch(
                    Rectangle(
                        (j - 0.5, i - 0.5),
                        1,
                        1,
                        fill=False,
                        edgecolor=HIGHLIGHT,
                        linewidth=1.8,
                        zorder=5,
                    )
                )
    ax.set_xticks(range(3))
    ax.set_yticks(range(3))
    ax.set_xticklabels([STANCE_LABELS[s] for s in STANCES], fontsize=8)
    ax.set_yticklabels([STANCE_LABELS[s] for s in STANCES], fontsize=8)
    if show_xlabel:
        ax.set_xlabel("Predicted stance", fontsize=8, color=MUTED, labelpad=3)
    else:
        ax.set_xlabel("")
    if show_ylabel:
        ax.set_ylabel("Gold stance", fontsize=8, color=MUTED, labelpad=3)
    else:
        ax.set_ylabel("")
    ax.set_title(title, loc="left", fontsize=10, pad=6)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.6)
        spine.set_color(RULE)
    ax.set_xticks(np.arange(-0.5, 3, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, 3, 1), minor=True)
    ax.grid(which="minor", color=PAPER, linewidth=1.2)
    ax.tick_params(which="minor", length=0)
    return im


def plot_fig3(outdir, default_rows, perm_rows, default_sum, perm_sum):
    fig = plt.figure(figsize=(11.4, 8.4))
    # 4 default matrices on row 1, then 3 permissive matrices plus 1 bar panel on row 2
    gs = fig.add_gridspec(
        2,
        4,
        height_ratios=[1, 1],
        wspace=0.38,
        hspace=0.42,
        left=0.07,
        right=0.88,
        top=0.90,
        bottom=0.08,
    )
    fig.text(0.07, 0.955, "A  Default prompt", fontsize=11, fontweight="semibold", color=INK)
    fig.text(0.07, 0.50, "B  Permissive prompt", fontsize=11, fontweight="semibold", color=INK)

    default_empty = {}
    im = None
    for i, sys in enumerate(SYSTEMS):
        ax = fig.add_subplot(gs[0, i])
        counts, empty = confusion(default_rows, sys["key"][0], sys["key"][1], "default")
        default_empty[sys["label"]] = empty
        star = " *" if empty else ""
        im = draw_matrix(
            ax,
            counts,
            sys["label"] + star,
            show_xlabel=True,
            show_ylabel=(i == 0),
        )

    # Permissive: skip ERNIE
    perm_systems = [s for s in SYSTEMS if s["key"][0] == "groq"]
    for i, sys in enumerate(perm_systems):
        ax = fig.add_subplot(gs[1, i])
        counts, empty = confusion(perm_rows, sys["key"][0], sys["key"][1], "permissive")
        # Highlight gold withhold (row 2) / pred partial (col 1) for gpt-oss
        hl = (2, 1) if "gpt-oss" in sys["label"] else None
        draw_matrix(
            ax,
            counts,
            sys["label"],
            highlight=hl,
            show_xlabel=True,
            show_ylabel=(i == 0),
        )

    # Panel C: withhold predicted as partial, default vs permissive
    ax = fig.add_subplot(gs[1, 3])
    ax.set_title("C  Gold withhold labeled partial", loc="left", fontsize=10, pad=6)
    labels = []
    default_vals = []
    perm_vals = []
    for sys in SYSTEMS:
        # ERNIE has no permissive run
        dcounts, _ = confusion(default_rows, sys["key"][0], sys["key"][1], "default")
        d_val = dcounts["withhold"].get("partial", 0)
        if sys["key"][0] != "groq":
            continue
        pcounts, _ = confusion(perm_rows, sys["key"][0], sys["key"][1], "permissive")
        p_val = pcounts["withhold"].get("partial", 0)
        labels.append(sys["label"])
        default_vals.append(d_val)
        perm_vals.append(p_val)
    x = np.arange(len(labels))
    width = 0.34
    ax.bar(x - width / 2, default_vals, width=width, color=ACCENT_TEAL, edgecolor="none", label="Default")
    ax.bar(x + width / 2, perm_vals, width=width, color=ACCENT_RUST, edgecolor="none", label="Permissive")
    for xi, d, p in zip(x, default_vals, perm_vals):
        ax.text(xi - width / 2, d + 0.25, str(d), ha="center", va="bottom", fontsize=8, color=INK)
        ax.text(xi + width / 2, p + 0.25, str(p), ha="center", va="bottom", fontsize=8, color=INK)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=7.5)
    ax.set_ylim(0, 16)
    ax.set_yticks([0, 4, 8, 12, 16])
    ax.set_ylabel("Count of 16 withhold items", fontsize=8, color=MUTED)
    restyle_axes(ax)
    ax.legend(frameon=False, loc="upper left", handlelength=1.1, fontsize=8)

    cax = fig.add_axes([0.90, 0.56, 0.015, 0.34])
    cb = fig.colorbar(im, cax=cax)
    cb.set_label("Share of gold class", fontsize=8, color=MUTED)
    cb.ax.tick_params(labelsize=7.5, length=0, colors=MUTED)
    cb.outline.set_linewidth(0.5)
    cb.outline.set_edgecolor(RULE)
    cb.set_ticks([0, 0.25, 0.5, 0.75, 1.0])
    cb.set_ticklabels(["0%", "25%", "50%", "75%", "100%"])

    note = (
        "Numbers are counts. Color is the share of that gold class. "
        "The highlighted cells in B are gold withhold items labeled partial. "
        "* gpt-oss-20b default: one gold-partial output was empty and is not in the matrix."
    )
    fig.text(0.07, 0.015, note, fontsize=8, color=MUTED, ha="left", va="bottom")
    return save_figure(fig, outdir, "fig3-confusion-default-permissive"), fig


# ---------------------------------------------------------------------------
# Figure 4  (illustrative example, not a benchmark item)
# ---------------------------------------------------------------------------
def rounded(ax, x, y, w, h, facecolor, edgecolor=RULE, lw=0.7, radius=0.08, z=1):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.01,rounding_size={radius}",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=lw,
        mutation_aspect=1,
        zorder=z,
    )
    ax.add_patch(patch)
    return patch


def plot_fig4(outdir):
    fig, ax = plt.subplots(figsize=(11.2, 5.35))
    ax.set_xlim(0, 112)
    ax.set_ylim(0, 53.5)
    ax.axis("off")
    ax.set_aspect("equal", adjustable="box")

    # Shared passage card
    rounded(ax, 2, 42.2, 108, 10.2, "#F4F1EC", RULE, 0.7, radius=0.6)
    ax.text(6, 50.0, "Passage (illustrative, not a benchmark item)", fontsize=8, color=MUTED, fontstyle="italic")
    ax.text(
        6,
        46.6,
        "Harbor Ferry runs hourly from 7 a.m. to 7 p.m., Friday through Sunday. Tickets are $6 each way.",
        fontsize=10.5,
        color=INK,
        fontweight="regular",
    )

    columns = [
        {
            "title": "Assert",
            "accent": ACCENT_TEAL,
            "bg": "#E8F0F2",
            "question": "Does the Friday 10 a.m. ferry run, and how much is a one-way ticket?",
            "why": "Both parts are stated in the passage.",
            "answer": "Yes. A one-way ticket is $6.",
        },
        {
            "title": "Partial",
            "accent": ACCENT_RUST,
            "bg": "#F8EFE8",
            "question": "Does the Friday 10 a.m. ferry run, and can I bring a bicycle?",
            "why": "The Friday sailing is supported. Bicycle policy is not stated.",
            "answer": "Yes, the Friday 10 a.m. ferry runs. The passage does not say whether bicycles are allowed.",
        },
        {
            "title": "Withhold",
            "accent": ACCENT_PLUM,
            "bg": "#F0ECF3",
            "question": "Are pets allowed, and how long does the crossing take?",
            "why": "The passage does not mention pets or how long the crossing takes.",
            "answer": "The passage does not say whether pets are allowed or how long the crossing takes.",
        },
    ]

    left = 2
    gap = 2.2
    width = (108 - 2 * gap) / 3
    bottom = 2.2
    height = 38.4

    def wrap(text, width_chars):
        words = text.split()
        lines, cur = [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if len(trial) <= width_chars:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    for i, col in enumerate(columns):
        x = left + i * (width + gap)
        rounded(ax, x, bottom, width, height, col["bg"], RULE, 0.7, radius=0.5)
        # accent bar at top of column
        rounded(ax, x, bottom + height - 1.15, width, 1.15, col["accent"], col["accent"], 0, radius=0.15)
        # cover bottom rounding of the accent so only the top is rounded-looking
        ax.add_patch(Rectangle((x, bottom + height - 0.7), width, 0.7, facecolor=col["accent"], edgecolor="none", zorder=2))

        cx = x + 1.5
        ax.text(
            x + width / 2,
            bottom + height - 3.6,
            col["title"],
            ha="center",
            va="center",
            fontsize=13,
            fontweight="bold",
            color=col["accent"],
        )
        y = bottom + height - 7.0
        ax.text(cx, y, "Question", fontsize=7.5, color=MUTED, fontweight="semibold")
        y -= 1.15
        for line in wrap(col["question"], 42):
            y -= 1.55
            ax.text(cx, y, line, fontsize=8.7, color=INK)
        y -= 2.4
        ax.text(cx, y, "Why this stance", fontsize=7.5, color=MUTED, fontweight="semibold")
        y -= 1.15
        for line in wrap(col["why"], 42):
            y -= 1.55
            ax.text(cx, y, line, fontsize=8.7, color=INK)
        y -= 2.4
        ax.text(cx, y, "A correct response", fontsize=7.5, color=MUTED, fontweight="semibold")
        y -= 1.15
        for line in wrap(col["answer"], 42):
            y -= 1.55
            ax.text(cx, y, line, fontsize=8.7, color=INK)

    fig.tight_layout()
    return save_figure(fig, outdir, "fig4-stance-schematic"), fig


# ---------------------------------------------------------------------------
# Figure 5
# ---------------------------------------------------------------------------
def plot_fig5(outdir, agreement_path: Path):
    data = json.loads(agreement_path.read_text())
    first = data["agreement"]
    corr = data["founder_corrections_post_comparison"]["agreement_corrected"]

    rows = [
        {
            "label": "Correct stance vs gold",
            "k": first["a_correct_stance_vs_gold"]["agree"],
            "n": first["a_correct_stance_vs_gold"]["n"],
            "kappa": first["a_correct_stance_vs_gold"]["cohens_kappa"],
            "color": ACCENT_TEAL,
        },
        {
            "label": "Item-correct vs strict three-way",
            "k": first["d_item_correct_strict"]["agree"],
            "n": first["d_item_correct_strict"]["n"],
            "kappa": first["d_item_correct_strict"]["cohens_kappa"],
            "color": ACCENT_FOREST,
        },
        {
            "label": "Actual stance vs judge, first pass",
            "k": first["b_actual_stance_vs_judge"]["agree"],
            "n": first["b_actual_stance_vs_judge"]["n"],
            "kappa": first["b_actual_stance_vs_judge"]["cohens_kappa"],
            "color": ACCENT_SLATE,
        },
        {
            "label": "Actual stance vs judge, after correction",
            "k": corr["b_actual_stance_vs_judge"]["agree"],
            "n": corr["b_actual_stance_vs_judge"]["n"],
            "kappa": corr["b_actual_stance_vs_judge"]["cohens_kappa"],
            "color": ACCENT_RUST,
        },
    ]

    fig, ax = plt.subplots(figsize=(8.8, 4.4))
    y = np.arange(len(rows))[::-1]
    for yi, row in zip(y, rows):
        lo, hi = wilson_ci(row["k"], row["n"])
        rate = row["k"] / row["n"]
        ax.hlines(yi, lo * 100, hi * 100, color=row["color"], linewidth=3.0, zorder=2, clip_on=False)
        ax.plot(rate * 100, yi, "o", color=row["color"], markersize=7.5, zorder=3, markeredgecolor=PAPER, markeredgewidth=0.7, clip_on=False)
        kappa = row["kappa"]
        kappa_s = f"{kappa:.3f}" if kappa is not None else "undefined"
        ax.text(
            102.0,
            yi,
            f"{row['k']}/{row['n']}  ({100 * rate:.1f}%),  kappa {kappa_s}",
            va="center",
            ha="left",
            fontsize=8.5,
            color=INK,
        )
    ax.set_yticks(y)
    ax.set_yticklabels([r["label"] for r in rows])
    ax.set_xlabel("Percent agreement")
    ax.set_xlim(40, 118)
    ax.set_xticks([40, 50, 60, 70, 80, 90, 100])
    ax.spines["bottom"].set_bounds(40, 100)
    restyle_axes(ax)
    ax.axvline(100, color=RULE, linewidth=0.6, zorder=0)
    for line in ax.lines:
        line.set_clip_on(False)
    for coll in ax.collections:
        coll.set_clip_on(False)
    fig.text(
        0.01,
        -0.04,
        "n = 18 outputs. Error bars are Wilson 95% intervals. "
        "The correction is CSB-09 actual stance, assert to partial. "
        "Headline first-pass numbers are the top three rows.",
        fontsize=8,
        color=MUTED,
        ha="left",
    )
    fig.tight_layout()
    return save_figure(fig, outdir, "fig5-blind-grade-agreement"), fig


# ---------------------------------------------------------------------------
# Contact sheet and captions
# ---------------------------------------------------------------------------
CAPTIONS = {
    "fig1-metrics-default-permissive": (
        "Figure 1. Accuracy of four API systems on ClaimStanceBench (55 frozen items) "
        "under the default prompt (A) and the permissive prompt (B). Bars show binary "
        "accuracy (n=55), three-way stance accuracy (n=55), four-part partial pass "
        "(n=22 gold partials), and strict three-way accuracy (n=55). Error bars are "
        "Wilson 95% confidence intervals. ERNIE 5.5 Flash was run only with the default "
        "prompt. gpt-oss-20b produced one empty output on the default prompt (BIK-05). "
        "That item is counted as incorrect."
    ),
    "fig2-baselines-binary-threeway": (
        "Figure 2. Binary accuracy versus three-way stance accuracy for three trivial "
        "baselines and the four default-prompt systems. Always withhold and always "
        "partial both reach 69.1% binary accuracy (38/55), the score of an always-abstain "
        "policy on this gold split (17 assert, 22 partial, 16 withhold). That baseline "
        "sits close to gpt-oss-120b's 78.2% binary score. Three-way scoring separates "
        "the two abstain policies (29.1% and 40.0%). Error bars are Wilson 95% intervals."
    ),
    "fig3-confusion-default-permissive": (
        "Figure 3. Gold stance versus the parsed STANCE label under the default prompt (A) "
        "and the permissive prompt (B). Cell color is the share of each gold class. "
        "Numbers are counts. (C) Of the 16 gold withhold items, both gpt-oss systems "
        "label many more as partial under the permissive prompt. gpt-oss-20b moves "
        "from 2 to 12, and gpt-oss-120b moves from 5 to 8. One gpt-oss-20b default "
        "output was empty and is omitted from that matrix (gold partial)."
    ),
    "fig4-stance-schematic": (
        "Figure 4. The three ClaimStanceBench stances, illustrated with a ferry schedule. "
        "The passage supports a complete answer (assert), a part of a two-part question "
        "(partial), or neither part (withhold). This example is not a benchmark item."
    ),
    "fig5-blind-grade-agreement": (
        "Figure 5. Founder agreement with gold labels and the automated judge on 18 "
        "blind-graded outputs. First-pass rates are uncorrected. After the founder "
        "corrected CSB-09's actual stance from assert to partial, actual-stance agreement "
        "with the judge rose from 16/18 to 17/18. A second correction (CSB-08 named "
        "missing facts set to n/a) does not change any rate shown here. Error bars are "
        "Wilson 95% intervals."
    ),
}

SHEET_TITLES = {
    "fig1-metrics-default-permissive": "Figure 1. Metrics by system and prompt",
    "fig2-baselines-binary-threeway": "Figure 2. Baselines next to default systems",
    "fig3-confusion-default-permissive": "Figure 3. Gold versus predicted stance",
    "fig4-stance-schematic": "Figure 4. Assert, partial, and withhold",
    "fig5-blind-grade-agreement": "Figure 5. Blind-grade agreement",
}


def write_figures_md(outdir: Path, stems):
    lines = [
        "# ClaimStanceBench figures",
        "",
        "Date: Saturday, Nov 14, 2026 (America/New_York).",
        "Every number in these figures was recomputed from the frozen 55-item set, "
        "the raw default and permissive run CSVs, and judge-annotations.csv in "
        "this repository. Intervals are Wilson 95%. No em dashes are used in "
        "labels or captions. PNG files are 300 dpi. PDF and SVG sit alongside each PNG.",
        "",
        "Generated by `scripts/plot_report_figures.py` in the sprint repo.",
        "",
    ]
    for stem in stems:
        lines.append(f"## {stem}")
        lines.append("")
        lines.append(f"Files: `{stem}.png`, `{stem}.pdf`, `{stem}.svg`.")
        lines.append("")
        lines.append(CAPTIONS[stem])
        lines.append("")
    lines.append("## Contact sheet")
    lines.append("")
    lines.append("File: `contact-sheet.png`. A preview of all five figures, not for the paper.")
    lines.append("")
    (outdir / "figures.md").write_text("\n".join(lines))


def contact_sheet(outdir: Path, stems, dpi=200):
    from PIL import Image, ImageDraw, ImageFont

    images = []
    for stem in stems:
        im = Image.open(outdir / f"{stem}.png").convert("RGB")
        images.append((stem, im))
    # Two columns, three rows (last cell empty or used by leftover)
    cols, rows = 2, 3
    pad = 36
    label_h = 48
    # Fit each image into a cell
    # Use max width/height ratio to choose a common cell width
    max_w = max(im.width for _, im in images)
    # scale so the sheet is about 2800 px wide
    cell_w = 1300
    font_path = str(FONT_DIR / "SourceSansPro-Semibold.ttf")
    font = ImageFont.truetype(font_path, 28)
    scaled = []
    cell_h = 0
    for stem, im in images:
        scale = cell_w / im.width
        new = im.resize((cell_w, int(im.height * scale)), Image.Resampling.LANCZOS)
        scaled.append((stem, new))
        cell_h = max(cell_h, new.height)
    sheet_w = cols * cell_w + (cols + 1) * pad
    sheet_h = rows * (cell_h + label_h) + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    for idx, (stem, im) in enumerate(scaled):
        r, c = divmod(idx, cols)
        # last figure can sit left on row 3
        x = pad + c * (cell_w + pad)
        y = pad + r * (cell_h + label_h + pad)
        # center vertically in cell
        y_im = y + label_h + (cell_h - im.height) // 2
        draw.text((x, y + 6), SHEET_TITLES[stem], font=font, fill=(28, 25, 23))
        sheet.paste(im, (x, y_im))
    path = outdir / "contact-sheet.png"
    sheet.save(path, dpi=(dpi, dpi))
    return path


def verify_against_summary(default_sum, perm_sum):
    """Sanity-check recomputed rates against the committed summary files."""
    committed = {}
    for path, variant in (
        (ROOT / "results" / "summary.json", "default"),
        (ROOT / "results" / "summary-permissive.json", "permissive"),
    ):
        blob = json.loads(path.read_text())
        for s in blob["systems"]:
            committed[(s["provider"], s["model"], s["variant"])] = s
    mismatches = []
    for store in (default_sum, perm_sum):
        for key, s in store.items():
            c = committed.get(key)
            if not c:
                mismatches.append(f"missing in committed summary: {key}")
                continue
            for field in (
                "binary_correct",
                "three_way_correct",
                "partial_pass",
                "strict_three_way_correct",
            ):
                if s.get(field) != c.get(field):
                    mismatches.append(f"{key} {field}: recomputed {s.get(field)} vs summary {c.get(field)}")
    return mismatches


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--outdir",
        default="figures",
        type=Path,
    )
    ap.add_argument(
        "--agreement",
        default="",
        type=Path,
        help="Optional path to blind-grade-agreement-v1.json (Figure 5)",
    )
    args = ap.parse_args()
    outdir = args.outdir
    outdir.mkdir(parents=True, exist_ok=True)

    if not check_frozen(ITEMS_PATH, FREEZE_PATH):
        sys.exit("REFUSED: frozen items hash mismatch.")
    items = load_items(ITEMS_PATH)
    items_by_id = {it["id"]: it for it in items}
    gold_counts = Counter(it["gold_stance"] for it in items)
    if dict(gold_counts) != {"assert": 17, "partial": 22, "withhold": 16}:
        sys.exit(f"Unexpected gold split: {dict(gold_counts)}")

    default_rows, default_sum = load_scored(RAW_DEFAULT, items_by_id)
    perm_rows, perm_sum = load_scored(RAW_PERMISSIVE, items_by_id)
    mismatches = verify_against_summary(default_sum, perm_sum)
    if mismatches:
        sys.exit("Recomputed scores do not match committed summaries:\n" + "\n".join(mismatches))

    apply_style()
    stems = [
        "fig1-metrics-default-permissive",
        "fig2-baselines-binary-threeway",
        "fig3-confusion-default-permissive",
        "fig4-stance-schematic",
    ]
    plot_fig1(outdir, default_sum, perm_sum)
    plt.close("all")
    plot_fig2(
        outdir,
        default_sum,
        gold_counts["assert"],
        gold_counts["partial"],
        gold_counts["withhold"],
    )
    plt.close("all")
    plot_fig3(outdir, default_rows, perm_rows, default_sum, perm_sum)
    plt.close("all")
    plot_fig4(outdir)
    plt.close("all")
    if args.agreement and Path(args.agreement).is_file():
        plot_fig5(outdir, args.agreement)
        plt.close("all")
        stems.append("fig5-blind-grade-agreement")
    else:
        print("skipping Figure 5 (pass --agreement path/to/blind-grade-agreement-v1.json)")
    write_figures_md(outdir, stems)
    contact_sheet(outdir, stems)
    print(f"wrote figures to {outdir}")
    for stem in stems:
        print(" ", stem)
    print("  contact-sheet.png")
    print("  figures.md")


if __name__ == "__main__":
    main()
