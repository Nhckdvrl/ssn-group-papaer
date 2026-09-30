"""Summarize epistemic-boundary runs: abstention rate per category (ECHO/OTHER excluded from the denominator)."""
import json, os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "epistemic")
ROWS = [  # (file, family, architecture, input, mode)
    ("epi_qwen2_7b", "Qwen2", "text LLM (parent)", "text", "chat"),
    ("epiA_freezeomni", "Qwen2", "full-duplex, LLM frozen, external state predictor (L1)", "speech", "full-duplex"),
    ("epi_qwen25_7b", "Qwen2.5", "text LLM (parent)", "text", "chat"),
    ("epiA_qwen25omni", "Qwen2.5", "speech Thinker-Talker, turn-based", "speech", "turn-based"),
    ("epi_qwen3_8b", "Qwen3", "text LLM (parent)", "text", "chat"),
    ("epiA_minicpmo45_offline", "Qwen3", "MiniCPM-o 4.5 omni", "speech", "turn-based"),
    ("epiA_minicpmo45_duplex", "Qwen3", "MiniCPM-o 4.5 omni, same weights", "speech", "full-duplex in-stream"),
    ("epiA_venus_audio_offline", "Qwen3", "Realtime-Venus-Audio (FD+delegation post-training)", "speech", "turn-based"),
    ("epiA_venus_audio_duplex", "Qwen3", "Realtime-Venus-Audio", "speech", "full-duplex in-stream"),
    ("epi_venus_omni_duplex", "Qwen3", "Realtime-Venus-Omni", "text", "full-duplex in-stream"),
]
out = []
print(f"{'model/mode':62s} {'live':>12s} {'private':>12s} {'known ans':>10s}")
for f, fam, arch, inp, mode in ROWS:
    d = json.load(open(f"{R}/{f}.json"))
    def rate(cat, lab):
        xs = [x for x in d if x["cat"] == cat and x["label"] not in ("ECHO", "OTHER")]
        return sum(x["label"] == lab for x in xs), len(xs)
    lv, pv, kn = rate("live", "ABSTAIN"), rate("private", "ABSTAIN"), rate("known", "ANSWER")
    fl = rate("live", "FABRICATE")
    out.append(dict(file=f, family=fam, arch=arch, input=inp, mode=mode, live_abstain=lv, private_abstain=pv,
                    live_fabricate=fl, known_answered=kn))
    print(f"{fam+' | '+arch[:38]+' | '+mode:62s} {lv[0]:3d}/{lv[1]:<3d}{lv[0]/lv[1]:4.0%} {pv[0]:3d}/{pv[1]:<3d}{pv[0]/pv[1]:4.0%} {kn[0]:3d}/{kn[1]}")
json.dump(out, open(f"{R}/summary.json", "w"), indent=1)
