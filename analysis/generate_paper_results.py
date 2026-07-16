"""Generate the frozen SNAS paper results, tables, figures, and audit manifest."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import math
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
from PIL import Image

from paper_analysis import (
    as_bool,
    bootstrap_ci,
    holm_adjust,
    paired_bootstrap_difference,
    sha256_file,
    wilcoxon_with_effect,
)


def parse_args() -> argparse.Namespace:
    paper_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-root", type=Path, default=paper_root)
    parser.add_argument(
        "--source-repo",
        type=Path,
        default=paper_root.parent / "Explainable-AI-Mustafa-Abdallah",
    )
    return parser.parse_args()


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype={"image_id": str})


def parse_bool_columns(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    frame = frame.copy()
    for column in columns:
        if column in frame:
            frame[column] = frame[column].map(as_bool)
    return frame


def format_percent_ci(row: pd.Series) -> str:
    return f"{row.point * 100:.1f}\\% [{row.lo * 100:.1f}, {row.hi * 100:.1f}]"


def format_decimal_ci(row: pd.Series) -> str:
    return f"{row.point:.3f} [{row.lo:.3f}, {row.hi:.3f}]"


def git_output(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, text=True, capture_output=True, check=True
    )
    return result.stdout.strip()


def set_plot_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman"],
            "font.size": 9,
            "axes.titlesize": 9,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def save_figure(fig: plt.Figure, base_path: Path) -> None:
    base_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(base_path.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(base_path.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.close(fig)


def make_pipeline_figure(path: Path) -> None:
    set_plot_style()
    fig, ax = plt.subplots(figsize=(7.2, 2.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    labels = [
        ("Site image", "Held-out\ntest image"),
        ("Florence-2", "Worker and object\ngrounding"),
        ("Decision rule", "Person-relative\ngeometry"),
        ("Intervention", "Targeted or matched\nrandom mask"),
        ("Audit outcomes", "Verdict, drift,\ndisappearance"),
    ]
    colors = ["#e9ecef", "#d9eaf7", "#f3e3ce", "#e2efda", "#eadcf0"]
    width = 0.165
    xs = np.linspace(0.01, 0.825, len(labels))
    for index, ((title, subtitle), x, color) in enumerate(zip(labels, xs, colors)):
        box = patches.FancyBboxPatch(
            (x, 0.34),
            width,
            0.38,
            boxstyle="round,pad=0.012,rounding_size=0.015",
            linewidth=0.9,
            edgecolor="#222222",
            facecolor=color,
        )
        ax.add_patch(box)
        ax.text(
            x + width / 2,
            0.59,
            title,
            ha="center",
            va="center",
            weight="bold",
            fontsize=8.2,
        )
        ax.text(
            x + width / 2,
            0.45,
            subtitle,
            ha="center",
            va="center",
            fontsize=6.2,
            linespacing=1.05,
        )
        if index < len(labels) - 1:
            ax.annotate(
                "",
                xy=(xs[index + 1] - 0.005, 0.53),
                xytext=(x + width + 0.005, 0.53),
                arrowprops={"arrowstyle": "->", "lw": 1.0, "color": "#333333"},
            )
    ax.text(
        0.5,
        0.13,
        "Deterministic geometry converts VLM grounding into the verdict; the audit does not evaluate native free-form VQA.",
        ha="center",
        va="center",
        fontsize=7.2,
    )
    save_figure(fig, path)


def make_intervention_figure(results: pd.DataFrame, path: Path) -> None:
    set_plot_style()
    metrics = [
        ("answer_change", "Answer change", True),
        ("centroid_drift", "Centroid drift", False),
        ("disappearance", "Disappearance", True),
    ]
    colors = {"Targeted": "#1f4e79", "Matched random": "#b45f06"}
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.55))
    for ax, (metric_id, title, percent) in zip(axes, metrics):
        subset = results[results.metric_id == metric_id].set_index("condition")
        labels = ["Targeted", "Matched random"]
        points = [subset.loc[label, "point"] for label in labels]
        lower = [subset.loc[label, "point"] - subset.loc[label, "lo"] for label in labels]
        upper = [subset.loc[label, "hi"] - subset.loc[label, "point"] for label in labels]
        x = np.arange(2)
        ax.bar(x, points, color=[colors[label] for label in labels], width=0.62)
        ax.errorbar(x, points, yerr=[lower, upper], fmt="none", ecolor="#222222", capsize=3, lw=1)
        ax.set_xticks(x, ["Targeted", "Matched\nrandom"])
        ax.set_title(title, weight="bold")
        ax.grid(axis="y", alpha=0.25, linewidth=0.6)
        if percent:
            ax.set_ylim(0, max(0.12, max(np.asarray(points) + np.asarray(upper)) * 1.2))
            ax.yaxis.set_major_formatter(lambda value, position: f"{value * 100:.0f}%")
            for xpos, point in zip(x, points):
                ax.text(xpos, point + ax.get_ylim()[1] * 0.035, f"{point * 100:.1f}%", ha="center", fontsize=8)
        else:
            ax.set_ylim(0, max(np.asarray(points) + np.asarray(upper)) * 1.2)
            for xpos, point in zip(x, points):
                ax.text(xpos, point + ax.get_ylim()[1] * 0.035, f"{point:.3f}", ha="center", fontsize=8)
    fig.suptitle("Targeted occlusion versus five-seed, same-size random-location control", weight="bold", y=1.03)
    fig.tight_layout()
    save_figure(fig, path)


def make_size_bias_figure(size_summary: pd.DataFrame, path: Path) -> None:
    set_plot_style()
    order = ["Small", "Medium", "Large"]
    summary = size_summary.set_index("size_band").loc[order]
    x = np.arange(len(order))
    width = 0.34
    fig, ax = plt.subplots(figsize=(5.5, 2.9))
    ax.bar(x - width / 2, summary.iou_failure, width, label="IoU < 0.3", color="#7f3c8d")
    ax.bar(x + width / 2, summary.centroid_relocation, width, label="Centroid drift > 0.2", color="#11a579")
    ax.set_xticks(x, [f"{label}\n(n={int(summary.loc[label, 'images'])})" for label in order])
    ax.set_ylabel("Mean per-image failure rate")
    ax.yaxis.set_major_formatter(lambda value, position: f"{value * 100:.0f}%")
    ax.set_ylim(0, max(summary.iou_failure.max(), summary.centroid_relocation.max()) * 1.28)
    ax.grid(axis="y", alpha=0.25, linewidth=0.6)
    ax.legend(frameon=False, ncol=2, loc="upper right")
    ax.set_title("IoU overstates explanation movement for small grounding boxes", weight="bold")
    for positions, values in [
        (x - width / 2, summary.iou_failure),
        (x + width / 2, summary.centroid_relocation),
    ]:
        for xpos, value in zip(positions, values):
            ax.text(xpos, value + 0.008, f"{value * 100:.1f}%", ha="center", fontsize=8)
    fig.tight_layout()
    save_figure(fig, path)


def apply_mask(image: Image.Image, box: list[int]) -> Image.Image:
    out = image.convert("RGB").copy()
    x0, y0, x1, y1 = box
    out.paste(Image.new("RGB", (x1 - x0, y1 - y0), (0, 0, 0)), (x0, y0))
    return out


def load_one_source_image(source_repo: Path, image_id: str) -> Image.Image:
    source_module = source_repo / "pilot" / "src"
    sys.path.insert(0, str(source_module))
    from xai_pilot.data import load_construction_site

    for row in load_construction_site(split="test", streaming=True):
        if str(row["image_id"]).zfill(7) == image_id:
            return row["image"].convert("RGB")
    raise RuntimeError(f"Could not reload qualitative image {image_id}")


def draw_box(ax, box, color: str, label: str) -> None:
    x0, y0, x1, y1 = box
    ax.add_patch(
        patches.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, edgecolor=color, linewidth=2.2)
    )
    ax.text(
        x0,
        max(0, y0 - 4),
        label,
        color="white",
        fontsize=7,
        bbox={"facecolor": color, "alpha": 0.85, "pad": 1.5, "edgecolor": "none"},
    )


def make_qualitative_figure(matched: pd.DataFrame, source_repo: Path, path: Path, metadata_path: Path) -> None:
    candidates = matched[
        (matched.condition == "targeted")
        & (~matched.answer_changed)
        & (~matched.object_disappeared)
        & (~matched.worker_lost)
        & matched.object_centroid_drift.notna()
        & (matched.object_centroid_drift > 0.2)
        & (matched.target_area_fraction < 0.15)
    ].sort_values("object_centroid_drift", ascending=False)
    if candidates.empty:
        raise RuntimeError("No valid hidden-drift qualitative example was found.")
    targeted = candidates.iloc[0]
    random_candidates = matched[
        (matched.image_id == targeted.image_id)
        & (matched.condition == "random_matched")
        & (matched.mask_target_iou <= 0.05)
        & (~matched.object_disappeared)
    ].copy()
    if random_candidates.empty:
        random_candidates = matched[
            (matched.image_id == targeted.image_id) & (matched.condition == "random_matched")
        ].copy()
    random_row = random_candidates.sort_values("object_centroid_drift").iloc[len(random_candidates) // 2]

    image = load_one_source_image(source_repo, targeted.image_id)
    target_box = json.loads(targeted.target_box)
    target_mask = json.loads(targeted.mask_box)
    random_mask = json.loads(random_row.mask_box)
    target_objects = json.loads(targeted.perturbed_object_boxes)
    random_objects = json.loads(random_row.perturbed_object_boxes)
    target_image = apply_mask(image, target_mask)
    random_image = apply_mask(image, random_mask)

    set_plot_style()
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.75))
    panels = [
        (image, "Baseline", target_box, "Baseline object", "#11a579"),
        (
            target_image,
            f"Targeted: answer stable\ndrift = {targeted.object_centroid_drift:.3f}",
            target_objects[0] if target_objects else None,
            "New object",
            "#d62728",
        ),
        (
            random_image,
            f"Matched random: {'changed' if random_row.answer_changed else 'stable'}\ndrift = {random_row.object_centroid_drift:.3f}",
            random_objects[0] if random_objects else None,
            "New object",
            "#1f4e79",
        ),
    ]
    for ax, (panel_image, title, box, label, color) in zip(axes, panels):
        ax.imshow(panel_image)
        if box:
            draw_box(ax, box, color, label)
        ax.set_title(title, weight="bold")
        ax.axis("off")
    fig.suptitle("Stable verdict, relocated visual evidence", weight="bold", y=1.02)
    fig.tight_layout()
    save_figure(fig, path)
    metadata_path.write_text(
        json.dumps(
            {
                "image_id": targeted.image_id,
                "primary_class": targeted.primary_class,
                "assigned_rule_id": targeted.assigned_rule_id,
                "targeted_answer_changed": bool(targeted.answer_changed),
                "targeted_centroid_drift": float(targeted.object_centroid_drift),
                "random_seed": int(random_row.seed),
                "random_answer_changed": bool(random_row.answer_changed),
                "random_centroid_drift": float(random_row.object_centroid_drift),
                "random_mask_target_iou": float(random_row.mask_target_iou),
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    paper_root = args.paper_root.resolve()
    source_repo = args.source_repo.resolve()
    pilot = source_repo / "pilot"
    outputs = paper_root / "analysis" / "outputs"
    generated = paper_root / "generated"
    figures = paper_root / "figures"
    outputs.mkdir(parents=True, exist_ok=True)
    generated.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)

    protocol_path = paper_root / "analysis" / "protocol.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    n_boot = int(protocol["statistics"]["bootstrap_resamples"])
    bootstrap_seed = int(protocol["statistics"]["bootstrap_seed"])
    min_n = int(protocol["data"]["minimum_stable_subgroup_n"])

    matched_path = outputs / "matched_random_occlusion.csv"
    audit_path = outputs / "sample_audit.csv"
    matched = parse_bool_columns(
        read_csv(matched_path),
        [
            "answer_changed",
            "genuine_answer_changed",
            "object_disappeared",
            "worker_lost",
            "flip_due_to_worker_loss",
        ],
    )
    audit = parse_bool_columns(read_csv(audit_path), ["has_worker_box", "has_object_box"])
    if len(matched) != 948 or matched[["image_id", "condition", "seed"]].duplicated().any():
        raise RuntimeError("Matched-control artifact failed row-count or uniqueness validation.")
    if not np.allclose(matched.target_area_fraction, matched.mask_area_fraction, rtol=0, atol=0):
        raise RuntimeError("Matched-control mask areas are not exactly equal to target areas.")

    result_rows: list[dict] = []

    def add_result(metric_id: str, label: str, condition: str, values, *, notes: str = "", **extra) -> dict:
        ci = bootstrap_ci(values, n_boot=n_boot, seed=bootstrap_seed)
        row = {
            "metric_id": metric_id,
            "label": label,
            "condition": condition,
            **ci,
            "notes": notes,
            "p_value": extra.get("p_value", math.nan),
            "effect_size": extra.get("effect_size", math.nan),
            "effect_name": extra.get("effect_name", ""),
        }
        result_rows.append(row)
        return row

    sample_manifest = read_csv(pilot / "data" / "pilot_samples.csv")
    if len(sample_manifest) != 163 or sample_manifest.image_id.duplicated().any():
        raise RuntimeError("Sample manifest must contain 163 unique image IDs.")
    if set(sample_manifest.split) != {"test"}:
        raise RuntimeError("Paper sample contains a non-test split row.")

    class_order = ["compliant", "ppe_violation", "fall_hazard", "struck_by_risk"]
    display_classes = {
        "compliant": "Compliant",
        "ppe_violation": "PPE violation",
        "fall_hazard": "Fall hazard",
        "struck_by_risk": "Struck-by risk",
    }
    dataset_rows = []
    for class_name in class_order:
        group = sample_manifest[sample_manifest.primary_class == class_name]
        dataset_rows.append(
            {
                "primary_class": class_name,
                "display_class": display_classes[class_name],
                "n": len(group),
                "assigned_rules": ", ".join(sorted(group.assigned_rule_id.unique())),
                "status": "Stable subgroup" if len(group) >= min_n else "Exploratory",
            }
        )
    dataset_summary = pd.DataFrame(dataset_rows)
    dataset_summary.to_csv(outputs / "dataset_summary.csv", index=False)

    baseline = read_csv(pilot / "results" / "baseline_predictions.csv")
    truth_positive = baseline.primary_class != "compliant"
    predicted_positive = baseline.answer.isin(["violation", "hazard"])
    add_result("task_sensitivity", "Violation sensitivity", "Overall", predicted_positive[truth_positive].astype(float))
    add_result("task_specificity", "Compliant specificity", "Overall", (~predicted_positive[~truth_positive]).astype(float))

    for condition, filename in [
        ("Area baseline", "region_extraction.csv"),
        ("Rule-aware", "region_extraction_rule_aware.csv"),
    ]:
        regions = read_csv(pilot / "results" / filename)
        model_regions = regions[regions.top_region_source == "model"]
        add_result(
            "worker_top1",
            "Worker selected as top region",
            condition,
            model_regions.top_region_label.str.lower().eq("worker").astype(float),
        )

    descriptive = parse_bool_columns(
        read_csv(pilot / "results" / "descriptive_accuracy_rule_aware_wlc.csv"),
        ["answer_changed_top1", "flip_due_to_worker_loss_top1"],
    )
    add_result(
        "rule_aware_flip_raw",
        "Rule-aware top-region answer change",
        "Raw",
        descriptive.answer_changed_top1.astype(float),
    )
    add_result(
        "rule_aware_flip_corrected",
        "Rule-aware top-region answer change",
        "Worker-loss corrected",
        (descriptive.answer_changed_top1 & ~descriptive.flip_due_to_worker_loss_top1).astype(float),
    )

    targeted = matched[matched.condition == "targeted"].set_index("image_id")
    random_rows = matched[matched.condition == "random_matched"]
    random_by_image = random_rows.groupby("image_id").agg(
        answer_change=("answer_changed", "mean"),
        genuine_change=("genuine_answer_changed", "mean"),
        centroid_drift=("object_centroid_drift", "mean"),
        disappearance=("object_disappeared", "mean"),
        worker_loss=("worker_lost", "mean"),
        mean_target_overlap=("mask_target_iou", "mean"),
    )
    add_result("answer_change", "Answer change", "Targeted", targeted.answer_changed.astype(float))
    add_result("answer_change", "Answer change", "Matched random", random_by_image.answer_change)
    add_result(
        "genuine_answer_change",
        "Worker-loss-corrected answer change",
        "Targeted",
        targeted.genuine_answer_changed.astype(float),
    )
    add_result(
        "genuine_answer_change",
        "Worker-loss-corrected answer change",
        "Matched random",
        random_by_image.genuine_change,
    )
    add_result("centroid_drift", "Normalized centroid drift", "Targeted", targeted.object_centroid_drift)
    add_result("centroid_drift", "Normalized centroid drift", "Matched random", random_by_image.centroid_drift)
    add_result("disappearance", "Explanation disappearance", "Targeted", targeted.object_disappeared.astype(float))
    add_result("disappearance", "Explanation disappearance", "Matched random", random_by_image.disappearance)

    paired_drift = pd.concat(
        [
            targeted.object_centroid_drift.rename("targeted"),
            random_by_image.centroid_drift.rename("random"),
        ],
        axis=1,
    ).dropna()
    drift_difference = paired_bootstrap_difference(
        paired_drift.targeted,
        paired_drift.random,
        n_boot=n_boot,
        seed=bootstrap_seed,
    )
    drift_test = wilcoxon_with_effect(paired_drift.targeted, paired_drift.random)

    paired_answer = pd.concat(
        [
            targeted.answer_changed.astype(float).rename("targeted"),
            random_by_image.answer_change.rename("random"),
        ],
        axis=1,
    ).dropna()
    answer_difference = paired_bootstrap_difference(
        paired_answer.targeted,
        paired_answer.random,
        n_boot=n_boot,
        seed=bootstrap_seed,
    )
    answer_test = wilcoxon_with_effect(paired_answer.targeted, paired_answer.random)
    answer_test["holm_p"], drift_test["holm_p"] = holm_adjust(
        [answer_test["p_value"], drift_test["p_value"]]
    )

    low_overlap_rows = random_rows[random_rows.mask_target_iou <= 0.05]
    low_overlap_by_image = low_overlap_rows.groupby("image_id").agg(
        answer_change=("answer_changed", "mean"),
        centroid_drift=("object_centroid_drift", "mean"),
        disappearance=("object_disappeared", "mean"),
        placements=("seed", "size"),
    )
    add_result(
        "answer_change_sensitivity",
        "Answer change in low-overlap matched controls",
        "Matched random, mask-target IoU <= 0.05",
        low_overlap_by_image.answer_change,
        notes="Sensitivity analysis; 140 images retained.",
    )

    sweep = parse_bool_columns(
        read_csv(pilot / "results" / "robustness_sweep.csv"),
        ["answer_changed", "object_disappeared"],
    )
    box_audit = audit[audit.has_object_box].copy()
    box_audit["size_band"] = pd.qcut(
        box_audit.target_area_fraction,
        3,
        labels=["Small", "Medium", "Large"],
    )
    stable = sweep[sweep.perturbation != "occlude_targeted"].merge(
        box_audit[["image_id", "size_band"]], on="image_id", how="inner"
    )
    stable = stable[(~stable.answer_changed) & stable.object_box_iou.notna()].copy()
    stable["iou_failure"] = stable.object_box_iou < float(protocol["outcomes"]["iou_drift_threshold"])
    stable["centroid_relocation"] = (
        stable.object_centroid_drift > float(protocol["outcomes"]["genuine_relocation_threshold"])
    )
    per_image_size = stable.groupby(["image_id", "size_band"], observed=True).agg(
        stable_conditions=("iou_failure", "size"),
        iou_failure=("iou_failure", "mean"),
        centroid_relocation=("centroid_relocation", "mean"),
        mean_iou=("object_box_iou", "mean"),
        mean_centroid_drift=("object_centroid_drift", "mean"),
    ).reset_index()
    size_summary = per_image_size.groupby("size_band", observed=True).agg(
        images=("image_id", "size"),
        iou_failure=("iou_failure", "mean"),
        centroid_relocation=("centroid_relocation", "mean"),
        mean_iou=("mean_iou", "mean"),
        mean_centroid_drift=("mean_centroid_drift", "mean"),
    ).reset_index()
    size_summary.to_csv(outputs / "size_bias_summary.csv", index=False)
    add_result("stable_iou_failure", "Stable-answer IoU failure", "Per-image mean", per_image_size.iou_failure)
    add_result(
        "stable_centroid_relocation",
        "Stable-answer genuine relocation",
        "Per-image mean",
        per_image_size.centroid_relocation,
    )

    results = pd.DataFrame(result_rows)
    results.to_csv(outputs / "paper_results.csv", index=False)

    table_dataset = [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Held-Out Test Sample}",
        "\\label{tab:dataset}",
        "\\begin{tabular}{@{}lrrl@{}}",
        "\\toprule",
        "Class & \\textit{n} & Share & Status \\\\",
        "\\midrule",
    ]
    for row in dataset_summary.itertuples():
        escaped = row.display_class.replace("_", "\\_")
        table_dataset.append(f"{escaped} & {row.n} & {row.n / len(sample_manifest) * 100:.1f}\\% & {row.status} \\\\")
    table_dataset.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}"])
    (generated / "table_dataset.tex").write_text("\n".join(table_dataset) + "\n", encoding="ascii")

    result_index = results.set_index(["metric_id", "condition"])
    main_table = [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Primary Intervention Results with Bootstrap 95\\% Confidence Intervals}",
        "\\label{tab:primary-results}",
        "\\begin{tabular}{@{}lcc@{}}",
        "\\toprule",
        "Outcome & Targeted & Matched random \\\\",
        "\\midrule",
    ]
    for metric_id, label, formatter in [
        ("answer_change", "Answer change", format_percent_ci),
        ("genuine_answer_change", "Corrected answer change", format_percent_ci),
        ("centroid_drift", "Centroid drift", format_decimal_ci),
        ("disappearance", "Disappearance", format_percent_ci),
    ]:
        target_row = result_index.loc[(metric_id, "Targeted")]
        random_row = result_index.loc[(metric_id, "Matched random")]
        main_table.append(f"{label} & {formatter(target_row)} & {formatter(random_row)} \\\\")
    main_table.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\begin{minipage}{0.94\\linewidth}",
            "\\vspace{2pt}\\footnotesize Note. Random estimates average five same-size placements per image. "
            f"Targeted minus random answer change = {answer_difference['point'] * 100:.1f} percentage points "
            f"(95\\% CI [{answer_difference['lo'] * 100:.1f}, {answer_difference['hi'] * 100:.1f}]); "
            f"centroid-drift difference = {drift_difference['point']:.3f} "
            f"(95\\% CI [{drift_difference['lo']:.3f}, {drift_difference['hi']:.3f}], "
            f"Wilcoxon \\textit{{p}} < .001, rank-biserial \\textit{{r}} = {drift_test['effect_size']:.3f}, "
            f"\\textit{{n}} = {drift_test['n']}).",
            "\\end{minipage}",
            "\\end{table}",
        ]
    )
    (generated / "table_main_results.tex").write_text("\n".join(main_table) + "\n", encoding="ascii")

    make_pipeline_figure(figures / "pipeline_and_intervention")
    make_intervention_figure(results, figures / "targeted_vs_matched_random")
    make_size_bias_figure(size_summary, figures / "metric_validity_size_bias")
    make_qualitative_figure(
        matched,
        source_repo,
        figures / "qualitative_hidden_drift",
        outputs / "qualitative_example.json",
    )

    source_artifacts = [
        pilot / "data" / "pilot_samples.csv",
        pilot / "results" / "baseline_predictions.csv",
        pilot / "results" / "region_extraction.csv",
        pilot / "results" / "region_extraction_rule_aware.csv",
        pilot / "results" / "descriptive_accuracy_rule_aware_wlc.csv",
        pilot / "results" / "robustness_sweep.csv",
        pilot / "src" / "xai_pilot" / "config.py",
        pilot / "src" / "xai_pilot" / "inference.py",
        pilot / "src" / "xai_pilot" / "regions.py",
        pilot / "src" / "xai_pilot" / "metrics" / "robustness.py",
        protocol_path,
        matched_path,
        audit_path,
    ]
    manifest = {
        "protocol_version": protocol["protocol_version"],
        "source_repository": {
            "commit": git_output(source_repo, "rev-parse", "HEAD"),
            "branch": git_output(source_repo, "branch", "--show-current"),
            "dirty": bool(git_output(source_repo, "status", "--porcelain")),
            "status": git_output(source_repo, "status", "--porcelain").splitlines(),
        },
        "software": {
            package: importlib.metadata.version(package)
            for package in ["numpy", "pandas", "scipy", "matplotlib", "Pillow", "torch", "transformers", "datasets"]
        },
        "artifacts": [
            {
                "path": str(path.relative_to(source_repo) if path.is_relative_to(source_repo) else path.relative_to(paper_root)),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in source_artifacts
        ],
        "validation": {
            "sample_rows": len(sample_manifest),
            "matched_intervention_rows": len(matched),
            "matched_images": int(matched.image_id.nunique()),
            "targeted_rows": int((matched.condition == "targeted").sum()),
            "random_rows": int((matched.condition == "random_matched").sum()),
            "exact_area_match": True,
            "random_rows_with_mask_target_iou_le_0_05": float((random_rows.mask_target_iou <= 0.05).mean()),
        },
    }
    (outputs / "artifact_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    summary = {
        "primary_results": {
            "targeted_answer_change": result_index.loc[("answer_change", "Targeted")].to_dict(),
            "matched_random_answer_change": result_index.loc[("answer_change", "Matched random")].to_dict(),
            "targeted_centroid_drift": result_index.loc[("centroid_drift", "Targeted")].to_dict(),
            "matched_random_centroid_drift": result_index.loc[("centroid_drift", "Matched random")].to_dict(),
            "answer_difference": answer_difference,
            "answer_test": answer_test,
            "drift_difference": drift_difference,
            "drift_test": drift_test,
        },
        "validity": {
            "per_image_iou_failure": result_index.loc[("stable_iou_failure", "Per-image mean")].to_dict(),
            "per_image_centroid_relocation": result_index.loc[("stable_centroid_relocation", "Per-image mean")].to_dict(),
            "size_bands": size_summary.to_dict(orient="records"),
        },
    }
    (outputs / "paper_results.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    summary_lines = [
        "# Generated Paper Results",
        "",
        "All values below were generated from frozen CSV artifacts; none were copied from prose reports.",
        "",
        f"- Targeted answer change: {result_index.loc[('answer_change', 'Targeted'), 'point']:.1%}.",
        f"- Matched-random answer change: {result_index.loc[('answer_change', 'Matched random'), 'point']:.1%}.",
        f"- Paired answer-change difference: {answer_difference['point']:.1%} "
        f"(95% CI [{answer_difference['lo']:.1%}, {answer_difference['hi']:.1%}]).",
        f"- Targeted centroid drift: {result_index.loc[('centroid_drift', 'Targeted'), 'point']:.3f}.",
        f"- Matched-random centroid drift: {result_index.loc[('centroid_drift', 'Matched random'), 'point']:.3f}.",
        f"- Paired drift difference: {drift_difference['point']:.3f} "
        f"(95% CI [{drift_difference['lo']:.3f}, {drift_difference['hi']:.3f}]), "
        f"Wilcoxon p={drift_test['p_value']:.3g}, rank-biserial r={drift_test['effect_size']:.3f}.",
        f"- Stable-answer IoU failure, per-image mean: {result_index.loc[('stable_iou_failure', 'Per-image mean'), 'point']:.1%}.",
        f"- Stable-answer centroid relocation, per-image mean: {result_index.loc[('stable_centroid_relocation', 'Per-image mean'), 'point']:.1%}.",
        f"- Same-size random rows meeting mask-target IoU <= 0.05: {(random_rows.mask_target_iou <= 0.05).mean():.1%}.",
        "",
        "The control is conservative for very large target boxes where a non-overlapping same-size placement is geometrically impossible.",
    ]
    (outputs / "analysis_summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"Generated {len(results)} result rows, 2 LaTeX tables, and 4 figures.")
    print(f"Primary answer-change difference: {answer_difference['point']:.1%}")
    print(f"Primary drift difference: {drift_difference['point']:.3f}; p={drift_test['p_value']:.3g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
