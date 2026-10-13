#!/usr/bin/env python3
"""E13 author-trained policy, author embeddings, unmodified native AEC world."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--research", type=Path, default=Path("/home/xiang/.cache/game-npc-research/sources/pcsp/research"))
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    sys.path.insert(0, str(args.research))
    import numpy as np
    import torch
    from src.env.mini_inzoi import PersonaConfig
    from src.env.mini_inzoi_v3 import MiniInzoiV3Env
    from src.env.v3_constants import N_ACTIONS_V3, OBS_DIM_V3_BASE, ACTION_NAMES_V3
    from src.training.pcsp_trainer import PCSPActorCritic
    torch.set_num_threads(1)
    args.out.mkdir(parents=True, exist_ok=False)
    policy_file = args.research / "results/pcsp_v3/full/policy.pt"
    embedding_file = args.research / "results/embeddings/persona_embeddings_300.npy"
    persona_file = args.research / "data/personas/test_60_v3.json"
    records = json.loads(persona_file.read_text())[:4]
    configs = [PersonaConfig.from_dict(r) for r in records]
    embeddings = np.load(embedding_file).astype(np.float32)
    e_llm = torch.from_numpy(embeddings[[int(r["id"])-1 for r in records]])
    policy = PCSPActorCritic(OBS_DIM_V3_BASE, N_ACTIONS_V3)
    policy.load_state_dict(torch.load(policy_file, map_location="cpu", weights_only=True), strict=True)
    policy.eval()
    manifest = {"source": str(args.research), "policy": str(policy_file),
        "persona_records": records, "steps": 40, "seeds": [801,802,803],
        "scope": "published v3 in-distribution checkpoint; no held-out policy claim",
        "cloud_calls": 0, "gpu_hours": 0,
        "hashes": {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in [policy_file, embedding_file, persona_file, Path(__file__)]}}
    (args.out/"manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    def state(env):
        return {"positions": env.positions.tolist(), "needs": env.needs.tolist(),
            "last_actions": env.last_actions.tolist(), "repeat_counts": env.repeat_counts.tolist(),
            "novelty_steps": env.novelty_steps.tolist(), "time_of_day": env.time_of_day,
            "step_count": env.step_count}
    start = time.monotonic()
    results, replay_hashes = [], []
    for seed in [801,802,803,801]:
        env = MiniInzoiV3Env(personas=configs, max_steps=40)
        env.reset(seed=seed)
        torch.manual_seed(seed+1_000_003)
        rows, persona_kl = [], []
        for cycle in range(40):
            observations = np.stack([env.observe(a) for a in env.possible_agents])
            with torch.inference_mode():
                obs = torch.from_numpy(observations)
                logits = policy.action_logits(obs, e_llm)
                probabilities = logits.softmax(-1)
                actions = torch.distributions.Categorical(logits=logits).sample().numpy()
                # A diagnostic only: source already studies KL at shared states.
                shifted = policy.action_logits(obs, e_llm.roll(1,0)).softmax(-1)
                kl = (probabilities * (probabilities.log()-shifted.log())).sum(-1).tolist()
                persona_kl.extend(kl)
            for i, (agent, action) in enumerate(zip(env.possible_agents, actions)):
                assert env.agent_selection == agent
                before = state(env)
                env.step(int(action))
                rows.append({"cycle": cycle, "agent": agent, "persona_id": records[i]["id"],
                    "obs": observations[i].tolist(), "action": int(action),
                    "action_name": ACTION_NAMES_V3[int(action)], "probs": probabilities[i].tolist(),
                    "counterfactual_same_state_kl": kl[i], "before": before, "after": state(env),
                    "native_rewards": dict(env.rewards)})
        trace = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",",":"))
        replay_hashes.append(hashlib.sha256(trace.encode()).hexdigest())
        suffix = "_replay" if len(results)==3 else ""
        (args.out/f"rollout_s{seed}{suffix}.json").write_text(trace+"\n")
        results.append({"seed": seed, "replay": bool(suffix), "native_actions": len(rows),
            "state_changed_actions": sum(r["before"]!=r["after"] for r in rows),
            "persona_same_state_kl_mean": float(np.mean(persona_kl)),
            "persona_same_state_kl_range": [float(min(persona_kl)),float(max(persona_kl))],
            "action_counts_by_persona": {str(records[i]["id"]):dict(Counter(
                r["action_name"] for r in rows if r["agent"]==f"agent_{i}")) for i in range(4)},
            "final_state": state(env), "trace_sha256": replay_hashes[-1]})
        env.close()
    assert replay_hashes[0] == replay_hashes[-1]
    summary = {"episodes": results[:3], "exact_seed801_replay": True,
        "wall_seconds": time.monotonic()-start, "manifest": str(args.out/"manifest.json"),
        "scientific_increment": 0, "scope": manifest["scope"], "gpu_hours": 0, "cloud_calls": 0}
    (args.out/"summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
