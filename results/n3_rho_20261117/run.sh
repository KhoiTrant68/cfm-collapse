export CUDA_VISIBLE_DEVICES=2
cd /home/jovyan/cfm-research/cfm-collapse
.venv-s10/bin/python -u -m scripts.n3_directional_q --network results/n3_edm_sub500_20261115/train_sub500_s0/00000-cifar10_sub500_s0-cond-ddpmpp-edm-gpus1-batch128-fp32/network-snapshot-010000.pkl --edm-repo /home/jovyan/cfm-research/edm --cifar-root data --indices data/edm_subsets/cifar10_sub500_s0_indices.npy --n-per-class 100 --out results/n3_rho_20261117/sub500 > results/n3_rho_20261117/sub500.log 2>&1
.venv-s10/bin/python -u -m scripts.n3_directional_q --network /home/jovyan/cfm-research/edm-checkpoints/edm-cifar10-32x32-cond-vp.pkl --edm-repo /home/jovyan/cfm-research/edm --cifar-root data --n-per-class 20 --out results/n3_rho_20261117/public > results/n3_rho_20261117/public.log 2>&1
.venv-s10/bin/python -m scripts.n3_directional_q --summarize results/n3_rho_20261117 > results/n3_rho_20261117/summary.log 2>&1
echo COMPLETE > results/n3_rho_20261117/STATUS
