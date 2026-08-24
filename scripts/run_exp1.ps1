# EXP-1 Phase A: core conditional-vs-unconditional collapse study (Windows).
# Runs SEEDS conditional + unconditional runs to full length, then analyzes.
#
#   pwsh scripts/run_exp1.ps1
#
$ErrorActionPreference = "Stop"
$UV = "uv"
$CFG = "configs/exp1_linear_gaussian.yaml"
$SEEDS = 0,1,2,3,4

foreach ($s in $SEEDS) {
    & $UV run python -m src.train --config $CFG --set run_name="exp1_cond_seed$s" seed=$s model.conditional=true
    & $UV run python -m src.train --config $CFG --set run_name="exp1_uncond_seed$s" seed=$s model.conditional=false
}

& $UV run python scripts/analyze_exp1.py `
    --cond "results/exp1/exp1_cond_seed*" `
    --uncond "results/exp1/exp1_uncond_seed*" `
    --out "results/exp1/_analysis"
