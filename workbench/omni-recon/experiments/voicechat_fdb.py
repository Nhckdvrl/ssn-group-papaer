"""A1 instrument: NemotronLabs VoiceChat (native parallel function-call head) on FDB-v3 real-human recordings.

Offline, iterative multi-pass version of NeMo's two-pass FC inference: pass k runs the whole recording with the
k-1 calls/responses found so far injected at their frame positions, looks for the first NEW call after the last
injected response, executes it on FDB-v3's mock API, injects, and repeats (max 5 calls). Per scenario we keep:
  - every native call (name, args, frame step) and the mock response
  - the agent-text channel (what the model says) and its per-frame token ids, so speech/action can be aligned
Tools exposed = the 3 tools of the scenario's domain (VoiceChat recommends <= 5). Scoring reuses FDB-v3's strict
pass logic via ../../realtime-computation-boundaries/experiments/score_fdb.py-compatible records.
usage: PYTHONPATH=<nemo clone> voicechat_fdb.py --out runs.json [--ids a,b] [--system-message ...]"""
import argparse
import json
import sys
from pathlib import Path

import torch

FDB = Path("/home/xiang/rt_ext/Full-Duplex-Bench/v3")
sys.path.insert(0, str(FDB))
sys.path.insert(0, "/home/xiang/rt_ext/nemo-speech-voicechat/examples/speechlm2")
from mock_apis import MockAPIRegistry  # noqa: E402
from nemo.collections.speechlm2.inference.utils.offline_voicechat import (  # noqa: E402
    build_model, encode_system_prompt, render_fc_system_prompt, run_offline_inference)
from offline_voicechat_fc_infer import DEFAULT_TEMPLATE  # noqa: E402
from policy_common import DEFAULT_SYSTEM_MESSAGE, POLICY, SCHEMA, tools_for  # noqa: E402

def load_wav_16k_mono(path, device="cuda"):  # soundfile+librosa: torchaudio.load needs torchcodec here
    import librosa
    y, _ = librosa.load(path, sr=16000, mono=True)
    w = torch.from_numpy(y)
    return w, w.unsqueeze(0).to(device), torch.tensor([w.shape[0]], device=device)


def parse_call(call_text):
    clean = call_text.replace("<SPECIAL_20>", "").replace("<SPECIAL_21>", "").strip()
    if "<TOOLCALL>" in clean:
        clean = clean.split("<TOOLCALL>")[1].split("</TOOLCALL>")[0].strip()
    try:
        calls = json.loads(clean) if clean.startswith("[") else [json.loads(clean)]
        out = []
        for tc in calls:
            args = tc.get("arguments", {})
            if isinstance(args, str):
                args = json.loads(args) if args.strip().startswith("{") else {}
            out.append({"name": tc.get("name", ""), "arguments": args})
        return clean, out, None
    except Exception as e:  # malformed serialization is itself a category of interest
        return clean, [], repr(e)


def pad3(seqs, dev):
    L = max(len(s) for s in seqs)
    t = torch.zeros(1, len(seqs), L, dtype=torch.long, device=dev)
    for i, s in enumerate(seqs):
        t[0, i, :len(s)] = torch.tensor(s, dtype=torch.long)
    return t, torch.tensor([[len(s) for s in seqs]], dtype=torch.long, device=dev)


