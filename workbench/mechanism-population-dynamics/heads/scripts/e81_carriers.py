"""E81: inheritance of attention roles vs causal IOI carriers, with split-half reliability. Protocol: experiments/E81-*.md.

Usage: e81_carriers.py --family dd|hf|pythia --repo REPO --rev REV
Writes results/e81/<tag>.npz (per-half head maps) and <tag>.json (summary).
Per head, computed separately on the two halves (odd / even prompts or sequences):
  dla      IOI direct logit attribution (IO - S) at END, norms linearised at their actual scale
  abl      IOI logit-difference drop when the head's input to the output projection is mean-ablated at END (ABC mean)
  att_io   attention END -> IO;  att_s2  attention END -> S2
  ind      induction attention on repeated random token blocks;  prev  previous-token attention on natural text
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import torch

import mp_common as mc

sys.path.insert(0, str(mc.CACHE / "circuits-over-time"))
from path_patching_cm.ioi_dataset import IOIDataset  # noqa: E402

OUT = mc.RESULTS / os.environ.get("CARRIER_OUT", "e81")


class Arch:
    """Uniform access to attention output projections and norms across DataDecide(Llama) / OLMo2 / GPTNeoX."""

    def __init__(self, model):
        self.m = model
        if hasattr(model, "gpt_neox"):
            self.kind = "neox"
            self.layers = model.gpt_neox.layers
            self.proj = [l.attention.dense for l in self.layers]
            self.final = model.gpt_neox.final_layer_norm
            self.WU = model.embed_out.weight
            self.post = None
        else:
            self.layers = model.model.layers
            self.proj = [l.self_attn.o_proj for l in self.layers]
            self.final = model.model.norm
            self.WU = model.lm_head.weight
            first = self.layers[0]
            self.kind = "olmo2" if hasattr(first, "post_feedforward_layernorm") else "llama"
            self.post = [l.post_attention_layernorm for l in self.layers] if self.kind == "olmo2" else None
        c = model.config
        self.L, self.H = c.num_hidden_layers, c.num_attention_heads
        self.dh = c.hidden_size // self.H


def load(family, repo, rev):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    if family == "dd":
        import dd_common as dd
        return dd.load(repo, rev, dtype=torch.float32, attn="eager")
    if family == "pythia":
        model = mc.load_hf_model(repo, int(rev), dtype=torch.float32, check_manifest=False).cuda()
        model.config._attn_implementation = "eager"
        for l in model.gpt_neox.layers:
            l.attention.config._attn_implementation = "eager"
        tok = AutoTokenizer.from_pretrained(repo, cache_dir=str(mc.HF_CACHE))
        return model.eval(), tok
    tok = AutoTokenizer.from_pretrained(repo, revision=rev, cache_dir=str(mc.HF_CACHE))
    model = AutoModelForCausalLM.from_pretrained(repo, revision=rev, cache_dir=str(mc.HF_CACHE), torch_dtype=torch.float32,
                                                 attn_implementation="eager").cuda().eval()
    return model, tok


class IOIProbe:
    def __init__(self, model, tok):
        self.A = Arch(model)
        self.m, self.tok = model, tok
        tok.add_bos_token = False
        if tok.pad_token is None:
            tok.pad_token = tok.eos_token
        self.ioi = IOIDataset(prompt_type="mixed", N=200, tokenizer=tok, prepend_bos=False, seed=42, device="cpu")
        self.abc = self.ioi.gen_flipped_prompts("ABB->ABA, BAB->BAA")
        self.end = torch.as_tensor(self.ioi.word_idx["end"])
        self.n = len(self.end)
        self.io = torch.as_tensor(self.ioi.io_tokenIDs)
        self.s = torch.as_tensor(self.ioi.s_tokenIDs)
        self.halves = [np.arange(self.n) % 2 == 0, np.arange(self.n) % 2 == 1]
        self.patch, self.capture, self.mean_z = {}, None, None
        self.hooks = [p.register_forward_pre_hook(self._hook(i)) for i, p in enumerate(self.A.proj)]

    def _hook(self, layer):
        A = self.A

        def fn(mod, args):
            x = args[0]
            if self.capture is not None:
                self.capture[layer] = x[self.cb, self.ce].detach().float()
            if layer in self.patch and self.patch[layer]:
                x = x.clone()
                for h in self.patch[layer]:
                    x[self.cb, self.ce, h * A.dh:(h + 1) * A.dh] = self.mean_z[layer][h * A.dh:(h + 1) * A.dh].to(x.dtype)
                return (x,)
        return fn

    @torch.no_grad()
    def fwd(self, toks, ends, **kw):
        self.cb = torch.arange(len(ends), device=self.m.device)
        self.ce = ends.to(self.m.device)
        return self.m(toks.long().to(self.m.device), **kw)

    @torch.no_grad()
    def ld_per_prompt(self, heads=()):
        self.patch = {}
        for l, h in heads:
            self.patch.setdefault(l, []).append(h)
        lg = self.fwd(self.ioi.toks, self.end).logits.float()[self.cb, self.ce]
        self.patch = {}
        return (lg[self.cb, self.io.to(lg.device)] - lg[self.cb, self.s.to(lg.device)]).cpu().numpy()

    @torch.no_grad()
    def maps(self):
        A = self.A
        self.capture = {}
        self.fwd(self.abc.toks, torch.as_tensor(self.abc.word_idx["end"]))
        self.mean_z = {l: v.mean(0) for l, v in self.capture.items()}
        # clean pass with norm inputs captured at END
        self.capture, pre = {}, {}
        hk = [A.final.register_forward_pre_hook(lambda mod, a: pre.__setitem__("final", a[0][self.cb, self.ce].float()))]
        if A.post is not None:
            for l, p in enumerate(A.post):
                hk.append(p.register_forward_pre_hook(
                    (lambda ll: lambda mod, a: pre.__setitem__(("post", ll), a[0][self.cb, self.ce].float()))(l)))
        out = self.fwd(self.ioi.toks, self.end, output_attentions=True)
        for h in hk:
            h.remove()
        zs, self.capture = self.capture, None
        x = pre["final"]
        if A.kind == "neox":
            mu = x.mean(-1, keepdim=True)
            scale = torch.rsqrt(((x - mu) ** 2).mean(-1, keepdim=True) + A.final.eps)
            center = True
        else:
            scale = torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + A.m.config.rms_norm_eps)
            center = False
        w = A.final.weight.float()
        WU = A.WU.float()
        udir = (WU[self.io.to(WU.device)] - WU[self.s.to(WU.device)]) * w  # [N, d]
        dla = torch.zeros(self.n, A.L, A.H)
        for l in range(A.L):
            Wo = A.proj[l].weight.float()
            z = zs[l].view(self.n, A.H, A.dh)
            if A.post is not None:
                xp = pre[("post", l)]
                pscale = torch.rsqrt(xp.pow(2).mean(-1, keepdim=True) + A.m.config.rms_norm_eps) * A.post[l].weight.float()
            for h in range(A.H):
                c = z[:, h] @ Wo[:, h * A.dh:(h + 1) * A.dh].T
                if A.post is not None:
                    c = c * pscale
                if center:
                    c = c - c.mean(-1, keepdim=True)
                dla[:, l, h] = ((c * scale) * udir).sum(-1).cpu()
        io_pos = torch.as_tensor(self.ioi.word_idx["IO"]).to(self.m.device)
        s2_pos = torch.as_tensor(self.ioi.word_idx["S2"]).to(self.m.device)
        att_io = torch.stack([a[self.cb, :, self.ce, io_pos].float().cpu() for a in out.attentions], 1)  # [N, L, H]
        att_s2 = torch.stack([a[self.cb, :, self.ce, s2_pos].float().cpu() for a in out.attentions], 1)
        clean = self.ld_per_prompt()
        abl = np.zeros((self.n, A.L, A.H))
        for l in range(A.L):
            for h in range(A.H):
                abl[:, l, h] = clean - self.ld_per_prompt([(l, h)])
        res = {}
        for name, arr in (("dla", dla.numpy()), ("abl", abl), ("att_io", att_io.numpy()), ("att_s2", att_s2.numpy())):
            res[name] = np.stack([arr[m].mean(0) for m in self.halves])  # [2, L, H]
        for hh in self.hooks:
            hh.remove()
        return res, float(clean.mean())


@torch.no_grad()
def generic_roles(model, tok, n_seq=100, blk=64, n_txt=60, txt_len=128):
    """Induction (repeated random blocks) and previous-token attention (natural text), two halves each."""
    rng = np.random.default_rng(0)
    V = min(tok.vocab_size, 50000)
    ind = []
    for i in range(0, n_seq, 10):
        b = torch.tensor(rng.integers(1000, V - 1000, size=(10, blk)))
        x = torch.cat([b, b], 1).to(model.device)
        att = model(x, output_attentions=True).attentions
        q = torch.arange(blk, 2 * blk - 1)
        ind.append(torch.stack([a[:, :, q, q - blk + 1].float().mean(-1).cpu() for a in att], 1))  # [10, L, H]
    ind = torch.cat(ind).numpy()
    from datasets import load_dataset
    ds = load_dataset("NeelNanda/pile-10k", split="train", cache_dir=str(mc.HF_CACHE))
    prev = []
    for t in ds["text"][:n_txt * 3]:
        ids = tok(t, add_special_tokens=False)["input_ids"][:txt_len]
        if len(ids) < txt_len:
            continue
        att = model(torch.tensor([ids], device=model.device), output_attentions=True).attentions
        p = torch.arange(1, txt_len)
        prev.append(torch.stack([a[0, :, p, p - 1].float().mean(-1).cpu() for a in att]))  # [L, H]
        if len(prev) == n_txt:
            break
    prev = torch.stack(prev).numpy()
    half = lambda a: np.stack([a[0::2].mean(0), a[1::2].mean(0)])  # noqa: E731
    return {"ind": half(ind), "prev": half(prev)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family")
    ap.add_argument("--repo")
    ap.add_argument("--rev")
    a = ap.parse_args()
    import e77_atlas as e77
    torch.set_grad_enabled(False)
    t0 = time.time()
    hrev = e77.hf_rev("pythia" if a.family == "pythia" else a.family, a.rev)
    was_cached = e77.is_cached(a.repo, hrev)
    model, tok = load(a.family, a.repo, a.rev)
    maps = generic_roles(model, tok)
    ioi, ld = IOIProbe(model, tok).maps()
    maps.update(ioi)
    OUT.mkdir(parents=True, exist_ok=True)
    tag = f"{a.family}__{a.repo.split('/')[-1]}__{a.rev}"
    np.savez_compressed(OUT / f"{tag}.npz", **{k: v.astype(np.float32) for k, v in maps.items()})
    from scipy.stats import spearmanr
    rel = {k: float(spearmanr(v[0].ravel(), v[1].ravel())[0]) for k, v in maps.items()}
    full_dla = maps["dla"].mean(0)
    top = np.argsort(full_dla.ravel())[::-1][:5]
    H = full_dla.shape[1]
    summ = {"tag": tag, "logit_diff": ld, "split_half": rel, "top_dla": [f"{t // H}.{t % H}" for t in top],
            "seconds": time.time() - t0}
    (OUT / f"{tag}.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ), flush=True)
    if not was_cached:
        del model
        if a.family == "hf" and a.repo.endswith(("-SFT", "-DPO", "-Instruct")):  # whole repo exists only for this run
            import shutil
            shutil.rmtree(mc.HF_CACHE / f"models--{a.repo.replace('/', '--')}", ignore_errors=True)
            print("removed one-off cache", a.repo, flush=True)
        else:
            e77.drop_revision(a.repo, hrev)


if __name__ == "__main__":
    main()
