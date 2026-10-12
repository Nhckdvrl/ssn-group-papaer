"""E45: label sequence x within-class placement factorial; label-stream predictability.
usage: e45_labelseq.py --model M --task num|sst --out NPZ
margins[set, seq(8), place(4), query(40)]; stream_lp[set, seq, place] (inputs masked as '?'), orig_lp[...] (real
prompt): mean teacher-forced log-prob of each demo's label word given everything before it."""
import argparse, sys
from pathlib import Path
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from e44_order_quality import make_sets  # noqa

SEQS = ["0101010101010101", "1010101010101010", "0011001100110011", "0000111100001111",
        "0000000011111111", "1111111100000000"]


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--task"); ap.add_argument("--out")
    ap.add_argument("--sets", type=int, default=40); ap.add_argument("--queries", type=int, default=40)
    a = ap.parse_args()
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda", attn_implementation="sdpa").eval()
    enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
    sets, head, key, words = make_sets(a.task, a.sets, a.queries, seed=995000)
    cid = [enc(" " + w)[0] for w in words]
    hid = enc(head)
    rng = np.random.default_rng(11)
    seqs = SEQS + ["".join(map(str, rng.permutation([0] * 8 + [1] * 8))) for _ in range(2)]
    M = np.zeros((a.sets, 8, 4, a.queries), np.float32)
    SL = np.zeros((a.sets, 8, 4), np.float32); OL = np.zeros((a.sets, 8, 4), np.float32)
    for s, (demo, qs) in enumerate(sets):
        byc = {c: [d for d in demo if d[1] == c] for c in (0, 1)}
        qids = [enc(f"{key}: {x}\nLabel:") for x, _ in qs]; qlen = [len(q) for q in qids]; QL = max(qlen)
        places = [{c: list(rng.permutation(8)) for c in (0, 1)} for _ in range(4)]
        for si, sq in enumerate(seqs):
            for pi, pl in enumerate(places):
                cnt = {0: 0, 1: 0}; order = []
                for ch in sq:
                    c = int(ch); order.append(byc[c][pl[c][cnt[c]]]); cnt[c] += 1
                ids = list(hid); lab_pos = []; mids = list(hid); mlab = []
                for x, c in order:
                    pre = enc(f"{key}: {x}\nLabel:"); w = enc(" " + words[c]); post = enc("\n\n")
                    lab_pos.append(len(ids) + len(pre)); ids += pre + w + post
                    mpre = enc(f"{key}: ?\nLabel:"); mlab.append(len(mids) + len(mpre)); mids += mpre + w + post
                # label log-probs (real prompt and input-masked prompt)
                for arr, lp, tgt in ((ids, lab_pos, OL), (mids, mlab, SL)):
                    lo = torch.log_softmax(model(input_ids=torch.tensor([arr]).cuda()).logits[0].float(), -1)
                    tgt[s, si, pi] = float(np.mean([lo[p - 1, arr[p]].item() for p in lp]))
                out = model(input_ids=torch.tensor([ids]).cuda(), use_cache=True)
                cache = out.past_key_values; cache.batch_repeat_interleave(len(qids))
                I = torch.zeros((len(qids), QL), dtype=torch.long); Am = torch.zeros((len(qids), len(ids) + QL), dtype=torch.long)
                Am[:, :len(ids)] = 1
                for qi, q in enumerate(qids):
                    I[qi, :len(q)] = torch.tensor(q); Am[qi, len(ids):len(ids) + len(q)] = 1
                P = torch.arange(len(ids), len(ids) + QL)[None].repeat(len(qids), 1)
                lo = model(input_ids=I.cuda(), attention_mask=Am.cuda(), position_ids=P.cuda(), past_key_values=cache, use_cache=True).logits.float()
                for qi in range(len(qids)):
                    c = qs[qi][1]; l = lo[qi, qlen[qi] - 1]; M[s, si, pi, qi] = float(l[cid[c]] - l[cid[1 - c]])
                del cache, out
        print(s, float(M[s].mean()), flush=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out, margins=M, stream_lp=SL, orig_lp=OL, seqs=np.array(seqs))
    print("done")


if __name__ == "__main__":
    main()
