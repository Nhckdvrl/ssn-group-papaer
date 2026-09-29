"""E04 analysis: text-style vs voice-style user (perfect transcripts), same agent/user LLMs, paired by task."""
import json
import os
import re

RUNS = "/home/xiang/rt_ext/runs"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "e04_style.json")
AUTH = {"find_user_id_by_email", "find_user_id_by_name_zip", "get_user_details"}


def load(dom, style):
    d = json.load(open(f"{RUNS}/e04_{dom}_{style}/results.json"))
    out = {}
    for s in d["simulations"]:
        msgs = s.get("messages") or []
        calls, errs = [], 0
        for m in msgs:
            for c in m.get("tool_calls") or []:
                calls.append(c["name"])
            if m.get("role") == "tool" and m.get("error"):
                errs += 1
        users = [m for m in msgs if m.get("role") == "user"]
        out[str(s["task_id"])] = dict(
            reward=(s.get("reward_info") or {}).get("reward"),
            term=s.get("termination_reason"),
            n_user=len(users),
            user_words=sum(len((m.get("content") or "").split()) for m in users),
            n_calls=len(calls), tool_errs=errs,
            auth_fail_calls=None,
        )
    return out


if __name__ == "__main__":
    res = {}
    for dom in ["retail", "airline"]:
        try:
            t, v = load(dom, "text"), load(dom, "voice")
        except FileNotFoundError:
            continue
        common = [k for k in t if k in v and t[k]["reward"] is not None and v[k]["reward"] is not None]
        pt = sum(t[k]["reward"] >= 1 for k in common) / len(common)
        pv = sum(v[k]["reward"] >= 1 for k in common) / len(common)
        tw = sum(t[k]["reward"] >= 1 and v[k]["reward"] < 1 for k in common)
        vw = sum(v[k]["reward"] >= 1 and t[k]["reward"] < 1 for k in common)
        mean = lambda d, key: sum(d[k][key] for k in common) / len(common)
        res[dom] = dict(n=len(common), pass_text=pt, pass_voice=pv, text_only_wins=tw, voice_only_wins=vw,
                        user_turns=(mean(t, "n_user"), mean(v, "n_user")),
                        user_words=(mean(t, "user_words"), mean(v, "user_words")),
                        tool_errs=(mean(t, "tool_errs"), mean(v, "tool_errs")),
                        terms=({k: sum(t[x]["term"] == k for x in common) for k in {t[x]["term"] for x in common}},
                               {k: sum(v[x]["term"] == k for x in common) for k in {v[x]["term"] for x in common}}),
                        text_only_win_tasks=[k for k in common if t[k]["reward"] >= 1 and v[k]["reward"] < 1])
        r = res[dom]
        print(f"{dom}: n={r['n']} text={pt:.2f} voice={pv:.2f} delta={pv-pt:+.2f} discordant text>voice={tw} voice>text={vw} "
              f"user_turns={r['user_turns'][0]:.1f}->{r['user_turns'][1]:.1f} tool_errs={r['tool_errs'][0]:.2f}->{r['tool_errs'][1]:.2f}")
    json.dump(res, open(OUT, "w"), indent=1)
