# CT03 Final Postmortem — Counterfactual Credit for MoE Routing

**Final status:** ❌ **KILLED / CLOSED**  
**Original topic:** Counterfactual Credit for MoE Routing  
**Closure rule:** no further GPU experiments, no benchmark rescue, no new loss search, no second-model replication for this topic.  
**Canonical kill record:** `chasing trends/topics/FAILED_TOPICS.md` → `CT-KILL-20260922-1`.

This document is the final scientific archive for CT03. It separates what was
successfully established from what failed, explains why the Main-level method
story collapsed, and records what must not be resurrected under a new name.

---

## 1. Original research question

CT03 started from a real pressure in sparse MoE routing:

> Can we cheaply estimate the counterfactual utility of unexecuted experts and
> use that information to train a better pretrained router without changing
> ordinary sparse Top-K inference?

The intended paper chain was:

```
misrouting exists
    ↓
cheap counterfactual credit is faithful
    ↓
credit can supervise the router
    ↓
the router executes better routes
    ↓
generation / reasoning improves
```

The project ultimately failed at the middle of this chain:

```
good counterfactual signal  ≠  good router supervision  ≠  intended deployed action
```

The estimator survived. The policy-learning story did not.

---

## 2. What was genuinely established

### 2.1 Counterfactual route utility is real and measurable

E01/E02 established that the local first-order estimator predicts exact
counterfactual route utility substantially better than router-score and random
baselines.

Key surviving facts:

- OLMoE E01: median Spearman `rho = 0.698` overall for the shared-gradient
  estimator; router score carried approximately no useful ranking signal.
- Qwen3-30B-A3B replication survived renormalised routing.
- Exact utility was close to a scalar potential at the calibrated deeper layers
  (reported `R² ≈ .87/.97/.999` across the tested depth ladder).
- The shallow-layer limitation was mainly an estimation limitation rather than
  an interaction/expressiveness failure.

These results remain reusable scientific assets.

### 2.2 The estimator is useful as a screening device

E08 evaluated the proxy in the parent EPO's full Gumbel top-K action space rather
than only one-swap routes.

At `m = 2`, retained oracle gain was:

- L36: `R_2 = 0.938`
- L44: `R_2 = 0.976`

Thus the proxy can remove most exact reruns while preserving most of the best
route gain inside the sampled candidate set.

This result also stands independently of the failed training method.

### 2.3 One-off rerouting is decision-local, not persistent state control

FG0 showed that a beneficial one-off route intervention can move the immediate
next-token distribution while the effect dissipates rapidly on a shared
continuation unless the emitted token changes.

This result matters because it rules out the naive story that a single local
reroute creates a long-lived latent-state improvement.

---

## 3. Where the method story first failed

### 3.1 Binary pairwise distillation did not learn calibrated utility

C0 / E03 showed that a binary pairwise objective admitted a shortcut:

- the training loss could be fitted without learning a utility-aligned router;
- shuffled labels could fit suspiciously well;
- the original moving-support route-regret metric was invalid;
- fixed-support re-evaluation still showed approximately zero utility alignment;
- apparent mean improvements were strongly tail-driven.

This was the first warning that recovering good counterfactual information and
turning it into router logits are different scientific problems.

### 3.2 CPD did not establish a credit-specific gain

CPD was introduced to remove the binary-margin shortcut by distilling a dense,
mass-preserving expert potential with a matched KL budget.

The headline free-generation gain over base was real, but attribution failed:

- CPD vs shuffled: not significant;
- CPD vs ordinary Router-CE: not significant;
- learned logit correction vs exact counterfactual utility: no measurable
  alignment (`A_delta`, `A_z` indistinguishable from zero);
- fixed-support route quality was not better than ordinary router-only CE.

Therefore the surviving explanation was generic router-only adaptation, not the
counterfactual content CT03 claimed as its contribution.

This alone was sufficient to kill CT03 as a Main-level method paper.

---

## 4. Why the later EPO reopening also failed to rescue the topic

After the original kill, E08–E10 tested a narrow reopening path:

> If the estimator is an excellent screening device, can it cheaply accelerate
> the parent paper's own exact EPO mechanism at a non-final layer?

This reopening required exact EPO itself to be a useful action mechanism.

### 4.1 Exact EPO moved route-value metrics but not generation quality

