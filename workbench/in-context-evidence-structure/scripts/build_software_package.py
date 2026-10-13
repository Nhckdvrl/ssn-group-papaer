"""Build the anonymous software supplement (software-submission/ and software-submission.zip).

Copies the experiment engines and analysis scripts with machine-specific defaults removed, the result files
needed to regenerate every figure and appendix table on CPU, and provenance notes for the code versions.
"""
import glob
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / 'software-submission'
CODE = ['e56_query_adapter', 'e109_reconstruction_audit', 'e115_llama_native_mechanism', 'e118_criterion_code_feature_crossing',
        'e118_mistral_materials', 'e119_criterion_scale', 'e119_native_scale', 'e120_operation_necessity', 'e121_sst_materials',
        'e121_natural_sentiment_mechanism', 'e122_source_preserving_formation', 'e123_natural_source_function_policy',
        'e123_wave_report', 'e125_public_output_schema_coordination', 'e125_swapped_minus_unrelated',
        'e127_shared_output_cache_composition', 'e131_dispatch', 'e131_mechanism', 'e131_native', 'e131_function',
        'e132_cross_source_edges', 'e132_merge', 'run_gemma', 'gemma_full_output', 'flip_single_source',
        'instruction_control', 'paper_figures_v2']
RESULTS = ['e123/*_confirmation/analysis.json', 'e123/*_confirmation/full_output_summary.json',
           'e123/*_confirmation/behavior.jsonl', 'e123/*_confirmation/preflight.json',
           'e131/*_confirmation_function/analysis.json', 'e131/*_confirmation_function/full_output_summary.json',
           'e131/*_confirmation_function/behavior.jsonl', 'e131/*_confirmation_native/analysis.json',
           'e131/*_confirmation_mechanism/analysis.json', 'e131/*_confirmation_mechanism/behavior.jsonl',
           'e120/*_confirmation/analysis.json', 'e121/*_confirmation/analysis.json', 'e121/*_confirmation/behavior.jsonl',
           'e125/summary.json', 'e125/*_confirmation/behavior.jsonl', 'e132/*_confirmation/analysis.json',
           'e132/*_confirmation/behavior.jsonl', 'e132/*_confirmation/preflight.json',
           ]


def scrub(obj):
    """Drop repository commit identifiers from result records."""
    if isinstance(obj, dict):
        return {k: scrub(v) for k, v in obj.items() if not k.startswith('git') and 'commit' not in k}
    if isinstance(obj, list):
        return [scrub(v) for v in obj]
    return obj


def model_name(path):
    m = re.search(r'models--[^/-]+--([^/]+)', path)
    return m.group(1) if m else Path(path).name


def sanitize(name, s):
    s = re.sub(r"/tmp/ices_models/", "models/", s)
    s = re.sub(r"subprocess\.check_output\(\[\s*['\"]git['\"],\s*['\"]rev-parse['\"],\s*['\"]HEAD['\"]\s*\],\s*text=True\)\.strip\(\)",
               "None", s)
    s = re.sub(r",\s*['\"]git_head['\"]\s*:\s*None(?=\s*[}\)])", "", s)
    s = re.sub(r"['\"]git_head['\"]\s*:\s*None\s*,\s*", "", s)
    s = s.replace("CACHE = Path('/home/xiang/.cache/huggingface/datasets/SetFit___sst5/default/0.0.0/e51bdcd8cd3a30da231967c1a249ba59361279a3')",
                  "CACHE = Path(os.environ.get('SST5_ARROW_DIR', Path.home() / '.cache/huggingface/datasets/SetFit___sst5/default/0.0.0/e51bdcd8cd3a30da231967c1a249ba59361279a3'))")
    if 'SST5_ARROW_DIR' in s and '\nimport os' not in s:
        s = s.replace('import hashlib\n', 'import hashlib\nimport os\n', 1)
    if name == 'e56_query_adapter':
        s = '"""Shared helpers: the prompt header, the Measuring Hate Speech comment pools and the context builder."""' + s[s.index('"""', 3) + 3:]
        # Only the prompt header, the Measuring Hate Speech pools and the context builder are used; the adapter
        # training entry point of this early exploratory script is not part of any experiment in the paper.
        s = s[:s.index('\ndef main():')] + '\n'
    if name == 'e109_reconstruction_audit':
        # Only summarize() is used by the engines and the figure script.
        s = s[:s.index('\ndef main')] + '\n' if '\ndef main' in s else s
    if name == 'e123_wave_report':
        # Only output_metrics() is used (by gemma_full_output.py, which applies to any E123 run); the original
        # wave report also needed run records and plotting directories that are not part of this package.
        s = s[:s.index('\ndef collect')] + '\n' if '\ndef collect' in s else s
        s = re.sub(r"\n\s*assert run\['script_sha256'\] == '[0-9a-f]+'\n",
                   "\n            # The engine hash recorded at run time is kept in the audit; see CODE_PROVENANCE.md.\n", s)
    return s


