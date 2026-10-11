"""CT08 E00 runner (docs/E00_PROTOCOL.md).

usage: e00_run.py ARM OUT.jsonl ROOT_URL ROOT_NAME SUB_URLS(comma) SUB_NAME [NWORKERS]
  ARM in {A, B} runs the RLM harness (vendor/rlm_v01) with the given root model;
  ARM C runs flat full-context chat against ROOT_URL (SUB args ignored).
"""
import json, multiprocessing as mp, os, sys, time, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "vendor", "rlm_v01"))
ARM, OUT, ROOT_URL, ROOT_NAME, SUB_URLS, SUB_NAME = sys.argv[1:7]
NW = int(sys.argv[7]) if len(sys.argv) > 7 else 32
SUB_URLS = SUB_URLS.split(",")
ROOT_URLS = ROOT_URL.split(",")  # same model behind every URL; load-balanced by iid
DECODE = dict(temperature=0.7, top_p=0.8, max_tokens=4096,
              extra_body={"chat_template_kwargs": {"enable_thinking": False}})
SYSTEM = open(os.path.join(HERE, "prompt_qwen3_8b.txt")).read()


def patch_client():
    from rlm.clients import openai as oc

    def completion(self, prompt, model=None):
        messages = [{"role": "user", "content": prompt}] if isinstance(prompt, str) else prompt
        r = self.client.chat.completions.create(model=model or self.model_name, messages=messages, **DECODE)
        self._track_cost(r, model or self.model_name)
        return r.choices[0].message.content

    async def acompletion(self, prompt, model=None):
        messages = [{"role": "user", "content": prompt}] if isinstance(prompt, str) else prompt
        r = await self.async_client.chat.completions.create(model=model or self.model_name, messages=messages,
                                                            **DECODE)
        self._track_cost(r, model or self.model_name)
        return r.choices[0].message.content
    oc.OpenAIClient.completion = completion
    oc.OpenAIClient.acompletion = acompletion


class Collector:
    def __init__(self):
        self.its = []

    def log_metadata(self, m):
        pass

    def log(self, it):
        from rlm.utils.parsing import format_execution_result
        self.its.append({"response": it.response,
                         "blocks": [{"code": b.code, "shown": format_execution_result(b.result)[:20000],
                                     "n_llm_calls": len(getattr(b.result, "rlm_calls", None) or
                                                        getattr(b.result, "llm_calls", None) or [])}
                                    for b in it.code_blocks],
                         "final": it.final_answer})


def run_one(inst):
    t0 = time.time()
    rec = {"iid": inst["iid"], "arm": ARM}
    try:
        if ARM == "C":
            import openai
            cl = openai.OpenAI(api_key="x", base_url=ROOT_URLS[0])
            msg = f"{inst['context']}\n\n{inst['question']}"
            r = cl.chat.completions.create(model=ROOT_NAME, messages=[{"role": "user", "content": msg}], **DECODE)
            rec["final"] = r.choices[0].message.content
        else:
            patch_client()
            from rlm import RLM
            sub = SUB_URLS[inst["iid"] % len(SUB_URLS)]
            col = Collector()
            rlm = RLM(backend="vllm", backend_kwargs={"base_url": ROOT_URLS[inst["iid"] % len(ROOT_URLS)], "model_name": ROOT_NAME, "api_key": "x"},
                      other_backends=["vllm"],
                      other_backend_kwargs=[{"base_url": sub, "model_name": SUB_NAME, "api_key": "x"}],
                      environment="local", max_depth=1, max_iterations=20, custom_system_prompt=SYSTEM,
                      logger=col, verbose=False)
            res = rlm.completion(inst["context"], root_prompt=inst["question"])
            rec["final"] = res.response
            rec["iters"] = col.its
            try:
                rec["usage"] = res.usage_summary.to_dict()
            except Exception:
                pass
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {str(e)[:300]}"
        rec["tb"] = traceback.format_exc()[-800:]
        rec.setdefault("final", "")
    rec["sec"] = time.time() - t0
    return rec


if __name__ == "__main__":
    insts = [json.loads(l) for l in open(os.path.join(HERE, "..", "data", "e00_instances.jsonl"))]
    if os.environ.get("LIMIT"):
        insts = insts[::max(1, len(insts) // int(os.environ["LIMIT"]))][:int(os.environ["LIMIT"])]
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(l)["iid"] for l in open(OUT)}
    todo = [i for i in insts if i["iid"] not in done]
    print(f"arm {ARM}: {len(todo)} to run", flush=True)
    with mp.get_context("spawn").Pool(NW, maxtasksperchild=4) as pool, open(OUT, "a") as fo:
        for k, rec in enumerate(pool.imap_unordered(run_one, todo)):
            fo.write(json.dumps(rec) + "\n"); fo.flush()
            if k % 10 == 0:
                print(k, rec["iid"], rec.get("error", "")[:80], f"{rec['sec']:.0f}s", flush=True)