At L47 (the parent's final-router setting in Qwen3-30B-A3B), exact EPO produced a
large held-out route-value gain and changed essentially every completion, but the
free-generation accuracy change was statistically indistinguishable from zero.

At L36, where exact route evaluation requires a genuine suffix replay:

- held-out route value improved to approximately `+0.375`;
- 99.2% of completions changed;
- free-generation accuracy changed by exactly `+0.000` on the locked FG0 set.

Thus exact counterfactual supervision could strongly move intermediate routing
metrics without producing evidence of downstream quality improvement.

The screening result from E08 therefore became an efficiency result for an
action mechanism with no demonstrated quality gain, not a new Main-level method.

---

## 5. Final mechanism diagnosis: preference success is not route adoption

The final frozen-target experiments explain the central failure more directly.

The same target routes `r+` were frozen. The linear gate was trainable. Only
the supervision objective changed.

### Parent-style preference objective, frozen targets

After prolonged probing:

- preference accuracy reached `0.947`;
- exact adoption remained `0.000`;
- overlap with `r+` fell from `3.77/8` to approximately `1.05/8`;
- approximately `7.71/8` executed experts changed.

This is not an optimisation failure in the ordinary sense: the stated
preference objective was nearly perfectly satisfied.

### Positive-only control

Removing the `r-` term did not solve the problem: target overlap still fell.

Therefore the failure is not reducible to "the model only learns to suppress
`r-`".

### Capacity / generalisation controls

A separate target-directed rank control, using the same `r+` supervision and
the same linear gate, moved overlap from `3.77` to `5.45`, so the gate is not
simply incapable of moving toward the targets.

Train and test curves for the preference objective were also essentially
matched, ruling out a simple train/test generalisation explanation.

The rank control is **not** a solved method:

- exact adoption only reached `0.101`;
- its parameter drift was substantially larger;
- it is a diagnostic control, not a principled repair.

### Direct executed-slot decomposition

The strongest final measurement decomposed each executed Top-8 slot after
preference training by membership in the frozen `r+` and `r-` sets:

| gate | only r+ | only r- | both | neither |
|---|---:|---:|---:|---:|
| pretrained `W0` | 0.000 | 0.528 | 0.472 | 0.000 |
| parent preference, frozen-target probe | 0.081 | 0.064 | 0.047 | **0.808** |

After training, **80.8% of actually executed experts belonged to neither
`r+` nor `r-`**.

This directly measures the mechanism that the earlier overlap metric only
suggested: the router can satisfy the pairwise route preference while moving the
deployed Top-K set into a third region of expert space.

---

## 6. Structural reason the mismatch is possible

For equal-cardinality routes and router logits `z_e`:

```
log pi(r+|x) - log pi(r-|x)
  = sum_{e in r+} z_e - sum_{e in r-} z_e
```

The shared softmax normaliser cancels, and experts common to both routes cancel.

Thus the pairwise margin directly constrains only the experts in the symmetric
difference between the two compared routes.

The deployed action, however, is:

```
TopK_e z_e
```

and adoption of `r+` requires its members to beat every competing outside
expert, not merely for `r+` to score above one particular `r-`.

The 80.8% "neither" result is therefore not random drift; it is an empirical
realisation of a degree of freedom left by the route-preference surrogate.

However, this observation is **not itself a new standalone topic**. In its more
general form it overlaps mature top-k calibration / consistency and
preference-ranking literature. The project should not be revived by turning
this diagnosis into an open-ended search over alternative ranking losses.

---

## 7. Why CT03 is closed rather than repaired

CT03 is not closed because one hyperparameter failed.

It is closed because every natural version of the intended information-to-action
chain was tested and the central contribution did not survive:

1. **Counterfactual signal exists.**
2. **The cheap estimator recovers it.**
3. **The signal can be screened efficiently.**
4. **Two direct distillation formulations failed to establish a
   counterfactual-specific router improvement.**
5. **The parent-style exact preference mechanism can improve route metrics
   without improving downstream generation.**
6. **Frozen-target probes show that the preference objective can be almost
   perfectly satisfied while the deployed Top-K route moves away from the
   preferred route.**

At this point, continuing would no longer be "testing CT03". It would be a new
research program on structured / Top-K router objectives.

That program is not authorised by this project and must not be created as a
rescue branch.

---

## 8. What must NOT be done next

Do not reopen CT03 by:

- adding a nonlinear / MLP router;
- adding more counterfactual data;
- trying more beta / learning-rate / epoch combinations;
- adding second-order credit;
- moving to on-policy "actionable" credit;
- running another MoE family solely to rescue the claim;
- running AIME/HMMT pass@K to search for a benchmark delta;
- searching over hinge / listwise / KPO-style / Plackett-Luce / soft-top-k /
  structured losses until adoption improves;
- renaming the 80.8% outside-route observation into a new CT04/CT05 without a
  separate question-formation and novelty audit.

These are method-search branches around a dead original causal chain.

---

## 9. What remains reusable

The following artifacts are valid and may be reused if another independently
motivated project needs them:

- exact counterfactual route replay infrastructure;
- proxy credit estimator and its calibration data;
- cross-family estimator validation;
- depth-dependent fidelity analysis;
- one-swap vs full-route action-space audit;
- E08 screening curve;
- cached L47 / suffix-replay L36 EPO infrastructure;
- fixed-support evaluation discipline;
- per-problem bootstrap / median / win-rate reporting;
- parent EPO spec verification;
- the frozen-target objective/action mismatch diagnostics.

Reuse does **not** constitute reopening CT03.

---

## 10. Process lesson

The expensive mistake was not that the estimator was weak. It was the opposite:
the estimator worked unusually well, which encouraged the project to assume that
a method would naturally grow out of it.

The missing question should have been asked before substantial method work:

> If the information signal were perfect, is there an obvious, natural,
> deployable action mechanism that is aligned with the actual decision rule?

A successful diagnostic / estimator is not evidence that such an action
mechanism exists.

Future method-first topic selection must separately audit:

```
measurement fidelity
        versus
information -> action identifiability
```

before a pilot is promoted into a full method program.

A second process lesson is equally important:

> Once the next experiment is repeatedly framed as "try another mechanism; if it
> works, the topic lives", the project has become rescue-by-outcome.

At that point, stop and re-evaluate the mother question rather than adding
another gate.

---

## 11. Final one-sentence verdict

> **CT03 successfully learned how to identify better counterfactual routes, but
> failed to establish a principled path from that information to a deployed
> router that executes those routes and improves downstream behavior; the final
> experiments show that route-preference success can be strongly decoupled from
> actual Top-K route adoption.**

**No further experiments are authorised under CT03.**
