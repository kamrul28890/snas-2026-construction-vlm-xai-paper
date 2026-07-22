"""Generate compact paper figures from checked benchmark artifacts."""

from __future__ import annotations

import csv
import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "paper" / "snas" / "figures"

plt.rcParams.update(
    {
        "font.family": "Times New Roman",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)


COLORS = {
    "data": "#4C78A8",
    "annotation": "#F58518",
    "model": "#54A24B",
    "intervention": "#B279A2",
    "score": "#E45756",
    "neutral": "#5F6B6D",
    "light": "#F4F6F8",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def save(fig: plt.Figure, name: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_DIR / name, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def box(ax, xy, width, height, text, color, fontsize=7.5):
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.015,rounding_size=0.025",
        linewidth=0.9,
        edgecolor=color,
        facecolor=color,
        alpha=0.12,
    )
    ax.add_patch(patch)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color="#1F2933",
        linespacing=1.12,
    )


def dark_box(ax, xy, width, height, title, subtitle, edge, face, title_color, subtitle_color):
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.014",
        linewidth=1.1,
        edgecolor=edge,
        facecolor=face,
    )
    ax.add_patch(patch)
    cx = xy[0] + width / 2
    ax.text(
        cx,
        xy[1] + height * 0.69,
        title,
        ha="center",
        va="center",
        fontsize=8.1,
        fontweight="bold",
        color=title_color,
    )
    ax.text(
        cx,
        xy[1] + height * 0.27,
        subtitle,
        ha="center",
        va="center",
        fontsize=6.2,
        color=subtitle_color,
    )


def arrow(ax, start, end, color="#67727E"):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=8,
            linewidth=0.8,
            color=color,
            shrinkA=3,
            shrinkB=3,
        )
    )


def dark_arrow(ax, points, color="#8D8D87"):
    xs, ys = zip(*points)
    if len(points) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, linewidth=1.2, solid_capstyle="round")
    ax.add_patch(
        FancyArrowPatch(
            points[-2],
            points[-1],
            arrowstyle="->",
            mutation_scale=10,
            linewidth=1.2,
            color=color,
            shrinkA=0,
            shrinkB=0,
        )
    )


def make_pipeline_figure() -> None:
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_facecolor("#FFFFFF")
    fig.patch.set_facecolor("#FFFFFF")

    neutral = {"edge": "#9A9A91", "face": "#F0EEE8", "title_color": "#4B4B47", "subtitle_color": "#696965"}
    purple = {"edge": "#6460FF", "face": "#E9E8F8", "title_color": "#393586", "subtitle_color": "#5A54C8"}
    salmon = {"edge": "#E97952", "face": "#F4E5DF", "title_color": "#7B3020", "subtitle_color": "#A24425"}
    teal = {"edge": "#22B8A8", "face": "#DDF4EF", "title_color": "#075C50", "subtitle_color": "#087564"}

    w, h = 0.21, 0.145
    top_y, mid_y, audit_y, score_y = 0.79, 0.55, 0.315, 0.075
    x1, x2, x3, x4 = 0.035, 0.275, 0.515, 0.755

    dark_box(ax, (x1, top_y), w, h, "Site data", "Metadata, images", **neutral)
    dark_box(ax, (x2, top_y), w, h, "Rule schema", "4 safety rules", **neutral)
    dark_box(ax, (x3, top_y), w, h, "Manifests", "163 / 588 rows", **purple)
    dark_box(ax, (x4, top_y), w, h, "Adapters", "Baseline, Florence", **purple)

    dark_box(ax, (x3, mid_y), w, h, "Audit set", "120 rows", **salmon)
    dark_box(ax, (x4, mid_y), w, h, "Interventions", "Target vs random", **salmon)

    dark_box(ax, (x1, audit_y), w, h, "A/B passes", "Two audit passes", **teal)
    dark_box(ax, (x2, audit_y), w, h, "Disagreements", "12 adjudicated", **teal)
    dark_box(ax, (x3, audit_y), w, h, "Final labels", "120 final labels", **teal)
    dark_box(ax, (0.275, score_y), 0.45, h, "Scores + paper tables", "Accuracy, macro-F1, effects", **teal)

    dark_arrow(ax, [(x1 + w, top_y + h / 2), (x2, top_y + h / 2)])
    dark_arrow(ax, [(x2 + w, top_y + h / 2), (x3, top_y + h / 2)])
    dark_arrow(ax, [(x3 + w, top_y + h / 2), (x4, top_y + h / 2)])
    dark_arrow(ax, [(x3 + w / 2, top_y), (x3 + w / 2, mid_y + h)])
    dark_arrow(ax, [(x4 + w / 2, top_y), (x4 + w / 2, mid_y + h)])
    dark_arrow(ax, [(x3 + w / 2, mid_y), (x3 + w / 2, 0.50), (x1 + w / 2, 0.50), (x1 + w / 2, audit_y + h)])
    dark_arrow(ax, [(x1 + w, audit_y + h / 2), (x2, audit_y + h / 2)])
    dark_arrow(ax, [(x2 + w, audit_y + h / 2), (x3, audit_y + h / 2)])
    dark_arrow(ax, [(x3 + w / 2, audit_y), (x3 + w / 2, score_y + h)])
    dark_arrow(ax, [(x4 + w / 2, mid_y), (x4 + w / 2, 0.255), (0.71, 0.255), (0.71, score_y + h)])
    save(fig, "pipeline_architecture.pdf")


