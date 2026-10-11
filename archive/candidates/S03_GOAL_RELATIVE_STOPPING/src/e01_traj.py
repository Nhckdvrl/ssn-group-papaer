"""S03 / Phase 1 — the REAL natural acquisition trajectory.

Two defects in the old `Layer B` curve are fixed here, and the fixes are the
whole point of the script:

1. **One fixed stop action.** Every checkpoint is scored on the same exact
   token, `<|endoftext|>` (id 100257), whose id is identical in all five OLMo-3
   tokenizers. `<|im_end|>` is recorded separately, never mixed in. The old
   curve used each checkpoint's own generation-config stop set, so base was
   scored on one token and every post-trained stage on a two-token logsumexp.

2. **The real chain.** OLMo-3 is
       Base -> Think-SFT -> Instruct-SFT -> DPO -> RLVR(Instruct)
   with Instruct-SFT warm-started from Think-SFT (verified by parameter
   distance, see the 2026-09-19 log entry), not `Base -> SFT -> DPO -> Instruct`.

**One serialization everywhere.** Every checkpoint, including Base and
Think-SFT, is measured in the Instruct chat format, so the input token ids are
byte-identical at every point on the curve; `e01_traj_report.py` asserts this
from the per-row `input_fp` fingerprint and refuses to plot a curve that mixes
stimuli. Think-SFT's native template differs (its own system prompt, and a
forced `<think>` opener that puts the model in a different mode), so it is
measured separately as a disclosed format control rather than being spliced
into the longitudinal curve.

Usage:
    python src/e01_traj.py --list
    python src/e01_traj.py --only spine          # the 5 stage endpoints
    python src/e01_traj.py --only think_sft      # densify inside a stage
    python src/e01_traj.py                       # everything in the table
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(HERE)

BASE = "allenai/Olmo-3-1025-7B"
THINK_SFT = "allenai/Olmo-3-7B-Think-SFT"
INST_SFT = "allenai/Olmo-3-7B-Instruct-SFT"
DPO = "allenai/Olmo-3-7B-Instruct-DPO"
RLVR = "allenai/Olmo-3-7B-Instruct"

# The serialization donor for EVERY checkpoint on the curve: its chat template
# AND its tokenizer.  Both are needed.  OLMo-3 post-training repurposed four
# reserved <|extra_id_*|> slots as function-calling tokens, and the Instruct
# system prompt contains <functions></functions>, so the BASE tokenizer encodes
# that same string as 5 ordinary tokens where the Instruct tokenizer emits 2
# special ones (66 vs 64 prompt tokens).  Encoding with one tokenizer makes the
# inputs byte-identical; the ids are shared and inside the base vocab (100278).
SERIALIZATION = RLVR

# Robustness serialization: an explicit system message containing no token that
# post-training added, so base and Instruct tokenizers agree exactly and the
# base checkpoint is never shown an id it has not seen in pretraining.  If the
# curve's qualitative shape survives this, the <functions> tokens are not
# driving it.
PLAIN_SYSTEM = "You are a helpful AI assistant."

# (label, repo, revision, stage, ordinal)
# `ordinal` orders the x axis across stages; it is a plotting order, not a
# claim about comparable step counts between stages.
SPINE = [
    ("base",             BASE,      None, "pretrain",  0),
    ("think_sft_final",  THINK_SFT, None, "think_sft", 100),
    ("inst_sft_final",   INST_SFT,  None, "inst_sft",  200),
    ("dpo_final",        DPO,       None, "dpo",       300),
    ("rlvr_final",       RLVR,      None, "rlvr",      400),
]

# Dense coverage where released intermediates exist. Instruct-SFT and DPO
# publish no intermediates (checked against the HF refs API), so those stages
# stay single-point and the trajectory can only localise them as whole stages.
THINK_STEPS = [1000, 3000, 6000, 10000, 15000, 21000, 28000, 35000, 43000]
RLVR_STEPS = [50, 100, 150, 200, 250, 300, 350, 400]

DENSE = (
    [(f"think_sft_s{s}", THINK_SFT, f"step{s}", "think_sft", 1 + i)
     for i, s in enumerate(THINK_STEPS)]
    + [(f"rlvr_s{s}", RLVR, f"step_{s:03d}", "rlvr", 301 + i)
       for i, s in enumerate(RLVR_STEPS)]
)

# Disclosed format control, NOT part of the longitudinal curve: Think-SFT in its
# own native (thinking) template, to show what the fixed-serialization choice
# costs at the one checkpoint where the native format genuinely differs.
NATIVE = [("think_sft_final_native", THINK_SFT, None, "think_sft_native", 100)]

TABLE = SPINE + DENSE + NATIVE
OUT = "results/e01_traj"


def job(label, repo, rev, stage, variant="main"):
    out = f"{OUT}/{label}.jsonl" if variant == "main" else f"{OUT}/{variant}/{label}.jsonl"
    cmd = [sys.executable, "-u", "src/e01_run.py", "--family", "olmo3-7b",
           "--stage", stage, "--repo", repo, "--stimuli", "stimuli/e01_pairs.jsonl",
           "--stop-token", "<|endoftext|>", "--out", out]
    if rev:
        cmd += ["--revision", rev]
    if not label.endswith("_native"):
        cmd += ["--graft-from", SERIALIZATION, "--tokenizer-from", SERIALIZATION]
    if variant == "plainsys":
        cmd += ["--system", PLAIN_SYSTEM]
    return out, cmd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None,
                    help="'spine', a stage name, or a comma-separated label list")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--gpus", default="0,1,2,3")
    ap.add_argument("--variant", default="main", choices=("main", "plainsys"),
                    help="'plainsys' re-runs the same checkpoints under a system "
                         "prompt containing no post-training-added token")
    args = ap.parse_args()

    tab = TABLE
    if args.only == "spine":
        tab = SPINE
    elif args.only:
        want = set(args.only.split(","))
        tab = [t for t in tab if t[0] in want or t[3] in want]

    if args.list:
        for lab, repo, rev, stage, o in tab:
            print(f"{o:>4}  {lab:<24}{stage:<18}{repo}@{rev or 'main'}")
        return

    os.makedirs(OUT if args.variant == "main" else f"{OUT}/{args.variant}",
                exist_ok=True)
    os.makedirs("results/logs", exist_ok=True)
    queue = [t for t in tab if not os.path.exists(job(*t[:4], args.variant)[0])]
    print(f"{len(tab)} checkpoints, {len(queue)} to run", flush=True)

    gpus = args.gpus.split(",")
    running = []
    while queue or running:
        while queue and len(running) < len(gpus):
            lab, repo, rev, stage, _ = queue.pop(0)
            gpu = [g for g in gpus
                   if g not in {r[1] for r in running}][0]
            out, cmd = job(lab, repo, rev, stage, args.variant)
            env = dict(os.environ, CUDA_VISIBLE_DEVICES=gpu,
                       PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True")
            env.pop("HF_HUB_OFFLINE", None)      # intermediates need fetching
            sfx = "" if args.variant == "main" else f"_{args.variant}"
            lg = open(f"results/logs/traj_{lab}{sfx}.log", "w")
            print(f"[gpu{gpu}] start {lab}", flush=True)
            running.append((subprocess.Popen(cmd, env=env, stdout=lg,
                                             stderr=subprocess.STDOUT), gpu, lab, lg))
        done = [r for r in running if r[0].poll() is not None]
        for p, gpu, lab, lg in done:
            lg.close()
            ok = os.path.exists(job(lab, "", None, "", args.variant)[0])
            print(f"[gpu{gpu}] {'done ' if ok else 'FAIL '} {lab} rc={p.returncode}",
                  flush=True)
            running.remove((p, gpu, lab, lg))
        if not done:
            import time
            time.sleep(5)


if __name__ == "__main__":
    main()
