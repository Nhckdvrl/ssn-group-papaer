#!/usr/bin/env python3
"""Run frozen E77 reporting with repeated pure value_fn evaluation deduplicated."""
import ast
import hashlib
import json
from pathlib import Path
import sys


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


original_path = Path(__file__).with_name('native_dialogue_outcome_report.py')
original = original_path.read_text()
before = '''            matrix = [np.mean([[value_fn(cid, seed)[f] for f in use_fields] for seed in SEEDS], axis=0)
                      for cid in cids]'''
after = '''            matrix = []
            for cid in cids:
                per_seed = []
                for seed in SEEDS:
                    point = value_fn(cid, seed)
                    per_seed.append([point[f] for f in use_fields])
                matrix.append(np.mean(per_seed, axis=0))'''
assert original.count(before) == 1
optimized = original.replace(before, after)
tree_before, tree_after = ast.parse(original), ast.parse(optimized)
get_metrics = lambda tree: next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'metrics')
assert ast.dump(get_metrics(tree_before)) == ast.dump(get_metrics(tree_after))
# Normalize only estimate's matrix assignment to verify that nothing else in
# the scientific script, including bootstrap, contrasts and schemas, changed.
estimate_before = next(n for n in ast.walk(tree_before) if isinstance(n, ast.FunctionDef) and n.name == 'estimate')
estimate_after = next(n for n in ast.walk(tree_after) if isinstance(n, ast.FunctionDef) and n.name == 'estimate')
assert len(estimate_before.body) == 2 and len(estimate_after.body) == 3
estimate_after.body = estimate_before.body
assert ast.dump(tree_before) == ast.dump(tree_after)
assert '--out' in sys.argv
out = Path(sys.argv[sys.argv.index('--out')+1])
audit = {'status': 'PASS', 'frozen_report': str(original_path), 'frozen_report_sha256': digest(original),
         'in_memory_optimized_sha256': digest(optimized),
         'metrics_ast_sha256': digest(ast.dump(get_metrics(tree_before))),
         'only_estimate_matrix_evaluation_changed': True,
         'scope': 'Pure deterministic value_fn evaluated once per world/seed; metric definitions, field order, contrast weights, bootstrap and output schema unchanged.'}
out.with_name(out.stem+'_compute_audit.json').write_text(json.dumps(audit, indent=2)+'\n')
namespace = {'__name__': '__main__', '__file__': str(original_path)}
exec(compile(optimized, str(original_path), 'exec'), namespace)
