# 2026-09-13 — Pressure-First Search VIII

Small continuation after `PRESSURE_FIRST_SEARCH_VII.md`. No portfolio status changes are made here.

---

## Hook P36 — Why is grammaticality linearly explicit internally but weak in absolute string probability?

**Status:** `DROP / REPRESENTATION–OUTPUT GAP ALREADY HAS GENERATIVE ACCOUNT`

### Pressure

ACL 2026 reports a striking-looking gap: hidden states contain a robust linearly decodable grammaticality signal across languages/benchmarks, while raw sentence probabilities do not cleanly separate grammatical from ungrammatical strings. A tempting mechanism paper would ask why the model internally represents grammar yet apparently fails to express it at the output.

### Why it dies

TACL 2026 *What Can String Probability Tell Us About Grammaticality?* already provides the load-bearing generative explanation: a string's probability reflects both the probability of the intended message/content and the grammaticality of the realization. Therefore, outside matched minimal-pair settings, absolute probability is not expected to be a clean grammaticality score even if grammatical well-formedness is represented internally. The paper validates this account at large scale in English and Chinese.

Thus the apparent `hidden state knows grammar / output probability ignores grammar` contradiction is largely dissolved before a new causal mechanism is needed. Combined with the already logged P7 causal-use literature, neither `why is the signal hidden?` nor `erase/steer the grammar direction` is a fresh parent.

### Anti-resurrection

Do not reopen as `internal grammar signal is not read out`, `why probability misses grammaticality`, `grammar is encoded but unused`, or `patch the grammar direction` without a different estimand beyond the TACL generative account and existing causal-probing program.

---

## Hook P37 — Are mechanistic mediators invariant properties of the function or artifacts of a gauge/basis choice?

**Status:** `DROP / DIRECT GAUGE-SYMMETRY MECHANISM-AUDIT OWNER`

### Pressure

The 2026 *Quest for the Right Mediator* survey makes explicit a foundational unresolved-looking issue in mechanistic interpretability: studies choose different causal units — neurons, heads, basis-aligned subspaces, arbitrary directions, learned features — and the field lacks a single privileged mediator type.

This suggested a stronger version of the Super-Weight question:

> **If two parameterizations implement exactly the same model function, should a claimed causal mechanism identify the same mediator?**

A function-preserving reparameterization would appear to offer an unusually decisive test: keep every input/output behavior fixed while asking whether neuron/direction/head-level mediation maps change.

### Why it dies

2026 *The Gauge-Symmetry Audit: A Falsifiable Probe for Gated Mixers in Sequence Models* already elevates precisely this symmetry concern into a mechanism-audit methodology. It constructs a closed-form gauge-preserving swap that reverses an interpretable gate direction while preserving the mixer computation, contrasting it with an asymmetric control, and argues that a named internal behavior can be gauge-orbit basin selection rather than a load-bearing mechanism. The paper tests the principle across speech, sign-language, OCR and a text Switch-Transformer MoE module.

In parallel, the ICLR-2026 submission *Maximal Gauge Symmetry in Transformer Architectures* formally characterizes the large function-preserving gauge groups of canonical Transformers, including GPT-2, BERT, LLaMA and Qwen, with RoPE/GQA variants.

Therefore the strongest proposed claim is already directly owned:

> **A mechanistic story attached to a non-invariant internal coordinate can change along a function-preserving symmetry orbit and therefore needs a gauge-style audit before being treated as causal explanation.**

A generic `rotate a neuron/direction and watch the mediation map move` paper would be confirmation/application, not a new Main-level scientific object.

### Anti-resurrection

Do not reopen as `mechanistic explanations are coordinate dependent`, `causal mediator should be gauge invariant`, `rotate the residual basis and re-run patching`, or `same function, different circuit map` unless a new invariant causal quantity is identified beyond the existing gauge-audit program.

---

# Round state

**New survivor: 0.**

Mainline remains **NONE**. L32 and L33 remain bounded `PILOT-AUTHORIZED — E01 ONLY`; this log does not alter `CURRENT_SEARCH.md`.

The useful search lesson is that exact symmetries are not automatically novel scientific instruments. Before promoting a symmetry-based intervention, check whether the symmetry has already been turned into the scientific claim itself.
