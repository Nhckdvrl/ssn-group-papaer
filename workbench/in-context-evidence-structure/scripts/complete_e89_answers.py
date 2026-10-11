"""Complete all censored E89 answers, preserving old responses and batch grouping."""
import argparse
import copy
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path
import numpy as np
from e88_criterion_transfer import NAMES, LABELS, prefix_text, interval
from e89_native_criterion import CLEAR_SYSTEM


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    source, dest = Path(a.source), Path(a.out)
    dest.mkdir(parents=True, exist_ok=True)
    assert not (dest/"behavior.jsonl").exists()
    rows = [json.loads(x) for x in (source/"behavior.jsonl").read_text().splitlines()]
    cs = [json.loads(x) for x in (source/"contexts.jsonl").read_text().splitlines()]
    oldrun = json.loads((source/"run.json").read_text())
    assert oldrun["args"]["clear_request"] and oldrun["args"]["generate"]
    before = sum(s["truncated"] for r in rows for c in r["conditions"].values() for s in c["application"])
    import torch
    import transformers
    from transformers import AutoTokenizer, AutoModelForCausalLM
    torch.set_num_threads(6)
    torch.manual_seed(0)
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True)
    t0 = time.time()
    print(f"Completing {before} censored responses; loading model", flush=True)
    model = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True, dtype=torch.float32,
                                               device_map="cuda", attn_implementation="eager").eval()
    settings = {"base": {}, "flip": {"flip": True}, "explicit": {"explicit": True},
                "explicit_flip": {"explicit": True, "flip": True}}
    prefixes_checked = 0
    completed_rows = []
    with torch.inference_mode(), (dest/"behavior.jsonl").open("w") as stream:
        for ci, (oldrow, ctx) in enumerate(zip(rows, cs)):
            row = copy.deepcopy(oldrow)
            for name, opts in settings.items():
                old = oldrow["conditions"][name]["application"]
                head = prefix_text(ctx, **opts)
                for start in range(0, len(old), 4):
                    if not any(s["truncated"] for s in old[start:start+4]):
                        continue
                    seqs = []
                    for q in ctx["queries"][start:start+4]:
                        content = (head + f"Source: {NAMES[q['source']]}\nReview: {q['text']}\n"
                                   + f"What is {NAMES[q['source']]}'s judgment of this review? Answer exactly positive or negative.")
                        seqs.append(tok.apply_chat_template([{"role":"system","content":CLEAR_SYSTEM},
                                                             {"role":"user","content":content}],
                                                            tokenize=True, add_generation_prompt=True, enable_thinking=False))
                    width = max(map(len, seqs))
                    ids = torch.full((len(seqs),width), tok.pad_token_id, dtype=torch.long, device="cuda")
                    mask = torch.zeros_like(ids)
                    for i, seq in enumerate(seqs):
                        ids[i,-len(seq):] = torch.tensor(seq,device="cuda")
                        mask[i,-len(seq):] = 1
                    generated = model.generate(input_ids=ids, attention_mask=mask, max_new_tokens=512,
                                               do_sample=False, pad_token_id=tok.pad_token_id, eos_token_id=tok.eos_token_id)
                    for i, tokens in enumerate(generated[:,width:].tolist()):
                        prior = old[start+i]
                        text = tok.decode(tokens,skip_special_tokens=True)
                        if prior["truncated"]:
                            assert text.startswith(prior["text"]), {"context":ci,"condition":name,"query":start+i,
                                                                   "old":prior["text"],"new":text[:200]}
                            prefixes_checked += 1
                            matches = set(re.findall(r"\b(negative|positive)\b",text.lower()))
                            s = row["conditions"][name]["application"][start+i]
                            s.update(short_text=prior["text"], text=text, continuation_token_ids=tokens,
                                     generated_class=LABELS.index(next(iter(matches))) if len(matches)==1 else -1,
                                     exact_word_class=LABELS.index(text.strip().lower()) if text.strip().lower() in LABELS else -1,
                                     truncated=tok.eos_token_id not in tokens)
                        else:
                            assert text == prior["text"], "Completed old answer changed on budget extension"
            stream.write(json.dumps(row)+"\n"); stream.flush()
            completed_rows.append(row)
            print(f"context {ci+1}/{len(rows)}, checked {prefixes_checked}, elapsed {time.time()-t0:.1f}s",flush=True)
    assert prefixes_checked == before
    out = {"conditions": {}}
    for key in settings:
        appgold=np.array([[q["donor_gold"] if "flip" in key else q["recipient_gold"] for q in r["queries"]] for r in rows])
        app=np.array([[s["generated_class"] for s in r["conditions"][key]["application"]] for r in completed_rows])
        cgold=np.array([[1-c if "flip" in key else c for c in r["criteria"]] for r in rows])
        rec=np.array([[s["generated_class"] for s in r["conditions"][key]["recognition"]] for r in completed_rows])
        disagree=np.array([q["food"]!=q["service"] for q in rows[0]["queries"]])
        out["conditions"][key]={"recognition_accuracy":interval((rec==cgold).mean(1)),
            "application_accuracy":interval((app==(appgold>0)).mean(1)),
            "discordant_accuracy":interval((app[:,disagree]==(appgold[:,disagree]>0)).mean(1)),
            "parse_fraction":interval((app>=0).mean(1)),
            "truncated_fraction":interval(np.array([[s["truncated"] for s in r["conditions"][key]["application"]] for r in completed_rows]).mean(1))}
    run={"args":vars(a),"source_run":oldrun,"seconds":time.time()-t0,"censored_before":before,
         "prefixes_checked":prefixes_checked,"n_contexts":len(rows),
         "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         "git_commit":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
         "torch":torch.__version__,"transformers":transformers.__version__}
    (dest/"run.json").write_text(json.dumps(run,indent=2)+"\n")
    out["run"]=run
    (dest/"analysis.json").write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2),flush=True)


if __name__=="__main__":
    main()
