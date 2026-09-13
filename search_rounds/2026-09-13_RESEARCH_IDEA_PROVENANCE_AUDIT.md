# 2026-09-13 — Research-Idea Provenance Audit

## Why this audit exists

The post-L32 search was still overusing one generator:

> published stable anomaly -> ask for its explanation

That generator is real, but it is not representative enough of how strong ACL/EMNLP/NAACL/ICLR/ICML/NeurIPS papers originate. It is also structurally late: once a striking anomaly has been published, the same paper or immediate successors often already own the obvious explanation.

This audit therefore asks a more basic question:

> **Where did the research question come from, and who discovered the central phenomenon: prior work or the focal paper itself?**

## Empirical warning against LLM-style idea generation

Chen, Zhao & Cohan (2026), *Measuring the Gap Between Human and LLM Research Ideas*, reverse-engineer literature context for 11,683 papers from ICLR/ICML/NeurIPS 2023–2026 and Nature Communications 2023–2025, then compare human paper ideas with LLM-generated ideas under comparable prior-work context.

Key result: human ideas are much less dominated by `connect A + B` and synthesis/unification than LLM-generated ideas. Only about 12.1% of human ideas are connection/fragmentation-bridge opportunities and about 5.1% use synthesis/unification centrally, versus roughly 47.1–64.2% and 22.5–38.7% for LLM-generated ideas.

Source: https://arxiv.org/abs/2607.01233

This strongly supports the project's existing anti-bridge rule: `Prior A + Prior B = paper` is not just aesthetically weak; it is a systematic LLM bias.

## Provenance types found in strong papers

### Type 1 — Prior work already owns the phenomenon; focal paper explains it

This is the search mode we had overused.

Examples:

- ACL 2026 Best, *Characterizing the Expressivity of Local Attention*: local attention was already known to sometimes improve quality despite being an efficiency restriction; the focal paper asks why and supplies a formal expressivity account.
- ACL 2024 Best, *Why Are Sensitive Functions Hard for Transformers?*: prior empirical work already showed persistent difficulty on functions such as PARITY; the focal paper supplies a unifying optimization/loss-landscape explanation.
- NeurIPS 2025 scaling-law work similarly starts from an established macro-phenomenon and seeks a mechanism.

This type remains useful, but by publication time it often has severe successor pressure.

### Type 2 — Related work creates a pressure/mismatch; focal paper designs the comparison and discovers the phenomenon

This appears repeatedly in strong work and should become a primary generator.

Examples:

- ICLR 2026 Outstanding, *LLMs Get Lost In Multi-Turn Conversation*: prior evaluation was overwhelmingly single-turn while real deployment is often progressively specified. The paper constructs a matched single-turn vs multi-turn comparison and **discovers** the large degradation itself. The 39% drop was not a previously established mother phenomenon.
- ACL 2025, *Did Translation Models Get More Robust Without Anyone Even Noticing?*: old NMT literature established fragility to character noise, but the model/training regime changed. The paper re-tests the old law under modern multilingual MT/LLM systems and **discovers** that robustness increased dramatically without explicit robustness training.
- EMNLP 2025 Outstanding, *Generative or Discriminative? Revisiting Text Classification in the Era of Transformers*: starts from a classic generative/discriminative sample-efficiency law and asks whether its premise survives pretrained Transformers; the focal paper discovers the revised modern-regime behavior.

The key provenance is not `find an anomaly in another paper`. It is:

> **find a load-bearing old assumption / evaluation convention / regime mismatch -> construct a matched test -> let the new phenomenon emerge from the test.**

### Type 3 — Widely accepted claim/premise has weak or indirect evidence; focal paper stress-tests it and discovers a contradiction

Examples:

- ACL 2024 Best, *Mission: Impossible Language Models*: starts from a strong theoretical/public claim about possible vs impossible languages, but direct evidence is weak. The authors construct impossible-language tests and discover a result that challenges the claim.
- NeurIPS 2025 Runner-Up, *Does Reinforcement Learning Really Incentivize Reasoning Capacity Beyond the Base Model?*: starts from a widely accepted premise that RLVR expands reasoning ability; a large-k capability-boundary test reveals that the base model often has broader support and RL can narrow it.
- ICML 2026 Outstanding, *The Flexibility Trap*: starts from the premise that arbitrary-order diffusion decoding should expand the reasoning solution space; direct stress tests reveal the opposite in important regimes.

