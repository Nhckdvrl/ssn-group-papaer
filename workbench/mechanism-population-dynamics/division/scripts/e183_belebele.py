#!/usr/bin/env python3
"""E183 Belebele per-language accuracy (card: division/experiments/E183-routing-alignment-vs-transfer.md).

Zero-shot, lm-evaluation-harness `belebele` prompt, log-likelihood of the next token " A"/" B"/" C"/" D".
One forward per item; only the last prompt position goes through the LM head.
  --chat : pre-registered fallback (only if the English positive control fails): the model's chat template.
Outputs: <out>/items_<model>[_chat].npz (per-item letter log-probs) and <json> with per-language accuracy.
"""
import argparse, json, os, time
import numpy as np
import torch

LANGS = ["eng_Latn", "arb_Arab", "asm_Beng", "bam_Latn", "ben_Beng", "fra_Latn", "hin_Deva", "lit_Latn",
         "ory_Orya", "pes_Arab", "srp_Cyrl", "tha_Thai", "zho_Hans",
         "deu_Latn", "spa_Latn", "jpn_Jpan", "kor_Hang", "swh_Latn", "rus_Cyrl", "tam_Taml"]
BELE = "/home/xiang/mechpop_cache/belebele"
MODELS = {"qwen3": ("Qwen/Qwen3-30B-A3B", "sdpa"),
          "gptoss": ("openai/gpt-oss-20b", "eager"),
          "olmoe": ("allenai/OLMoE-1B-7B-0125-Instruct", "sdpa")}

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True, choices=list(MODELS))
ap.add_argument("--out", required=True)
ap.add_argument("--json", required=True)
ap.add_argument("--chat", action="store_true")
ap.add_argument("--batch-tokens", type=int, default=24000)
ap.add_argument("--limit", type=int, default=0, help="items per language (0 = all); smoke tests only")
ap.add_argument("--langs", default=",".join(LANGS))
ap.add_argument("--suffix", default="", help="output-file suffix when a run is split across GPUs")
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
langs = args.langs.split(",")
MODEL, ATTN = MODELS[args.model]
t0 = time.time()


def log(*a):
    print(f"[{time.strftime('%H:%M:%S')} +{time.time() - t0:7.1f}s]", *a, flush=True)


def prompt(r):
    return (f"P: {r['flores_passage']}\nQ: {r['question'].strip()}\nA: {r['mc_answer1']}\nB: {r['mc_answer2']}\n"
            f"C: {r['mc_answer3']}\nD: {r['mc_answer4']}\nAnswer:")


from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402
tok = AutoTokenizer.from_pretrained(MODEL)
LET = []
for c in "ABCD":
    ids = tok(" " + c, add_special_tokens=False)["input_ids"]
    assert len(ids) == 1, (c, ids)
    LET.append(ids[0])
log("letter ids", LET, "tokens", [tok.decode([i]) for i in LET])


def encode(text):
    if not args.chat:
        return tok(text)["input_ids"]
    msgs = [{"role": "user", "content": text + "\nAnswer with the letter only."}]
    kw = {"enable_thinking": False} if args.model == "qwen3" else {}
    s = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **kw)
    if args.model == "gptoss":
        s = s + "<|channel|>final<|message|>"
    return tok(s, add_special_tokens=False)["input_ids"]


items = []  # (lang_idx, item_idx, ids, gold)
for li, lg in enumerate(langs):
    rows = [json.loads(x) for x in open(f"{BELE}/{lg}.jsonl", encoding="utf-8") if x.strip()]
    assert len(rows) == 900, (lg, len(rows))
    if args.limit:
        rows = rows[:args.limit]
    for j, r in enumerate(rows):
        items.append((li, j, encode(prompt(r)), int(r["correct_answer_num"]) - 1))
lens = np.array([len(x[2]) for x in items])
log(f"{len(items)} items; tokens total {lens.sum()}, max {lens.max()}; mean by lang:",
    {lg: int(lens[[i for i, x in enumerate(items) if x[0] == li]].mean()) for li, lg in enumerate(langs)})
if args.chat:
    log("chat example tail:", repr(tok.decode(items[0][2][-40:])))
else:
    log("example tail:", repr(tok.decode(items[0][2][-30:])))

log("loading", MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16, device_map={"": 0}, attn_implementation=ATTN)
model.eval()
dev = torch.device("cuda")
pad = tok.pad_token_id if tok.pad_token_id is not None else 0
LP = np.zeros((len(items), 4), np.float32)
order = np.argsort(lens)
batches, cur = [], []
for i in order:
    if cur and (len(cur) + 1) * lens[i] > args.batch_tokens:
        batches.append(cur); cur = []
    cur.append(i)
if cur:
    batches.append(cur)
lid = torch.tensor(LET, device=dev)
with torch.no_grad():
    for bi, b in enumerate(batches):
        T = int(lens[b].max())
        ids = torch.full((len(b), T), pad, dtype=torch.long)
        am = torch.zeros((len(b), T), dtype=torch.long)
        for r, i in enumerate(b):
            ids[r, :lens[i]] = torch.tensor(items[i][2]); am[r, :lens[i]] = 1
        ids, am = ids.to(dev), am.to(dev)
        hs = model.model(input_ids=ids, attention_mask=am, use_cache=False).last_hidden_state
        last = hs[torch.arange(len(b), device=dev), am.sum(1) - 1]
        logits = model.lm_head(last).float()
        lp = torch.log_softmax(logits, -1)[:, lid]
        LP[b] = lp.cpu().numpy()
        if bi % 50 == 0:
            log(f"batch {bi}/{len(batches)} T={T} B={len(b)}")

L_ = np.array([x[0] for x in items]); J = np.array([x[1] for x in items]); G = np.array([x[3] for x in items])
pred = LP.argmax(1)
tag = ("_chat" if args.chat else "") + args.suffix
np.savez(os.path.join(args.out, f"items_{args.model}{tag}.npz"), lang=L_, item=J, gold=G, lp=LP, langs=np.array(langs))
acc = {lg: float((pred[L_ == li] == G[L_ == li]).mean()) for li, lg in enumerate(langs)}
# letter-prior diagnostic: share of predictions per letter
pdist = {lg: np.bincount(pred[L_ == li], minlength=4).tolist() for li, lg in enumerate(langs)}
res = {"model": MODEL, "key": args.model, "chat": args.chat, "n_per_lang": int((L_ == 0).sum()), "acc": acc,
       "pred_letter_counts": pdist, "mean_len": {lg: float(lens[L_ == li].mean()) for li, lg in enumerate(langs)},
       "wall_s": time.time() - t0, "host": os.uname().nodename, "gpu": torch.cuda.get_device_name(0),
       "prompt": "lm-eval-harness belebele: P/Q/A-D/Answer:, letter log-likelihood, zero-shot"}
os.makedirs(os.path.dirname(os.path.abspath(args.json)), exist_ok=True)
json.dump(res, open(args.json, "w"), indent=1)
log("done", json.dumps(acc))
