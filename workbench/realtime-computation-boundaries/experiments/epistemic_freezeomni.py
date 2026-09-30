"""Epistemic-boundary probe for Freeze-Omni (full-duplex speech model whose Qwen2-7B-Instruct LLM is FROZEN):
spoken questions in, text out (TTS decoder skipped). Control lineage: parent = Qwen2-7B-Instruct (text)."""
import argparse
import json
import os
import math
import sys

import soundfile as sf
import torch
import torchaudio
from openai import OpenAI

FO = "/home/xiang/rt_ext/Freeze-Omni"
sys.path.insert(0, FO)
sys.path.insert(0, FO + "/bin")
import torchaudio.compliance.kaldi as k  # noqa: E402


class audioEncoderProcessor:
    """Copied from Freeze-Omni bin/inference.py (importing that file pulls in the flask web demo)."""

    def __init__(self, chunk_size=16):
        self.chunk_size, self.chunk_overlap, self.feat_dim = 16, 3, 80
        self.frame_size, self.frame_shift = 400, 160
        self.frame_overlap = self.frame_size - self.frame_shift
        self.CHUNK = self.frame_shift * self.chunk_size
        self.reset()

    def get_chunk_size(self):
        return self.CHUNK

    def reset(self):
        self.input_chunk = torch.zeros([1, self.chunk_size + self.chunk_overlap, self.feat_dim])
        self.input_sample = torch.zeros([1, self.CHUNK + self.frame_overlap, 1])

    def process(self, audio):
        with torch.no_grad():
            sample = torch.tensor(audio).reshape(1, -1, 1)[:, :, :1] * 32768
            self.input_sample[:, :self.frame_overlap, :] = self.input_sample[:, -self.frame_overlap:, :].clone()
            self.input_sample[:, self.frame_overlap:, :] = sample
            xs = k.fbank(waveform=self.input_sample.squeeze(-1), dither=0, frame_length=25, frame_shift=10,
                         num_mel_bins=self.feat_dim)
            self.input_chunk[:, :self.chunk_overlap, :] = self.input_chunk[:, -self.chunk_overlap:, :].clone()
            self.input_chunk[:, self.chunk_overlap:, :] = xs.squeeze(0)
        return self.input_chunk.clone()
from models.pipeline import inferencePipeline  # noqa: E402

from epistemic_eval import judge  # noqa: E402

AUD = os.environ.get("AUD", "/home/xiang/rt_ext/runs/epi_audio")


def answer(pipeline, proc, wav_path):
    wav, fs = sf.read(wav_path)
    wav = torch.tensor(wav)
    if fs != 16000:
        wav = torchaudio.transforms.Resample(orig_freq=fs, new_freq=16000)(wav.float())
    outputs = pipeline.speech_dialogue(None, stat="pre", role="You are a helpful assistant.")
    cs = proc.get_chunk_size()
    x = torch.zeros(math.ceil(wav.shape[0] / cs) * cs)
    x[: wav.shape[0]] = wav
    for i in range(0, x.shape[0], cs):
        outputs = pipeline.speech_dialogue(proc.process(x[i:i + cs]), **outputs)
        outputs["stat"] = "cl"
    proc.reset()
    outputs.update(adapter_cache=None, encoder_cache=None, pe_index=0, stat="ss")
    outputs = pipeline.speech_dialogue(None, **outputs)
    text = ""
    while len(outputs["past_tokens"]) <= 128:
        del outputs["text"]
        del outputs["hidden_state"]
        outputs = pipeline.speech_dialogue(None, **outputs)
        if outputs["stat"] == "cs":
            text = outputs["text"]
        if outputs["stat"] == "sl":
            break
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--queries", default="probes/epistemic.json")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cfg = argparse.Namespace(model_path=FO + "/checkpoints", llm_path=FO + "/Qwen2-7B-Instruct", top_k=20, top_p=0.8,
                             temperature=0.8)
    pipeline = inferencePipeline(cfg)
    proc = audioEncoderProcessor()
    jc = OpenAI(base_url="http://localhost:8100/v1", api_key="x")
    res = []
    for q in json.load(open(a.queries)):
        for lang in os.environ.get("LANGS", "en,zh").split(","):
            for s in range(a.seeds):
                torch.manual_seed(s)
                with torch.inference_mode():
                    ans = answer(pipeline, proc, f"{AUD}/{q['id']}_{lang}_{s % 2}.wav")
                lab = judge(jc, q["cat"], q[lang], ans)
                res.append(dict(id=q["id"], cat=q["cat"], lang=lang, seed=s, reply=ans[:600], label=lab))
                print(q["cat"], q["id"], lang, s, lab, "|", ans[:90].replace("\n", " "), flush=True)
        json.dump(res, open(a.out, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
