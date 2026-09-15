# 2026-09-15 — Searcher Diagnosis and Next-Session Handoff

**Target:** ACL / EMNLP / NAACL Main, calibrated continuously against TACL / ICLR / ICML / NeurIPS / AAAI.

**Current result:** no new Main-level candidate from the latest broad search. This is not evidence that there are no good topics. The main bottleneck is still the **question generator / research taste**, not the strictness of Selection.

## 1. Core diagnosis

The search process has improved from `paper -> limitation -> gap`, but it still too often behaves like a **successor-paper generator**:

> strong paper / stable anomaly / important mother problem  
> -> ask what remains unexplained  
> -> owner audit  
> -> mechanism / intervention / residual distinction  
> -> kill because a mature program already exists.

This is better than paper-gap autocomplete, but it is still not enough. The searcher is reading literature from **inside an already-defined problem frame**, rather than spending enough time creating / recognizing the problem frame itself.

The strongest research examples we keep returning to have a different origin:

- **ACL 2026 local attention:** a restriction that should look weaker empirically improves quality; the paper explains a real broken expectation rather than filling a missing cell.
- **ICLR 2026 succinctness:** the old quantity `expressivity` is too coarse; a new quantity changes the scientific question.
- **ICLR 2026 multi-turn:** a load-bearing training/deployment mismatch exposes a capability failure that should matter even without the evaluation framework.
- **ICML 2026 Flexibility Trap:** a celebrated architectural advantage itself creates a hidden failure mode.
- **ICML 2026 memorization:** a vague debate is replaced by an information-theoretic quantity that can support a strong scientific claim.
- **NeurIPS 2025 RLVR capacity:** `better benchmark score` is separated from `expanded capability boundary`.

The transferable lesson is not the topic. It is the move:

> **find the assumption / quantity / expectation that the field is leaning on, then discover that it is incomplete or wrong.**

## 2. Why recent searches keep yielding zero survivors

### A. We still enter the literature too close to existing papers

Searching from named phenomena (`attention sink`, `world model`, `process supervision`, `MoE specialization`, etc.) causes retrieval to return the already-mature theory program. The remaining space is therefore naturally a mechanism sequel, a narrower cell, or a new intervention.

### B. We overuse `stable anomaly -> mechanism`

This is a valid provenance, but it is currently overrepresented. Recent strong papers often already own both the anomaly and the first explanatory layer. Starting from their anomaly almost guarantees successor pressure.

### C. We engineer candidates too early

As soon as a question feels interesting, the process begins thinking about SAME-QUANTITY, crossover, patching, matched treatments, MDE, etc. This rewards questions that are close to an experiment rather than questions with the highest scientific consequence.

A beautiful Layer-3 design can still hide an ordinary Layer-1 question.

### D. We confuse an important standing problem with an available paper

Scaling laws, systematicity, world-model identifiability, plasticity, grounding, etc. remain excellent scientific problems even when the current paper surface is saturated. Killing the current route must not delete the standing problem; conversely, the importance of the standing problem must not justify shrinking to an unowned residual.

### E. We do not yet spend enough search budget on `quantity/state-variable mistakes`

The strongest recent examples repeatedly change **what is being measured or treated as the scientific object**: expressivity -> succinctness; score -> capability boundary; memorization -> bits / intended vs unintended memorization; current competence -> future learnability.

This provenance is currently more promising than another mechanistic sequel.

## 3. What a genuinely good question should look like

Do **not** mechanically score candidates. But a serious question should usually have all of these properties:

**Low description length.** A strong researcher should understand the question before hearing the method.

**Independent scientific pressure.** The reason to care exists before our experiment and before the latest paper's limitation section.

**High best-case consequence.** The answer changes a belief about learning, reasoning, representation, language, or model design—not merely adds another failure mode.

**Genuine uncertainty.** The answer is not obvious from standard theory, and the project is not merely confirming a fashionable explanation.

**Both directions matter.** The question is informative even if the surprising effect disappears or the rival explanation wins.

**Longevity.** It survives model generations and benchmark turnover.

**Reasonable attack.** Following Hamming, an important problem becomes actionable when there is now a credible way to attack it; attackability is necessary, but it must not create the question.

A useful compression is:

> **low description length + high consequence + real uncertainty + new leverage**.

## 4. Preferred provenance classes for the next search

Prioritize these before `behavior -> mechanism`:

1. **Broken load-bearing expectation**  
   Something the field genuinely expects to be monotone / invariant / helpful is robustly false.

