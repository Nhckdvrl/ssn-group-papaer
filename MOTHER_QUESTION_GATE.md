# Mother-Question Value Gate

**Added:** 2026-09-17 after K194 / L36.  
**Applies before:** owner search, novelty audit, experiment design, pilot authorization, and serious compute.

This gate exists because a technically clean project can still be a bad research project if the parent question is not worth answering.

## 1. Mandatory question

Before discussing methods, mechanisms, datasets, checkpoints, or experiments, write the strongest plausible successful answer in one sentence and ask:

> **Why would a strong ACL / EMNLP / NAACL Main reader care about knowing this answer today?**

The answer must be scientific, not operational.

Passing reasons include at least one of:

- resolves a current, consequential model failure or limitation;
- overturns or sharply conditions a load-bearing scientific belief;
- explains a stable anomaly that current theory cannot account for;
- reveals a hidden trade-off or failure behind an apparent improvement;
- identifies a training/computational law that transfers beyond the original task or benchmark;
- changes how an important modern model behavior should be understood, diagnosed, or controlled;
- reconciles two strong results that genuinely conflict on the same quantity.

## 2. Default NO-GO shapes

Treat the following as low-pressure by default, even when novelty and experiments look clean:

- **old problem → modern model is better → explain why it got better**;
- a historical pathology that no longer materially limits current systems;
- explaining why a benchmark/challenge became easier without exposing a new modern failure, trade-off, or general law;
- a deeper mechanism for a phenomenon whose answer would not change current model understanding;
- a technically novel decomposition of an issue that readers no longer need solved;
- “nobody has explained X yet” when X itself is not important anymore;
- a beautiful causal experiment attached to a mother question that would still feel optional if the experiment did not exist.

The burden is on the candidate to show why the answer matters **independently of experiment elegance and sunk work**.

## 3. Counterfactual importance test

Ask four questions before a lead can become `SERIOUS`:

1. **If the strongest expected result were already known tomorrow, what belief or decision would change?**
2. **If the answer were the opposite, would the question still matter?**
3. **Can the importance be explained without naming our method, dataset, or surprising pilot result?**
4. **Would the question still be worth a paper if the old benchmark/problem name disappeared?**

If the answer to (1) is “we would understand an old issue better” and little else changes, default to `NO`.

## 4. Old-law / modern-regime exception

Revisiting an old law or challenge can still be strong, but only if the modern regime creates a **new scientific tension**, not merely a success story.

A candidate may survive when modern models:

- violate a law that is still used to reason about current systems;
- solve one visible problem by moving the bottleneck elsewhere;
- hide the old failure under a new failure mode;
- reveal that the old explanation was wrong in a way that matters beyond the historical task;
- expose a training-stage transition with a broadly consequential mechanistic interpretation.

A candidate should die when the only story is:

> old systems failed; modern systems mostly do not; we will explain the improvement.

## 5. Separation from novelty and feasibility

This gate is upstream of novelty, identification, and feasibility.

A project can be:

- novel but unimportant;
- well identified but unimportant;
- cheap but unimportant;
- mechanistically deep but attached to an unimportant parent question.

None of those should receive serious compute.

The correct order is:

> **mother-question value → scientific pressure → ownership/novelty → identification → successful-result inference → feasibility → compute**

Do not reverse this order.

## 6. L36 lesson

K194 / L36 accumulated valid work on uncertainty, beam search, termination, format-conditioned stopping, Base→SFT→DPO/RLVR lineages, and full-sequence mode-seeking stability.

The experimental programme became increasingly sophisticated, but the parent motivation remained too weak:

> explaining why a classical decoding pathology is less severe in modern systems.

The mistake was not insufficient rigor. It was allowing technical progress and interesting sub-results to postpone the more basic question:

> **Is this parent question important enough to deserve a paper at all?**

That check must now happen before serious literature expansion or compute.

## 7. Required rough-lead field

Every new rough lead must include, in plain language:

### Mother-question value

> **If we obtain the strongest plausible result, why does this matter now?**

Then choose one:

- `PASS — current scientific pressure is clear`
- `MAYBE — importance depends on <one explicit unresolved consequence>`
- `NO — technically open but not important enough`

A `NO` here ends the lead. Do not rescue it with a better mechanism, cleaner experiment, newer model, or broader evaluation.

---

**Hard rule:** A strong experiment does not make a weak question strong.
