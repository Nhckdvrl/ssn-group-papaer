"""Information-equivalent source relocation; test where mapping effects travel."""
import argparse
import copy
import hashlib
import json
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from e58_factorization import HEAD, INSTRUCTION, NAMES, make_contexts
from e59_mediation import patch, real_contexts, score


def encode_relocated(tok, ctx, labels, dataset, layout, donor="base", instruction=False):
    enc = lambda s: tok.encode(s, add_special_tokens=False)
    fields = ("Comment", "Annotator") if dataset == "real" else ("Item", "Source")
    head = "Below are comments and the labels that individual annotators gave them.\n\n" if dataset == "real" else HEAD
    ids = enc(head + (INSTRUCTION if instruction else ""))
    sites = {"source_name": [], "label_anchor": []}
    order = ("source_name", "label_anchor") if layout == "before" else ("label_anchor", "source_name")
    for demo in ctx["demos"]:
        ids += enc(f'{fields[0]}: {demo["word"]}\n')
        for slot in order:
            ids += enc(f'{fields[1] if slot == "source_name" else "Label"}:')
            sites[slot].append(len(ids))
            word = NAMES[demo["source"] ^ int(donor == "source")] if slot == "source_name" else labels[demo["label"] ^ int(donor == "label")]
            wid = enc(" " + word)
            assert len(wid) == 1
            ids += wid + enc("\n")
        ids += enc("\n")
    return ids, sites


@torch.inference_mode()
def score_query_first(model, tok, cache, ctx, labels, plen, dataset):
    item, source = ("Comment", "Annotator") if dataset == "real" else ("Item", "Source")
    seqs = [tok.encode(f'{source}: {NAMES[q["source"]]}\n{item}: {q["word"]}\nLabel:', add_special_tokens=False) for q in ctx["queries"]]
    width = max(map(len, seqs))
    ids = torch.zeros((len(seqs), width), dtype=torch.long, device="cuda")
    mask = torch.zeros((len(seqs), plen + width), dtype=torch.long, device="cuda")
    pos = torch.zeros_like(ids)
    mask[:, :plen] = 1
    for i, seq in enumerate(seqs):
        ids[i, -len(seq):] = torch.tensor(seq, device="cuda")
        mask[i, -len(seq):] = 1
        pos[i, -len(seq):] = torch.arange(plen, plen + len(seq), device="cuda")
    cache.batch_repeat_interleave(len(seqs))
    lo = model(input_ids=ids, attention_mask=mask, position_ids=pos, past_key_values=cache, use_cache=True, logits_to_keep=1).logits[:, -1].float()
    lid = [tok.encode(" " + x, add_special_tokens=False)[0] for x in labels]
    return (lo[:, lid[1]] - lo[:, lid[0]]).cpu().numpy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dataset", choices=["synthetic", "real"], required=True)
    ap.add_argument("--stage", choices=["discovery", "confirmation"], required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    a = ap.parse_args()
    torch.set_num_threads(6)
    torch.manual_seed(0)
    d = Path(a.out)
    d.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    ctxs = make_contexts(a.stage, a.n, a.seed) if a.dataset == "synthetic" else real_contexts(
        "train" if a.stage == "discovery" else "test", a.n, a.seed)
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True, dtype=torch.bfloat16,
                                               device_map="cuda", attn_implementation="sdpa").eval()
    (d / "contexts.jsonl").write_text("".join(json.dumps(c) + "\n" for c in ctxs))
    errors = []
    with (d / "behavior.jsonl").open("w") as f, torch.inference_mode():
        for i, ctx in enumerate(ctxs):
            scores = {}
            lengths = []
            for vocab, labels in (("yes_no", ["yes", "no"]), ("toxic_safe", ["toxic", "safe"])):
                for layout in ("before", "after"):
                    caches, sites_all = {}, {}
                    for donor in ("base", "source", "label"):
                        ids, sites = encode_relocated(tok, ctx, labels, a.dataset, layout, donor)
                        lengths.append(len(ids))
                        sites_all[donor] = sites
                        caches[donor] = model(input_ids=torch.tensor([ids], device="cuda"), use_cache=True, logits_to_keep=1).past_key_values
                        assert sites == sites_all["base"]
                    plen = len(ids)
                    root = vocab + "." + layout + "."
                    for c, cache in caches.items():
                        scores[root + c] = score(model, tok, copy.deepcopy(cache), ctx, labels, plen, a.dataset)
                    for donor, site, channel in (("source", "source_name", "key"), ("source", "label_anchor", "kv"),
                                                  ("label", "source_name", "kv"), ("label", "label_anchor", "kv")):
                        c = patch(caches["base"], caches[donor], sites_all["base"][site], channel)
                        scores[root + f"{donor}.{site}.{channel}"] = score(model, tok, c, ctx, labels, plen, a.dataset)
                    all_pos = list(range(plen))
                    c = patch(caches["base"], caches["source"], all_pos, "kv")
                    full = score(model, tok, c, ctx, labels, plen, a.dataset)
                    errors.append(float(abs(full - scores[root + "source"]).max()))
                    scores[root + "query_source_first"] = score_query_first(model, tok, copy.deepcopy(caches["base"]), ctx, labels, plen, a.dataset)
                    ids, _ = encode_relocated(tok, ctx, labels, a.dataset, layout, instruction=True)
                    c = model(input_ids=torch.tensor([ids], device="cuda"), use_cache=True, logits_to_keep=1).past_key_values
                    scores[root + "instruction"] = score(model, tok, c, ctx, labels, len(ids), a.dataset)
                    scores[root + "noop"] = score(model, tok, copy.deepcopy(caches["base"]), ctx, labels, plen, a.dataset)
                    errors.append(float(abs(scores[root + "noop"] - scores[root + "base"]).max()))
            assert len(set(lengths)) == 1, lengths
            f.write(json.dumps({"context": i, "signs": [2 * q["label"] - 1 for q in ctx["queries"]],
                                "scores": {k: list(map(float, v)) for k, v in scores.items()}}) + "\n")
            f.flush()
            if i % 8 == 0:
                print(i, round(time.time() - t0, 1), flush=True)
    run = {"args": vars(a), "seconds": time.time() - t0, "sanity_max_error": max(errors),
           "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "gpu": torch.cuda.get_device_name()}
    (d / "run.json").write_text(json.dumps(run, indent=2))
    print(json.dumps(run), flush=True)


if __name__ == "__main__":
    main()
