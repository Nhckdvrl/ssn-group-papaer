"""P1 trace-residency driver: Realtime-Venus-Audio (fast, 9B full-duplex) + local slow backend on FDB-v3.

Simulated, deterministic clock in 1 s model chunks:
  user audio (real human FDB-v3 recording, 16 kHz) is streamed chunk by chunk, followed by silence;
  whenever the fast model closes a <delegate>...</delegate> span, the objective is sent to the slow
  backend (OpenAI-compatible LLM with the FDB-v3 mock tools); its spoken-form result is injected as
  <backend>...</backend> via streaming_prefill (the path used by the released demo adapter) after
  --latency-chunks model chunks. Everything is logged per chunk.

Boundary knobs (one at a time, for later interventions):
  --visibility objective|objective+transcript|transcript   what the slow side is shown
  --latency-chunks N                                        age of the result when admitted
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import librosa
import numpy as np
import torch
from openai import OpenAI
from transformers import AutoModel, set_seed

FDB = Path("/home/xiang/rt_ext/Full-Duplex-Bench/v3")
sys.path.insert(0, str(FDB))
from mock_apis import MockAPIRegistry  # noqa: E402

DELEGATE_RE = re.compile(r"<delegate>(.*?)</delegate>", re.S)

TOOLS = [  # FDB-v3 mock API schemas (from mock_apis.py signatures)
    ("search_flights", {"destination": "string", "date": "string"}, ["destination", "date"]),
    ("book_flight", {"passenger_name": "string", "flight_id": "string"}, ["passenger_name"]),
    ("update_identity_doc", {"doc_type": "string", "doc_number": "string"}, ["doc_type", "doc_number"]),
    ("get_card_benefits", {"card_type": "string"}, ["card_type"]),
    ("get_exchange_rate", {"amount": "number", "from_currency": "string", "to_currency": "string"},
     ["amount", "from_currency", "to_currency"]),
    ("modify_autopay", {"bill_type": "string", "source_account": "string"}, ["bill_type", "source_account"]),
    ("search_apartments", {"city": "string", "bedrooms": "integer", "max_price": "number"},
     ["city", "bedrooms", "max_price"]),
    ("calculate_commute", {"origin_address": "string", "destination_address": "string", "mode": "string"},
     ["origin_address", "destination_address"]),
    ("update_search_filter", {"filter_name": "string", "value": "string"}, ["filter_name", "value"]),
    ("track_order", {"order_id": "string"}, ["order_id"]),
    ("search_products", {"query": "string", "max_price": "number"}, ["query"]),
    ("add_to_cart", {"product_id": "string", "quantity": "integer"}, ["product_id", "quantity"]),
]
OPENAI_TOOLS = [{"type": "function", "function": {"name": n, "description": n.replace("_", " "),
                 "parameters": {"type": "object", "properties": {k: {"type": v} for k, v in p.items()},
                                "required": r}}} for n, p, r in TOOLS]

SLOW_SYSTEM = ("You are the background execution agent of a realtime voice assistant. You receive a task "
               "written by the live conversational frontend{extra}. Use the tools to complete it, then reply "
               "with a short spoken-style result (at most 3 sentences) for the frontend to say to the user.")


def run_slow(client, model, objective, transcript, visibility, max_rounds=6):
    if visibility == "objective":
        user, extra = f"Task: {objective}", ""
    elif visibility == "objective+transcript":
        user = f"Task: {objective}\n\nWhat the user actually said (ASR/reference transcript): {transcript}"
        extra = " together with the user's own words"
    else:  # transcript
        user, extra = f"The user said: {transcript}", ""
    msgs = [{"role": "system", "content": SLOW_SYSTEM.format(extra=extra)}, {"role": "user", "content": user}]
    reg = MockAPIRegistry(latency_profile="instant")
    for _ in range(max_rounds):
        r = client.chat.completions.create(model=model, messages=msgs, tools=OPENAI_TOOLS, temperature=0.0,
                                           extra_body={"chat_template_kwargs": {"enable_thinking": False}})
        m = r.choices[0].message
        if not m.tool_calls:
            return (m.content or "").strip(), reg.logger.calls
        msgs.append({"role": "assistant", "content": m.content or "", "tool_calls": [
            {"id": t.id, "type": "function", "function": {"name": t.function.name, "arguments": t.function.arguments}}
            for t in m.tool_calls]})
        for t in m.tool_calls:
            try:
                args = json.loads(t.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            try:
                res = reg.call(t.function.name, **args)
            except Exception as e:  # bad args
                res = {"status": "error", "message": repr(e)[:200]}
            msgs.append({"role": "tool", "tool_call_id": t.id, "content": json.dumps(res)})
    return "Sorry, I could not finish that.", reg.logger.calls


def run_example(duplex, tok, ex_dir, args, client):
    meta = json.load(open(ex_dir / "metadata.json"))
    transcript = " ".join(t["user"] for t in meta["dialogue"])
    audio, _ = librosa.load(ex_dir / "input.wav", sr=16000, mono=True)
    audio = audio.astype(np.float32)
    n_user = int(np.ceil(len(audio) / 16000))
    total = n_user + args.tail_chunks
    audio = np.pad(audio, (0, total * 16000 - len(audio)))

    duplex.prepare(prefix_system_prompt=args.system_prompt)
    if getattr(duplex, "_force_state", None) is not None:
        duplex._force_state["armed"] = True
    log, pending, raw_prev = [], [], len(duplex.total_ids)
    delegates, slow_runs, spoken_after_backend, injected_at = [], [], "", None
    buf = ""
    for k in range(total):
        chunk = audio[k * 16000:(k + 1) * 16000]
        inject = [p for p in pending if p["at"] == k]
        text_list = [p["text"] for p in inject] or None
        if text_list:
            injected_at = k
        backend_raw = ""
        if text_list and args.inject_mode in ("separate", "resume"):
            # released demo adapter path: text-only <backend> unit written to the live KV; in "resume" mode
            # generation resumes immediately on that unit (as demos/model/adapter.py does) before the next audio
            duplex.streaming_prefill(None, None, text_list, 1, False)
            text_list = None
            if args.inject_mode == "resume":
                r0 = duplex.streaming_generate(max_new_speak_tokens_per_chunk=args.max_tokens, decode_mode=args.decode,
                                               temperature=0.7, top_k=20, top_p=0.8)
                backend_raw = tok.decode(duplex.total_ids[raw_prev:], skip_special_tokens=False)
                raw_prev = len(duplex.total_ids)
                if not r0.get("is_listen"):
                    spoken_after_backend += r0.get("text", "")
        pre = duplex.streaming_prefill(audio_waveform=chunk, text_list=text_list)
        if not pre.get("success"):
            raise RuntimeError(pre)
        res = duplex.streaming_generate(max_new_speak_tokens_per_chunk=args.max_tokens, decode_mode=args.decode,
                                         temperature=0.7, top_k=20, top_p=0.8)
        raw_ids = duplex.total_ids[raw_prev:]
        raw_prev = len(duplex.total_ids)
        raw = tok.decode(raw_ids, skip_special_tokens=False)
        buf += raw
        entry = dict(chunk=k, user_audio=k < n_user, listen=bool(res.get("is_listen")), text=res.get("text", ""),
                     raw=raw, injected=[p["text"] for p in inject], eot=bool(res.get("end_of_turn")),
                     backend_raw=backend_raw)
        # completed delegate spans
        for m in DELEGATE_RE.finditer(buf):
            obj = m.group(1).strip()
            if any(d["objective"] == obj and d["closed_at"] <= k for d in delegates):
                continue
            t0 = time.time()
            result, calls = run_slow(client, args.slow_model, obj, transcript, args.visibility)
            slow_runs.append(dict(objective=obj, result=result, calls=calls, wall_s=time.time() - t0))
            delegates.append(dict(objective=obj, closed_at=k))
            pending.append(dict(at=k + args.latency_chunks, text=f"<backend>{result}</backend>"))
            entry["delegate"] = obj
        buf = DELEGATE_RE.sub("", buf) if "</delegate>" in buf else buf[-2000:]
        if injected_at is not None and k >= injected_at and not entry["listen"]:
            spoken_after_backend += entry["text"]
        log.append(entry)
        if injected_at is not None and k > injected_at + args.max_after and all(p["at"] <= k for p in pending):
            break
    return dict(id=ex_dir.name, meta=meta, transcript=transcript, n_user_chunks=n_user,
                visibility=args.visibility, latency_chunks=args.latency_chunks, delegates=delegates,
                slow_runs=slow_runs, spoken_after_backend=spoken_after_backend,
                actual_tool_calls=[c for r in slow_runs for c in r["calls"]], log=log)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-path", default="/home/xiang/rt_ext/models/Realtime-Venus/Realtime-Venus-Audio")
    ap.add_argument("--examples", nargs="*", default=None)
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--out", required=True)
    ap.add_argument("--visibility", default="objective", choices=["objective", "objective+transcript", "transcript"])
    ap.add_argument("--latency-chunks", type=int, default=2)
    ap.add_argument("--tail-chunks", type=int, default=25)
    ap.add_argument("--max-after", type=int, default=15)
    ap.add_argument("--max-tokens", type=int, default=20)
    ap.add_argument("--decode", default="sampling", choices=["sampling", "greedy"])
    ap.add_argument("--inject-mode", default="separate", choices=["separate", "merged", "resume"])
    ap.add_argument("--force-delegate", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--system-prompt", default="Streaming Omni Conversation.")
    ap.add_argument("--slow-url", default="http://localhost:8100/v1")
    ap.add_argument("--slow-model", default="Qwen/Qwen3-32B")
    args = ap.parse_args()

    set_seed(args.seed)
    model = AutoModel.from_pretrained(args.model_path, trust_remote_code=True, local_files_only=True,
                                      attn_implementation="sdpa", torch_dtype=torch.bfloat16,
                                      init_vision=False, init_audio=True, init_tts=True)
    model.eval().cuda()
    duplex = model.as_duplex(generate_audio=False)
    tok = duplex.tokenizer
    if args.force_delegate:
        # Trigger control: the first time the model would close its first speaking turn with <|turn_eos|>,
        # emit <delegate> instead (the slot the training format uses), then let it write the objective itself.
        did, teos = tok.convert_tokens_to_ids("<delegate>"), tok.convert_tokens_to_ids("<|turn_eos|>")
        orig = duplex.decoder.decode
        state = duplex._force_state = {"armed": True}

        def forced(logits=None, **kw):
            out = orig(logits=logits, **kw)
            if state["armed"] and int(out.item()) == teos:
                state["armed"] = False
                return torch.tensor([did], dtype=out.dtype, device=out.device).reshape(out.shape)
            return out

        duplex.decoder.decode = forced
    client = OpenAI(base_url=args.slow_url, api_key="x")

    exs = sorted((FDB / "fdb_v3_data_released").iterdir())
    exs = [e for e in exs if e.is_dir() and (args.examples is None or e.name in args.examples)][: args.limit]
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    out = []
    for e in exs:
        t0 = time.time()
        with torch.inference_mode():
            r = run_example(duplex, tok, e, args, client)
        r["wall_s"] = time.time() - t0
        out.append(r)
        print(f"{e.name}: delegates={len(r['delegates'])} calls={[c['function'] for c in r['actual_tool_calls']]} "
              f"expected={[c['function'] for c in r['meta']['expected_tool_calls']]} ({r['wall_s']:.0f}s)", flush=True)
        json.dump(out, open(args.out, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
