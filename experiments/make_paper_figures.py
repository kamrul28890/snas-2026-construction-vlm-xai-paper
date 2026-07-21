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


def make_pipeline_figure() -> None:
    fig, ax = plt.subplots(figsize=(7.1, 2.55))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    nodes = [
        ((0.02, 0.58), 0.14, 0.28, "ConstructionSite\nmetadata + images", COLORS["data"]),
        ((0.19, 0.58), 0.14, 0.28, "Rule schema\n4 safety rules", COLORS["data"]),
        ((0.36, 0.58), 0.14, 0.28, "Manifests\n163 pilot / 588 scale", COLORS["annotation"]),
        ((0.53, 0.58), 0.14, 0.28, "Adapters\nbaselines + Florence", COLORS["model"]),
        ((0.70, 0.58), 0.14, 0.28, "Interventions\ntargeted vs random", COLORS["intervention"]),
        ((0.86, 0.58), 0.12, 0.28, "Scores +\npaper tables", COLORS["score"]),
    ]
    for xy, width, height, text, color in nodes:
        box(ax, xy, width, height, text, color)
    for i in range(len(nodes) - 1):
        x1 = nodes[i][0][0] + nodes[i][1]
        y1 = nodes[i][0][1] + nodes[i][2] / 2
        x2 = nodes[i + 1][0][0]
        y2 = nodes[i + 1][0][1] + nodes[i + 1][2] / 2
        arrow(ax, (x1, y1), (x2, y2))

    audit_nodes = [
        ((0.18, 0.17), 0.18, 0.23, "Prioritized audit\n120 rows", COLORS["annotation"], 7.2),
        ((0.40, 0.17), 0.18, 0.23, "Role-conditioned\nA/B audit passes", COLORS["annotation"], 7.2),
        ((0.62, 0.17), 0.15, 0.23, "12 disagreements\nadjudicated", COLORS["intervention"], 7.0),
        ((0.81, 0.17), 0.17, 0.23, "Final labels\n108 consensus\n12 adjudicated", COLORS["score"], 6.8),
    ]
    for xy, width, height, text, color, fontsize in audit_nodes:
        box(ax, xy, width, height, text, color, fontsize=fontsize)
    for i in range(len(audit_nodes) - 1):
        x1 = audit_nodes[i][0][0] + audit_nodes[i][1]
        y1 = audit_nodes[i][0][1] + audit_nodes[i][2] / 2
        x2 = audit_nodes[i + 1][0][0]
        y2 = audit_nodes[i + 1][0][1] + audit_nodes[i + 1][2] / 2
        arrow(ax, (x1, y1), (x2, y2))
    arrow(ax, (0.43, 0.58), (0.27, 0.40), "#8A6F3D")
    arrow(ax, (0.895, 0.40), (0.92, 0.58), "#8A6F3D")
    ax.text(0.02, 0.045, "All outputs use normalized JSONL/CSV schemas and SHA-256 release manifests.", fontsize=7, color="#4B5563")
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
        ("model_assisted_bootstrap", "Bootstrap"),
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
        ("Evidence disappear", "targeted_evidence_disappearance_rate", "matched_random_evidence_disappearance_rate"),
    ]
    fig, ax = plt.subplots(figsize=(7.1, 2.2))
    x = range(len(metrics))
    width = 0.34
    targeted = [float(rows[t]["value"]) for _, t, _ in metrics]
    random = [float(rows[r]["value"]) for _, _, r in metrics]
    ax.bar([i - width / 2 for i in x], targeted, width=width, label="Targeted", color="#B279A2")
    ax.bar([i + width / 2 for i in x], random, width=width, label="Matched random", color="#72B7B2")
    ax.set_xticks(list(x), [name for name, _, _ in metrics], fontsize=8)
    ax.set_ylabel("Rate / normalized drift", fontsize=8)
    ax.set_ylim(0, 0.46)
    ax.tick_params(axis="y", labelsize=7)
    ax.set_title("Rule-evidence occlusion has larger effects than matched random masking", fontsize=9, pad=4)
    ax.legend(frameon=False, fontsize=7, loc="upper right")
    ax.spines[["top", "right"]].set_visible(False)
    for idx, value in enumerate(targeted):
        ax.text(idx - width / 2, value + 0.012, f"{value:.2f}", ha="center", fontsize=7)
    for idx, value in enumerate(random):
        ax.text(idx + width / 2, value + 0.012, f"{value:.2f}", ha="center", fontsize=7)
    diff = float(rows["paired_answer_flip_rate_difference"]["value"])
    lo = float(rows["paired_answer_flip_rate_difference"]["ci_low"])
    hi = float(rows["paired_answer_flip_rate_difference"]["ci_high"])
    ax.text(
        0.03,
        0.94,
        f"Paired answer-flip diff: {diff:.2f} (95% CI {lo:.2f}, {hi:.2f})",
        transform=ax.transAxes,
        fontsize=7,
        color="#374151",
        va="top",
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
