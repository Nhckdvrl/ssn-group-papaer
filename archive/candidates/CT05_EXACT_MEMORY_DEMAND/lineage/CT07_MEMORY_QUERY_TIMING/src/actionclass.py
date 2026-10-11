"""Target-token classes for logged actions (same rules as CT05 src/analyze_action.py)."""
import bisect, re
import numpy as np
from render import _tmpl


def target_body(tok, rec):
    msgs, tools = rec["messages"], rec.get("tools")
    k = len(msgs) - 1
    prompt = _tmpl(tok, msgs[:k], tools, True)
    full_conv = _tmpl(tok, msgs, tools, False)
    last = full_conv[full_conv.rindex("<|im_start|>assistant"):]
    body = last[len("<|im_start|>assistant\n"):]
    if body.startswith("<think>\n\n</think>\n\n"):
        body = body[len("<think>\n\n</think>\n\n"):]
    body = body.rstrip()
    if body.endswith("<|im_end|>"):
        body = body[:-len("<|im_end|>")]
    return prompt, body


def char_classes(src, body):
    cls = np.array(["syntax"] * len(body), dtype=object)
    first_key = None
    if src == "tau":
        for m in re.finditer(r"<function=([^>\n]+)>", body):
            cls[m.start(1):m.end(1)] = "name"
        for m in re.finditer(r"<parameter=([^>\n]+)>\n(.*?)\n</parameter>", body, re.S):
            cls[m.start(1):m.end(1)] = "key"
            cls[m.start(2):m.end(2)] = "value"
            if first_key is None:
                first_key = m.group(1)
        name = re.search(r"<function=([^>\n]+)>", body)
        name = name.group(1) if name else None
    else:
        cls[:] = "prose"
        name = None
        blocks = list(re.finditer(r"```(?:\w*\n)?(.*?)```", body, re.S))
        if blocks:
            b = blocks[-1]
            cmd = body[b.start(1):b.end(1)]
            words = list(re.finditer(r"\S+", cmd))
            nname = 2 if words and words[0].group() == "str_replace_editor" else 1
            cls[b.start(0):b.end(0)] = "syntax"
            for i, w in enumerate(words):
                cls[b.start(1) + w.start():b.start(1) + w.end()] = "name" if i < nname else "value"
            if words:
                name = words[0].group()
    return cls, name, first_key


def token_classes(tok, rec):
    """Returns (classes per target token, tool/command name string, first argument key string)."""
    prompt, body = target_body(tok, rec)
    enc = tok(prompt + body, return_offsets_mapping=True, add_special_tokens=False)
    offs = enc["offset_mapping"]
    start = bisect.bisect_left([a for a, b in offs], len(prompt))
    cc, name, key = char_classes(rec["src"], body)
    out = []
    for a, b in offs[start:]:
        a, b = a - len(prompt), b - len(prompt)
        seg = list(cc[max(a, 0):max(b, a + 1)])
        out.append(next((c for c in ("name", "value", "key") if c in seg), seg[0] if seg else "syntax"))
    return out, name, key