2. **Wrong scientific quantity / state variable**  
   A long-standing debate is stuck because the field measures the wrong object; a new quantity makes rival claims falsifiable.

3. **Regime change breaks an old inference**  
   A theorem, tradeoff, or explanation relied on assumptions that foundation-model training or deployment no longer satisfies.

4. **Long-standing linking assumption fails**  
   The field treats observable X as evidence for construct Y, but the bridge is only valid under untested assumptions.

5. **Stable law without a satisfying explanation**  
   Prefer laws appearing across independent settings, not a single paper's strange cell.

6. **Standing important problem + genuinely new leverage**  
   Modern models make an old problem answerable in a way that changes the inference, not merely because hidden states are observable.

## 5. Search procedure — keep it simple

### First: recalibrate taste every round

Before generating topics, freshly read a small but serious set of **Best / Outstanding / strong Main / TACL papers**, plus relevant strong-author lineages and research-advice material.

For each, reconstruct only:

> What was believed before?  
> What pressure made that belief unsatisfactory?  
> What did the authors notice that others missed?  
> What new quantity / contradiction / regime change made the paper possible?  
> What scientific belief changed?

Predict the result / next experiment before reading the authors' move when possible. Study why their move is better than the searcher's prediction.

### Second: maintain a Standing Important Problems Portfolio

Keep important unresolved problems even when no current project exists. New papers should be asked:

> **Does this bear on one of our standing problems?**

not:

> **What topic can be generated next to this paper?**

### Third: choose one WALL and turn candidate generation OFF

Reconstruct old theory, evidence, contradictions, replications, and modern regime. Do not search for an empty cell yet.

Wait until a natural uncertainty crystallizes.

### Fourth: apply only the 10-second gate

State:

> **Question:** what do we genuinely not know?  
> **Pressure:** why should a strong researcher already care / why is the default expectation under pressure?

No probe, benchmark, operator, metric, patching, SAE, checkerboard, or dataset names.

If the question becomes interesting only after the method is explained, do not promote it.

### Fifth: only then audit ownership and Selection

Check parent ownership, SAME-QUANTITY, rival explanations, identification, construct validity, MDE, compute, and paper-scale consequence.

If the mother problem is already a mature theory program, **do not shrink to escape owners**. Return to the standing portfolio and switch scientific object.

## 6. Searcher health checks

Immediately stop candidate generation and recalibrate if several ideas in a row become:

- `Paper A + Paper B`;
- `classic phenomenon × LLM`;
- `behavior paper -> mechanism sequel`;
- `limitation -> new setting`;
- `new intervention -> find a distinction`;
- increasingly technical wording needed to preserve novelty;
- Layer-3 identification more exciting than Layer-1 question.

Also switch scientific object after repeated direct-owner kills. Do not spend the whole round mining one fashionable program.

## 7. Important negative lessons from the latest search

The latest broad round repeatedly found questions with excellent first-layer taste but saturated current surfaces: scaling-law origins, predictive world-state identifiability, process supervision, minimal grounding, update spillover, reasoning-vs-control, equal-resource MoE, representation convergence, etc. This supports the diagnosis above: **large important problems are not the shortage; finding an unowned, consequential scientific uncertainty inside or outside them is.**

The positional-memory route is a useful warning. Its initial question was excellent—why does a memorized continuation require the document beginning as a key?—but the simplest causal-LM context-mismatch explanation was too plausible, forcing increasingly elaborate controls. It was correctly closed once Layer-3 became more interesting than Layer-1. The latest live WATCH from the pasted handoff is `local predictability vs global execution efficiency`: next-token learning may prefer longer/local algorithms because each step is easier to predict, but this currently lacks enough independent evidence beyond the shortest-path lineage to become a project.

## 8. Next-session instruction

Do **not** treat this document or any prompt as a fixed algorithm.

The next searcher must actively ask:

> **What do the newest genuinely excellent ACL / EMNLP / NAACL / TACL / ICLR / ICML / NeurIPS papers reveal about idea provenance that our current doctrine still misses?**

If award papers, author lineages, Related Work, talks, or strong-researcher advice reveal a better way to search, **update the search method immediately**.

The goal is not to obey the checklist perfectly. The goal is to develop better research taste than the checklist currently encodes.

**Final target:**

> **A natural, important, genuinely uncertain question that a strong researcher wishes were already answered; modern foundation models provide a credible new way to answer it; identification makes the answer trustworthy, but does not create the question.**
