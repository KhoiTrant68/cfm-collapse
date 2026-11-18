cd /home/jovyan/cfm-research/cfm-collapse
export CUDA_VISIBLE_DEVICES=2
P=.venv-s10/bin/python
EDM=/home/jovyan/cfm-research/edm
NET=results/n3_edm_sub500_20261115/train_sub500_s0/00000-cifar10_sub500_s0-cond-ddpmpp-edm-gpus1-batch128-fp32/network-snapshot-010000.pkl
PUB=/home/jovyan/cfm-research/edm-checkpoints/edm-cifar10-32x32-cond-vp.pkl
O=results/n3_steps_20261117
mkdir -p $O
printf 'ablation start %s\n' "$(date -u)" > $O/chain.log
for S in 18 36 64; do
  $P -u -m scripts.n3_directional_q --forward-only --steps $S --network $NET --edm-repo $EDM --cifar-root data --indices data/edm_subsets/cifar10_sub500_s0_indices.npy --n-per-class 100 --batch 50 --out $O/s$S/sub500 > $O/s${S}_sub500.log 2>&1
  $P -u -m scripts.n3_directional_q --forward-only --steps $S --network $PUB --edm-repo $EDM --cifar-root data --n-per-class 50 --batch 50 --out $O/s$S/public > $O/s${S}_public.log 2>&1
  $P -W ignore -m scripts.n3_directional_q --summarize $O/s$S > $O/s${S}_summary.log 2>&1
  printf 'steps %s done %s\n' "$S" "$(date -u)" >> $O/chain.log
done
echo COMPLETE > $O/STATUS
# sub2000 training (seed 0), then evaluation, on the same GPU
GPU=2 EDM_REPO=$EDM PYTHON=$P CIFAR_ROOT=data STAGES=2 SUBSETS=2000 SEED=0 BATCH_GPU=128 DUMP=25 \
  OUT=results/n3_edm_sub2000_20261117 bash scripts/server_n3_edm.sh > results/n3_edm_sub2000_20261117.launcher.log 2>&1
