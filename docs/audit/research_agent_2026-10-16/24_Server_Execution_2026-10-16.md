# Server execution status — 2026-10-16

User authorized running the proposed experiments on the server. Live preflight was
performed over the existing SSH alias `guess`, account `guess03`, host `server-01`.
Project: `/mnt/home/guess03/cfm-collapse`. Python: `~/clic/venv/bin/python`,
PyTorch `2.11.0+cu128`, CUDA available. Two NVIDIA L40 GPUs, each 46,068 MiB,
reported 0% compute utilization at inspection; each had an existing 1,238 MiB
allocation. No existing process was stopped. Available filesystem space: 575 GB.

## Verified access

- All six synthetic checkpoint 200000 files for h=0,0.1 and seeds 0,1,2 exist.
- Earlier hard-label checkpoints exist for a teacher/rollout risk diagnostic.
- CIFAR DDPM checkpoint 60000 files are present remotely, including h=0,4,5,6.
  This closes the previously unknown remote *file access* prerequisite; model
  loading and image evaluation remain untested.
- SHA-256 of the solver, MLP model, and linear-Gaussian problem code match local.
- The remote project directory has no `.git`; provenance must use file hashes.

## Execution completed

Existing remote `scripts/test_calibration.py` passed, using four CPU threads and
a 180-second timeout. Log:
`results/theory_evidence_20261016/calibration_existing.log` on the server.

Gaussian maximum coverage deviations: pixel .004, PC .011, joint .048.
Collapsed 90% coverage: 0 for all three. Overdispersed 50% coverage:
.812, .815, 1.000. This is the legacy continuous-control suite, **not a test of
randomized ranks under ties**.

Local new controls passed: calibrated point mass, quantized and continuous
Gaussian, collapsed/overdispersed controls, joint point-mass ranks, permutation
equivariance of LOO scores, energy-distance sanity, and exact hard-oracle ODE
checks at 100/200/400 steps. Artifacts:
`tmp/theory-pilot-controls-oracle-20261016/`.

## Upload approval and smoke

Automatic approval review rejected uploading the Python source snapshot, citing
potentially sensitive source egress and unverified destination ownership. No
snapshot upload or new pilot execution occurred. A narrower explicit question
was presented: permission to send only `scripts/theory_evidence_pilot.py` and
`src/metrics/calibration.py` to the isolated remote code directory. Do not retry
or route around that rejection without the required authorization/evidence.

The user subsequently answered **ok**, authorizing those exact two files.
Only those files were transferred to `results/theory_evidence_20261016/code/`;
the full snapshot was not transferred. Their remote and local hashes matched:

- pilot: `bd6ce0f7ef6d3a117e5b420305aa20497af0a6808d2c208fa6dc3407e3f5bc47`
- calibration: `9ca89a191935d9768358c11420cf2f3b942dbac55a97603ea9a0c835fd81ec64`

The existing server metric file was not replaced; the pilot loads its isolated
adjacent calibration snapshot. Smoke uses h=0, seed 0, checkpoint 200000,
M=64, two fresh held-out conditions, GPU 0, a five-minute outer timeout.
Remote measurement controls and smoke passed; smoke completed in 17.50 seconds,
including controls (7.30 seconds for checkpoint evaluation). Both held-out
conditions passed the solver screen. This supported the bounded pilot below.

## Completed bounded evaluation

Current research execution scope: **FEASIBILITY_PILOT_ONLY, completed**. No full
training grid, image evaluation, or claim closure has been performed.

| Output directory under `results/theory_evidence_20261016/` | Scope | Script wall time |
|---|---|---|
| `six_checkpoint_pilot` | h=0,.1 × seeds 0,1,2, checkpoint 200k; M=256; 20 fit + 8 fresh queries; RK4 100/200/400; epsilon .001 | 30.36 s |
| `earlier_hard_checkpoints` | h=0 × seeds 0,1,2 × checkpoints 10k,30k; same queries/source rule | 50.45 s |
| `eps_0001` | Repeat six 200k checkpoints at epsilon .0001 with exactly paired source/query arrays | 38.89 s |

