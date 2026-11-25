#!/usr/bin/env python3
"""E230: same check phrase at the start of the model's text in C / S / O (card: experiments/E230-*.md).
Reuses E229's data, formats and judge prompt; adds a second judge question (does the text say the earlier answer is wrong?).

usage:
  gen   : python e230_check_frame.py gen <model_dir> <out.jsonl> --data scli5.json gsm8k_sc300.json [--chat]
  judge : python e230_check_frame.py judge <judge_model_dir> <in.jsonl> [<in.jsonl> ...]
"""
import argparse, json, sys, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e229_blind_spot import items, PRE, STOPS, JUDGE

FRAMES = {"V": "Let me check whether this answer is correct.", "W": "Wait,"}

FLAG = ("Question: {q}\nEarlier in the conversation this answer was given:\n{err}\n\nCorrect answer: {gold}\n\n"
        "Text written afterwards:\n<<<\n{cont}\n>>>\n\n"
        "Does the text written afterwards explicitly say that the earlier answer was wrong, incorrect or mistaken? "
        "Simply giving a different answer without saying the earlier one was wrong counts as No. Reply with only Yes or No.")


def f1(it, cond, fr):
    q, e = it["q"], it["err"]
    return {"C": f"{PRE}Alice: {q}\n\nBob: {e} {fr}",
            "S": f"{PRE}Alice: {q}\n\nBob: {e}\n\nBob: {fr}",
            "O": f"{PRE}Alice: {q} {e}\n\nBob: {fr}"}[cond]


def f2(tok, it, cond, fr):
    q, e = it["q"], it["err"]
    ap = lambda msgs: tok.apply_chat_template(msgs, tokenize=False, continue_final_message=True)
    u = lambda c: {"role": "user", "content": c}
    a = lambda c: {"role": "assistant", "content": c}
    if cond == "C":
        return ap([u(q), a(f"{e} {fr}")])
    if cond == "S":
        return ap([u(q), a(e), a(fr)])
    return ap([u(f"{q} {e}"), a(fr)])


def gen(args):
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    tok = AutoTokenizer.from_pretrained(args.model)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.bfloat16, device_map="cuda").eval()
    jobs = []
    si, sn = map(int, args.shard.split("/"))
    for k, it in enumerate(items(args.data)):
        if k % sn != si:
            continue
        for fk, fr in FRAMES.items():
            for cond in ["C", "S", "O"]:
                jobs.append((it, "F1", fk, cond, tok(f1(it, cond, fr))["input_ids"]))
                if args.chat:
                    jobs.append((it, "F2", fk, cond, tok(f2(tok, it, cond, fr), add_special_tokens=False)["input_ids"]))
    order = sorted(range(len(jobs)), key=lambda j: (jobs[j][0]["ds"], len(jobs[j][4])))
    out = open(args.out, "w")
    t0 = time.time()
    for b in range(0, len(order), args.bs):
        idx = order[b:b + args.bs]
        maxnew = 384 if jobs[idx[0]][0]["ds"] == "gsm8k_sc" else 160
        batch = tok.pad({"input_ids": [jobs[j][4] for j in idx]}, return_tensors="pt").to("cuda")
        with torch.no_grad():
            g = model.generate(**batch, max_new_tokens=maxnew, do_sample=False, stop_strings=STOPS, tokenizer=tok,
                               pad_token_id=tok.pad_token_id)
        for r, j in enumerate(idx):
            it, fmt, fk, cond, _ = jobs[j]
            cont = tok.decode(g[r, batch["input_ids"].shape[1]:], skip_special_tokens=True)
            for s in STOPS:
                cont = cont.split(s)[0]
            out.write(json.dumps(dict(ds=it["ds"], id=it["id"], type=it["type"], fmt=fmt, frame=fk, cond=cond,
                                      q=it["q"], err=it["err"], gold=it["gold"], wrong=it["wrong"],
                                      cont=f"{FRAMES[fk]}{cont}")) + "\n")
        out.flush()
        if b // args.bs % 20 == 0:
            print(f"{b + len(idx)}/{len(order)} {time.time() - t0:.0f}s", flush=True)
    print("done", args.out, f"{time.time() - t0:.0f}s")


