"""Probe: does Venus-Audio delegate when the FDB-v3 request arrives as injected TEXT (no speech perception),
in English vs Chinese? Silence audio is streamed; the request is injected via text_list at chunk 1
(the same channel the model uses for injected questions / <backend>). Counts <delegate> spans and logs
what the model says instead. Sampling as in the released defaults; n seeds per request."""
import argparse
import json
import re
from pathlib import Path

import numpy as np
import torch
from openai import OpenAI
from transformers import AutoModel, set_seed

FDB = Path("/home/xiang/rt_ext/Full-Duplex-Bench/v3/fdb_v3_data_released")
DEL = re.compile(r"<delegate>(.*?)</delegate>", re.S)


def translate(client, text):
    r = client.chat.completions.create(model="Qwen/Qwen3-32B", temperature=0.0, messages=[
        {"role": "user", "content": "Translate this spoken customer request into natural spoken Chinese, keeping all "
                                    "names, numbers and IDs. Output only the translation.\n\n" + text}],
        extra_body={"chat_template_kwargs": {"enable_thinking": False}})
    return r.choices[0].message.content.strip()


def probe(duplex, tok, text, chunks, prompt):
    duplex.prepare(prefix_system_prompt=prompt)
    prev, raw = len(duplex.total_ids), ""
    for k in range(chunks):
        duplex.streaming_prefill(audio_waveform=np.zeros(16000, dtype=np.float32),
                                 text_list=[text] if k == 1 else None)
        duplex.streaming_generate(max_new_speak_tokens_per_chunk=20, decode_mode="sampling",
                                  temperature=0.7, top_k=20, top_p=0.8)
        raw += tok.decode(duplex.total_ids[prev:], skip_special_tokens=False)
        prev = len(duplex.total_ids)
    spoken = re.sub(r"<\|[a-z_]+\|>|</?unit>", "", DEL.sub("", raw)).strip()
    return dict(delegates=DEL.findall(raw), spoken=spoken[:400])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-path", default="/home/xiang/rt_ext/models/Realtime-Venus/Realtime-Venus-Audio")
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--chunks", type=int, default=15)
    ap.add_argument("--prompt", default="Streaming Omni Conversation.")
    ap.add_argument("--out", required=True)
    ap.add_argument("--queries", default=None, help="JSON list with id/type/en/zh; overrides FDB requests")
    a = ap.parse_args()
    client = OpenAI(base_url="http://localhost:8100/v1", api_key="x")
    model = AutoModel.from_pretrained(a.model_path, trust_remote_code=True, local_files_only=True,
                                      attn_implementation="sdpa", torch_dtype=torch.bfloat16,
                                      init_vision=False, init_audio=True, init_tts=True).eval().cuda()
    duplex = model.as_duplex(generate_audio=False)
    tok = duplex.tokenizer
    seen, reqs = set(), []
    for e in sorted(x for x in FDB.iterdir() if x.is_dir()):
        m = json.load(open(e / "metadata.json"))
        if m["id"] in seen:
            continue
        seen.add(m["id"])
        reqs.append((m["id"], " ".join(t["user"] for t in m["dialogue"])))
    reqs = [(r, en, None, "fdb") for r, en in reqs[:: max(1, len(reqs) // a.n)][: a.n]]
    if a.queries:
        reqs = [(q["id"], q["en"], q["zh"], q["type"]) for q in json.load(open(a.queries))]
    out = []
    for rid, en, zh, rtype in reqs:
        zh = zh or translate(client, en)
        for lang, text in (("en", en), ("zh", zh)):
            for s in range(a.seeds):
                set_seed(s)
                with torch.inference_mode():
                    r = probe(duplex, tok, text, a.chunks, a.prompt)
                out.append(dict(id=rid, type=rtype, lang=lang, seed=s, text=text, **r))
                print(rid, lang, s, "DELEGATE" if r["delegates"] else "-", (r["delegates"] or [r["spoken"]])[0][:100],
                      flush=True)
        json.dump(out, open(a.out, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
