# Pressure Seed — Access-Conditioned Learning Operator

**Date:** 2026-09-14  
**Status:** **UNREGISTERED PRESSURE SEED — NOT A CANDIDATE — NO EXPERIMENT AUTHORIZED**  
**Origin:** post-mortem of killed candidate `L34_PROSPECTIVE_ENCODING`

## Pressure

Jiang et al. (ACL 2024) motivate pre-instruction tuning partly with the idea that prior QA/access experience changes how later document knowledge is acquired. L34 tried to identify that explanation through a pre-access × query-family × NEW/OLD interaction. The attempt failed at the manipulation level, and the later Selection audit showed that the original estimand was not encoding-specific.

The broader unresolved pressure is narrower and more causal:

> **Does learning an access function change the learning operator by which a later, identical raw-text update makes new knowledge usable?**

This is not a continuation of L34 and must not inherit its authorization.

## Why L34 cannot simply be repaired

1. Its A/B families were different relations/attributes rather than different access functions over the same underlying fact.
2. `NEW - OLD` does not identify encoding locus: a readout/answer prior can affect recently learned knowledge more strongly than older knowledge.
3. A true PIT order control (`QA -> DOC` vs `DOC -> QA`) is necessary but not sufficient, because neural training order is generically non-commutative.
4. The first-stage curriculum must be shown to install the intended access function rather than answer-format priors or relation-specific interference.

## Candidate-level quantity worth auditing

Do not test final QA preference first. Ask what the **same document update** changes.

For access view `q`:

```text
Delta_q(theta, doc) = L_q(theta) - L_q(U_doc(theta))
```

A possible future quantity is the difference in `Delta_A - Delta_B` after different prior access training, while the later document update is byte-identical.

This only becomes scientifically meaningful if A/B refer to the **same underlying fact** and the answer/output side is fully matched.

## Mandatory gates before any registration

1. **Same-fact access:** A/B are genuine alternative access functions/cues for one fact, not different attributes or answer types.
2. **Output matching:** answer tokens, answer distribution, length, format, and candidate space are matched across A/B.
3. **First-stage validity:** on a grounded third fact set, the prior curriculum demonstrably changes access behavior in the intended direction while target NEW facts remain unseen.
4. **Update-level identification:** the primary estimand is the change caused by the identical document update; final QA preference and NEW/OLD subtraction are secondary controls only.
5. **Order control:** if framed as PIT, compare matched `access -> document` and `document -> access` histories.
6. **Fresh ownership audit:** search PIT descendants, self-tuning/document internalization, curriculum/continual learning, gradient alignment/interference, factual-learning dynamics, and any work measuring query-conditioned update geometry.
7. **Reviewer-compression gate:** a successful result must establish more than relation-specific transfer or generic path dependence.

Failure of any gate means this remains a pressure seed and does not become an L-series candidate.

## Anti-resurrection

Do not call this `L34-R`, `L34-E02`, or a repaired prospective-encoding experiment. Do not reuse L34's relation partition or its `PROSPECTIVE = CROSSOVER(NEW) - CROSSOVER(OLD)` estimand as the decisive quantity.

A future project must earn a new identity from scratch.