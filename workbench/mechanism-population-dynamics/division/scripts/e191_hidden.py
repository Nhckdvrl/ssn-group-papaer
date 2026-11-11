#!/usr/bin/env python3
"""E191 (card: division/experiments/E191-flame-early-trajectory-decomposition.md): per-token ROUTER-INPUT hidden states of
one FLAME-MoE-290M checkpoint on a fixed token subsample, in the E186 store format (e186_hidden.py), plus the LM loss on
the English text (positive control a1) and the bf16 forward's own top-6 (positive control b).
Model: Megatron torch_dist -> Qwen2MoeForCausalLM in memory (e191_convert.convert), bf16, sdpa.
Token subsample (same positions for every checkpoint; E186 rule with E191 counts): FLORES-200 dev, E179's 20 languages
in E179 order, first 997 sentences, add_special_tokens=False, pythia-12b tokenizer; global positions uniform without
replacement, rng default_rng(179) drawn in language order, eng_Latn 6000, the other 19 languages 500 each;
+ UD EWT dev+test passages (E184 rule, <= 400 words), 6000 positions, default_rng(1179).  N = 21,500.
Router input = tensor entering mlp.gate (after post_attention_layernorm = Megatron pre_mlp_layernorm), MoE layers only.
Writes OUT/toksub.npy [8, N, 1024] fp16, OUT/toksub_meta.npz (src 0..19 FLORES language / 20 UD; sid; pos; inp),
OUT/router.npz (gate [8, 64, 1024] fp32, post_attention_layernorm [8, 1024], input_layernorm [8, 1024]),
OUT/topk_bf16.npy [8, N, 6] int8 (top-6 of the bf16 gate logits inside the forward), OUT/meta.json.
usage: e191_hidden.py --dcp DIR --key KEY --out DIR [--data DIR] [--tok DIR]"""
import argparse, json, os, sys, time
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ud_passages import sentences  # noqa: E402
from e191_convert import convert, build_model  # noqa: E402

LANGS = ["eng_Latn", "arb_Arab", "asm_Beng", "bam_Latn", "ben_Beng", "fra_Latn", "hin_Deva", "lit_Latn",
         "ory_Orya", "pes_Arab", "srp_Cyrl", "tha_Thai", "zho_Hans",
         "deu_Latn", "spa_Latn", "jpn_Jpan", "kor_Hang", "swh_Latn",
         "rus_Cyrl", "tam_Taml"]                       # e179_capture.LANGS, same order
PER_LANG = {lg: (6000 if lg == "eng_Latn" else 500) for lg in LANGS}
UD_N = 6000


def build_sequences(tok, data):
    SEQS, SRC, SID = [], [], []
    for li, lg in enumerate(LANGS):
        with open(f"{data}/flores200_dataset/dev/{lg}.dev", encoding="utf-8") as f:
            for j, s in enumerate([x.rstrip("\n") for x in f][:997]):
                SEQS.append(tok(s, add_special_tokens=False)["input_ids"]); SRC.append(li); SID.append(j)
    MAX_WORDS, ud = 400, []
    for name in ("dev", "test"):
        cur = None
        for newdoc, text, toks in sentences(f"{data}/lingdata/en_ewt-ud-{name}.conllu"):
            if cur is None or newdoc or cur["n"] + len(toks) > MAX_WORDS:
                if cur and cur["text"]:
                    ud.append(cur["text"])
                cur = {"text": "", "n": 0}
            cur["text"] = (cur["text"] + " " + text) if cur["text"] else text
            cur["n"] += len(toks)
        if cur and cur["text"]:
            ud.append(cur["text"])
    for j, s in enumerate(ud):
        SEQS.append(tok(s, add_special_tokens=False)["input_ids"]); SRC.append(len(LANGS)); SID.append(j)
    return SEQS, np.array(SRC), np.array(SID)


