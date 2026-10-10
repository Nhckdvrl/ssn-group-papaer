"""E90 pilot-followup, registered after pilot and before this run.

Evaluate the same frozen E56 query module when no foreign source exists.
Reuse every discovery context; native scores must match the original single.
"""
import argparse
import copy
import hashlib
import json
import time
from pathlib import Path

import numpy as np

from e90_source_isolation import HEAD, interval


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="results/e90/qwen3_discovery")
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="/tmp/ices_models/Qwen3-8B")
    ap.add_argument("--weights", default="results/e56/Qwen3-8B_query_saved.pt")
    args = ap.parse_args()
    source, dest = Path(args.source), Path(args.out)
    cs = [json.loads(s) for s in (source / "contexts.jsonl").read_text().splitlines()]
    refs = [json.loads(s) for s in (source / "behavior.jsonl").read_text().splitlines()]
    assert len(cs) == len(refs)
    dest.mkdir(parents=True, exist_ok=True)
    assert not (dest / "behavior.jsonl").exists()
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_num_threads(6)
    started = time.time()
    tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    enc = lambda t: tok.encode(t, add_special_tokens=False)
    label_ids = [enc(" safe")[0], enc(" toxic")[0]]
    assert all(len(enc(" " + s)) == 1 for s in ["safe", "toxic"])
    model = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True,
        dtype=torch.float32, device_map="cuda", attn_implementation="eager").eval()
    model.requires_grad_(False)
    L = model.config.num_hidden_layers
    L1 = L // 2 - 2
    w = torch.load(args.weights, map_location="cpu", weights_only=True)
    assert len(w) == 2 * (L - L1)
    modules = {l: (w[2*i].cuda().float(), w[2*i+1].cuda().float())
               for i, l in enumerate(range(L1, L))}
    state = {"on": False}
    for l in range(L1, L):
        def hook(module, inputs, output, layer=l):
            if not state["on"]:
                return output
            down, up = modules[layer]
            out = output.clone()
            out[:, -1] += ((inputs[0][:, -1].float() @ down.T) @ up.T).to(out.dtype)
            return out
        model.model.layers[l].self_attn.q_proj.register_forward_hook(hook)
    records, errors = [], []
    with torch.inference_mode(), (dest / "behavior.jsonl").open("w") as stream:
        for ci, (ctx, ref) in enumerate(zip(cs, refs)):
            ids = enc(HEAD)
            for (text, role, y), name in zip(ctx["demos"], ctx["shown"]):
                if role != 0:
                    continue
                ids += enc(f"Comment: {text}\nAnnotator: {name}\nLabel:")
                ids += enc(" " + ("toxic" if y else "safe")) + enc("\n\n")
            state["on"] = False
            cache = model(input_ids=torch.tensor([ids], device="cuda"), use_cache=True, logits_to_keep=1).past_key_values
            qs = [enc(f"Comment: {t}\nAnnotator: {ctx['names'][0]}\nLabel:") for t, _ in ctx["q"]]
            gold = np.array(ref["gold"])
            n, plen, qlen = len(qs), len(ids), max(map(len, qs))
            inputs = torch.zeros((n, qlen), dtype=torch.long, device="cuda")
            pos = torch.zeros_like(inputs)
            mask = torch.zeros((n, plen+qlen), dtype=torch.long, device="cuda")
            mask[:, :plen] = 1
            for i, q in enumerate(qs):
                inputs[i, -len(q):] = torch.tensor(q, device="cuda")
                pos[i, -len(q):] = torch.arange(plen, plen+len(q), device="cuda")
                mask[i, -len(q):] = 1
            scores = {}
            for on in [False, True]:
                copied = copy.deepcopy(cache)
                copied.batch_repeat_interleave(n)
                state["on"] = on
                lo = model(input_ids=inputs, position_ids=pos, attention_mask=mask,
                    past_key_values=copied, use_cache=True, logits_to_keep=1).logits[:, -1].float()
                state["on"] = False
                z = (lo[:, label_ids[1]] - lo[:, label_ids[0]]).cpu().numpy()
                top = lo.argmax(-1).cpu().numpy()
                scores["adapter" if on else "native"] = {
                    "z": z.tolist(), "accuracy": float(np.mean((z > 0) == (gold > 0))),
                    "signed_margin": float(np.mean(z*gold)),
                    "argmax_label_rate": float(np.isin(top, label_ids).mean()),
                    "argmax_accuracy": float(np.mean(top == np.array(label_ids)[(gold > 0).astype(int)]))}
            errors.append(max(abs(x-y) for x,y in zip(scores["native"]["z"], ref["conditions"]["single"]["z"])))
            assert max(errors) <= .001, errors
            row = {"context": ci, "scores": scores, "native_replication_error": errors[-1]}
            records.append(row)
            stream.write(json.dumps(row) + "\n"); stream.flush()
            print(ci+1, "/", len(cs), "native", scores["native"]["accuracy"], "adapter", scores["adapter"]["accuracy"], flush=True)
    out = {"registered_after_pilot_before_followup": True, "n_contexts": len(cs),
           "numeric_max_error": max(errors), "metrics": {}}
    for k in ["native", "adapter"]:
        out["metrics"][k] = {m: interval([r["scores"][k][m] for r in records])
                             for m in ["accuracy", "signed_margin", "argmax_label_rate", "argmax_accuracy"]}
    out["contrasts"] = {m: interval([r["scores"]["adapter"][m] - r["scores"]["native"][m] for r in records])
                        for m in ["accuracy", "signed_margin"]}
    (dest / "analysis.json").write_text(json.dumps(out, indent=2) + "\n")
    elapsed = time.time() - started
    run = {"args": vars(args), "elapsed_seconds": elapsed, "gpu_hours": elapsed/3600,
           "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "source_contexts_sha256": hashlib.sha256((source / "contexts.jsonl").read_bytes()).hexdigest(),
           "weights_sha256": hashlib.sha256(Path(args.weights).read_bytes()).hexdigest(),
           "torch": torch.__version__, "transformers": transformers.__version__,
           "dtype": "float32", "attn": "eager", "foreign_source_tokens": 0,
           "prefill_adapter_enabled": False, "adapter_scope": "answer last position only"}
    (dest / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(json.dumps(out, indent=2), flush=True)


if __name__ == "__main__":
    main()
