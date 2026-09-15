# 2026-09-15 — Resource-Substitution Wall Audit

**Target:** ACL / EMNLP / NAACL Main  
**Calibration:** ICLR / ICML / NeurIPS / ACL  
**Mode:** NEW SCIENTIFIC OBJECT AFTER WALL-E CLOSURE  
**Outcome:** **0 new L-series; 0 new pilot authorization.**  
**State update:** evidence added to IP04 / resource constraints; generic internal-compute ↔ generated-token substitution is **not** a new topic generator under current ownership.

---

# 0. Why this wall was opened

After closing the generic WALL-E competence/plasticity surface, candidate generation remained off and the search moved to a different object.

A fresh empirical pressure came from Hu et al., Findings ACL 2026, *Lil: Less is Less When Applying Post-Training Sparse-Attention Algorithms in Long-Decode Stage*.

They target an apparently straightforward efficiency intervention: reduce decode-stage attention cost through sparsification.

But information loss can induce substantially longer generated sequences, so an intervention that makes each decode step cheaper can make end-to-end inference **more expensive**.

Source:
- https://aclanthology.org/2026.findings-acl.91/

This gives an immediately natural tension:

> **Why can making each step cheaper make the whole computation more expensive?**

The scientific temptation is to lift the phenomenon into a broader question:

> **When computation inside each generation step is restricted, does a language model compensate by externalizing more computation into additional generated steps?**

This wall audit asks whether that broader question is genuinely unowned.

---

# 1. 10-second test

### Question

> **Can a weaker/cheaper forward pass be made equivalent to a stronger one simply by letting the model think for more steps?**

### Pressure

> Extra reasoning tokens can add serial computation, while sparse-attention interventions can make models emit more tokens; this suggests that per-step computation and generation length may trade off rather than behave as independent resources.

This passes the first-layer naturalness test better than `sparse attention causes long generations on benchmark X`.

Both answers would matter:

- **substitutable:** architecture-level compute and token-level compute lie on a meaningful common resource frontier;
- **non-substitutable:** some computation must occur inside a step / latent state and cannot be recovered by more verbalized steps, changing how test-time scaling should be understood.

---

# 2. Theoretical ancestry: extra tokens already have a computational meaning

Li, Liu, Zhou & Ma, ICLR 2024, *Chain of Thought Empowers Transformers to Solve Inherently Serial Problems*, establish an explicit theoretical reason that additional generated steps can increase computational expressivity.

For constant-depth transformers, CoT steps provide a route to computations that cannot be performed in a single shallow parallel pass under their assumptions. Their experiments further show larger CoT gains on tasks designed to require serial computation, especially for low-depth transformers.

Source:
- https://proceedings.iclr.cc/paper_files/paper/2024/hash/3309b4112c9f04a993f2bbdd0274bba1-Abstract-Conference.html

Thus the idea that tokens can function as **additional serial compute** is already a first-class scientific object, not a new interpretation supplied by the Lil anomaly.

---

# 3. Direct modern owner 1: model scale versus test-time compute

Snell, Lee, Xu & Kumar (2024), *Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters*, explicitly study the tradeoff between stronger pretrained models and inference-time computation.

In FLOPs-matched comparisons, compute-optimal test-time scaling with a smaller model can outperform a model roughly 14× larger on some problem regimes, while the preferred allocation depends strongly on problem difficulty.

Source:
- https://arxiv.org/abs/2408.03314

This already owns the high-level question:

> **Should a fixed compute budget buy a stronger base model or more inference-time computation?**

A project whose identity is only `smaller model thinks longer vs larger model thinks shorter` therefore has a direct owner/program.

---

# 4. Direct modern owner 2: latent depth versus verbalized token compute

Geiping et al., NeurIPS 2025, *Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach*, make the contrast even closer.

Their recurrent-depth model increases test-time compute by repeatedly applying a latent recurrent block **before emitting the next token**, explicitly contrasting this with scaling compute through longer textual chains of thought.

The paper shows substantial performance improvements from recurrent depth, including compute levels comparable to much larger materialized fixed-depth models.

