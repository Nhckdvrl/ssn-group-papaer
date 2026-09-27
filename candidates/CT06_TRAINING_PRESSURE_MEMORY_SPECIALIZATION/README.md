# CT06 — Does Abundant Attention Keep Recurrence from Learning History? (training pressure × memory specialization)

**Status: CANDIDATE — nearest-prior audit done, pre-registration drafted. NOT pilot-authorized. No compute used.**
Opened 2026-09-27 as a *separate* candidate after CT05 was killed (`CT-KILL-20260927-1`).
It is not a CT05 rescue. CT05 assumed that pretrained recurrence already carries history, and that
assumption is dead. CT06 asks whether training-time access to attention is what prevents it.

## Question

In hybrid LMs, is the split "attention recalls, recurrence controls" an architectural law, or a
specialization produced by training pressure? Concretely: if exact attention is made unreliable
during (continued) training, does the recurrent channel start carrying the history that agent
decisions depend on, *including verbatim-copy tokens*, while attention is still available at test
time?

The measurement is CT05 E01's causal metric, reused unchanged:
`rho = 1 − dNLL(KV evicted, recurrence kept) / dNLL(text deleted)`, split by token class
(copy-from-history / tool name / argument value / other). Pretrained Qwen3.5-9B scores
rho ≈ 0, with copy-token carry 1% and other-token carry 26%.

## Nearest-prior audit (2026-09-27)

| Prior | What it already shows | Consequence for CT06 |
|---|---|---|
| **SWAX** (Meta FAIR, ICLR 2026, 2509.24552) | xLSTM + SWA from scratch, 1.4B/7B, 150B tokens. Window 128 beats 2048 on RULER NIAH at 65k–131k (~30% vs ~0%); stochastic 128/2048 keeps short-context quality. Explanation: large windows remove the incentive to train the recurrent memory. No channel ablation, no measure of what the state stores, from-scratch only. | **Owns the core "architectural vs learned" question for SWA hybrids.** In SWAX-128, anything recalled beyond 128 tokens must come from recurrence, so "pressure shifts specialization" is already demonstrated behaviourally. |
| **Rethinking the Role of Efficient Attention in Hybrid Architectures** (THUNLP, 2606.15378, code released) | 15M–477M, ≤100B tokens, 1:1 full / efficient hybrids including GDN and Mamba-2. Restricting the efficient layers' receptive field barely changes long PPL; restricting full attention hurts sharply, so efficient layers store little long-range information. "Large-window laziness": big SWA windows delay full-attention retrieval. Architecture gaps **shrink with sufficient training**. | Owns "recurrence stores little when full attention exists" at small scale. Raises the **speed-vs-endpoint threat**: pressure may change *when* capabilities emerge, not where they end up. |
| **What Attention Recalls and Recurrence Controls** (2609.04434) | Static retrieval / control split in pretrained Qwen3.5, Falcon-H1, Kimi-Linear, OLMo-Hybrid, Jamba2. | No training intervention. |
| **Functional Component Ablation in Hybrid LMs** (2603.22473) | Qwen3.5-0.8B / Falcon-H1-0.5B component ablations. Explicitly lists "vary training conditions to test architectural vs learned specialization" as **future work**. | Confirms the gap is open *as stated*. It also means others see it. |
| HAM (2603.22325), HOLA (2607.02303), learnable-token-eviction hybrids (2510.20787), NHA | Add or route to an explicit exact memory instead of expecting recurrence to absorb it. | Alternative answer: design, not pressure. They are the baselines if a method emerges. |
| Olmo Hybrid token analysis (Ai2 blog) | Hybrids win on non-repeated meaning tokens; recurrent-only models lose on repeated (copy) tokens. | Consistent with the CT05 copy/other split. |
| Copy-capacity theory (Jelassi et al. 2024; Zoology) | Fixed-state models have strictly lower copying capacity. | Upper bound: rho_copy may be capped regardless of pressure. |

**Audit verdict.** The broad question, "is the split learned?", is substantially answered by
SWAX (yes, for SWA hybrids trained from scratch) together with Rethinking (little long-range
storage in efficient layers; gaps shrink with training). The residual not covered by any prior:

1. **Post-hoc re-specialization of an already-pretrained full-attention hybrid.** Can
   continued training under memory pressure make Qwen3.5-class recurrence a working *backup*
   for exact history while full attention remains available at test time (rho > 0 at test)?
2. **Channel-level causal measurement split by token class on real agent decisions.** Does
   pressure move copy-token carry, or only semantic/control carry?

Both are narrower than the mother question. (1) is closest to an engineering property,
eviction-robust hybrids, and sits next to learnable-eviction training and HAM/HOLA. The residual
is honest but thin. Main-level value depends on whether rho_copy actually moves, which the copy-
capacity bound makes doubtful. **Recommendation: do not authorize a pilot until the user judges
residual (1)+(2) worth one bounded Gate 0; default lean is KILL at selection.**

## Pre-registered Gate 0 (drafted; runs only on explicit authorization)

- **Backbone:** Qwen3.5-0.8B-Base (18 GDN + 6 full attention; the same family as E01).
  Qwen3.5-2B-Base for confirmation only.
- **Data:** SWE-smith and APIGen-MT training trajectories disjoint from the CT05 E01 trajectories.
  Matched token budget, same seed and order across arms (~0.3–0.5B tokens).
- **Arms** (only the full-attention layers' access differs during training; test is always full):
  1. `FULL` — ordinary continued training;
  2. `WIN128` — full-attention layers restricted to a 128-token sliding window;
  3. `STOCH` — per batch, window 128 with p = 0.5, else full (SWAX schedule);
  4. `EVDROP` — per sequence, KV of random past harness events hidden from later tokens.
- **Measurement:** CT05 E01 unchanged (`src/e01.py`, `analyze_e01.py`, `analyze_copy.py`,
  `analyze_action.py`) on the held-out E01 checkpoints.
- **Cost estimate:** ~6·N·D per arm ≈ 2–3e18 FLOPs, i.e. under ~20 A100-hours for all four arms.
- **Continue only if all hold** for at least one pressure arm vs `FULL`:
  - `rho_pressure ≥ 0.3` at k = 2 and 4, bootstrap CI excluding `rho_FULL`;
  - **copy-token carry ≥ 0.2** (vs 0.01 in pretrained Qwen3.5-9B); movement in other-token carry
    alone is a kill, because the agent bottleneck is copy tokens;
  - full-context target NLL within 5% of `FULL`, so the fake compensation of a degraded
    full-context model is excluded;
  - the effect survives a second seed.
- **Kill otherwise.** Also kill if the arms separate at mid-training but converge by the end.
  That is the Rethinking "speed not endpoint" outcome and is reported as such, not rescued with
  longer training.
- **Forbidden rescues:** other backbones (Falcon-H1, OLMo-Hybrid), longer budgets after a null,
  new pressure schedules picked after seeing the Gate 0 signs, and synthetic copy tasks swapped
  in for real agent trajectories.
