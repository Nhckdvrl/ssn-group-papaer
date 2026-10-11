"""Previous-token map of Pythia checkpoints (Fig. 3b): per head, the mean attention from each position to the previous
token on 64 x 256 tokens of the natural-text probe set (prepare_data.py probes). Writes
results/pythia_checkpoints/<model>__step<k>.json; then run lockin_pythia.py.
Usage: pythia_checkpoints.py --repo EleutherAI/pythia-70m-seed1 --step 2000
"""
import argparse
import json
import re

import torch

import common as mc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--step", type=int, required=True)
    a = ap.parse_args()
    torch.set_grad_enabled(False)
    from transformer_lens import HookedTransformer
    hf = mc.load_hf_model(a.repo, a.step, check_manifest=False)
    model = HookedTransformer.from_pretrained(re.sub(r"-seed\d+$", "", a.repo), hf_model=hf, device="cuda", dtype=torch.float32)
    pile = torch.load(mc.CACHE / "pile_eval_2000_seed42.pt")["tokens"]
    _, cache = model.run_with_cache(pile[:64, :256].to(model.cfg.device), names_filter=lambda n: n.endswith("hook_pattern"))
    s_prev = {f"{l}.{h}": float(cache["pattern", l].diagonal(offset=-1, dim1=-2, dim2=-1)[:, h].mean())
              for l in range(model.cfg.n_layers) for h in range(model.cfg.n_heads)}
    out = mc.RESULTS / "pythia_checkpoints"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{a.repo.split('/')[-1]}__step{a.step}.json").write_text(json.dumps({"repo": a.repo, "step": a.step, "S_prev": s_prev}))


if __name__ == "__main__":
    main()
