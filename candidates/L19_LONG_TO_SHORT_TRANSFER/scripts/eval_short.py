"""Short-context evaluation, following the mother paper's Appendix B Table 3 protocol.

MMLU      0-shot,  no CoT, accuracy
BBH       3-shot,  CoT,    exact match
LAMBADA   0-shot,  no CoT, accuracy
GSM8K     4-shot,  CoT,    accuracy

NQ is deliberately NOT evaluated: in-domain QA adaptation is not the outcome of interest.
"""
import argparse, json, os, subprocess, sys

TASKS = [
    ("mmlu",              0,   None),
    ("lambada_openai",    0,   None),
    ("gsm8k_cot",         4,   None),
    ("bbh_cot_fewshot",   3,   100),   # per-subtask cap, frozen before any run
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--batch_size", default="8")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for task, shots, lim in TASKS:
        cmd = [sys.executable, "-m", "lm_eval", "--model", "hf",
               "--model_args", f"pretrained={a.model},dtype=bfloat16,attn_implementation=sdpa",
               "--tasks", task, "--num_fewshot", str(shots),
               "--batch_size", a.batch_size,
               "--output_path", os.path.join(a.out, task)]
        if lim: cmd += ["--limit", str(lim)]
        print(" ".join(cmd), flush=True)
        subprocess.run(cmd, check=True)

if __name__ == "__main__":
    main()
