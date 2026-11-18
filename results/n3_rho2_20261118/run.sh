cd /home/jovyan/cfm-research/cfm-collapse
export CUDA_VISIBLE_DEVICES=3
P=.venv-s10/bin/python
EDM=/home/jovyan/cfm-research/edm
O=results/n3_rho2_20261118
mkdir -p $O
N2=$(ls results/n3_edm_sub2000_20261117/train_sub2000_s0/*/network-snapshot-010000.pkl)
N1=$(ls results/n3_edm_sub500s1_20261117/train_sub500_s1/*/network-snapshot-010000.pkl)
$P -u -m scripts.n3_directional_q --forward-only --network $N2 --edm-repo $EDM --cifar-root data --indices data/edm_subsets/cifar10_sub2000_s0_indices.npy --n-per-class 100 --batch 50 --out $O/sub2000 > $O/sub2000.log 2>&1
$P -u -m scripts.n3_directional_q --forward-only --network $N1 --edm-repo $EDM --cifar-root data --indices data/edm_subsets/cifar10_sub500_s1_indices.npy --n-per-class 100 --batch 50 --out $O/sub500s1 > $O/sub500s1.log 2>&1
$P -W ignore -m scripts.n3_directional_q --summarize $O > $O/summary.log 2>&1
echo COMPLETE > $O/STATUS
