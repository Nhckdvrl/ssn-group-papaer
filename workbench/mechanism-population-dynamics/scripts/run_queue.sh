#!/bin/bash
# E02 queue runner: each worker repeatedly claims the next (repo, step) that is accepted in the R0 manifest and not
# yet done (claim = atomic mkdir of results/e02/claims/<tag>). Usage: GPUS="0 3 fvcrc10:1" bash scripts/run_e02.sh
set -u
cd "$(dirname "$0")"
PY=${PY:-$HOME/.venvs/mechpop/bin/python}
GPUS=(${GPUS:-0})
OUT=../results/${EXP:-e02}
mkdir -p "$OUT/logs" "$OUT/claims"
REPOS=${REPOS:-"EleutherAI/pythia-70m $(for i in 1 2 3 4 5 6 7 8 9; do printf "EleutherAI/pythia-70m-seed%s " $i; done)"}
STEPS=${STEPS:-"0 128 256 512 1000 2000 3000 4000 6000 8000 16000 32000 64000 100000 130000 143000"}
accepted() {  # $1 repo $2 step
  python3 - "$1" "$2" <<'EOF'
import json, sys
m = json.load(open("../results/artifact_manifest_70m.json"))
ok = any(r["model_id"] == sys.argv[1] and r["step"] == int(sys.argv[2]) and r["accepted"] for r in m["checkpoints"])
sys.exit(0 if ok else 1)
EOF
}
worker() {
  local gpu=$1
  while true; do
    local pending=0 ran=0
    for step in $STEPS; do for repo in $REPOS; do
      tag="$(basename $repo)__step$step"
      [ -f "$OUT/$tag.json" ] && continue
      [ -d "$OUT/claims/$tag" ] && continue   # running elsewhere, or failed (kept claimed; see logs)
      pending=1
      accepted "$repo" "$step" || continue
      mkdir "$OUT/claims/$tag" 2>/dev/null || continue
      if [[ $gpu == *:* ]]; then
        ssh -o BatchMode=yes "${gpu%%:*}" "cd $PWD && CUDA_VISIBLE_DEVICES=${gpu##*:} HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 $PY ${SCRIPT:-e02_population.py} --repo $repo --step $step" > "$OUT/logs/$tag.log" 2>&1
      else
        CUDA_VISIBLE_DEVICES=$gpu HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 "$PY" ${SCRIPT:-e02_population.py} --repo "$repo" --step "$step" > "$OUT/logs/$tag.log" 2>&1
      fi
      rc=$?
      echo "[gpu$gpu] $tag exit=$rc"
      ran=1
    done; done
    [ $pending -eq 0 ] && break
    [ $ran -eq 0 ] && sleep 30
  done
}
for g in "${GPUS[@]}"; do worker "$g" & done
wait
