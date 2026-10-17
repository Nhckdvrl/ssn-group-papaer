#!/usr/bin/env python3
"""CPU-only audit of two pinned public source files; NOT a model benchmark.

Read-only inputs must be original upstream files. The Git blob digests fail
closed on version drift. Only NCP's pure survival_curve function is executed,
without importing its package; annotations are postponed. CPDC is parsed only.
Synthetic records test a metric contract, not NPC behavior. No third-party
source, checkpoints, user data, API calls, or packages are downloaded.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import platform
from datetime import date
from pathlib import Path
from types import SimpleNamespace

PINS = {
    "metrics": "4ba08045919c9860a35d7b14c6f1244bea71c43f",
    "actions": "a5eaf793635d1d7303d09997ea68540d12253aff",
}

def read_pinned(path: Path, expected: str) -> tuple[str, str]:
    raw = path.read_bytes()
    digest = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if digest != expected:
        raise ValueError(f"Source version mismatch for {path}: {digest} != {expected}")
    return raw.decode("utf-8"), digest

def raises_value_error(function, *args, **kwargs) -> bool:
    try:
        function(*args, **kwargs)
    except ValueError:
        return True
    return False

def audit(metrics_path: Path, actions_path: Path) -> dict:
    metrics, msha = read_pinned(metrics_path, PINS["metrics"])
    actions, asha = read_pinned(actions_path, PINS["actions"])
    nodes = [n for n in ast.parse(metrics).body
             if isinstance(n, ast.FunctionDef) and n.name == "survival_curve"]
    if len(nodes) != 1:
        raise ValueError("Expected one survival_curve function")
    # Execute the unchanged original function body, without package side effects.
    future = ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)
    module = ast.fix_missing_locations(ast.Module(body=[future, nodes[0]], type_ignores=[]))
    namespace: dict = {}
    exec(compile(module, str(metrics_path), "exec"), namespace)
    curve = namespace["survival_curve"]
    def record(n: int, termination: str):
        return SimpleNamespace(turn_count=n, termination=termination)
    checks = []
    def add(name: str, observed, expected):
        checks.append({"name": name, "observed": observed, "expected": expected,
                       "passed": observed == expected})
    add("duration_positive_control", list(curve([record(1,"conflict"), record(3,"max_turns")],max_turns=4)),
        [1.0,1.0,0.5,0.5,0.0])
    failure = list(curve([record(2,"conflict")], max_turns=4))
    success = list(curve([record(2,"all_resolved")], max_turns=4))
    add("termination_label_does_not_change_curve", failure == success, True)
    add("stored_terminal_turn_counts_as_reached", failure[2], 1.0)
    add("empty_collection_rejected", raises_value_error(curve, [], max_turns=4), True)
    add("negative_horizon_rejected", raises_value_error(curve, [record(1,"conflict")], max_turns=-1), True)
    add("zero_horizon", list(curve([record(0,"max_turns")], max_turns=0)), [1.0])
    functions = [n for n in ast.parse(actions).body if isinstance(n, ast.FunctionDef)]
    stubs = []
    for fn in functions:
        body = list(fn.body)
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
            body = body[1:]
        if len(body) == 1 and isinstance(body[0], ast.Pass):
            stubs.append(fn.name)
    add("specified_cpdc_actions_are_declaration_stubs", sorted(stubs), ["equip", "sell"])
    add("specified_file_has_two_top_level_functions", len(functions), 2)
    return {"scope":"E01 CPU source-contract tests; NOT an NPC benchmark",
            "session_date":date.today().isoformat(), "python":platform.python_version(),
            "source_git_blobs":{"metrics":msha,"actions":asha},
            "sources":{
                "metrics":"https://github.com/NLP2CT/NCP-Bench/blob/main/src/ncpbench/metrics.py",
                "actions":"https://github.com/MahammadNuriyev62/CPDC-challenge-2025-solution/blob/main/function_call_langchain/action_functions_0001.py"},
            "input_kind":"synthetic metric-contract records, not game episodes",
            "upstream_package_imported":False, "gpu_hours":0, "model_calls":0,
            "checks":checks,"passed":sum(c["passed"] for c in checks),"total":len(checks),
            "limitations":["No published scores or figure regenerated.",
                           "No conflict detection, action execution, NPC policy or human experience evaluated.",
                           "CPDC conclusion is limited to this public sample file, not the private official evaluator.",
                           "The NCP function correctly documents turn-threshold reach; test results are not a declaration of a bug."]}

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics",type=Path,required=True)
    parser.add_argument("--actions",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args = parser.parse_args()
    try:
        result = audit(args.metrics,args.actions)
    except (OSError, UnicodeError, ValueError, SyntaxError) as exc:
        parser.exit(2, f"Audit failed before completion: {exc}\n")
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"{result['passed']}/{result['total']} source contracts passed; 0 model calls; 0 GPU hours")
    if result["passed"] != result["total"]:
        raise SystemExit(1)
if __name__ == "__main__":
    main()
