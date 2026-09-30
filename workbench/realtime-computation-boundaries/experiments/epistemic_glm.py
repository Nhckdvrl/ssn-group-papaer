"""Epistemic-boundary probe, GLM lineage (independent of Qwen/MiniCPM):
  glm4voice : GLM-4-Voice-9B, turn-based speech LM (speech-in, interleaved text+audio out; text tokens kept)
  bayling   : BayLing-Duplex, native in-stream full-duplex model fine-tuned from GLM-4-Voice (text channel kept)
Spoken questions (edge-tts, 2 voices/lang); same judge as epistemic_eval.py. Text parent (glm-4-9b-chat-hf) is
run separately via the OpenAI-compatible path of epistemic_eval.py."""
import argparse
import json
import os
import sys

import soundfile as sf
import torch
from openai import OpenAI

from epistemic_eval import judge

AUD = os.environ.get("AUD", "/home/xiang/rt_ext/runs/epi_audio")
M = "/home/xiang/rt_ext/models"


def glm4voice_backend():
    sys.path.insert(0, "/home/xiang/rt_ext/GLM-4-Voice")
    sys.path.insert(0, "/home/xiang/rt_ext/GLM-4-Voice/third_party/Matcha-TTS")
    from speech_tokenizer.modeling_whisper import WhisperVQEncoder
    from speech_tokenizer.utils import extract_speech_token
    from transformers import AutoModel, AutoTokenizer, WhisperFeatureExtractor
    tok = AutoTokenizer.from_pretrained(f"{M}/glm-4-voice-9b", trust_remote_code=True)
    model = AutoModel.from_pretrained(f"{M}/glm-4-voice-9b", trust_remote_code=True, torch_dtype=torch.bfloat16,
                                      device_map={"": 0}).eval()
    sys.path.insert(0, "/home/xiang/rt_ext/BayLing-Duplex")
    from bayling_duplex.duplex import _patch_model_for_new_transformers  # same ChatGLM code; transformers>=4.45 compat
    _patch_model_for_new_transformers(model)
    wm = WhisperVQEncoder.from_pretrained(f"{M}/glm-4-voice-tokenizer").eval().cuda()
    fe = WhisperFeatureExtractor.from_pretrained(f"{M}/glm-4-voice-tokenizer")
    audio_offset = tok.convert_tokens_to_ids("<|audio_0|>")
    end_id = tok.convert_tokens_to_ids("<|user|>")
    sysmsg = ("User will provide you with a speech instruction. Do it step by step. First, think about the instruction "
              "and respond in a interleaved manner, with 13 text token followed by 26 audio tokens. ")

    def gen(wav, seed):
        y, sr = sf.read(wav, dtype="float32")  # tuple input avoids torchaudio.load (needs torchcodec)
        toks = extract_speech_token(wm, fe, [(torch.from_numpy(y).unsqueeze(0), sr)])[0]
        user = "<|begin_of_audio|>" + "".join(f"<|audio_{x}|>" for x in toks) + "<|end_of_audio|>"
        prompt = f"<|system|>\n{sysmsg}<|user|>\n{user}<|assistant|>streaming_transcription\n"
        ids = tok([prompt], return_tensors="pt").to("cuda")
        torch.manual_seed(seed)
        with torch.inference_mode():
            out = model.generate(**ids, max_new_tokens=600, do_sample=True, temperature=0.2, top_p=0.8,
                                 eos_token_id=end_id)
        new = out[0, ids["input_ids"].shape[1]:].tolist()
        text_ids = [t for t in new if t < audio_offset and t != end_id]
        return tok.decode(text_ids, skip_special_tokens=True)
    return gen


def bayling_backend():
    sys.path.insert(0, "/home/xiang/rt_ext/BayLing-Duplex")
    from bayling_duplex import BayLingDuplex
    m = BayLingDuplex(model_path=f"{M}/BayLing-Duplex", speech_tokenizer_path=f"{M}/glm-4-voice-tokenizer",
                      decoder_path=None, interleave_ratio="10:5:10", device="cuda")

    def gen(wav, seed):
        torch.manual_seed(seed)
        r = m.generate(wav, max_duration=30.0, temperature=0.8, top_p=0.8)
        return r.text or ""
    return gen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=["glm4voice", "bayling"], required=True)
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--queries", default="probes/epistemic.json")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    gen = glm4voice_backend() if a.model == "glm4voice" else bayling_backend()
    jc = OpenAI(base_url="http://localhost:8100/v1", api_key="x")
    res = []
    for q in json.load(open(a.queries)):
        for lang in os.environ.get("LANGS", "en,zh").split(","):
            for s in range(a.seeds):
                ans = gen(f"{AUD}/{q['id']}_{lang}_{s % 2}.wav", s)
                lab = judge(jc, q["cat"], q[lang], ans)
                res.append(dict(id=q["id"], cat=q["cat"], lang=lang, seed=s, reply=ans[:600], label=lab))
                print(q["cat"], q["id"], lang, s, lab, "|", ans[:90].replace("\n", " "), flush=True)
        json.dump(res, open(a.out, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