Source:
- https://proceedings.neurips.cc/paper_files/paper/2025/hash/3b01972cf31e6fa0fe29e4b8b5c2a0a1-Abstract-Conference.html

Therefore the axes

- `more computation inside/around a token`, and
- `more generated reasoning tokens`

are already an active architecture/test-time-compute design space.

---

# 5. Why Lil does NOT establish adaptive compensation

A key inferential correction is necessary.

Lil shows:

> sparse attention → information loss → longer sequences → possibly larger end-to-end complexity.

That does **not** by itself show:

> the model recognizes lost internal compute and adaptively converts it into useful external reasoning steps.

The longer sequence may instead be:

- repetition;
- failed termination;
- degraded state tracking;
- recovery attempts with low information gain;
- generic decoding instability.

Indeed, Lil's mitigation is early stopping when information loss exceeds information gain, which is more consistent with pathological expansion than with a clean resource-rational compensation law.

So the attractive story

> `internal compute removed → model strategically thinks longer`

cannot be taken as the mother phenomenon without a new, independently established effect.

Doing so would be **betting on a phenomenon** and narrating it afterward—the exact search behavior the repository bans.

---

# 6. Why no new candidate survives

The strongest possible first-layer question is scientifically good:

> **Can missing internal computation be replaced by more generated computation?**

But current literature already owns the core axes:

1. CoT as serial computational depth — ICLR 2024;
2. stronger model versus more inference compute — Snell et al.;
3. latent recurrent depth versus token-based reasoning — NeurIPS 2025;
4. per-step efficiency interventions changing output length/end-to-end cost — Findings ACL 2026 Lil;
5. extensive 2025–2026 work on compute-optimal / thinking-optimal test-time scaling.

The obvious residuals therefore collapse into existing program cells:

- depth × CoT length factorial;
- attention sparsity × reasoning length;
- smaller/deeper model × token budget;
- equal-FLOPs latent versus verbalized reasoning;
- task serial-depth × resource allocation;
- `does the model compensate intentionally?` via another probe/intervention.

A cleaner SAME-COMPUTE experiment could still be useful science inside this program, but we currently lack a new first-layer inference that makes it a Main-level paper identity.

### Verdict

**NO L42. NO PILOT.**

Generic `internal compute ↔ external token compute` is **CLOSED AS A NEW TOPIC GENERATOR** under current ownership.

---

# 7. Standing-state update to IP04

This wall nevertheless produces a durable update for the repository's resource-constraint problem.

IP04 should remember:

> **Resource interventions can move cost between computational axes. Measuring the constrained resource alone can be scientifically misleading.**

For autoregressive models in particular, at least three budgets must be distinguished:

- computation per token / per step;
- number of sequential generation steps;
- total end-to-end compute / latency.

An intervention can improve the first while worsening the second enough to lose on the third.

That is not itself a paper candidate. It is a constraint on future resource-rational questions:

> before claiming that restriction X induces a useful new representation/algorithm, audit whether the system merely shifted cost into another resource dimension.

---

# 8. Anti-resurrection

Do not regenerate, absent genuinely new pressure:

- `sparse attention makes reasoning longer` as a standalone scientific paper;
- `smaller model + more CoT vs larger model + less CoT`;
- `depth vs reasoning tokens` factorial as the contribution;
- `latent reasoning vs verbal reasoning` benchmark comparison;
- equal-FLOPs architecture/model-size/token-budget sweeps without a new scientific quantity;
- mechanistic probing of Lil merely to distinguish repetition from recovery;
- an anthropomorphic `compensation` story without evidence that additional tokens restore the lost computation.

---

# 9. Searcher lesson

The wall is a useful example of the new doctrine working correctly.

The initial anomaly is excellent:

> making each step cheaper can make the total computation more expensive.

But lifting an anomaly to a broader scientific question is not automatically novelty.

Here, the broader question lands inside a mature theory/architecture program on **where test-time computation is performed**.

The correct action is therefore:

> preserve the anomaly as evidence bearing on IP04, update the resource accounting, and switch scientific object.

not:

> narrow until a free depth × token × sparsity cell appears.
