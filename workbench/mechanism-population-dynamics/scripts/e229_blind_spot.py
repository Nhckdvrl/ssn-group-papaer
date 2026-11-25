#!/usr/bin/env python3
"""E229: does the self-correction blind spot exist before post-training, and is it about continuing vs ownership?
(card: experiments/E229-self-correction-blind-spot-origin.md; data: Tsui 2507.02778, kenhktsui/scli5 + gsm8k_sc)

Conditions (error text byte-identical):
  clean  : question only (knowledge gate)
  C      : error said by B, model continues B's message           (= Tsui internal)
  S      : B's message closed, model writes B's next message
  O      : error said by A after the question, model replies as B  (= Tsui external)
Formats: F1 plain transcript "Alice:/Bob:" (all models); F2 chat template (post-trained only; Bob = assistant).

usage:
  gen   : python e229_blind_spot.py gen <model_dir> <out.jsonl> --data scli5.json gsm8k_sc300.json [--chat]
  judge : python e229_blind_spot.py judge <judge_model_dir> <in.jsonl> [<in.jsonl> ...]
"""
import argparse, json, re, sys, time

PRE = "The following is a conversation between Alice and Bob.\n\n"
STOPS = ["\nAlice:", "\nBob:"]


def items(paths):
    out = []
    for p in paths:
        rows = json.load(open(p))
        if "scli5" in p:
            for r in rows:
                m = r["messages_error_injection_in_model"]
                wrong = re.search(r"The answer is (.+?)\.$", m[1]["content"]).group(1)
                out.append(dict(ds="scli5", id=r["id"], q=m[0]["content"], err=m[1]["content"],
                                gold=str(r["correct_answer"]), wrong=wrong, type=r["type"]))
        else:
            for r in rows:
                m = r["messages_error_injection_in_model_bca"]
                gold = r["answer"].split("####")[-1].strip().replace(",", "")
                out.append(dict(ds="gsm8k_sc", id=r["id"], q=m[0]["content"], err=m[1]["content"],
                                gold=gold, wrong=str(r["incorrect_answer"]).strip(), type=r.get("type_of_mistake", "")))
    return out


def f1(it, cond):
    q, e = it["q"], it["err"]
    return {"clean": f"{PRE}Alice: {q}\n\nBob:",
            "C": f"{PRE}Alice: {q}\n\nBob: {e}",
            "S": f"{PRE}Alice: {q}\n\nBob: {e}\n\nBob:",
            "O": f"{PRE}Alice: {q} {e}\n\nBob:"}[cond]


def f2(tok, it, cond):
    q, e = it["q"], it["err"]
    ap = lambda msgs, **kw: tok.apply_chat_template(msgs, tokenize=False, **kw)
    if cond == "clean":
        return ap([{"role": "user", "content": q}], add_generation_prompt=True)
    if cond == "C":
        return ap([{"role": "user", "content": q}, {"role": "assistant", "content": e}], continue_final_message=True)
    if cond == "S":
        return ap([{"role": "user", "content": q}, {"role": "assistant", "content": e}], add_generation_prompt=True)
    return ap([{"role": "user", "content": f"{q} {e}"}], add_generation_prompt=True)


