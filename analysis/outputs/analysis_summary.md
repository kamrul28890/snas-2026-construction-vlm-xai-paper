# Generated Paper Results

All values below were generated from frozen CSV artifacts; none were copied from prose reports.

- Targeted answer change: 39.2%.
- Matched-random answer change: 9.2%.
- Paired answer-change difference: 30.0% (95% CI [22.3%, 37.7%]).
- Targeted centroid drift: 0.196.
- Matched-random centroid drift: 0.031.
- Paired drift difference: 0.166 (95% CI [0.140, 0.193]), Wilcoxon p=4.59e-21, rank-biserial r=0.892.
- Stable-answer IoU failure, per-image mean: 22.1%.
- Stable-answer centroid relocation, per-image mean: 12.3%.
- Same-size random rows meeting mask-target IoU <= 0.05: 88.2%.

The control is conservative for very large target boxes where a non-overlapping same-size placement is geometrically impossible.