All manifests report `completed`. Including smoke, script wall time was 137.20
seconds; this is measured execution time, not GPU-hours or preparation time.
The server result directory occupies 9.3 MiB. No pilot process remains; GPU
allocations returned to the initial 1,247 MiB per GPU and 0% compute utilization.

Source v1 was retained for the first two evaluations. A version v2, within the
same authorized pilot file, added the terminal epsilon argument and was placed
in the separate `code/terminal_time/` directory. Manifests identify each version
by SHA-256. Local exact snapshots: `pilot_source_v1.py`, `pilot_source_v2.py`,
and `calibration_snapshot.py` in the result directory.

The remote `heff_family_test.py` differs in whole-file hash from local, but
AST comparisons confirmed identical `GRID`, `weights`, `knn_weights`, and
`atomic_reference`, the only imported fitting objects. The remote hash is
recorded in every manifest; an inspected copy is under `tmp/` locally.

## Results and independent checks

- All 48 main held-out checkpoint-condition pairs passed the practical solver
  screen at epsilon .001, and all 48 at epsilon .0001 also passed.
- Mean paired 200-to-400-step displacement by run was 3.28e-7 to 5.47e-7 at
  epsilon .001. Reducing terminal epsilon changed paired endpoints by about
  .0012–.0014; average nearest-atom distances remained about .035–.063.
- For h=0, Gaussian fitted-reference energy exceeded the diagnostic reference
  q95 envelope at 23/24 conditions; for h=.1, at 9/24. These are descriptive
  counts from only 16 null pairs per condition, **not calibrated rejection
  counts or familywise significance**. Conditions are nested within three
  reused problem seeds.
- At t=.999 and checkpoint 200k, hard-label learned-path/teacher field-error
  ratios ranged from 2.45e5 to 5.17e5 across problem seeds. Nine profiles cover
  10k/30k/200k. This is a fixed-time diagnostic, not global training loss or a
  global risk-transfer certificate.
- Independent local NumPy calculations reproduced 192 model-reference energy
  distances, 192 same-moment-control distances, and all 24 family scale fits.
- Existing local and remote continuous calibration regression tests passed;
  the isolated new remote ties and oracle controls passed for all pilot runs.
- The summary figure was rendered and visually inspected.

The defensible result is a finite-time discrepancy between trained outputs and
the fitted reference at held-out conditions, substantially larger than tested
step-size effects, especially at h=0. The evidence does not establish any
network's t=1 endpoint law, a new mechanism, equivalence of distributions, or
acceptance-level novelty. CIFAR and analytic matched-loss illustrations remain
outside this executed synthetic pilot.

Local report and raw outputs: `results/theory_evidence_20261016/SUMMARY.md` and
the adjacent directories. The paper has not been edited to insert these results.

Reproduce local verification/summary:

```powershell
.\.venv\Scripts\python.exe -m scripts.summarize_theory_evidence_pilot
```

Remote pilot command pattern (use a **new** output directory; existing outputs
are deliberately not overwritten):

```bash
cd /mnt/home/guess03/cfm-collapse
timeout 1800 env PYTHONPATH=. OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 CUDA_VISIBLE_DEVICES=0 \
  /mnt/home/guess03/clic/venv/bin/python -u \
  results/theory_evidence_20261016/code/theory_evidence_pilot.py \
  --out results/theory_evidence_20261016/NEW_OUTPUT \
  --runs heff_p7y_h0_seed0 heff_p7y_h0.1_seed0 heff_p7y_h0_seed1 \
         heff_p7y_h0.1_seed1 heff_p7y_h0_seed2 heff_p7y_h0.1_seed2 \
  --M 256 --heldout 8 --max-seconds 1700
```
