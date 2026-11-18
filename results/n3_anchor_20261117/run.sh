cd /home/jovyan/cfm-research/cfm-collapse
export CUDA_VISIBLE_DEVICES=2
P=.venv-s10/bin/python
EDM=/home/jovyan/cfm-research/edm
NET=results/n3_edm_sub500_20261115/train_sub500_s0/00000-cifar10_sub500_s0-cond-ddpmpp-edm-gpus1-batch128-fp32/network-snapshot-010000.pkl
PUB=/home/jovyan/cfm-research/edm-checkpoints/edm-cifar10-32x32-cond-vp.pkl
O=results/n3_anchor_20261117
mkdir -p $O
printf 'start %s\n' "$(date -u)" > $O/chain.log
$P -u -m scripts.n3_directional_q --forward-only --network $NET --edm-repo $EDM --cifar-root data --indices data/edm_subsets/cifar10_sub500_s0_indices.npy --n-per-class 100 --batch 20 --out $O/sub500 > $O/sub500.log 2>&1
$P -u -m scripts.n3_directional_q --forward-only --network $PUB --edm-repo $EDM --cifar-root data --n-per-class 50 --batch 20 --out $O/public > $O/public.log 2>&1
printf 'done %s\n' "$(date -u)" >> $O/chain.log
echo COMPLETE > $O/STATUS
