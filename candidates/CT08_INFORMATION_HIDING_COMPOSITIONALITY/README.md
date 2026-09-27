# CT08 — Does Compositional Generalization Require Information Hiding?

**Status: CANDIDATE — registered 2026-09-27. E00 (first-stage validity, inference only) frozen
below; E01 (the visibility triad) drafted, NOT authorized.** No compute used yet.
Unrelated to CT05–07 (hybrid KV memory), which stay closed.

## Question

RLM-style harnesses generalize compositionally. Zhang & Khattab (*Language model harnesses are
compositional generalizers*, 2026) report 8–32× length transfer and cross-domain strategy transfer.
Their explanation: payload lives in REPL variables and sub-calls, so the root LM's control
trajectory is near-isomorphic across tasks, and printing domain-specific data back to the root is
"often undesirable from a generalization perspective".

The RLM package bundles several things: context offloading, symbolic variables, hiding the payload
from the controller, sub-calls, and a shorter root context. The load-bearing variable is not
identified:

> Does the controller need to be causally **unable to see** the task payload (information
> hiding), or is a **structural control/data separation** with the payload visible enough?

## Nearest priors (checked 2026-09-27)

| Prior | Owns | Gap left |
|---|---|---|
| Zhang & Khattab 2026 (harness blog / alphaXiv); Qwen3-30B-A3B, RL (prime-rl), 150–500 steps | length and cross-domain transfer of RLM vs the same model trained flat | **no ablation separating hiding from offloading / sub-calls**; admits the root often prints payload |
| RLM paper (2512.24601, NeurIPS 2026) | REPL-only (no sub-calls) ablation, performance only | not generalization; not visibility |
| RLM-Qwen3-8B (mit-oasys, public) | **SFT on 1,000 teacher trajectories** already transfers to unseen task types | makes a matched-strategy SFT triad affordable |
| Multi-Stream LLMs (2605.12460) | parallel role streams with cross-stream attention; efficiency, injection robustness, monitorability | no compositional / cross-domain transfer; no visibility barrier |
| Russin et al. 2019 (Syntactic Attention, SCAN); entity / variable anonymisation in semantic parsing | **classic: separate + hide content from the structure pathway → compositional generalization** | small seq2seq, no LM-harness scale; separation and hiding never contrasted |
| Smaller Abstract State Spaces (2605.20272) | RL theory + experiments: smaller abstract states give cross-scale transfer | not LMs / harnesses |
| Shared Program State / Nightjar; Context as an Environment; Control-Data Flow Separation | harness-level variables, print-on-demand context, typed protocol objects for pipeline stability | no visibility × generalization contrast |
| Don't Mask the Environment (2609.20715) | *loss* masking of observation tokens changes RL exploration | loss masking, not what the policy can attend to |

Honest framing: "hiding content from the structural pathway helps compositionality" is an old idea
(Russin 2019, anonymisation). The new object is only the contrast **separation vs hiding** at
LM-harness scale, where a live 2026 claim rests on it.

## Identification problems in the first-draft design (fixed below)

1. **Short→long is confounded for MIXED / SEPARATE-VISIBLE.** Their root context grows with the
   payload, so an 8–32× test is mostly positional / length extrapolation (or does not fit Qwen3-8B
   at all). **Primary axis = cross-domain at matched length inside the window.** Length transfer
   is reported only for ranges all arms can hold.
2. **RL vs SFT.** The harness result is RL at 30B, which is infeasible here. SFT on *identical*
   teacher trajectories matches the target strategy by construction, and RLM-Qwen3-8B shows SFT
   already transfers. Consequence: an RL-only phenomenon would not be tested. This is stated as a
   limit, not rescued.
3. **"Opaque" is not opaque.** The RLM root prints payload slices on request. OPAQUE therefore
   means *hidden by default, readable on explicit request*, which is the Selective Data Access
   idea itself. Leakage (payload tokens printed into the root) is measured per trajectory.
4. **SEPARATE-VISIBLE has no pretrained architecture.** Two pre-registered implementations:
   `V-tag` (payload in a delimited data segment, same positions as MIXED) and `V-pos` (data segment
   with its own position range; control positions start at the same offset regardless of payload
   length, as in Multi-Stream). `V-pos` is off-distribution for pretrained RoPE and only adapts
   through the same SFT, so a V-pos loss can be a format artefact. V-tag guards against that.

## E00 — first-stage validity (inference only; frozen)

The triad needs a transfer effect to decompose, at a scale we can train. First check that one
exists:

- **Models:** RLM-Qwen3-8B (released; trained on LongBenchPro) vs Qwen3-8B zero-shot in the same
  RLM harness vs Qwen3-8B flat (full context, direct answer).
- **Data:** OOLONG-synth task families not seen in RLM-Qwen3-8B training, at context lengths
  ≤ 32k so that all arms fit.
- **Gate:** RLM-Qwen3-8B beats the untrained harness (zero-shot Qwen3-8B RLM) by ≥ 5 points on
  unseen domains, with the paired bootstrap CI excluding 0, **and** the root control skeletons
  on the unseen domains are measurably closer to training-style skeletons than the zero-shot
  harness's are. The skeleton is the sequence of REPL operations with payload literals
  stripped; the measure is normalised edit distance.
- **If the gate fails, KILL.** At feasible scale there is no learned transfer to attribute to
  hiding vs separation, and scaling up to 30B RL is outside the envelope.
- Also recorded (descriptive): the payload leakage rate per trajectory, in-domain vs out-of-domain.

## E01 — visibility triad (drafted; runs only after E00 passes and explicit authorization)

- Teacher: a local 27B model as RLM root with Qwen3-8B sub-calls on a training domain (≤ 32k).
  Filter ~1,000 correct trajectories. **The same trajectories go to every arm.**
- Student: Qwen3-8B, identical SFT recipe, seed and token budget. The only manipulation is what
  the root context contains during training *and* test:
  `MIXED` (payload inline), `V-tag`, `V-pos`, `OPAQUE` (standard RLM).
- Test: held-out domains at matched length. Primary = accuracy; secondary = skeleton isomorphism
  and leakage.
- **Outcome reading, not a prediction:** M≈V≈O → KILL; V≈O>M → separation suffices;
  O>V≈M → hiding is load-bearing; O>V>M → both contribute. The effect must hold for both
  V-tag and V-pos before any "separation" conclusion, and a second seed is required before any
  claim.
- Estimated cost: teacher generation plus 4 × SFT on ~1k trajectories plus harness evals. A few
  A100-days, within the 8-card envelope.
