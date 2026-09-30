"""Diagnostic: at every decoding step of Venus-Audio, record P(<delegate>) and the chosen token.
Answers whether 'I will search for X...' without a handoff is the model choosing not to delegate
(P(<delegate>) small everywhere) or a near-miss (P(<delegate>) high at some step but not sampled)."""
import argparse
import json

import numpy as np
import torch
from transformers import AutoModel, set_seed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-path", default="/home/xiang/rt_ext/models/Realtime-Venus/Realtime-Venus-Audio")
    ap.add_argument("--queries", default="probes/request_types.json")
    ap.add_argument("--chunks", type=int, default=15)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    model = AutoModel.from_pretrained(a.model_path, trust_remote_code=True, local_files_only=True,
                                      attn_implementation="sdpa", torch_dtype=torch.bfloat16,
                                      init_vision=False, init_audio=True, init_tts=True).eval().cuda()
    duplex = model.as_duplex(generate_audio=False)
    tok = duplex.tokenizer
    did = tok.convert_tokens_to_ids("<delegate>")
    steps = []
    orig = duplex.decoder.decode

    def wrapped(logits=None, **kw):
        p = torch.softmax(logits.float().reshape(-1), -1)
        out = orig(logits=logits, **kw)
        steps.append(dict(p_delegate=float(p[did]), chosen=tok.convert_ids_to_tokens(int(out.item())),
                          top=tok.convert_ids_to_tokens(int(p.argmax()))))
        return out

    duplex.decoder.decode = wrapped
    res = []
    for q in json.load(open(a.queries)):
        for lang in ("en", "zh"):
            set_seed(0)
            steps.clear()
            duplex.prepare(prefix_system_prompt="Streaming Omni Conversation.")
            with torch.inference_mode():
                for k in range(a.chunks):
                    duplex.streaming_prefill(audio_waveform=np.zeros(16000, dtype=np.float32),
                                             text_list=[q[lang]] if k == 1 else None)
                    duplex.streaming_generate(max_new_speak_tokens_per_chunk=20, decode_mode="greedy")
            mx = max(steps, key=lambda s: s["p_delegate"]) if steps else {}
            i = steps.index(mx) if steps else -1
            ctx = "".join(s["chosen"] for s in steps[max(0, i - 12): i])
            res.append(dict(id=q["id"], type=q["type"], lang=lang, max_p_delegate=mx.get("p_delegate"),
                            chosen_at_max=mx.get("chosen"), context_before=ctx,
                            text="".join(s["chosen"] for s in steps)))
            print(f"{q['type']:11s} {q['id']:14s} {lang} maxP={mx.get('p_delegate', 0):.3f} chosen={mx.get('chosen')} "
                  f"ctx=...{ctx[-60:]!r}", flush=True)
    json.dump(res, open(a.out, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
