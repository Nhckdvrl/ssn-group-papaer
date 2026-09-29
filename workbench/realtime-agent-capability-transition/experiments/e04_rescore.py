"""Re-score E04 sims that hit max_steps only because the local user simulator never emitted ###STOP###
(goodbye loop). We keep messages as-is, set termination to USER_STOP, and run the official evaluator.
Both conditions are rescored identically. Writes <run>/rescored.json with per-sim official and rescored reward."""
import json
import sys

from tau2.data_model.simulation import SimulationRun, TerminationReason
from tau2.data_model.tasks import Task
import tau2.evaluator.evaluator_nl_assertions as nl
from tau2.evaluator.evaluator import EvaluationType, evaluate_simulation

# The default NL-assertion judge is gpt-4.1 (no key here): use the local user-sim model for BOTH conditions.
nl.DEFAULT_LLM_NL_ASSERTIONS = "hosted_vllm/Qwen/Qwen3-30B-A3B"
nl.DEFAULT_LLM_NL_ASSERTIONS_ARGS = {"temperature": 0.0, "api_base": "http://localhost:8101/v1", "api_key": "x",
                                     "extra_body": {"chat_template_kwargs": {"enable_thinking": False}}}


def goodbye_loop(sim):
    """True if the tail is a no-tool-call exchange loop (the simulator artifact)."""
    tail = sim.messages[-12:]
    return all(not getattr(m, "tool_calls", None) and m.role in ("user", "assistant") for m in tail)


for run in sys.argv[1:]:
    d = json.load(open(f"{run}/results.json"))
    tasks = {str(t["id"]): Task.model_validate(t) for t in d["tasks"]}
    domain = d["info"]["environment_info"]["domain_name"]
    out = []
    for s in d["simulations"]:
        sim = SimulationRun.model_validate(s)
        official = (s.get("reward_info") or {}).get("reward")
        rescored, loop = official, None
        if sim.termination_reason == TerminationReason.MAX_STEPS:
            loop = goodbye_loop(sim)
        if sim.messages and (loop or sim.termination_reason in (TerminationReason.USER_STOP, TerminationReason.AGENT_STOP,
                                                                  TerminationReason.INFRASTRUCTURE_ERROR)):
            sim.termination_reason = TerminationReason.USER_STOP if loop else sim.termination_reason
            if sim.termination_reason == TerminationReason.INFRASTRUCTURE_ERROR:
                sim.termination_reason = TerminationReason.USER_STOP
            try:
                rescored = evaluate_simulation(sim, tasks[str(sim.task_id)], EvaluationType.ALL, False, domain,
                                               strict_replay=False).reward
            except Exception as e:  # judge/replay failure -> keep as missing
                print("eval error", sim.task_id, repr(e)[:120])
                rescored = None
        elif sim.termination_reason == TerminationReason.MAX_STEPS:
            rescored = 0.0
        out.append(dict(task=str(sim.task_id), term=s["termination_reason"], goodbye_loop=loop,
                        official=official, rescored=rescored))
    json.dump(out, open(f"{run}/rescored.json", "w"), indent=1)
    ok = [o for o in out if o["rescored"] is not None]
    print(run, len(out), "official", round(sum((o["official"] or 0) >= 1 for o in ok) / len(ok), 3),
          "rescored", round(sum(o["rescored"] >= 1 for o in ok) / len(ok), 3),
          "max_steps non-loop", sum(o["goodbye_loop"] is False for o in out))
