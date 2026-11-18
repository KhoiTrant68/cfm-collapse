cd /home/jovyan/cfm-research/cfm-collapse
export CUDA_VISIBLE_DEVICES=2
P=.venv-s10/bin/python
EDM=/home/jovyan/cfm-research/edm
O=results/n3_strips_20261118
mkdir -p $O
$P -u -m scripts.n3_image_strips --network results/n3_edm_sub500_20261115/train_sub500_s0/00000-cifar10_sub500_s0-cond-ddpmpp-edm-gpus1-batch128-fp32/network-snapshot-010000.pkl --edm-repo $EDM --cifar-root data --indices data/edm_subsets/cifar10_sub500_s0_indices.npy --classes 1,3,7,8 --n-per-class 8 --out $O/sub500.npz > $O/sub500.log 2>&1
$P -u -m scripts.n3_image_strips --network /home/jovyan/cfm-research/edm-checkpoints/edm-cifar10-32x32-cond-vp.pkl --edm-repo $EDM --cifar-root data --classes 1,3,7,8 --n-per-class 8 --out $O/public.npz > $O/public.log 2>&1
echo COMPLETE > $O/STATUS
