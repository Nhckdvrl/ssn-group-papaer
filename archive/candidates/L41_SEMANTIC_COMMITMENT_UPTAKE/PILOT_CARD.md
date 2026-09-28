# L41 — E01 Pilot Card

**Candidate:** L41 — Does Parameter Learning Respect Semantic Commitment?  
**Authorization:** `E01 ONLY`  
**Primary substrate:** two-way implicatives `manage / fail x polarity`

## Locked scientific sentence

> **After a model has demonstrated that it correctly understands a sentence's implicative meaning in context, does training on that sentence change its later neutral belief about the embedded event according to the sentence's semantic commitment, rather than mere mention or local negation?**

---

# 1. E01 has two sealed stages

## E01-A — instrument construction

May inspect only:

- in-context implicative understanding;
- direct assertion/direct denial factual uptake;
- baseline neutral-query behavior;
- tokenization/surface balance;
- training loss/capability sanity;
- variance estimates that do **not** use the critical `manage/fail` post-training interaction.

May tune:

- one fixed model checkpoint/revision;
- learning rate / optimizer;
- exposure count;
- generic-data mix if needed;
- micro-document shell;
- neutral evaluation prompt family;
- confirmation sample size if the pre-declared variance rule requires it.

Forbidden during E01-A:

- looking at post-training `manage/fail x polarity` cell differences;
- selecting a verb pair by whichever gives an effect;
- selecting model family by checkerboard strength;
- choosing query wording by checkerboard strength.

## E01-B — untouched confirmation

After E01-A, freeze the complete contract and generate fresh proposition identities. No critical outcome may influence any design choice.

If E01-A choices have ever been informed by the critical checkerboard, E01-B must use fresh model runs and fresh proposition identities after a new freeze.

---

# 2. Primary model / training regime

Use **one open pretrained/base causal LM in the 4B–8B range** that is already available in the local training stack. Freeze the exact model ID, revision/hash, tokenizer, precision, optimizer and training code before E01-B.

Preference: ordinary causal-LM continued training / document-style finetuning rather than factuality-label supervision. The scientific object is the ordinary language-to-parameter update.

Do not switch to another model after seeing a null or wrong-sign E01-B result.

If the chosen model fails the pre-training semantic-understanding gate or direct signed-uptake gate, report **instrument failure**. Do not model-shop inside E01.

---

# 3. Novel proposition generator

Use invented entities/events with negligible prior factual support.

Schematic proposition:

```text
p_i = "Neris entered Chamber 47."
```

Critical training realizations:

```text
M+ : Neris managed to enter Chamber 47.
M- : Neris did not manage to enter Chamber 47.
F+ : Neris failed to enter Chamber 47.
F- : Neris did not fail to enter Chamber 47.
```

Semantic gold:

```text
M+ =>  p
M- => ~p
F+ => ~p
F- =>  p
```

Use a generator that creates many proposition identities while keeping the complement event simple, non-modal, non-negated, and semantically plausible.

Do not use events for which `manage` or `fail` is pragmatically bizarre. Do not select events after seeing learning outcomes.

---

# 4. Surface / tokenization balance

Before confirmation, audit:

- number of complement mentions;
- position of the proposition-bearing tokens;
- document length;
- number of training tokens contributing loss;
- matrix-verb tokenization;
- negation tokenization;
- entity/event tokenization;
- exposure count;
- document-shell frequency.

The factorial interaction already cancels many fixed verb/polarity effects, but gross arm imbalance still invalidates the experiment.

Use the same neutral fillers/micro-document shells across arms via counterbalancing. Surrounding text must never separately state whether `p` occurred.

---

# 5. Mandatory semantic-understanding gate

Before using a construction as training evidence, test the **base model in context**.

For fresh development propositions, provide one of the four critical sentences and ask neutrally whether the embedded event occurred.

Required interpretation:

```text
M+ -> Yes
M- -> No
F+ -> No
F- -> Yes
```

Freeze the evaluation prompt family before E01-B.

Minimum gate:

- overall semantic accuracy >= 90%;
- no critical cell < 85%;
- predicted checkerboard visible in mean Yes-vs-No log-odds, not only final decoded labels.

If the gate fails, **STOP / instrument failure**. A post-training result is not interpretable as a learning-vs-understanding dissociation.

---

# 6. Direct signed-uptake control

On separate development proposition identities, calibrate training using:

```text
A+ : Neris entered Chamber 47.
A- : Neris did not enter Chamber 47.
```

After the context is removed, query neutrally:

```text
Did Neris enter Chamber 47?  Yes / No
```

For proposition `p`, define neutral belief log-odds:

```text
B(p) = log P(Yes | q_p) - log P(No | q_p)
```

and uptake:

```text
U = B_after - B_before
```

Direct-control contrast:

```text
D = mean(U_A+) - mean(U_A-)
```

E01-A may tune exposure/training budget until the **direct** control is resolvable.

Frozen minimum before E01-B:

- `D >= 1.0` log-odds;
- paired/proposition bootstrap 95% CI for `D` excludes 0;
- capability / generic LM sanity does not show catastrophic collapse.

If this cannot be achieved under the bounded compute budget, **STOP / instrument failure**.

Do not inspect critical implicative uptake while tuning this control.

---

# 7. Confirmation randomization

Default E01-B design:

- **256 fresh proposition identities**;
- 4 Latin-square assignments;
- 3 independent training-order seeds per assignment;
- total: 12 bounded finetuning runs from the same frozen base checkpoint.

Across the four Latin-square assignments, every proposition identity appears exactly once in every critical condition:

```text
M+ / M- / F+ / F-
```

within independent resets from the same base checkpoint.

This controls proposition-specific learnability and prior plausibility without putting contradictory versions of the same proposition into one run.

