"""Native-chat criterion identification vs application; no state/head selection."""
import argparse
import hashlib
import json
import platform
import subprocess
import time
from pathlib import Path
import numpy as np
from e88_criterion_transfer import NAMES, LABELS, contexts, prefix_text, interval

SYSTEM = ("Infer each reviewer's judgment criterion from the examples and follow the requested reviewer's criterion. "
          "For a review, answer exactly positive or negative. For a criterion question, answer exactly food or service. "
          "Use no other words.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--seed", type=int, default=89001)
    a = ap.parse_args()
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_num_threads(6)
    torch.manual_seed(0)
    dest = Path(a.out)
    dest.mkdir(parents=True, exist_ok=True)
    assert not (dest / "behavior.jsonl").exists()
    cs = contexts(a.n, a.seed, "confirmation")
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True)
    groups = {}
    for label in LABELS + ["food", "service"]:
        ids = {tok.encode(pre + word, add_special_tokens=False)[0]
               for pre in ("", " ") for word in (label, label.capitalize())
               if len(tok.encode(pre + word, add_special_tokens=False)) == 1}
        assert ids
        groups[label] = sorted(ids)
    assert not set(groups["positive"]) & set(groups["negative"])
    assert not set(groups["food"]) & set(groups["service"])

    def prompt(content):
        return tok.apply_chat_template([{"role": "system", "content": SYSTEM}, {"role": "user", "content": content}],
                                       tokenize=True, add_generation_prompt=True, enable_thinking=False)

    example = prompt(prefix_text(cs[0]) + f"Source: {NAMES[0]}\nReview: {cs[0]['queries'][0]['text']}\nLabel:")
    (dest / "preflight.json").write_text(json.dumps({"args": vars(a), "groups": groups,
        "example_native_prompt": tok.decode(example), "example_ids": example}, indent=2) + "\n")
    (dest / "contexts.jsonl").write_text("".join(json.dumps(c) + "\n" for c in cs))
    t0 = time.time()
    print("loading model", flush=True)
    model = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True, dtype=torch.float32,
                                               device_map="cuda", attn_implementation="eager").eval()

    def logits_batch(seqs):
        width = max(map(len, seqs))
        ids = torch.full((len(seqs), width), tok.pad_token_id, dtype=torch.long, device="cuda")
        mask = torch.zeros_like(ids)
        for i, seq in enumerate(seqs):
            ids[i, -len(seq):] = torch.tensor(seq, device="cuda")
            mask[i, -len(seq):] = 1
        pos = mask.cumsum(-1) - 1
        pos.masked_fill_(mask == 0, 0)
        return model(input_ids=ids, attention_mask=mask, position_ids=pos,
                     use_cache=False, logits_to_keep=1).logits[:, -1].float()

    def score(seqs, words):
        data = []
        for start in range(0, len(seqs), 4):
            logits = logits_batch(seqs[start:start+4])
            z = (torch.logsumexp(logits[:, groups[words[1]]], -1)
                 - torch.logsumexp(logits[:, groups[words[0]]], -1))
            top = logits.argmax(-1).tolist()
            data.extend({"z": float(v), "argmax_token": t,
                         "argmax_class": 0 if t in groups[words[0]] else 1 if t in groups[words[1]] else -1}
                        for v, t in zip(z, top))
        return data

    errors = []
    rows = []
    settings = {"base": {}, "flip": {"flip": True}, "explicit": {"explicit": True},
                "explicit_flip": {"explicit": True, "flip": True}}
    with torch.inference_mode(), (dest / "behavior.jsonl").open("w") as stream:
        for ci, ctx in enumerate(cs):
            row = {"context": ci, "criteria": ctx["criteria"], "queries": ctx["queries"], "conditions": {}}
            for name, opts in settings.items():
                head = prefix_text(ctx, **opts)
                seqs = [prompt(head + f"Source: {NAMES[q['source']]}\nReview: {q['text']}\nLabel:") for q in ctx["queries"]]
                if ci == 0 and name == "base":
                    batched = logits_batch(seqs[:4])
                    for i in range(4):
                        single = logits_batch([seqs[i]])
                        errors.append(float((batched[i] - single[0]).abs().max()))
                    assert max(errors) <= .01, errors
                criteria_seqs = [prompt(head + f"Source: {source}\nQuestion: Which aspect determines this reviewer's judgments?\nAnswer:")
                                 for source in NAMES]
                row["conditions"][name] = {"application": score(seqs, LABELS),
                                           "recognition": score(criteria_seqs, ["food", "service"])}
            stream.write(json.dumps(row) + "\n")
            stream.flush()
            rows.append(row)
            print(f"context {ci+1}/{len(cs)}, elapsed {time.time()-t0:.1f}s", flush=True)
    out = {"conditions": {}, "contrasts": {}}
    for key in settings:
        gold = np.array([[q["donor_gold"] if "flip" in key else q["recipient_gold"] for q in r["queries"]] for r in rows])
        z = np.array([[s["z"] for s in r["conditions"][key]["application"]] for r in rows])
        top = np.array([[s["argmax_class"] for s in r["conditions"][key]["application"]] for r in rows])
        cgold = np.array([[1-c if "flip" in key else c for c in r["criteria"]] for r in rows])
        cz = np.array([[s["z"] for s in r["conditions"][key]["recognition"]] for r in rows])
        ctop = np.array([[s["argmax_class"] for s in r["conditions"][key]["recognition"]] for r in rows])
        disagree = np.array([q["food"] != q["service"] for q in rows[0]["queries"]])
        out["conditions"][key] = {
            "recognition_accuracy": interval(((cz > 0) == cgold).mean(1)),
            "recognition_unrestricted_accuracy": interval((ctop == cgold).mean(1)),
            "application_accuracy": interval(((z > 0) == (gold > 0)).mean(1)),
            "application_unrestricted_accuracy": interval((top == (gold > 0)).mean(1)),
            "discordant_accuracy": interval(((z[:, disagree] > 0) == (gold[:, disagree] > 0)).mean(1)),
            "recognition_minus_discordant_accuracy": interval(((cz > 0) == cgold).mean(1)
                - ((z[:, disagree] > 0) == (gold[:, disagree] > 0)).mean(1)),
            "application_label_argmax_fraction": interval((top >= 0).mean(1)),
            "recognition_label_argmax_fraction": interval((ctop >= 0).mean(1))}
    run = {"args": vars(a), "seconds": time.time()-t0, "numeric_max_error": max(errors),
           "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "data_engine_sha256": hashlib.sha256(Path(__file__).with_name("e88_criterion_transfer.py").read_bytes()).hexdigest(),
           "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
           "torch": torch.__version__, "transformers": transformers.__version__, "host": platform.node(), "gpu": torch.cuda.get_device_name()}
    out["run"] = run
    (dest / "run.json").write_text(json.dumps(run, indent=2)+"\n")
    (dest / "analysis.json").write_text(json.dumps(out, indent=2)+"\n")
    print(json.dumps(out, indent=2), flush=True)


if __name__ == "__main__":
    main()
