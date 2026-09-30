"""Does the streaming context suppress the sparse action token? Same weights, prompt and request; vary only
how the request sits in the stream:
  C1 text      : request in a TEXT unit, whole turn generated inside that unit (no audio embeddings)
  C2 audio1    : request + 1 s silence in one AUDIO unit, whole turn inside that unit
  C3 audio10   : 10 silent AUDIO units first, then C2
  C4 chunked   : released regime - request with silence at unit 1, 20 tokens per 1 s unit, silence continues
For every decoding step we record P(<delegate>); we report P at the end-of-first-turn slot (where the model
emits <|turn_eos|> or <delegate>) and whether greedy decoding delegates."""
import argparse
import json

import numpy as np
import torch
from transformers import AutoModel

SIL = np.zeros(16000, dtype=np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-path", default="/home/xiang/rt_ext/models/Realtime-Venus/Realtime-Venus-Audio")
    ap.add_argument("--queries", default="probes/request_types.json")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    model = AutoModel.from_pretrained(a.model_path, trust_remote_code=True, local_files_only=True,
                                      attn_implementation="sdpa", torch_dtype=torch.bfloat16,
                                      init_vision=False, init_audio=True, init_tts=True).eval().cuda()
    d = model.as_duplex(generate_audio=False)
    tok = d.tokenizer
    did, teos = tok.convert_tokens_to_ids("<delegate>"), tok.convert_tokens_to_ids("<|turn_eos|>")
    steps = []
    orig = d.decoder.decode

    def wrapped(logits=None, **kw):
        p = torch.softmax(logits.float().reshape(-1), -1)
        out = orig(logits=logits, **kw)
        steps.append((float(p[did]), float(p[teos]), int(out.item())))
        return out

    d.decoder.decode = wrapped

    def gen(n):
        d.streaming_generate(max_new_speak_tokens_per_chunk=n, decode_mode="greedy")

    def run(cond, q):
        steps.clear()
        d.prepare(prefix_system_prompt="Streaming Omni Conversation.")
        if cond == "C1_text":
            d.streaming_prefill(None, None, [q], 1, False); gen(200)
        elif cond == "C2_audio1":
            d.streaming_prefill(audio_waveform=SIL, text_list=[q]); gen(200)
        elif cond == "C3_audio10":
            for _ in range(10):
                d.streaming_prefill(audio_waveform=SIL); gen(20)
            steps.clear()
            d.streaming_prefill(audio_waveform=SIL, text_list=[q]); gen(200)
        else:  # C4 chunked
            d.streaming_prefill(audio_waveform=SIL); gen(20)
            steps.clear()
            d.streaming_prefill(audio_waveform=SIL, text_list=[q]); gen(20)
            for _ in range(12):
                d.streaming_prefill(audio_waveform=SIL); gen(20)
        # slot = first step where the model chose <|turn_eos|> or <delegate> after having generated something
        slot = next((s for i, s in enumerate(steps) if s[2] in (teos, did) and i > 0), None)
        text = tok.decode([s[2] for s in steps], skip_special_tokens=False)
        return dict(p_delegate_slot=slot[0] if slot else None, p_teos_slot=slot[1] if slot else None,
                    delegated=did in [s[2] for s in steps], max_p_delegate=max((s[0] for s in steps), default=0),
                    text=text[:400])

    res = []
    for q in json.load(open(a.queries)):
        for lang in ("en", "zh"):
            for cond in ("C1_text", "C2_audio1", "C3_audio10", "C4_chunked"):
                with torch.inference_mode():
                    r = run(cond, q[lang])
                res.append(dict(id=q["id"], type=q["type"], lang=lang, cond=cond, **r))
                print(f"{q['type']:11s} {q['id']:14s} {lang} {cond:11s} Pdel@slot={r['p_delegate_slot']} "
                      f"maxP={r['max_p_delegate']:.3f} deleg={r['delegated']}", flush=True)
        json.dump(res, open(a.out, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
