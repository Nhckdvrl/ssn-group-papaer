# CT05 — What Must an Agent Remember Exactly? (hybrid KV vs recurrent memory)

Opened 2026-09-27 from the user's reading of Alex Zhang, *Language model "shape"* (2026 blog).
Status: **KILLED AFTER E01 (2026-09-27), `CT-KILL-20260927-1`**, pre-registered Kill A.
Result: `docs/E01_RESULTS.md`. In one sentence: in Qwen3.5-9B, evicting an agent event's KV costs
as much as deleting its text (rho = −0.005 [−0.034, 0.024]), because agent decisions depend mostly
on verbatim copying, which only attention supplies (recurrence carry 1% on copy tokens).

## Question

A hybrid LM (Qwen3.5: Gated DeltaNet + full attention) has already folded the whole agent history
into its recurrent state. At a given decision, which past events still need their **exact,
addressable attention KV**, and which are served by the recurrent state alone?
`importance` (does deleting the event change the action?) is not the same quantity as
`exactness demand` (does hiding only its KV, with the recurrent state intact, change the action?).

## Nearest priors checked (2026-09-27)

| Prior | Owns | Not covered |
|---|---|---|
| What Attention Recalls and Recurrence Controls (2609.04434) | KV-only / rec-only split-prefill, State-swap on synthetic tasks | agent trajectories, per-span deletion, eviction |
| HAM (2603.22325), HOLA (2607.02303) | route to KV what recurrence cannot predict/reconstruct; trained architectures | decision-conditioned demand, agents |
| DeltaS (2609.27470) | GDN state drift -> KV retention, streaming video | agents; drift is our baseline |
| NHA (ACL 2026) | recent exact + old compressed | — |
| AgentKV, MemDecay, RoleKV, SideQuest, IntentKV, Leyline | agent KV eviction on pure Transformers | recurrent channel |
| TRACE, TRACER, DTOC, PACE, CaT | text-level agent context attribution / compaction | model-internal channels |
| Multi-Stream LLMs (2605.12460) | per-role streams incl. per-stream recurrent state | — (per-role streams not pursued) |

## Layout

- `docs/E01_PROTOCOL.md` — frozen readouts and kill gates.
- `src/prep.py` — decision checkpoints from SWE-smith and APIGen-MT logs.
- `src/render.py`, `src/cachelib.py` — chat-template rendering and cache interventions.
- `src/e01.py` — runner; `src/analyze_e01.py` — readouts A–C.
- `src/env.sh` — runtime (openslime python + vendored transformers 5.12.1).
- `results/e01/` — raw per-checkpoint jsonl; `logs/` — launch log and run logs.
