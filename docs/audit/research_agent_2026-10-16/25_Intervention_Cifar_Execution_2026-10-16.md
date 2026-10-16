# Intervention and CIFAR execution — 2026-10-16

User request: run the next experiments proposed for the paper. Scope begins with
oracle interventions, an exact matched-teacher-loss illustration, and a bounded
CIFAR solver/calibration pilot. No new training has been launched. This record
does not imply a novelty pass or full-run readiness.

## Verified server preflight

SSH alias `guess`, `guess03@server-node.wondertek.space:2525`, remote hostname
`server-01`, repository `/mnt/home/guess03/cfm-collapse`. At inspection 16:44
Asia/Bangkok, both L40 GPUs reported 0% compute utilization, each with an existing
1,247 MiB allocation; available disk space was 574 GB. The Python environment
`/mnt/home/guess03/clic/venv/bin/python`, CIFAR training/test data, and final h=0
and h=4 checkpoints are present. No prior job or output was removed.

`src/models/unet.py` and `scripts/calib_image_checkpoints.py` match local SHA-256.
The inpainting module differs in whole-file hash, but AST comparisons confirmed
identical `InpaintingProblem.create`, `condition`, `observation`, and `channels`.
The new CIFAR script asserts the DDPM configuration and >30M parameters, records
the actual count and checkpoint/config hashes, and preserves unclipped samples.

## Prepared scripts and checks

- `scripts/oracle_intervention_pilot.py`: hard CFG and positive-bandwidth CFG
  at w=0,3,12; average of three conditional fields; exact endpoint-noise mixture
  draws at rho=0,.15; symmetric tie trajectory and perturbed controls. Shared
  source samples and geometry. Endpoints at epsilon .01,.0001,.000001 using RK4
  in s=-log(1-t), with paired resolutions. Finite simulation is an illustration,
  not a proof of almost-sure atomicity or exact guided endpoint weights.
- The same script independently integrates the teacher-risk profile of the
  loss-only counterexample, matches its teacher loss to the sharp-Lipschitz
  attainer, and compares exact endpoint variances. This compares two explicit
  fields, not a causal single-factor trained-network ablation.
- `scripts/cifar_solver_pilot.py`: paired Euler 50/100/200/400; same test images
  and source noise; randomized tie ranks through the previously approved metric
  snapshot. Records pixel/PC/joint calibration, hidden covariance trace,
  reconstruction errors, nearest-training-image MSE, and paired solver RMS.
  Images, rather than pixels, are independent evaluation units.
- Both scripts passed syntax checks. Local oracle smoke (seed101,M16,steps192/384)
  completed; all seven ODE arms had final mean nearest-atom distance <3.4e-6.
  Independent Euler controls matched exact hard-conditioned affine trajectories.

## Upload approval and execution history

Automatic approval review rejected transferring the two new scripts, requiring
explicit user authorization for these exact files and SSH destination. Neither
new script was uploaded at that point. An asynchronous question asked for
permission to send only these two scripts into
`~/cfm-collapse/results/intervention_cifar_pilot_20261016/code/`; no dataset or
checkpoint upload is requested. Prior approval for different files is not being
used to route around this rejection.

The user subsequently confirmed **chạy đi** in direct response to the exact-file
question. Both scripts were uploaded successfully and hashes matched local:
oracle `860004fdc1bb6b08ff5923eecd6151032d9a8c29a1683d799892c2a6fca7c2c9`,
CIFAR `c88810a8b7d97c863f13cc401dc2e54cdd0f530fcaf877dbb6f28a9cefc638d4`.
No shared source, dataset, checkpoint or prior output was overwritten.

Remote oracle smoke passed. The five-seed oracle illustration completed in
51.62 seconds (seeds101–105,M128,768/1536 log-time RK4 steps). All 135 saved
rows were independently checked locally against raw outputs. At epsilon1e-6,
the largest mean nearest-atom distance among the 35 ODE arms was4.60e-6;
largest mean paired solver displacement was6.85e-12. Exact rho=.15 noisy-target
controls retained mean nearest-atom distances .178–.199 across seeds. Four
matched-loss constructions matched analytic loss and segmentwise quadrature.
These are finite numerical illustrations and explicit fields, not new proof
certificates or trained-model causal interventions.

CIFAR smoke completed on the exact35,750,915-parameter architecture, h0seed0,
two held-out images,M16, all four solver resolutions. Checkpoint execution took
33.86 seconds including artifact writing. Outputs were finite. Covariance trace
increased materially from50 to400 steps;400 is a comparison resolution, not a
convergence certificate.

The h0three-seed pilot completed successfully in425.67 seconds at16:56–17:00
Asia/Bangkok, using8test images,M32 per image and four resolutions. The attempted
h4launch and artifact download were then prevented by an automatic approval
review **usage-limit failure**, rather than a safety rejection. On the user's
later **tiếp tục đi**, access resumed and the h4three-seed pilot was launched
onGPU1 around20:31 with the same settings and a30-minute ceiling. Its output is
`cifar_smoothed_three_seeds/`; final results were subsequently inspected below.
No new training has been launched.

## Completed results after continuation

