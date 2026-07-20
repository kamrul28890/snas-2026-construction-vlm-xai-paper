# Disagreement Analysis — human_audit_batch_001

Two independent annotation passes were produced for all 120 rows, using the two
personas defined in `PERSONAS.md`:

- **Annotator A — "The Compliance Officer"**: strict, evidence-first, defaults
  to `uncertain` when anything is unresolved, tight minimal boxes.
- **Annotator B — "The Site Superintendent"**: pragmatic field read, commits to
  a label when the overall scene makes the call clear, contextual boxes.

Neither annotator saw the other's labels while annotating.

## Agreement summary

| Metric | Value |
|---|---|
| Rows | 120 |
| Agreement on `answer_label` | 108 / 120 (90.0%) |
| Disagreements | 12 |
| Pass A distribution | 85 violation / 24 compliant / 11 uncertain |
| Pass B distribution | 81 violation / 35 compliant / 4 uncertain |

Disagreements by rule:

| Rule | Disagreements |
|---|---|
| `guardrail_edge` | 6 |
| `struck_by_equipment` | 4 |
| `ppe_hard_hat` | 1 |
| `fall_harness` | 1 |

No disagreement is a direct `violation` ↔ `compliant` clash driven by looking
at different things in the image — every case traces to one of three
identifiable, explainable sources of divergence. That makes this batch
straightforward to adjudicate: a reviewer isn't choosing between two
contradictory readings of the same evidence, but deciding which *threshold or
definition* should govern the label.

## Why the two personas disagree

### 1. Graded slope vs. protected "edge" (6 of 12 — all `guardrail_edge`)

Rows: `audit_001_0051`, `audit_001_0059`, `audit_001_0068`, `audit_001_0069`,
`audit_001_0072`, `audit_001_0073`.

The rule asks whether a visible elevated edge/opening has a guardrail or
equivalent barrier. All six images show a **graded, sloped, or benched
embankment/excavation wall** rather than a sheer vertical drop — workers
walking or standing on an inclined surface, not at a cliff-like edge.

- **Annotator A** applies the rule literally: any unprotected elevation change
  next to a worker counts as exposure, so a graded slope with no guardrail
  still gets flagged (usually as `violation, ambiguous: yes`, since A
  explicitly notes "the slope grade partly mitigates the drop").
- **Annotator B** applies field judgment: a walkable graded batter is a normal
  site condition that construction crews traverse routinely and doesn't read
  as the kind of "elevated edge" the guardrail rule is aimed at (that rule
  exists for sheer/vertical drops — trench walls, floor openings, wall tops).
  B calls these `compliant, ambiguous: no` — confidently, not hedging.

This is a genuine **rule-scope judgment call**, not a perception disagreement
— both annotators see the same slope. The adjudicator's decision here (does
"elevated edge" include graded slopes?) will likely resolve all six at once,
since they're the same underlying question asked six times.

### 2. Equipment swing-radius / proximity reads (4 of 12 — all `struck_by_equipment`)

Rows: `audit_001_0061`, `audit_001_0089`, `audit_001_0114`, `audit_001_0117`.

The rule asks whether a worker is unsafely close to active heavy equipment.
Distance/depth in a single static frame is inherently hard to judge, and the
prompt's own guidance calls this out as a common ambiguity.

- **Annotator A** hedges to `uncertain` whenever the worker's exact position
  relative to the machine's swing arc, or whether a distant blur is even a
  worker, can't be pinned down with confidence.
- **Annotator B** commits to a read based on equipment orientation and scene
  context (e.g., "worker's off to the side and forward of the machine while
  it's digging, that's a normal working position") — using field experience
  with how excavators actually operate rather than treating the ambiguity as
  disqualifying.

Net effect: A's `uncertain` becomes B's `compliant` in three cases and B's
`compliant` in the fourth (`audit_001_0114`, where A leaned `violation` on a
possible figure between two machines that B read as too faint to count as a
worker at all — the one case in this batch closest to a genuine perception
disagreement, since it hinges on whether a faint shape is a person).

### 3. Hedge vs. commit on borderline visibility (2 of 12 — one `ppe_hard_hat`, one `fall_harness`)

- `audit_001_0015` (ppe_hard_hat): both annotators read the figures as
  probably helmeted; A hedges to `uncertain` on the one unclear headwear, B
  commits to `compliant` on the same evidence.
- `audit_001_0101` (fall_harness): a crew works an elevated slab pour with no
  visible edge nearby. A treats "not near a visible edge" as insufficient
  basis to judge fall-protection need at all (`uncertain`). B treats
  "elevated deck, no harnesses visible on anyone" as enough to call it
  regardless of edge proximity (`violation`).

Both are the same underlying pattern as source #1: a threshold/definition
question (how much visual clarity, or how directly tied to an edge, is
required before committing), not a disagreement about what's visible in the
image.

## Recommendation for adjudication

- The 6 `guardrail_edge` graded-slope cases should be resolved as a **single
  policy decision** (does the rule's "elevated edge" include walkable graded
  slopes/embankments, yes or no) rather than adjudicated row by row — the
  visual facts are consistent across all six.
- The `struck_by_equipment` cases benefit from a similar policy call: how much
  benefit of the doubt to give a worker positioned near, but not obviously
  inside, an equipment's swing arc.
- `audit_001_0114` merits a closer human look, since it's the one case where
  the two annotators may be looking at different things (a possibly-a-worker
  shape) rather than applying a different standard to the same thing.
