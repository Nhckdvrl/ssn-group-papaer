"""Render a checkpoint with a model's chat template into token ids + event spans + decision chunk."""
import bisect, re
import torch


def _tmpl(tok, msgs, tools, gen):
    m = [{k: v for k, v in x.items() if k in ("role", "content", "tool_calls")} for x in msgs]
    return tok.apply_chat_template(m, tools=tools, tokenize=False, add_generation_prompt=gen,
                                   enable_thinking=False)


def render(tok, rec, max_hist=12000):
    msgs, tools = rec["messages"], rec.get("tools")
    k = len(msgs) - 1
    hist = _tmpl(tok, msgs[:k], tools, False)
    prompt = _tmpl(tok, msgs[:k], tools, True)
    assert prompt.startswith(hist)
    full_conv = _tmpl(tok, msgs, tools, False)
    last = full_conv[full_conv.rindex("<|im_start|>assistant"):]
    body = last[len("<|im_start|>assistant\n"):]
    if body.startswith("<think>\n\n</think>\n\n"):
        body = body[len("<think>\n\n</think>\n\n"):]
    body = body.rstrip()
    if body.endswith("<|im_end|>"):
        body = body[:-len("<|im_end|>")]
    full = prompt + body
    # event boundaries: one <|im_start|> block per message
    starts = [m.start() for m in re.finditer(re.escape("<|im_start|>"), hist)]
    if len(starts) != k:
        raise ValueError(f"block count {len(starts)} != {k}")
    bounds = starts + [len(hist)]
    enc = tok(full, return_offsets_mapping=True, add_special_tokens=False)
    ids, offs = enc["input_ids"], enc["offset_mapping"]
    starts_tok = [a for a, b in offs]
    import bisect

    def c2t(c):
        return bisect.bisect_left(starts_tok, c)
    tb = [c2t(c) for c in bounds]
    N = tb[-1]
    if N > max_hist:
        raise ValueError(f"history too long")
    p_end = c2t(len(prompt))
    act = None
    if rec.get("action_char_span") is not None:
        a0, a1 = rec["action_char_span"]
        cs = len(prompt) + body.find(msgs[-1]["content"][:40]) if msgs[-1]["content"][:40] in body else None
        if cs is not None and body.find(msgs[-1]["content"][:40]) >= 0:
            act = (c2t(cs + a0) - N, c2t(cs + a1) - N)
    events = [{"j": j, "ev": msgs[j]["ev"], "s": tb[j], "e": tb[j + 1]} for j in range(k)]
    return {"ids": torch.tensor(ids), "N": N, "dec_lo": p_end - N, "L": len(ids) - N, "events": events,
            "act": act}