def main():
    if PKG.exists():
        shutil.rmtree(PKG / 'code', ignore_errors=True)
        shutil.rmtree(PKG / 'results', ignore_errors=True)
    (PKG / 'code').mkdir(parents=True, exist_ok=True)
    provenance = []
    for name in CODE:
        src = ROOT / 'scripts' / f'{name}.py'
        text = src.read_text()
        out = sanitize(name, text)
        (PKG / 'code' / f'{name}.py').write_text(out)
        provenance.append((name, hashlib.sha256(src.read_bytes()).hexdigest(), hashlib.sha256(out.encode()).hexdigest()))
    n = 0
    for pattern in RESULTS:
        for f in sorted(glob.glob(str(ROOT / 'results' / pattern))):
            dest = PKG / 'results' / Path(f).relative_to(ROOT / 'results')
            dest.parent.mkdir(parents=True, exist_ok=True)
            if f.endswith('.json'):
                data = scrub(json.loads(Path(f).read_text()))
                text = json.dumps(data, indent=1)
                dest.write_text(re.sub(r'"model": "([^"]*)"', lambda m: '"model": "models/%s"' % model_name(m.group(1)), text) + '\n')
            else:
                shutil.copy(f, dest)
            n += 1
    recorded = {}
    for run in sorted(glob.glob(str(ROOT / 'results/e1[2-3]*/*_confirmation*/run*.json'))):
        r = json.loads(Path(run).read_text())
        if 'script_sha256' in r:
            recorded.setdefault(Path(run).parts[-3], set()).add(r['script_sha256'])
    lines = ['# Code provenance', '',
             'Each experiment run records the SHA256 of the engine that produced it (`script_sha256` in its run file).',
             'The engines in `code/` differ from those recorded hashes in two ways, neither of which changes the computation for',
             'the models already run:', '',
             '1. After the Qwen3, Mistral and Llama runs, the engines of E119/E120/E121/E123 gained a Gemma-2 branch (import of the',
             '   Gemma-2 attention module and revision entries) and call the native attention function with keyword arguments,',
             '   because Gemma-2 orders `dropout` before `scaling`.',
             '2. For this package, machine-specific defaults were replaced (model paths, the SST-5 cache path, which can be set',
             '   with `SST5_ARROW_DIR`), and the call that recorded the git commit was removed.', '',
             'Engine hashes recorded in the runs:', '']
    for exp, hs in recorded.items():
        lines.append(f'- {exp}: ' + ', '.join(sorted(h[:12] for h in hs)))
    lines += ['', 'Hashes of the files in this package and of their repository versions:', '',
              '| File | Repository | Package |', '|---|---|---|']
    lines += [f'| `{n}.py` | `{a[:12]}` | `{b[:12]}` |' for n, a, b in provenance]
    (PKG / 'CODE_PROVENANCE.md').write_text('\n'.join(lines) + '\n')
    zipf = ROOT / 'software-submission.zip'
    zipf.unlink(missing_ok=True)
    subprocess.run(['zip', '-qrX', str(zipf), 'software-submission', '-x', '*/__pycache__/*', '*/outputs/*'], cwd=ROOT, check=True)
    print('code files', len(CODE), 'result files', n, 'zip MB', round(zipf.stat().st_size / 1e6, 1))


if __name__ == '__main__':
    main()
