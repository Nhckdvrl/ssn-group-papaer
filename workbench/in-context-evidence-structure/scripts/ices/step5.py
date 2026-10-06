"""Minimal concurrent client for StepFun step-5 (max concurrency 8), with jsonl cache.

API key is read from env STEPFUN_API_KEY (never committed).
"""
import asyncio, hashlib, json, os, random, re
from pathlib import Path

import aiohttp

URL = "https://api.stepfun.com/step_plan/v1/chat/completions"  # Step Plan credit account; never the cash /v1 endpoint
MODEL = "step-5-preview"


def _key():
    k = os.environ.get("STEPFUN_API_KEY")
    if not k:
        raise RuntimeError("set STEPFUN_API_KEY")
    return k


def extract_json(text):
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if m:
        text = m.group(1)
    for opener, closer in (("[", "]"), ("{", "}")):
        i, j = text.find(opener), text.rfind(closer)
        if i != -1 and j > i:
            try:
                return json.loads(text[i:j + 1])
            except json.JSONDecodeError:
                continue
    raise ValueError("no json in: " + text[:200])


async def _one(session, sem, messages, max_tokens, retries=14):
    last = None
    async with sem:
        for a in range(retries):
            try:
                async with session.post(URL, json={"model": MODEL, "messages": messages,
                                                   "max_tokens": max_tokens, "temperature": 0},
                                        headers={"Authorization": f"Bearer {_key()}"},
                                        timeout=aiohttp.ClientTimeout(total=900)) as r:
                    if r.status == 429 or r.status >= 500:
                        raise RuntimeError(f"http {r.status}: {(await r.text())[:200]}")
                    d = await r.json(content_type=None)
                    if "choices" not in d:
                        raise RuntimeError(str(d)[:300])
                    return d["choices"][0]["message"]["content"]
            except Exception as e:  # noqa: BLE001
                await asyncio.sleep(min(90, 3 * 2 ** a) * (0.5 + random.random()))
                last = e
        raise last


async def run_all(prompts, cache_path, max_tokens=8000, concurrency=4, system=None):
    """prompts: list of (id, user_text). Returns dict id -> content. Cached by id+hash."""
    cache_path = Path(cache_path)
    done = {}
    if cache_path.exists():
        for line in cache_path.open():
            r = json.loads(line); done[r["key"]] = r["content"]
    sem = asyncio.Semaphore(concurrency)
    out = {}
    async with aiohttp.ClientSession() as session:
        async def task(pid, text):
            key = pid + ":" + hashlib.sha1(((system or "") + text).encode()).hexdigest()[:12]
            if key in done:
                out[pid] = done[key]; return
            msgs = ([{"role": "system", "content": system}] if system else []) + \
                   [{"role": "user", "content": text}]
            c = await _one(session, sem, msgs, max_tokens)
            out[pid] = c
            with cache_path.open("a") as f:
                f.write(json.dumps({"key": key, "id": pid, "content": c}) + "\n")
        rs = await asyncio.gather(*(task(p, t) for p, t in prompts), return_exceptions=True)
    errs = [r for r in rs if isinstance(r, Exception)]
    if errs:
        print(f"[step5] {len(errs)} failed calls (rerun to retry; cache keeps successes):", errs[:3])
    return out
