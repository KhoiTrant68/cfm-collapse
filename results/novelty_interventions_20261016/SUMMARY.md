# Novelty intervention experiments — verified server results

Finite-time diagnostics; no theorem or novelty certification.

Raw metric rows independently checked: 984.
Exact final cells: 200; max q95 nearest distance 6.11937e-06; max mean solver displacement 7.54797e-13.
Max paired assignment disagreement: 0.
Max fraction outside 1% minimum-separation threshold: 0.

| queries | radius / label std | seed-mean energy | range over seed means | network nearest | oracle nearest | network solver displacement |
|---|---|---|---|---|---|---|
| training | 0.0 | 0.00562722 | 0.00268338–0.0076804 | 0.0539211 | 0.00168242 | 6.9081e-07 |
| training | 0.5 | 0.0111998 | 0.00260439–0.0170046 | 0.0871795 | 0.00312151 | 7.15779e-07 |
| training | 1.5 | 0.289771 | 0.00260773–1.36314 | 0.107768 | 0.00399686 | 1.65919e-06 |
| fresh | 0.0 | 0.00722666 | 0.00187649–0.00932678 | 0.0572937 | 0.0018258 | 7.80967e-07 |
| fresh | 0.5 | 0.0110536 | 0.0018868–0.018859 | 0.0915741 | 0.00327688 | 6.97839e-07 |
| fresh | 1.5 | 0.143176 | 0.00175822–0.544995 | 0.110563 | 0.00478774 | 7.38989e-07 |

Five independent problem seeds; conditions and samples are nested, not independent replications.
Finite-M energy is biased and has no null/equivalence threshold in this study. Small values are not proof of law equality.
Full per-cell metrics are in CSV; raw arrays and checkpoint hashes are retained.
