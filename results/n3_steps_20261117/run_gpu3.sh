cd /home/jovyan/cfm-research/cfm-collapse
# second sub500 run: new 500-image subset and training seed 1
GPU=3 EDM_REPO=/home/jovyan/cfm-research/edm PYTHON=.venv-s10/bin/python CIFAR_ROOT=data STAGES=2 SUBSETS=500 SEED=1 \
  BATCH_GPU=128 DUMP=25 OUT=results/n3_edm_sub500s1_20261117 bash scripts/server_n3_edm.sh \
  > results/n3_edm_sub500s1_20261117.launcher.log 2>&1