def make_audit_dashboard() -> None:
    summary = json.loads((ROOT / "benchmark" / "annotations" / "human_audit_batch_001_final_labels_summary.json").read_text())
    scores = [row for row in read_csv(ROOT / "results" / "tables" / "human_audit_batch_001_final_label_scores.csv") if row["slice_id"] == "overall"]
    score_by_model = {row["model_id"]: row for row in scores}
    labels = ["compliant", "violation", "uncertain"]
    counts = [summary["final_answer_counts"][label] for label in labels]

    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.45), gridspec_kw={"width_ratios": [0.85, 1.35]})
    ax = axes[0]
    colors = ["#4C78A8", "#E45756", "#8E6C8A"]
    ax.bar(labels, counts, color=colors, width=0.65)
    ax.set_title("Final audit labels (n=120)", fontsize=9, pad=4)
    ax.set_ylabel("Rows", fontsize=8)
    ax.tick_params(axis="both", labelsize=7)
    ax.spines[["top", "right"]].set_visible(False)
    for i, value in enumerate(counts):
        ax.text(i, value + 1.2, str(value), ha="center", fontsize=7)

    ax = axes[1]
    order = [
        ("model_assisted_bootstrap", "Baseline"),
        ("florence_grounding", "Florence"),
        ("ai_annotator_1", "Audit A"),
        ("ai_annotator_2", "Audit B"),
    ]
    x = range(len(order))
    accuracy = [float(score_by_model[key]["accuracy"]) * 100 for key, _ in order]
    macro_f1 = [float(score_by_model[key]["macro_f1"]) * 100 for key, _ in order]
    width = 0.34
    ax.bar([i - width / 2 for i in x], accuracy, width=width, label="Accuracy", color="#4C78A8")
    ax.bar([i + width / 2 for i in x], macro_f1, width=width, label="Macro-F1", color="#F58518")
    ax.set_title("Scores vs final audit labels", fontsize=9, pad=4)
    ax.set_ylim(0, 105)
    ax.set_xticks(list(x), [label for _, label in order], fontsize=7)
    ax.set_ylabel("%", fontsize=8)
    ax.tick_params(axis="y", labelsize=7)
    ax.legend(frameon=False, fontsize=7, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)
    for i, value in enumerate(accuracy):
        ax.text(i - width / 2, value + 1.4, f"{value:.1f}", ha="center", fontsize=6)
    save(fig, "audit_result_dashboard.pdf")