Use several frozen neutral query paraphrases per proposition if desired, but average them **within proposition**. Query paraphrases are not independent observations.

Primary independent unit: **proposition identity**.  
Training runs/seeds are blocks/random factors.  
Documents, repetitions, and query paraphrases are not independent units.

---

# 8. Primary estimand

For verb `v`, polarity `s`, proposition `p`:

```text
U(v,s,p) = B_after(v,s,p) - B_before(p)
```

Primary checkerboard interaction:

```text
I = [mean U(M,+) - mean U(M,-)]
    - [mean U(F,+) - mean U(F,-)]
```

Semantic-commitment prediction:

```text
U(M,+) > U(M,-)
U(F,+) < U(F,-)
I > 0
```

Also report all four means and both within-verb polarity contrasts. A significant `I` generated by one pathological cell does not count as a clean checkerboard.

Secondary normalized quantity:

```text
F_sem = I / (2D)
```

where `D` is the direct assertion-vs-denial contrast from a matched control run.

`F_sem = 1` corresponds to an implicative checkerboard as strong as direct positive-vs-negative factual training under the simple symmetric idealization.

Do not make probe accuracy or hidden-state geometry primary.

---

# 9. Resolution / MDE rule

With 256 paired proposition identities, an idealized proposition-level SD of the checkerboard contribution of:

- 2.0 log-odds gives approximate 80%-power MDE ~0.35 log-odds;
- 3.0 log-odds gives approximate 80%-power MDE ~0.53 log-odds.

These are planning approximations, not observed variance claims.

During E01-A, estimate neutral-belief measurement variance and direct-control variance without computing the critical interaction.

Rules:

1. confirmation N may be increased before E01-B if projected MDE is >0.5 log-odds;
2. confirmation N may **not** be reduced below 256 because the dev variance looks favorable;
3. freeze N before any critical uptake results are inspected;
4. report seed-blocked / proposition-paired uncertainty, not pseudo-replication over documents or prompts.

---

# 10. Primary decision table

| E01-B observation | scientific interpretation | decision |
|---|---|---|
| clean predicted checkerboard; both within-verb reversals; direct control passes | parameter learning respects implicative semantic commitment in this regime | **PASS E01 / develop E02** |
| all/most cells push `p` similarly; `I ~= 0`; forward semantics gate passed | mention/co-occurrence dominates factual uptake | **PASS E01 / scientifically important opposite answer** |
| negative polarity suppresses both verbs similarly; `I ~= 0`; forward semantics gate passed | local polarity/syntax gates uptake, not full semantic signature | **PASS E01 / scientifically important opposite answer** |
| mixed lexical idiosyncrasy; interaction driven by one cell only | no general semantic-commitment inference | **HOLD / likely KILL unless independent preregistered pair was already included** |
| direct assertion/denial control fails | factual-learning instrument unresolved | **STOP / instrument failure** |
| in-context implicative semantics fails | semantic treatment not represented by base model | **STOP / instrument failure** |
| effect appears only after model/LR/query/verb shopping | phenomenon gambling | **KILL contaminated E01** |

A clean scientific opposite answer is allowed. E01 is not a positive-effect gate.

---

# 11. Anti-compression controls

## Against `Negation Neglect with another wording`

The paper lives or dies on the **difference-of-differences**. Report local-negation main effects separately, but do not call them the contribution.

## Against `mere token co-occurrence`

Every critical condition contains the same proposition-bearing complement. The question is whether its **signed** neutral uptake follows the implicative signature.

## Against `fail is just a negative word`

The key reversal includes `did not fail to p -> p`; a purely negative lexical prior does not predict the full verb x polarity checkerboard.

## Against `the model never understood the sentence`

Mandatory forward-semantics gate on the exact critical constructions.

## Against `negative facts are simply hard to learn`

Direct assertion/direct denial controls establish that the frozen training regime can create signed positive and negative factual uptake.

---

# 12. Hard anti-gambling rules

1. No changing `manage/fail` after E01-B starts.
2. No model-family shopping after seeing critical uptake.
3. No learning-rate or exposure-count search using the checkerboard.
4. No prompt selection using the checkerboard.
5. No dropping proposition identities because they weaken the effect unless excluded by a predeclared generator/semantic-gate rule independent of training outcome.
6. No seed selection.
7. No mechanism/probe/patching rescue after a non-semantic pattern.
8. No broad factivity/modality sweep until E01 is interpreted.
9. No claiming general `semantic understanding -> semantic learning` from one pair without later replication.
10. No treating generated documents or query paraphrases as independent samples.

---

# 13. Compute bound

E01 is intentionally small relative to the available local hardware.

The experiment should remain a short continued-pretraining/finetuning study on one 4B–8B checkpoint, with thousands rather than millions of critical micro-documents per run.

Planning cap for the full E01-B confirmation: **24 single-GPU RTX-PRO-6000-96GB-equivalent GPU-hours**. If the direct-control instrument requires orders of magnitude more data/compute, return to Selection rather than silently expanding the project.

The cap is a workload guardrail, not a scientific estimate of exact runtime.

---

# 14. Minimum E01 report

Return all of:

1. exact checkpoint/revision/tokenizer;
2. proposition generator contract and frozen exclusion rules;
3. tokenization/surface balance table;
4. in-context semantic-understanding table for all four cells;
5. direct assertion/denial uptake calibration and frozen `D`;
6. training hyperparameters and document counts;
7. Latin-square assignment manifest;
8. pre/post neutral belief cell means;
9. both within-verb polarity contrasts;
10. primary checkerboard interaction `I` with proposition-paired, seed-blocked uncertainty;
11. normalized `F_sem`;
12. per-seed results;
13. capability / generic-LM sanity check;
14. one preregistered decision from the table in §10.

Do not broaden the claim in the pilot report.