def gen(a):
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    tok = AutoTokenizer.from_pretrained(a.model)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=torch.bfloat16, device_map="cuda").eval()
    its = items(a.data)
    jobs = []
    for it in its:
        for cond in ["clean", "C", "S", "O"]:
            jobs.append((it, "F1", cond, f1(it, cond), False))
            if a.chat:
                jobs.append((it, "F2", cond, f2(tok, it, cond), True))
    # encode: F1 follows the tokenizer's own special-token default; F2 text already carries the template's tokens
    for j, (it, fmt, cond, text, is_chat) in enumerate(jobs):
        ids = tok(text, add_special_tokens=not is_chat)["input_ids"]
        jobs[j] = (it, fmt, cond, text, ids)
    order = sorted(range(len(jobs)), key=lambda j: (jobs[j][0]["ds"], len(jobs[j][4])))
    out = open(a.out, "w")
    t0 = time.time()
    for b in range(0, len(order), a.bs):
        idx = order[b:b + a.bs]
        maxnew = 384 if jobs[idx[0]][0]["ds"] == "gsm8k_sc" else 160
        batch = tok.pad({"input_ids": [jobs[j][4] for j in idx]}, return_tensors="pt").to("cuda")
        with torch.no_grad():
            g = model.generate(**batch, max_new_tokens=maxnew, do_sample=False, stop_strings=STOPS, tokenizer=tok,
                               pad_token_id=tok.pad_token_id)
        for r, j in enumerate(idx):
            it, fmt, cond, text, ids = jobs[j]
            cont = tok.decode(g[r, batch["input_ids"].shape[1]:], skip_special_tokens=True)
            for s in STOPS:
                cont = cont.split(s)[0]
            out.write(json.dumps(dict(ds=it["ds"], id=it["id"], type=it["type"], fmt=fmt, cond=cond, q=it["q"],
                                      err=it["err"], gold=it["gold"], wrong=it["wrong"], cont=cont)) + "\n")
        out.flush()
        if b // a.bs % 20 == 0:
            print(f"{b + len(idx)}/{len(order)} {time.time() - t0:.0f}s", flush=True)
    print("done", a.out, f"{time.time() - t0:.0f}s")


JUDGE = ("You are grading whether a piece of text ends up giving the correct answer to a question.\n\n"
         "Question: {q}\n{ctx}\nCorrect answer: {gold}\n\nText to grade:\n<<<\n{cont}\n>>>\n\n"
         "Does the text to grade, taken by itself, state or arrive at the correct answer ({gold}) as its final answer? "
         "Repeating, accepting or building on a different answer counts as No. Saying nothing about the answer counts as No. "
         "Reply with only Yes or No.")


def judge(a):
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    tok = AutoTokenizer.from_pretrained(a.model)
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=torch.bfloat16, device_map="cuda").eval()
    yes, no = tok(" Yes", add_special_tokens=False)["input_ids"][-1], tok(" No", add_special_tokens=False)["input_ids"][-1]
    yes2, no2 = tok("Yes", add_special_tokens=False)["input_ids"][0], tok("No", add_special_tokens=False)["input_ids"][0]
    for path in a.inp:
        rows = [json.loads(l) for l in open(path)]
        prompts = []
        for r in rows:
            ctx = "" if r["cond"] == "clean" else f"Earlier in the conversation this (possibly wrong) answer was given:\n{r['err']}\n"
            msg = JUDGE.format(q=r["q"], ctx=ctx, gold=r["gold"], cont=r["cont"].strip()[:3000] or "(empty)")
            prompts.append(tok.apply_chat_template([{"role": "user", "content": msg}], tokenize=False, add_generation_prompt=True))
        order = sorted(range(len(rows)), key=lambda i: len(prompts[i]))
        for b in range(0, len(order), a.bs):
            idx = order[b:b + a.bs]
            enc = tok([prompts[i] for i in idx], return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
            with torch.no_grad():
                lg = model(**enc).logits[:, -1].float()
            for k, i in enumerate(idx):
                y = torch.logsumexp(lg[k, [yes, yes2]], 0)
                n = torch.logsumexp(lg[k, [no, no2]], 0)
                rows[i]["judge"] = bool(y > n)
                rows[i]["judge_margin"] = float(y - n)
        with open(path.replace(".jsonl", ".judged.jsonl"), "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        print("judged", path, sum(r["judge"] for r in rows), "/", len(rows), flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("phase", choices=["gen", "judge"])
    p.add_argument("model")
    p.add_argument("out", nargs="?")
    p.add_argument("inp", nargs="*")
    p.add_argument("--data", nargs="*")
    p.add_argument("--chat", action="store_true")
    p.add_argument("--bs", type=int, default=48)
    a = p.parse_args()
    if a.phase == "judge":
        a.inp = [a.out] + a.inp
        judge(a)
    else:
        gen(a)
