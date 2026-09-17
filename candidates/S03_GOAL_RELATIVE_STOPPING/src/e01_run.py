"""
S03 / E01 — exact-prefix goal intervention on native assistant stopping.

This experiment distinguishes:
  X: the native stop decision responds to USER-GOAL COMPLETION
from
  Y: the native stop decision responds only to TEXTUAL/SURFACE CLOSURE of the
     generated prefix
about the acquisition target, by holding the assistant prefix token-for-token
identical and changing only the user's requested completion condition.

Primary estimand (per matched pair):

    stop_margin = logit(stop) - logit(correct_next_missing_token)
    d_goal      = stop_margin(complete) - stop_margin(incomplete)

Controls emitted for every item:
  * prefix_token_identity  -- hard assertion that the two conditions share the
                              exact same assistant prefix token ids
  * continuation awareness -- rank/prob of the correct missing continuation in
                              the INCOMPLETE condition
  * base textual closure   -- (separate script) pretrained EOS propensity on the
                              same prefix in a plain, non-chat format
"""
import argparse
import json
import os

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM

STAGE_REPOS = {
    "olmo2-1b": {
        "base": "allenai/OLMo-2-0425-1B",
        "sft": "allenai/OLMo-2-0425-1B-SFT",
        "dpo": "allenai/OLMo-2-0425-1B-DPO",
        "instruct": "allenai/OLMo-2-0425-1B-Instruct",
    },
    "olmo3-7b": {
        "base": "allenai/Olmo-3-1025-7B",
        "sft": "allenai/Olmo-3-7B-Instruct-SFT",
        "dpo": "allenai/Olmo-3-7B-Instruct-DPO",
        "instruct": "allenai/Olmo-3-7B-Instruct",
    },
}


def stop_token_ids(tok, model):
    """Every token id that actually terminates an assistant turn for this model.

    We take the union of the generation config's eos ids and the tokenizer eos,
    restricted to ids that exist.  Reported individually AND as a logsumexp so a
    dual-stop-token model (Olmo-3 uses <|im_end|> and <|endoftext|>) is not
    silently mismeasured.
    """
    ids = set()
    gc = model.generation_config
    e = gc.eos_token_id
    if isinstance(e, (list, tuple)):
        ids.update(int(x) for x in e)
    elif e is not None:
        ids.add(int(e))
    if tok.eos_token_id is not None:
        ids.add(int(tok.eos_token_id))
    return sorted(ids)


def build_pair_ids(tok, item, cond, chat):
    """Return (full_ids, p1_index, p2_index, sep_ids, missing_ids).

    The assistant prefix is assembled by CONCATENATING separately tokenized
    pieces so that the two conditions are guaranteed identical at the token
    level regardless of what the differing user message does to BPE.
    """
    user = item["user_complete"] if cond == "complete" else item["user_incomplete"]
    if chat:
        prompt_ids = tok.apply_chat_template(
            [{"role": "user", "content": user}], tokenize=True, add_generation_prompt=True
        )
    else:
        # plain-format fallback for base models with no chat template
        text = f"User: {user}\nAssistant:\n"
        prompt_ids = tok.encode(text, add_special_tokens=False)

    body_ids = tok.encode(item["prefix_text"], add_special_tokens=False)
    sep_ids = tok.encode(item["separator"], add_special_tokens=False)
    missing_ids = tok.encode(item["missing_text"], add_special_tokens=False)

    full = list(prompt_ids) + list(body_ids) + list(sep_ids)
    p1 = len(prompt_ids) + len(body_ids) - 1      # predicts the separator
    p2 = len(full) - 1                            # predicts the missing content
    return full, p1, p2, body_ids, sep_ids, missing_ids


@torch.no_grad()
def score(model, tok, ids, positions):
    x = torch.tensor([ids], device=model.device)
    out = model(x)
    logits = out.logits[0].float()
    return {p: logits[p] for p in positions}


def measure(model, tok, item, cond, chat, stop_ids):
    full, p1, p2, body_ids, sep_ids, missing_ids = build_pair_ids(tok, item, cond, chat)
    lg = score(model, tok, full, [p1, p2])
    sep_tok = sep_ids[0]
    mis_tok = missing_ids[0]
    rec = {}
    for tag, pos, comp in (("p1", p1, sep_tok), ("p2", p2, mis_tok)):
        v = lg[pos]
        stop_logit = torch.logsumexp(v[stop_ids], dim=0).item()
        rec[f"{tag}_stop_logit"] = stop_logit
        rec[f"{tag}_comp_logit"] = v[comp].item()
        rec[f"{tag}_margin"] = stop_logit - v[comp].item()
        probs = F.softmax(v, dim=-1)
        rec[f"{tag}_p_stop"] = float(probs[stop_ids].sum())
        rec[f"{tag}_p_comp"] = float(probs[comp])
        # continuation awareness: where does the correct missing token rank?
        rec[f"{tag}_comp_rank"] = int((v > v[comp]).sum())
        rec[f"{tag}_stop_rank"] = int((v > v[stop_ids].max()).sum())
        top = torch.topk(v, 5)
        rec[f"{tag}_top5"] = [tok.convert_ids_to_tokens(int(i)) for i in top.indices]
    rec["_prefix_ids"] = body_ids + sep_ids
    rec["_comp_tok_p2"] = tok.convert_ids_to_tokens(mis_tok)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", default="olmo2-1b")
    ap.add_argument("--stage", default="instruct")
    ap.add_argument("--stimuli", default="stimuli/e01_pairs.jsonl")
    ap.add_argument("--out", default=None)
    ap.add_argument("--plain", action="store_true",
                    help="force the plain User/Assistant format (used for base)")
    args = ap.parse_args()

    repo = STAGE_REPOS[args.family][args.stage]
    tok = AutoTokenizer.from_pretrained(repo)
    model = AutoModelForCausalLM.from_pretrained(
        repo, torch_dtype=torch.bfloat16, device_map="cuda"
    ).eval()
    chat = (tok.chat_template is not None) and not args.plain
    sids = stop_token_ids(tok, model)
    print(f"{repo}  chat_template={chat}  stop_ids={sids} "
          f"({[tok.convert_ids_to_tokens(i) for i in sids]})", flush=True)

    items = [json.loads(l) for l in open(args.stimuli)]
    rows = []
    for it in items:
        c = measure(model, tok, it, "complete", chat, sids)
        i = measure(model, tok, it, "incomplete", chat, sids)
        assert c.pop("_prefix_ids") == i.pop("_prefix_ids"), \
            f"exact-prefix violation on {it['item_id']}"
        comp_tok = c.pop("_comp_tok_p2"); i.pop("_comp_tok_p2")
        row = dict(item_id=it["item_id"], family=it["family"], n_given=it["n_given"],
                   comp_token=comp_tok, stage=args.stage, model_family=args.family,
                   chat=chat)
        for k, v in c.items():
            row["cmp_" + k] = v
        for k, v in i.items():
            row["inc_" + k] = v
        for tag in ("p1", "p2"):
            row[f"d_goal_{tag}"] = row[f"cmp_{tag}_margin"] - row[f"inc_{tag}_margin"]
        rows.append(row)

    outp = args.out or f"results/e01/{args.family}_{args.stage}{'_plain' if args.plain else ''}.jsonl"
    os.makedirs(os.path.dirname(outp), exist_ok=True)
    with open(outp, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("wrote", outp, len(rows))


if __name__ == "__main__":
    main()