Here the focal paper both creates the decisive test and discovers the anomaly. Related work supplies **the belief to attack**, not the anomaly to explain.

### Type 4 — Mature scientific question/debate; focal paper contributes a new identifying instrument

Examples:

- EMNLP 2025 Outstanding, *Measuring Chain of Thought Faithfulness by Unlearning Reasoning Steps*: CoT faithfulness was already heavily debated, but existing evidence did not identify whether verbalized reasoning reflects parametric reasoning. The contribution is a causal instrument that changes what evidence can support the claim.
- EMNLP 2025 Outstanding work on filler-gap constructions similarly uses causal interventions to answer an existing representational/mechanistic question more decisively.

The novelty is not a new anomaly and not a new benchmark. It is:

> **same important question, but previous evidence cannot identify the answer; a new operation can.**

### Type 5 — Under-examined structural choice/design axis; systematic test discovers a stable effect, then paper explains it

Example:

- NeurIPS 2025 Best, *Gated Attention for Large Language Models*: gating was common elsewhere but its role inside softmax attention was under-examined. A controlled design sweep discovers that a simple head-specific sigmoid gate consistently improves training/performance; the paper then explains the effect.

This is not `method combination` when the scientific object is the structural choice itself and the sweep is used to discover a general law rather than win a leaderboard.

## Main correction to the search doctrine

Do **not** make `stable published anomaly -> unresolved why` the dominant search generator.

It should be one generator among several. The higher-yield provenance-first search should start from **scientific pressure**:

1. **Old law under a changed regime**
   - What premise was load-bearing in 2018–2023?
   - Did pretraining, post-training, reasoning, scale, or architecture invalidate that premise?
   - What matched comparison would expose the change?

2. **Widely accepted claim with weak identification**
   - What does the field repeatedly say `X happens because Y` or `method Z expands capability`?
   - What evidence actually supports it?
   - Can a modern checkpoint/intervention directly stress-test it?

3. **Evaluation/deployment or training/inference mismatch**
   - What condition is systematically absent from standard evaluation but naturally present at deployment/training time?
   - Can the same underlying information/task be held fixed while only that condition changes?

4. **Under-examined structural choice**
   - What ubiquitous modeling/training choice is treated as default rather than as a scientific variable?
   - Is there a controlled comparison that could reveal a general law rather than a method win?

5. **Known phenomenon -> explanation**
   - Keep this route, but use it selectively because successor pressure is high.

## Search-stage change

The search-stage target should be broadened from:

> `mother phenomenon already exists -> find missing explanation`

into:

> `strong prior pressure already exists -> find the cheapest matched stress test whose outcome is genuinely not implied by the literature`

The focal paper may therefore **discover the central phenomenon itself**. This is not the same as gambling on an arbitrary effect: the experiment must be motivated by a pre-existing scientific tension, claim, law, or mismatch, and both plausible outcomes must teach us something about that pressure.

This distinction is important:

- **Bad phenomenon gamble:** invent an intervention and hope a quirky effect appears.
- **Good phenomenon discovery:** a strong prior claim/premise creates a sharp prediction; a matched test can confirm, revise, or overturn it.

## Practical reading card for the next round

For each strong paper, before looking for follow-up anomalies, extract only:

1. **Prior belief / law / convention:** what did related work make researchers believe?
2. **Pressure:** why was that belief no longer sufficient?
3. **Who discovered the key phenomenon?** prior work or this paper?
4. **First decisive comparison:** what experiment made the paper possible?
5. **Minimal move:** what single inference did the paper add beyond its closest 3–5 predecessors?
6. **Transferable provenance move:** old-law retest, belief stress-test, mismatch exposure, new causal instrument, under-examined structural axis, or inherited-anomaly explanation.

Do not copy the topic. Transfer the provenance move.

## Bottom line

The earlier post-L32 search was too biased toward a late-stage provenance class: **someone else already published the anomaly; we search for explanation space**.

Strong papers show a broader and often more fertile pattern:

> **Related work supplies the pressure; the focal paper designs the decisive comparison; the focal paper itself often discovers the phenomenon and then explains or delimits it.**

The next search round should therefore search for **pressure first, phenomenon second** rather than `published anomaly first`.