def make_intervention_figure() -> None:
    rows = {row["metric_id"]: row for row in read_csv(ROOT / "results" / "tables" / "pilot_florence_interventions_summary.csv")}
    metrics = [
        ("Answer flip", "targeted_answer_flip_rate", "matched_random_answer_flip_rate"),
        ("Centroid drift", "targeted_mean_centroid_drift", "matched_random_mean_centroid_drift"),
        ("Evidence\nmissing", "targeted_evidence_disappearance_rate", "matched_random_evidence_disappearance_rate"),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.35), gridspec_kw={"width_ratios": [1.25, 0.95]})
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.22, top=0.82, wspace=0.34)

    ax = axes[0]
    x = range(len(metrics))
    width = 0.30
    targeted = [float(rows[t]["value"]) for _, t, _ in metrics]
    random = [float(rows[r]["value"]) for _, _, r in metrics]
    ax.bar([i - width / 2 for i in x], targeted, width=width, label="Targeted", color="#B279A2")
    ax.bar([i + width / 2 for i in x], random, width=width, label="Matched random", color="#72B7B2")
    ax.set_xticks(list(x), [name for name, _, _ in metrics], fontsize=8)
    ax.set_ylabel("Rate / normalized drift", fontsize=8)
    ax.set_ylim(0, 0.46)
    ax.tick_params(axis="y", labelsize=7)
    ax.set_title("A. Mask response", fontsize=9, pad=5)
    ax.legend(frameon=False, fontsize=7, loc="upper right", borderaxespad=0.2)
    ax.spines[["top", "right"]].set_visible(False)
    for idx, value in enumerate(targeted):
        ax.text(idx - width / 2, value + 0.012, f"{value:.2f}", ha="center", fontsize=7)
    for idx, value in enumerate(random):
        ax.text(idx + width / 2, value + 0.012, f"{value:.2f}", ha="center", fontsize=7)

    ax = axes[1]
    paired = [
        ("Answer flip", "paired_answer_flip_rate_difference"),
        ("Centroid drift", "paired_centroid_drift_difference"),
    ]
    y = list(range(len(paired)))
    values = [float(rows[key]["value"]) for _, key in paired]
    lows = [float(rows[key]["ci_low"]) for _, key in paired]
    highs = [float(rows[key]["ci_high"]) for _, key in paired]
    lower = [value - low for value, low in zip(values, lows)]
    upper = [high - value for value, high in zip(values, highs)]
    ax.barh(y, values, color=["#B279A2", "#8E6C8A"], height=0.42)
    ax.errorbar(values, y, xerr=[lower, upper], fmt="none", ecolor="#27313A", elinewidth=0.9, capsize=3)
    ax.axvline(0, color="#6B7280", linewidth=0.7)
    ax.set_yticks(y, [name for name, _ in paired], fontsize=8)
    ax.set_xlim(0, 0.43)
    ax.set_xlabel("Targeted - random", fontsize=8)
    ax.set_title("B. Paired effect (95% CI)", fontsize=9, pad=5)
    ax.tick_params(axis="x", labelsize=7)
    ax.spines[["top", "right"]].set_visible(False)
    for idx, (value, high) in enumerate(zip(values, highs)):
        ax.text(
            min(high + 0.014, 0.415),
            idx,
            f"{value:.2f}",
            va="center",
            fontsize=7,
            color="#1F2933",
        )
    fig.suptitle(
        "Rule-evidence occlusion has larger effects than matched random masking",
        fontsize=9,
        y=0.96,
    )
    save(fig, "intervention_effects_chart.pdf")


def make_rule_slice_figure() -> None:
    rows = [
        row
        for row in read_csv(ROOT / "results" / "tables" / "scaleup_florence_grounding_slices.csv")
        if row["slice_type"] == "rule_id"
    ]
    labels = {
        "fall_harness": "Fall",
        "guardrail_edge": "Guardrail",
        "ppe_hard_hat": "PPE",
        "struck_by_equipment": "Struck-by",
    }
    fig, ax = plt.subplots(figsize=(7.1, 2.2))
    x = range(len(rows))
    accuracy = [float(row["accuracy"]) * 100 for row in rows]
    evidence = [float(row["evidence_presence_rate"]) * 100 for row in rows]
    width = 0.34
    ax.bar([i - width / 2 for i in x], accuracy, width=width, label="Answer accuracy", color="#4C78A8")
    ax.bar([i + width / 2 for i in x], evidence, width=width, label="Evidence present", color="#54A24B")
    ax.set_xticks(list(x), [labels[row["slice_value"]] for row in rows], fontsize=8)
    ax.set_ylabel("%", fontsize=8)
    ax.set_ylim(0, 110)
    ax.tick_params(axis="y", labelsize=7)
    ax.set_title("Scale-up Florence: evidence is usually present while answers remain weak", fontsize=9, pad=4)
    ax.legend(frameon=False, fontsize=7, loc="upper right")
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "scaleup_rule_slice_chart.pdf")


def main() -> int:
    global FIG_DIR
    parser = argparse.ArgumentParser(description="Generate compact paper figures from checked benchmark artifacts.")
    parser.add_argument("--output-dir", default=str(FIG_DIR), help="Directory where figure PDFs are written.")
    args = parser.parse_args()
    FIG_DIR = Path(args.output_dir)

    make_pipeline_figure()
    make_audit_dashboard()
    make_intervention_figure()
    make_rule_slice_figure()
    print(f"Wrote paper figures to {FIG_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
