# Execution notes — before model outputs, 2026-09-08

Use existing `/home/xiang/miniconda3/envs/verl-clean/bin/python` read-only:
torch 2.8.0+cu128, transformers 4.57.6, accelerate 1.13.0. The local audit
environment has no GPU dependencies. No shared environment is modified.
Set PYTHONDONTWRITEBYTECODE=1 and all runtime caches inside L02.

The installed tokenizer reports its known Mistral regex issue. Explicitly enable
`fix_mistral_regex=True` for Mistral before any probe outputs are produced.
Both A/B labels are single tokens (1065, 1066) in the initial tokenizer check.
Preserve original frozen prompts/protocol, snapshot executed script and rendered
prompts; this is a runtime correction, not output-dependent prompt tuning.

The scientific target remains native interpretation discrimination. Forced A/B
likelihoods are not free-generation decisions or filler-support measurements.

Source inspection while loading (before predictions): only 2/21 paired strata
have exactly the same surface predicate in both members (`attempt`, `face`).
The other pairs can differ in lexical item, inflection and syntactic construction.
The design removes the deterministic frame/role-only shortcut, **not all lexical
or syntactic shortcuts**. Accuracy above 50% therefore does not by itself prove
use of cross-sentence evidence. The paired full-versus-sentence contrast is the
actual context-availability diagnostic, with original labels retained in both.

The shared NFS weight load stalls on memory-mapped reads. A separate, two-reader
sequential prefetch (`scripts/prefetch_probe_weights.py`) warms the OS page cache
from the same pinned files, without copying, downloading or modifying weights.
Its paths, byte counts and timings are saved in `runs/E001a_prefetch_weights.jsonl`.

After continued NFS stalls, only the auxiliary prefetch process was restarted
with four readers and interleaved model shards. The original loader/model
processes continue unchanged. Preserve the v1 script/log; v2 timings are in
`runs/E001a_prefetch_weights_v2.jsonl`. This is an I/O scheduling change only.
