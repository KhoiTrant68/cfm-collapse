# Corrected CIFAR-10 midpoint counts

Each of the eight selected pairs and twelve randomly drawn pairs shares a pool of 512 Gaussian sources. The entries count source–pair combinations that converge to the pair midpoint under the reduced two-image continuation. The baseline runs use relative tolerance `1e-6`, absolute tolerance `1e-9`, and hand off once all three posteriors assign total mass greater than `1 - 1e-12` to the pair.

| Guidance / threshold | Selected, out of 4096 | Direct bounds | Random, out of 6144 | Direct bounds |
|---:|---:|---:|---:|---:|
| 0 | 0 | 0–0 | — | — |
| 0.5 | 0 | 0–0 | — | — |
| 0.9 | 0 | 0–0 | 0 | 0–0 |
| 1.1 | 109 | 0–216 | 41 | 1–53 |
| 2 | 917 | 872–960 | 309 | 307–311 |
| 5 | 2075 | 2072–2086 | 874 | 874–875 |
| 10 | 2608 | 2607–2611 | — | — |

Direct bounds use the inward and outward barriers evaluated at each archived handoff. Below the threshold, any nonzero projected handoff escapes toward the atom on its initial side. At five times the threshold, one random source, index 172 for pair 118/1188, remained unresolved before handoff. It is included in the denominator and the upper bound. Each fixed guidance level reuses the same sources across pairs, and different guidance levels reuse each source–pair combination.

## Replay and independent checks

Run the following from the directory containing `scripts/` and `results/`. The replay needs SciPy. The independent audit also uses NumPy. The figure uses Matplotlib and Pillow.

```sh
python -m scripts.replay_cifar_composition
python scripts/make_theory_cifar_composition_figure.py
python scripts/audit_cifar_handoffs.py --compare-replays results/cifar_composition_replay --sources-csv cifar_signed_sources.csv
```

The replay reads the original 2,000-image run outputs in the two archived CIFAR result directories. It keeps first-stage atom decisions and unresolved cases, and recomputes the continuation of every saved pair handoff using its time and signed projection. The six JSON files retain the class for every source. `summary.json` contains each pair's fractions. The figure command regenerates `paper_theory/figures/fig_cifar_composition.pdf` and `fig_cifar_curve.json` using the 16 native RGB images in `selected_images.npz`.

`selected.json` and `random.json` are the two baseline panels. The four sensitivity files refer to the **eight selected pairs**. The `handoff` files loosen the handoff to `1e-9`, while the `rtol` files tighten relative and absolute tolerances to `1e-8` and `1e-11`. In both settings all signed classes match the baseline on shared rows. The `_large` files cover ratios 5 and 10 on all eight pairs. The remaining files cover 0.9, 1.1 and 2 on all eight pairs and also 5 on 292/1938.

The independent audit integrates two bracketing trajectories backward in log time from opposite outcome classes at time 3, each with Radau at relative tolerances `1e-9` and `1e-11`. It pads the bracket by the observed spread across both endpoints and both tolerances. Every supercritical pair handoff lies outside its padded bracket. Across all six groups the audit and replay agree on **95,232** signed classes, including **59,390** pair handoffs. The archive-to-replay changes comprise **13,527** atom-to-midpoint corrections, counting repeated sensitivity configurations. The audit uses floating-point integration. Full-field posterior truncation at handoff remains an approximation. [Signed per-source table](audit/cifar_signed_sources.csv.gz) · [Counts, bounds and mismatch lists](audit/cifar_signed_audit.json)

## Fresh 2,000-image spot checks

Reconstruct the input from the CIFAR-10 training split with PyTorch, torchvision and NumPy. The subset uses the first 2,000 indices in the seed-0 CPU permutation of all 50,000 training images. Images are scaled in float32 and flattened in channel-first order. The labels are the visible top 16 rows of each channel.

```sh
python - <<'PY'
import numpy as np
from src.problems.inpainting import InpaintingProblem
p = InpaintingProblem.create(N=2000, seed=0, dataset="cifar10")
np.savez("cifar2000_seed0.npz", X=p.X.flatten(1).numpy(),
         Y=p.X[:, :, :16, :].flatten(1).numpy())
PY
```

The reconstructed pair radii, squared label separations, and squared midpoint margin ratios match all 20 archived pairs within `6e-14`. The figure archive stores the 16 selected images at their original 32-by-32 resolution as unsigned 8-bit RGB. To rebuild it and the figure from this full instance, run `python scripts/make_cifar_composition_figure.py --data cifar2000_seed0.npz`. The plotting script computes each pixelwise midpoint from the two image arrays. For each rerun, the solver generates the complete seed-20261105 pool of 512 sources in float64 before selecting the zero-based source indices. The first-stage solver uses `rtol=1e-8`, `atol=1e-11` and handoff mass tolerance `1e-14`.

```sh
fresh() {
    python -m scripts.cifar_composition_exact --data cifar2000_seed0.npz \
        --B 1 --sources 512 --rtol 1e-8 --atol 1e-11 --handoff 1e-14 "$@"
}
out=results/cifar_composition_replay
fresh --pair 1104 1984 --source-indices 23 4 154 --ratios 2 5 10 --tau0 1e-4 --out "$out/fresh_check"
for tau in 1e-4 0; do
    case "$tau" in 0) group=fresh_zero ;; 1e-4) group=fresh_boundary ;; esac
    fresh --pair 1443 1695 --source-indices 110 --ratios 1.1 --tau0 "$tau" --out "$out/${group}_1443_1695"
    fresh --pair 292 1938 --source-indices 323 --ratios 1.1 --tau0 "$tau" --out "$out/${group}_292_1938"
    fresh --pair 1491 1514 --source-indices 124 --ratios 2 --tau0 "$tau" --out "$out/${group}_1491_1514"
done
python scripts/audit_cifar_handoffs.py --check-fresh "$out"
```

| Pair | Source | Guidance / threshold | Strict full-field run through handoff, followed by scalar continuation |
|---|---:|---:|---|
| 1104/1984 | 23, 4, 154 | 2 | midpoint, atom 1104, atom 1447 |
| 1104/1984 | 23, 4, 154 | 5 and 10 | all midpoint |
| 1443/1695 | 110 | 1.1 | midpoint |
| 292/1938 | 323 | 1.1 | atom 292 |
| 1491/1514 | 124 | 2 | midpoint |

The last three cases include the closest random and selected handoffs to the projected basin boundary and the closest selected handoff at twice the threshold, measured by distance in the unscaled projection. Each returned the same endpoint starting at the archived initial log time `1e-4` and at zero. All 12 distinct source–pair–guidance combinations agreed with the archived-state replay. The independent audit also checked the newly projected handoff states. These targeted reruns cover four pairs. [Fresh signed audit](audit/fresh_signed_audit.json)

A separate two-dimensional translation test uses matched sources with analytically identical basin membership. Fixed-step RK4 detected all 108 and 252 midpoint sources in the centered examples at 2 and 10 times threshold, respectively, and detected zero after translating both atoms by (0.25, 0). This occurred at both 256 and 512 steps per log-time segment and at all three terminal gaps. Reproduce with `python -m scripts.stress_positive_control --translation 0.25 0`. [Translated positive control](../stress_positive_control_20261121/translated.json)
