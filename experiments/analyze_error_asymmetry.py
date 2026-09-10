"""Break the audit-set errors into safety-relevant categories.

Overall accuracy hides the distinction that matters in a safety setting: a
missed violation and a false alarm are not equally costly. This script builds
the confusion matrix over the adjudicated reference labels and reports missed
violations separately from false alarms.

Writes results/tables/error_asymmetry.csv.
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "results" / "tables" / "human_audit_batch_001_final_label_per_example_scores.csv"
OUT = ROOT / "results" / "tables" / "error_asymmetry.csv"

LABELS = ("compliant", "violation", "uncertain")


def main() -> None:
    rows = list(csv.DictReader(SRC.open(encoding="utf-8")))
    models = sorted({r["model_id"] for r in rows})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["model_id", "n", "missed_violations", "true_violations",
                         "missed_violation_rate", "false_alarms", "true_compliant",
                         "false_alarm_rate", "uncertain_predicted", "true_uncertain"])

        for model in models:
            subset = [r for r in rows if r["model_id"] == model]
            matrix = {(t, p): 0 for t in LABELS for p in LABELS}
            for r in subset:
                truth = r["final_answer_label"].strip().lower()
                pred = r["predicted_answer"].strip().lower()
                if truth in LABELS and pred in LABELS:
                    matrix[(truth, pred)] += 1

            true_viol = sum(matrix[("violation", p)] for p in LABELS)
            # A missed violation is a real violation reported as compliant.
            missed = matrix[("violation", "compliant")]
            true_comp = sum(matrix[("compliant", p)] for p in LABELS)
            false_alarm = matrix[("compliant", "violation")]
            true_unc = sum(matrix[("uncertain", p)] for p in LABELS)
            pred_unc = sum(matrix[(t, "uncertain")] for t in LABELS)

            writer.writerow([
                model, len(subset), missed, true_viol,
                f"{missed / true_viol:.6f}" if true_viol else "",
                false_alarm, true_comp,
                f"{false_alarm / true_comp:.6f}" if true_comp else "",
                pred_unc, true_unc,
            ])

            print(f"\n{model}  (n={len(subset)})")
            print("            pred:  " + "".join(f"{p:>11}" for p in LABELS))
            for t in LABELS:
                print(f"  truth {t:>9}: " + "".join(f"{matrix[(t, p)]:>11}" for p in LABELS))
            if true_viol:
                print(f"  missed violations : {missed}/{true_viol} = {missed / true_viol:.1%}")
            if true_comp:
                print(f"  false alarms      : {false_alarm}/{true_comp} = {false_alarm / true_comp:.1%}")
            print(f"  answered uncertain: {pred_unc} (reference has {true_unc})")

    print(f"\nwrote {OUT.relative_to(ROOT).as_posix()}")
    report_agreement(rows)


def report_agreement(rows: list[dict[str, str]]) -> None:
    """Chance-corrected agreement between the two independent audit passes.

    Raw percent agreement overstates consistency when one label dominates, which
    it does here. Cohen's kappa corrects for agreement expected by chance.
    """
    passes: dict[str, dict[str, str]] = {}
    for r in rows:
        passes.setdefault(r["model_id"], {})[r["audit_id"]] = r["predicted_answer"].strip().lower()

    a = passes.get("ai_annotator_1", {})
    b = passes.get("ai_annotator_2", {})
    shared = sorted(set(a) & set(b))
    if not shared:
        return

    observed = sum(1 for i in shared if a[i] == b[i]) / len(shared)
    labels = sorted({a[i] for i in shared} | {b[i] for i in shared})
    expected = sum((sum(1 for i in shared if a[i] == label) / len(shared))
                   * (sum(1 for i in shared if b[i] == label) / len(shared))
                   for label in labels)
    kappa = (observed - expected) / (1 - expected) if expected < 1 else float("nan")

    print("\ninter-pass agreement on the audit set")
    print(f"  rows compared      {len(shared)}")
    print(f"  raw agreement      {observed:.3f}")
    print(f"  expected by chance {expected:.3f}")
    print(f"  Cohen's kappa      {kappa:.3f}")

    out = ROOT / "results" / "tables" / "audit_pass_agreement.csv"
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["n_rows", "raw_agreement", "expected_agreement", "cohens_kappa"])
        writer.writerow([len(shared), f"{observed:.6f}", f"{expected:.6f}", f"{kappa:.6f}"])
    print(f"wrote {out.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
