# Simulated review, round 4: ICLR 2027, NeurIPS, ICML

- **Version reviewed**: `paper/main.tex` after PR #22 (general calibration theorem,
  Proposition `prop:filtered` in the main text, interventions moved to the appendix).
- Same four perspectives and scales as round 3
  (`review_round3_math_2026-10-02.md`); written by one model, not independent reviewers.

## What changed against round 3, per reviewer

**A (mathematics).**
- Weakness 4 (Gaussian-only) is addressed. Theorem 2(a,b) holds for any prior and
  forward map. The TV bound is uniform over region rules and nearly tight at $h=\sigma/2$
  on a mixture posterior.
- Weakness 3 (local identifiability) is addressed by the sublevel-set statement.
- Weakness 1 stands: the tools are still elementary (Pinsker, Gaussian conditioning).
  Proposition 7 has real content: an asymptotic argument showing the spatial factor beats
  any label average. But it is about a model of a learner, not a trained network.
- Weakness 2 (no theorem about trained networks) is softened, not removed. The paper is
  candid that neither model reproduces $p\approx1.3$ or the stop above $h$.
- Rating 5 → **6**. NeurIPS 3 → **4**. ICML 2 → **3**.

**B (empirical memorisation).**
- The scale concern is unchanged: no image-scale calibration yet. The pipeline exists but
  has not been run.
- Proposition 7's corollary is useful and testable: off-atom samples need spatial error.
  It turns the CIFAR-10 38% off-atom observation into a diagnosis.
- Rating stays **5**. NeurIPS **3**. ICML **2**. It would move to 6 / 4 / 3 with the
  CIFAR-10 PIT-vs-$h_{\mathrm{eff}}$ result.

**C (UQ).**
- The prior-free bound is exactly what was missing. "Label noise costs at most
  $O(h^2/\sigma^2)$ coverage" is a clean practical rule.
- The 50% result is now in the main text.
- Rating 6 → **6** (confidence up). NeurIPS **4**. ICML **3**.

**D (clarity).**
- The refocus works: the theory section is the exact law, and Section 4.3 now carries two
  propositions, a theorem and two figures.
- The 4.1/4.3 inconsistency is gone.
- Still dense with numbers. Figure 3's caption points to an appendix equation.
- Rating 5 → **6**. NeurIPS **4**. ICML **3**.

## Meta-review

| Venue | Round 3 | Round 4 | Reading |
|---|---|---|---|
| ICLR 2027 main | 5/5/6/5 (5.25) | 6/5/6/6 (5.75) | borderline; acceptance plausible with a good rebuttal (~40%) |
| NeurIPS | 3/3/4/3 | 4/3/4/4 | borderline accept / reject (~30–35%) |
| ICML | 2/2/3/2 | 3/2/3/3 | weak accept / weak reject (~30%) |
| ICLR workshop | accept | accept | clear accept |

**Remaining blockers, ranked.**
1. **Image-scale calibration.** Run `ANALYSIS=calib` on the six CIFAR-10 runs (three
   Kaggle sessions, ~1 h each) and `scripts/analyze_calib_image.py`. A positive result
   (h_eff predicts PIT error / coverage beyond iteration) moves reviewer B. A negative
   one must be reported, and it bounds the claim to low dimension.
2. **The networks' exponent and floor.** Either explain $p\approx1.3$ and the $1.08h$
   stop, or show with more seeds that $p=2$ cannot be rejected. Then drop $p$ from the
   story.
3. **A theorem about the trained network** (lazy regime, field-level). This is the
   remaining distance to a "mathematical" paper at NeurIPS/ICML. It is high risk; the
   paper is acceptable without it at ICLR if 1 lands.
