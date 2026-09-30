"""Text-LLM control for the tool-policy instruction-following probe: same FDB-v3 scenarios (gold human transcripts,
all user turns concatenated), same domain tools, same three policies; first assistant turn only.
Records whether a tool is called and what is said. usage: text_policy_control.py --policy never --out x.json"""
import argparse
import json
import sys
from pathlib import Path

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).parent))
from policy_common import DEFAULT_SYSTEM_MESSAGE, FDB, POLICY, tools_for  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", default="default", choices=list(POLICY))
    ap.add_argument("--ids", default="")
    ap.add_argument("--model", default="Qwen/Qwen3-8B")
    ap.add_argument("--url", default="http://localhost:8104/v1")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    c = OpenAI(base_url=a.url, api_key="x")
    out = []
    for d in sorted(p for p in (FDB / "fdb_v3_data_released").iterdir() if p.is_dir()):
        if a.ids and not any(d.name.startswith(i) for i in a.ids.split(",")):
            continue
        meta = json.load(open(d / "metadata.json"))
        user = " ".join(t["user_annotated"] for t in meta["dialogue"])
        r = c.chat.completions.create(model=a.model, temperature=0.0, max_tokens=300, tools=tools_for(meta["domain"]),
                                      messages=[{"role": "system", "content": DEFAULT_SYSTEM_MESSAGE + POLICY[a.policy]},
                                                {"role": "user", "content": user}],
                                      extra_body={"chat_template_kwargs": {"enable_thinking": False}})
        m = r.choices[0].message
        calls = [dict(function=t.function.name, args=t.function.arguments) for t in (m.tool_calls or [])]
        out.append(dict(id=meta["id"], policy=a.policy, calls=calls, text=m.content or ""))
        print(meta["id"], a.policy, [x["function"] for x in calls], "|", (m.content or "")[:100].replace("\n", " "))
    json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
