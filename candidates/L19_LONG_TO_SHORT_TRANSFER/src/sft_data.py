"""Prompt construction and loss masking for L19.

Every run trains on 20,000 examples: a fixed UltraChat *block A* that is byte-identical
across all conditions, plus a *block B* that is the only thing the condition changes.

    condition        block B
    SHORT-SUPPORT    NQ, context = human gold long-answer paragraph
    LONG-FULL        NQ, context = the whole Wikipedia page   (same ids, same targets)
    PC-UC-UC         more UltraChat            } parent's dataset swap,
    PC-UC-CHATQA2    ChatQA2 long SFT          } run in the same pilot regime

For the SHORT-SUPPORT / LONG-FULL pair the block-B examples differ in exactly one
substring and produce identical completion tokens, hence identical loss-bearing tokens.
"""
import random

NQ_USER = "{context}\n\nQuestion: {question}"
UC_MAX_TOK = 4096


def _render(tokz, messages):
    """(input_ids, labels) with loss on assistant turns only."""
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


def _pack(tokz, msgs, source, _id, cap=None):
    ids, labels = _render(tokz, msgs)
    if cap:
        ids, labels = ids[:cap], labels[:cap]
    return dict(input_ids=ids, labels=labels, source=source, id=_id)


def nq_example(tokz, pair, condition):
    ctx = pair["support"] if condition == "SHORT-SUPPORT" else pair["page"]
    return _pack(tokz, [{"role": "user",
                         "content": NQ_USER.format(context=ctx, question=pair["question"])},
                        {"role": "assistant", "content": pair["answer"]}],
                 "nq", pair["id"])


def uc_example(tokz, conv):
    return _pack(tokz, [{"role": m["role"], "content": m["content"]}
                        for m in conv["messages"]],
                 "ultrachat", conv.get("prompt_id", ""), cap=UC_MAX_TOK)


def chatqa2_example(tokz, rec, cap=32768):
    """ChatQA2 long_sft records: a document plus a QA turn list."""
    doc = rec.get("document") or rec.get("context") or ""
    msgs = []
    turns = rec.get("messages") or rec.get("conversations") or []
    for i, m in enumerate(turns):
        role = m.get("role") or ("user" if m.get("from") in ("human", "user") else "assistant")
        content = m.get("content") or m.get("value") or ""
        if i == 0 and doc:
            content = f"{doc}\n\n{content}"
        msgs.append({"role": role, "content": content})
    if not msgs:
        return None
    if rec.get("answers"):
        msgs.append({"role": "assistant", "content": rec["answers"][0]})
    return _pack(tokz, msgs, "chatqa2", str(rec.get("id", "")), cap=cap)


def build_run(tokz, block_a, block_b_raw, condition, seed, max_len):
    """block_a: UltraChat records. block_b_raw: NQ pairs / UltraChat / ChatQA2 records."""
    items = [uc_example(tokz, c) for c in block_a]
    for r in block_b_raw:
        if condition in ("SHORT-SUPPORT", "LONG-FULL"):
            items.append(nq_example(tokz, r, condition))
        elif condition == "PC-UC-UC":
            items.append(uc_example(tokz, r))
        elif condition == "PC-UC-CHATQA2":
            e = chatqa2_example(tokz, r, cap=max_len)
            if e: items.append(e)
        else:
            raise ValueError(condition)
    items = [x for x in items if len(x["input_ids"]) <= max_len
             and any(y != -100 for y in x["labels"])]
    random.Random(seed).shuffle(items)
    return items
