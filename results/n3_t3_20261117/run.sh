export CUDA_VISIBLE_DEVICES=2
cd /home/jovyan/cfm-research/cfm-collapse
O=results/n3_t3_20261117
mkdir -p $O
printf 'start %s\n' "$(date -u)" > $O/chain.log
.venv-s10/bin/python -u -m scripts.n3_directional_q --forward-only --network results/n3_edm_sub500_20261115/train_sub500_s0/00000-cifar10_sub500_s0-cond-ddpmpp-edm-gpus1-batch128-fp32/network-snapshot-010000.pkl --edm-repo /home/jovyan/cfm-research/edm --cifar-root data --indices data/edm_subsets/cifar10_sub500_s0_indices.npy --n-per-class 100 --batch 50 --out $O/sub500 > $O/sub500.log 2>&1
printf 'sub500 done %s\n' "$(date -u)" >> $O/chain.log
.venv-s10/bin/python -u -m scripts.n3_directional_q --forward-only --network /home/jovyan/cfm-research/edm-checkpoints/edm-cifar10-32x32-cond-vp.pkl --edm-repo /home/jovyan/cfm-research/edm --cifar-root data --n-per-class 50 --batch 50 --out $O/public > $O/public.log 2>&1
printf 'public done %s\n' "$(date -u)" >> $O/chain.log
.venv-s10/bin/python -W ignore -m scripts.n3_directional_q --summarize $O > $O/summary.log 2>&1
echo COMPLETE > $O/STATUS