def run_scenario(model, ex_dir, system_message, dev, max_calls=5):
    meta = json.load(open(ex_dir / "metadata.json"))
    tok = model.stt_model.tokenizer
    sp = render_fc_system_prompt(str(DEFAULT_TEMPLATE), system_message, tools_for(meta["domain"]))
    pt, ptl = encode_system_prompt(model, sp, device=dev)
    _, sig, sig_len = load_wav_16k_mono(str(ex_dir / "input.wav"), device=dev)
    api = MockAPIRegistry(latency_profile="instant", enable_logging=False)
    calls, call_ids, call_steps, resp_ids, resp_steps, passes = [], [], [], [], [], []
    for _ in range(max(max_calls, 0) + 1):
        kw = {}
        if call_ids:
            fc, fcl = pad3(call_ids, dev)
            fr, frl = pad3(resp_ids, dev)
            kw = dict(function_calls=fc, function_call_lengths=fcl,
                      function_call_steps=torch.tensor([call_steps], device=dev),
                      function_responses=fr, function_response_lengths=frl,
                      function_response_steps=torch.tensor([resp_steps], device=dev))
        res = run_offline_inference(model, input_signal=sig, input_signal_lens=sig_len, prompt_tokens=pt,
                                    prompt_token_lens=ptl, decode_audio=False, **kw)
        ft = res.get("tokens_function_pred", res.get("tokens_function"))
        pos = model.stt_model._extract_function_call_positions(ft, res["tokens_len"], res["tokens_text"])[0] \
            if ft is not None else {"function_calls": []}
        after = resp_steps[-1] if resp_steps else -1
        new = [c for c in pos["function_calls"] if c["start_pos"] > after]
        passes.append(dict(text=res["text"][0], n_calls_seen=len(pos["function_calls"])))
        if not new or max_calls == 0:
            if new and max_calls == 0:
                calls.append(dict(step=new[0]["start_pos"], end=new[0]["end_pos"], raw=new[0]["call_text"],
                                  parsed=parse_call(new[0]["call_text"])[1], parse_error=None, responses=[]))
            break
        c = new[0]
        clean, parsed, err = parse_call(c["call_text"])
        responses = [api.call(p["name"], **p["arguments"]) if p["name"] in SCHEMA else {"error": "unknown tool"}
                     for p in parsed] or [{"error": "unparseable tool call"}]
        calls.append(dict(step=c["start_pos"], end=c["end_pos"], raw=c["call_text"], parsed=parsed, parse_error=err,
                          responses=responses))
        call_ids.append(tok.text_to_ids(clean))
        call_steps.append(c["start_pos"])
        resp_ids.append(tok.text_to_ids("<TOOL_RESPONSE>" + json.dumps(responses) + "</TOOL_RESPONSE>"))
        resp_steps.append(c["end_pos"] + 1)
    actual = [dict(function=p["name"], args=p["arguments"]) for c in calls for p in c["parsed"]]
    return dict(id=meta["id"], meta=meta, calls=calls, actual_tool_calls=actual, passes=passes,
                final_text=passes[-1]["text"], text_tokens=res["tokens_text"][0, :res["tokens_len"][0]].tolist(),
                delegates=calls, spoken_after_backend="")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="/home/xiang/rt_ext/models/VoiceChat-11B")
    ap.add_argument("--out", required=True)
    ap.add_argument("--ids", default="")
    ap.add_argument("--system-message", default=DEFAULT_SYSTEM_MESSAGE)
    ap.add_argument("--policy", default="default", choices=list(POLICY), help="tool-use policy appended to the prompt")
    ap.add_argument("--bf16", action="store_true")
    ap.add_argument("--max-calls", type=int, default=5, help="0 = single pass: only detect whether/what it calls")
    a = ap.parse_args()
    dev = "cuda"
    model = build_model(a.ckpt, device=dev)
    dirs = sorted(p for p in (FDB / "fdb_v3_data_released").iterdir() if p.is_dir())
    if a.ids:
        dirs = [d for d in dirs if any(d.name.startswith(i) for i in a.ids.split(","))]
    out = []
    for d in dirs:
        with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16, enabled=a.bf16):
            r = run_scenario(model, d, a.system_message + POLICY[a.policy], dev, max_calls=a.max_calls)
        r["policy"] = a.policy
        out.append(r)
        exp = [(c["function"], c["args"]) for c in r["meta"]["expected_tool_calls"]]
        print(r["id"], "| expected", exp, "| native", [(c["function"], c["args"]) for c in r["actual_tool_calls"]],
              "| says:", r["final_text"][:120].replace("\n", " "), flush=True)
        json.dump(out, open(a.out, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
