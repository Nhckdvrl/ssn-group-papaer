"""Per-token NLL on packed windows for HF or mamba_ssm checkpoints (Pile zoo, 2k windows).
usage: SHAPE_PACK=neox2k_ score_any.py {hf|ssm} MODEL_PATH TAG DOMAINS [REVISION]
Writes scores/<TAG>/<domain>.npy (S, L-1) float32; nll[s, i] = -log p(ids[s, i+1] | ids[s, :i+1]).
mamba_ssm models run with use_mem_eff_path=False (no causal_conv1d extension: nn.Conv1d + triton SSD).
"""
import json, os, sys, time
import numpy as np
import torch

PFX = os.environ.get("SHAPE_PACK", "")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = int(os.environ.get("SHAPE_V", 50277))   # real NeoX vocab; padded rows excluded from the softmax for every model


def load(kind, path, rev):
    if not os.path.isdir(path):
        from huggingface_hub import snapshot_download
        path = snapshot_download(path, revision=rev or "main", local_files_only=True)
    if kind == "hf":
        from transformers import AutoModelForCausalLM
        return AutoModelForCausalLM.from_pretrained(path, revision=rev, dtype=torch.bfloat16, device_map="cuda",
            # Pythia step branches can carry main's model.safetensors (seen: pythia-2.8b step36000);
            # the real weights for a revision are in pytorch_model.bin.
            use_safetensors=False if rev and os.path.exists(f"{path}/pytorch_model.bin") else None).eval()
    from mamba_ssm.models.config_mamba import MambaConfig
    from mamba_ssm.models.mixer_seq_simple import MambaLMHeadModel
    cfg = json.load(open(f"{path}/config.json"))
    if cfg.get("ssm_cfg", {}).get("layer") == "Mamba2":
        cfg["ssm_cfg"]["use_mem_eff_path"] = False
    m = MambaLMHeadModel(MambaConfig(**cfg), device="cuda", dtype=torch.bfloat16)
    sd = torch.load(f"{path}/pytorch_model.bin", map_location="cuda")
    missing, unexpected = m.load_state_dict(sd, strict=False)
    print("missing", missing, "unexpected", unexpected, flush=True)
    return m.eval()


@torch.no_grad()
def main(kind, path, tag, domains, rev=None):
    model = load(kind, path, rev)
    os.makedirs(f"{ROOT}/scores/{tag}", exist_ok=True)
    for dom in domains:
        out_f = f"{ROOT}/scores/{tag}/{dom}.npy"
        if os.path.exists(out_f) and os.path.exists(out_f.replace(".npy", "_lpin.npy")):
            continue
        ids = np.load(f"{ROOT}/data/pack_{PFX}{dom}.npz")["ids"]
        out = np.zeros((ids.shape[0], ids.shape[1] - 1), np.float32)
        lpin = np.zeros_like(out); lpout = np.zeros_like(out)   # log P(next in / not in prefix token set)
        t0 = time.time()
        for s in range(ids.shape[0]):
            x = torch.from_numpy(ids[s]).long().cuda()[None]
            lg = model(x).logits[0, :-1, :V].float()
            lse = torch.logsumexp(lg, -1)
            out[s] = (lse - lg.gather(-1, x[0, 1:, None])[:, 0]).cpu().numpy()
            first = torch.full((V,), 1 << 30, dtype=torch.long, device=x.device).scatter_reduce(
                0, x[0], torch.arange(x.shape[1], device=x.device), reduce="amin")
            seen = first[None, :] <= torch.arange(lg.shape[0], device=x.device)[:, None]
            lpin[s] = (torch.logsumexp(lg.masked_fill(~seen, -1e30), -1) - lse).cpu().numpy()
            lpout[s] = (torch.logsumexp(lg.masked_fill(seen, -1e30), -1) - lse).cpu().numpy()
        np.save(out_f, out)
        np.save(out_f.replace(".npy", "_lpin.npy"), lpin); np.save(out_f.replace(".npy", "_lpout.npy"), lpout)
        print(tag, dom, ids.shape, f"{time.time() - t0:.0f}s", "mean nll", out.mean(), flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[1], a[2], a[3].split(","), a[4] if len(a) > 4 else None)