Both CIFAR manifests report **completed**: h0took425.67seconds; h4took436.79seconds.
Scope: six exact60kcheckpoints, three seeds per h, eight shared held-out images,
M32, Euler50/100/200/400, epsilon.001. This is a **completed feasibility pilot**,
not a full validation study or an ICLR-readiness certificate.

At400steps, per-seed averages over the eight images were:

| h | pixel rank90% coverage | hidden covariance trace | joint32 coverage |
|---|---|---|---|
|0|.0728,.0815,.0830|.5885,.6798,.7197|0,0,0|
|4|.7820,.7709,.7983|223.86,203.27,203.51|.875,.375,.875|

The finite-Mcalibrated central-rank reference is29/33=.87879; the upper-rank
reference is30/33=.90909. These are distinct. h4broadens outputs and improves
marginal coverage, while mean reconstruction MSE is worse than h0on this pilot.
Marginal improvement does not establish calibrated joint posterior sampling.
Joint coverage has only1/8resolution because the independent evaluation units
are images; neither pixels nor repeated seeds create more distinct test images.

At h4, paired200-to400-step RMS was .0139–.0233 across seeds, and joint32coverage
for seed1 changed from .75 at50steps to .375 at400steps. Therefore solver
convergence for all image metrics is **unresolved** at400steps. Do not attribute
all observed image-level changes to learned-field error, or treat400steps as an
exact endpoint. No additional sweep was silently expanded to claim convergence.

Full raw NumPy verification ran on the server to avoid delaying analysis on the
large download. It independently recomputed pixel coverage, hidden trace,
hidden-mean MSE and paired RMS for **192 image/solver rows**. It also checked
exact input-array hashes (truth, training images, all source draws and conditions)
across h0and h4. Result JSON hashes were then checked locally against that audit.
Oracle135rows and four matched-loss constructions were independently checked
locally. The two summary plots were rendered and visually inspected.

Artifacts: `results/intervention_cifar_pilot_20261016/SUMMARY.md`, `summary.json`,
`oracle_matched_loss.png/.pdf`, `cifar_solver.png/.pdf`, and
`raw_verification/raw_verification.json`. All raw samples remain on the server;
oracle and h0full raw files were also copied locally. h4raw files remain remote.
Remote directory size142MiB. No pilot or verifier process remained on final
inspection; both GPUs reported0MiB allocated and0%compute utilization.

The generation source snapshot is retained remotely and locally as
`cifar_solver_pilot_generation_snapshot.py`. The same approved CIFAR script was
subsequently extended with a direct NumPy `--verify-folders` mode, and its verifier
hash is recorded in the audit. The running generation code was not changed.

Local summary reproduction using the server raw audit:

```powershell
.\.venv\Scripts\python.exe -m scripts.summarize_intervention_cifar --server-audit results/intervention_cifar_pilot_20261016/raw_verification/raw_verification.json
```

Decision: retain theory/oracle claims within their stated assumptions; report
trained-model calibration and discretization limitations. Do not promote a
moment-fit bandwidth to a full-law identity, or claim posterior recovery from
increased variance. The10newsynthetictrainingruns were not started: priority and
the central contribution still require a resolved novelty/claim decision. The
canonical paper was not edited to insert pilot results.

Unaffected work: the existing remote `scripts/verify_cfg_affine.py` was launched
with 180-second timeout and four CPU threads. Log:
`results/intervention_cifar_pilot_20261016/existing_cfg_check.log`. Its initial
affine-hull checks printed exact ratios to shown precision; its full endpoint
sweep subsequently completed successfully within the timeout: **144 trajectories**,
maximum nearest-atom endpoint distance **1.21e-6**, zero distances exceeding
1e-4, and zero hard-conditioned endpoints assigned to another atom. The command
returned exit code 0. Its log was copied locally into the corresponding result
directory. This older script does not test field
averaging or the new matched-loss illustration.

## Ready commands after exact-file authorization

Oracle smoke, then the bounded five-seed illustration after checking its output:

```bash
cd /mnt/home/guess03/cfm-collapse
timeout 180 env OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 \
  /mnt/home/guess03/clic/venv/bin/python -u \
  results/intervention_cifar_pilot_20261016/code/oracle_intervention_pilot.py \
  --out results/intervention_cifar_pilot_20261016/oracle_smoke \
  --seeds 101 --M 16 --steps 192 --max-seconds 150
```

CIFAR engineering smoke (one checkpoint, two held-out images, M16; 15-minute
ceiling, not a runtime estimate):

```bash
timeout 900 env PYTHONPATH=. OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 CUDA_VISIBLE_DEVICES=0 \
  /mnt/home/guess03/clic/venv/bin/python -u \
  results/intervention_cifar_pilot_20261016/code/cifar_solver_pilot.py \
  --out results/intervention_cifar_pilot_20261016/cifar_smoke \
  --runs exp3_cifar_heff_h0_s0 --n-test 2 --M 16 --max-seconds 840 \
  --calibration-path results/theory_evidence_20261016/code/calibration.py
```

Inspect timing, finite outputs, exact parameter count, paired source arrays and
step-size effects before choosing a larger pilot. Stop if source/config mismatch,
nonfinite output, time ceiling or memory failure occurs. No claim that the
resulting paper meets ICLR acceptance criteria is authorized by execution alone.
