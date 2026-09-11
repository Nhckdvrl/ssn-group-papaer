"""Prompt construction and loss masking for L19.

Invariant enforced here: for a given NQ id the SHORT-SUPPORT and LONG-FULL examples
differ in exactly one substring -- the context -- and produce identical completion
token sequences, hence identical loss-bearing tokens.
"""
import json, random

NQ_USER = "{context}\n\nQuestion: {question}"
UC_MAX_TOK = 4096


def _render(tokz, messages):
    """Return (input_ids, labels) with loss on assistant turns only."""
    ids, labels = [tokz.bos_token_id], [-100]
    for m in messages:
        head = tokz(f"<|start_header_id|>{m['role']}<|end_header_id|>\n\n",
                    add_special_tokens=False)["input_ids"]
        body = tokz(m["content"].strip() + "<|eot_id|>",
                    add_special_tokens=False)["input_ids"]
        ids += head + body
        labels += [-100] * len(head)
        labels += body if m["role"] == "assistant" else [-100] * len(body)
    return ids, labels


def nq_example(tokz, pair, condition):
    ctx = pair["support"] if condition == "SHORT-SUPPORT" else pair["page"]
    msgs = [{"role": "user",
             "content": NQ_USER.format(context=ctx, question=pair["question"])},
            {"role": "assistant", "content": pair["answer"]}]
    ids, labels = _render(tokz, msgs)
    return dict(input_ids=ids, labels=labels, source="nq", id=pair["id"])


def uc_example(tokz, conv, max_tok=UC_MAX_TOK):
    msgs = [{"role": m["role"], "content": m["content"]} for m in conv["messages"]]
    ids, labels = _render(tokz, msgs)
    return dict(input_ids=ids[:max_tok], labels=labels[:max_tok],
                source="ultrachat", id=conv.get("prompt_id", ""))


def build_run(tokz, pairs, ultrachat, condition, seed):
    """Same examples, same order, for every condition at a given seed."""
    items = [nq_example(tokz, p, condition) for p in pairs] + \
            [uc_example(tokz, c) for c in ultrachat]
    random.Random(seed).shuffle(items)
    return items