def sample_rows(SEQS, SRC):
    rows = []
    rs = np.random.default_rng(179)
    for li, lg in enumerate(LANGS):
        idx = np.where(SRC == li)[0]
        lens = np.array([len(SEQS[i]) for i in idx]); off = np.concatenate([[0], np.cumsum(lens)])
        for g in np.sort(rs.choice(off[-1], PER_LANG[lg], replace=False)):
            k = int(np.searchsorted(off, g, side="right") - 1)
            rows.append((int(idx[k]), int(g - off[k])))
    idx = np.where(SRC == len(LANGS))[0]
    lens = np.array([len(SEQS[i]) for i in idx]); off = np.concatenate([[0], np.cumsum(lens)])
    for g in np.sort(np.random.default_rng(1179).choice(off[-1], UD_N, replace=False)):
        k = int(np.searchsorted(off, g, side="right") - 1)
        rows.append((int(idx[k]), int(g - off[k])))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dcp", required=True); ap.add_argument("--key", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--data", default="/tmp/xiang_flame/data"); ap.add_argument("--tok", default="/tmp/xiang_flame/tok/pythia12b")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.tok)
    SEQS, SRC, SID = build_sequences(tok, a.data)
    rows = sample_rows(SEQS, SRC)
    N = len(rows)
    need = {}
    for r, (si, p) in enumerate(rows):
        need.setdefault(si, []).append((p, r))
    cfg, sdict, margs = convert(a.dcp)
    model = build_model(cfg, sdict); del sdict
    layers = model.model.layers
    moe = [l for l in range(cfg.num_hidden_layers) if l not in cfg.mlp_only_layers]
    L, d, K = len(moe), cfg.hidden_size, cfg.num_experts_per_tok
    OUT = np.zeros((L, N, d), np.float16); TK = np.zeros((L, N, K), np.int8)
    CUR = {}

    def mk(j):
        def hook(mod, inp, out):
            h = inp[0].reshape(-1, d)
            if CUR["flat"].numel():
                OUT[j, CUR["rows"]] = h[CUR["flat"]].float().cpu().numpy().astype(np.float16)
                TK[j, CUR["rows"]] = out.reshape(-1, out.shape[-1])[CUR["flat"]].topk(K, -1).indices.cpu().numpy().astype(np.int8)
        return hook
    for j, l in enumerate(moe):
        layers[l].mlp.gate.register_forward_hook(mk(j))
    eng = [i for i in range(len(SEQS)) if SRC[i] in (0, len(LANGS))]
    todo = sorted(set(need) | set(eng), key=lambda i: len(SEQS[i]))
    B = 64
    nll = {"flores_eng": [0.0, 0], "ud": [0.0, 0], "other": [0.0, 0]}
    with torch.no_grad():
        for b0 in range(0, len(todo), B):
            b = todo[b0:b0 + B]
            T = max(len(SEQS[i]) for i in b)
            ids = torch.zeros((len(b), T), dtype=torch.long); am = torch.zeros((len(b), T), dtype=torch.long)
            flat, rr = [], []
            for q, i in enumerate(b):
                ids[q, :len(SEQS[i])] = torch.tensor(SEQS[i]); am[q, :len(SEQS[i])] = 1
                for p, r in need.get(i, []):
                    flat.append(q * T + p); rr.append(r)
            CUR["flat"] = torch.tensor(flat, device="cuda", dtype=torch.long); CUR["rows"] = np.array(rr, dtype=np.int64)
            logits = model(input_ids=ids.cuda(), attention_mask=am.cuda(), use_cache=False).logits.float()
            lp = torch.nn.functional.cross_entropy(logits[:, :-1].reshape(-1, logits.shape[-1]), ids[:, 1:].reshape(-1).cuda(),
                                                   reduction="none").view(len(b), T - 1)
            m = am[:, 1:].cuda().float()
            for q, i in enumerate(b):
                kname = "flores_eng" if SRC[i] == 0 else "ud" if SRC[i] == len(LANGS) else "other"
                nll[kname][0] += float((lp[q] * m[q]).sum()); nll[kname][1] += int(m[q].sum())
    np.save(f"{a.out}/toksub.npy", OUT); np.save(f"{a.out}/topk_bf16.npy", TK)
    np.savez(f"{a.out}/toksub_meta.npz", src=np.array([SRC[s] for s, _ in rows], np.int8), sid=np.array([SID[s] for s, _ in rows], np.int32),
             pos=np.array([p for _, p in rows], np.int32), inp=np.array([SEQS[s][p] for s, p in rows], np.int64))
    np.savez(f"{a.out}/router.npz", gate=np.stack([layers[l].mlp.gate.weight.detach().float().cpu().numpy() for l in moe]),
             post_attention_layernorm=np.stack([layers[l].post_attention_layernorm.weight.detach().float().cpu().numpy() for l in moe]),
             input_layernorm=np.stack([layers[l].input_layernorm.weight.detach().float().cpu().numpy() for l in moe]))
    it = int(os.path.basename(a.dcp.rstrip("/")).split("_")[-1])
    json.dump({"key": a.key, "N": N, "L": L, "d": d, "K": K, "E": cfg.num_experts, "moe_layer_ids": moe, "langs": LANGS,
               "src_ud": len(LANGS), "seed_flores": 179, "seed_ud": 1179, "per_lang": PER_LANG, "ud_tokens": UD_N,
               "iteration": it, "tokens": it * margs["global_batch_size"] * margs["seq_length"],
               "consumed_train_samples": margs.get("consumed_train_samples"),
               "definition": "input of mlp.gate (after post_attention_layernorm = Megatron pre_mlp_layernorm)",
               "lm_loss": {k: (v[0] / v[1] if v[1] else None, v[1]) for k, v in nll.items()},
               "tokenizer": "EleutherAI/pythia-12b", "wall_s": time.time() - t0, "host": os.uname().nodename},
              open(f"{a.out}/meta.json", "w"), indent=1)
    print(f"[{time.time() - t0:.0f}s] saved {a.key} toksub {OUT.shape} loss", {k: round(v[0] / max(v[1], 1), 4) for k, v in nll.items()}, flush=True)


if __name__ == "__main__":
    main()
