# EXP-1 adversarial-pairing ablation (Windows): shuffle Y relative to X and
# check that conditional collapse is unchanged (Proposition 4 needs only
# distinct labels, not a real x-y relationship). Compare against the
# already-run real-pairing baseline (exp1_cond_seed*).
#
#   pwsh scripts/run_exp1_adversarial.ps1
#
$ErrorActionPreference = "Stop"
$UV = "uv"
$CFG = "configs/exp1_adversarial_shuffle.yaml"
$SEEDS = 0,1,2,3,4

foreach ($s in $SEEDS) {
    & $UV run python -m src.train --config $CFG --set run_name="exp1_adv_shuffle_seed$s" seed=$s
}

& $UV run python scripts/analyze_exp1_adversarial.py `
    --real "results/exp1/exp1_cond_seed*" `
    --shuffled "results/exp1/exp1_adv_shuffle_seed*" `
    --out "results/exp1/_analysis_adversarial"
