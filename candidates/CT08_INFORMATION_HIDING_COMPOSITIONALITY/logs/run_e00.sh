# usage: run_e00.sh ARM ROOT_URL ROOT_NAME NWORKERS
cd /home/xiang/ssn-group-papaer/candidates/CT08_INFORMATION_HIDING_COMPOSITIONALITY/src
SUBS=http://fvcrc10:8102/v1,http://fvcrc10:8103/v1,http://fvcrc12:8111/v1
/home/xiang/miniconda3/envs/verl-clean/bin/python e00_run.py $1 ../results/e00/arm_$1.jsonl $2 $3 $SUBS qwen3-8b $4 > ../logs/e00_arm_$1.log 2>&1