VERDICT = ("Below is a question, an answer that was given to it, and a text written afterwards by someone checking that answer.\n\n"
           "Question: {q}\nGiven answer: {err}\n\nText written afterwards (it begins with \"{frame}\"):\n<<<\n{frame} {body}\n>>>\n\n"
           "Decide what the text concludes about the given answer. Do not judge whether the given answer is actually right; "
           "only report what the text itself says.\n"
           "A = the text says the given answer is correct, or it ends up with the same answer as the given answer\n"
           "B = the text says the given answer is wrong, or it ends up with a different answer\n"
           "C = the text gives neither a verdict nor a final answer\n"
           "Reply with one letter.")


def verdict(args):
    """11-25 added after validation showed the flag prompt reads the check phrase itself as flagging and the answer
    prompt accepts 'X is smaller than Y. Yes, the answer is correct.' as correct; judges only the model's own text."""
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    tok = AutoTokenizer.from_pretrained(args.model)
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.bfloat16, device_map="cuda").eval()
    L = [tok(x, add_special_tokens=False)["input_ids"][0] for x in "ABC"]
    for path in args.inp:
        rows = json.load(open(path)) if path.endswith(".json") else [json.loads(l) for l in open(path)]
        prompts = []
        for r in rows:
            fr = FRAMES[r["frame"]]
            body = r["cont"][len(fr):].strip()[:3000] or "(nothing)"
            msg = VERDICT.format(q=r["q"], err=r["err"], frame=fr, body=body)
            prompts.append(tok.apply_chat_template([{"role": "user", "content": msg}], tokenize=False, add_generation_prompt=True))
        order = sorted(range(len(rows)), key=lambda i: len(prompts[i]))
        for b in range(0, len(order), args.bs):
            idx = order[b:b + args.bs]
            enc = tok([prompts[i] for i in idx], return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
            with torch.no_grad():
                lg = model(**enc).logits[:, -1].float()
            for k, i in enumerate(idx):
                rows[i]["verdict"] = "ABC"[int(lg[k, L].argmax())]
                if not rows[i]["cont"][len(FRAMES[rows[i]["frame"]]):].strip():
                    rows[i]["verdict"] = "C"
        with open(path.replace(".judged.jsonl", ".verdict.jsonl").replace("manual60.json", "manual60.v2.json"), "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        import collections
        print("verdict", path, dict(collections.Counter(r["verdict"] for r in rows)), flush=True)


def judge(args):
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    tok = AutoTokenizer.from_pretrained(args.model)
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.bfloat16, device_map="cuda").eval()
    ids = lambda w: tok(w, add_special_tokens=False)["input_ids"]
    Y, N = [ids(" Yes")[-1], ids("Yes")[0]], [ids(" No")[-1], ids("No")[0]]
    for path in args.inp:
        rows = [json.loads(l) for l in open(path)]
        for key, tmpl in [("judge", "answer"), ("flag", "flag")]:
            prompts = []
            for r in rows:
                cont = r["cont"].strip()[:3000] or "(empty)"
                if tmpl == "answer":
                    ctx = f"Earlier in the conversation this (possibly wrong) answer was given:\n{r['err']}\n"
                    msg = JUDGE.format(q=r["q"], ctx=ctx, gold=r["gold"], cont=cont)
                else:
                    msg = FLAG.format(q=r["q"], err=r["err"], gold=r["gold"], cont=cont)
                prompts.append(tok.apply_chat_template([{"role": "user", "content": msg}], tokenize=False, add_generation_prompt=True))
            order = sorted(range(len(rows)), key=lambda i: len(prompts[i]))
            for b in range(0, len(order), args.bs):
                idx = order[b:b + args.bs]
                enc = tok([prompts[i] for i in idx], return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
                with torch.no_grad():
                    lg = model(**enc).logits[:, -1].float()
                for k, i in enumerate(idx):
                    rows[i][key] = bool(torch.logsumexp(lg[k, Y], 0) > torch.logsumexp(lg[k, N], 0))
        with open(path.replace(".jsonl", ".judged.jsonl"), "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        print("judged", path, sum(r["judge"] for r in rows), sum(r["flag"] for r in rows), "/", len(rows), flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("phase", choices=["gen", "judge", "verdict"])
    p.add_argument("model")
    p.add_argument("out", nargs="?")
    p.add_argument("inp", nargs="*")
    p.add_argument("--data", nargs="*")
    p.add_argument("--chat", action="store_true")
    p.add_argument("--bs", type=int, default=48)
    p.add_argument("--shard", default="0/1", help="i/n: keep items with index %% n == i")
    a = p.parse_args()
    if a.phase in ("judge", "verdict"):
        a.inp = [a.out] + a.inp
        (judge if a.phase == "judge" else verdict)(a)
    else:
        gen(a)
