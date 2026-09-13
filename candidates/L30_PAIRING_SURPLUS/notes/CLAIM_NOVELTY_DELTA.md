# L30 — Claim Novelty Delta (post-E01)

Written per `RESEARCH_EXECUTION.md` §8. E01's result moved the paper identity, so
the previous authorization has expired. This is a **selection request, not an
execution plan**; nothing below has been run.

---

## 1. Old statement

> Holding the prompt pool and response pool fixed, what is the marginal causal
> value of preserving the correct `X↔Y` correspondence? (`Pairing Surplus`)

## 2. New statement

> Post-training damage comes from **contradicted** supervision, not from
> **missing** supervision. A pretrained model's instruction→response map
> survives being ignored but not being actively decorrelated — and the size of
> that damage is the quantity worth explaining.

## 3. Evidence that motivated the change

E01, 12 matched runs, 3 seeds, IFEval 541 prompts (`notes/E01_REPORT.md`):

| contrast | pp | 95% CI |
|---|---|---|
| `Delta_corr` P − S | **+14.97** | [+10.66, +19.29] |
| `Delta_wrong` D_mask − S | **+13.12** | [+8.81, +17.44] |
| `Delta_pair` P − D_mask | +1.85 | [−1.79, +5.42] |

Two facts did the work:

1. **`Delta_pair` is unresolvable here and cannot be rescued.** Of its 7.58 pp
   interval width only ~1.6 pp is training-seed variance; ~6 pp is the
   541-prompt IFEval sample. More seeds, bigger models and longer training all
   hit the same wall. The original estimand is not measurable in any affordable
   deterministic-evaluation regime.

2. **The asymmetry is not a small number.** S collapses to 6–11 distinct
   responses over 541 prompts in *every* seed (median 62–241 chars), while
   D_mask — equally correspondence-free — keeps 537–539 distinct responses at
   441–585 chars. A ~50x difference in output diversity needs no confidence
   interval.

So the quantity we owned is unmeasurable, and the quantity that is measurable is
a different one: not what correct pairing *teaches*, but what wrong pairing
*destroys*, with "no pairing at all" as the control that makes it non-trivial.

## 4. Closest owners — and why they do not own this

Every prior "the input–output mapping matters less than you think" result
concerns **demonstrations**, not the supervised pair:

| work | what is corrupted | finding |
|---|---|---|
| Min et al. 2022 | labels in ICL demonstrations | mapping largely unimportant |
| Kung & Peng, ACL 2023 | *positive examples inside the training prompt* (drawn from NatInst-V2 negative examples); **the supervised instance stays correctly paired** | mapping unimportant at training time, important at ICL test time |
| Hewitt et al. 2024; An et al. 2025 | instruction **removed** entirely | much instruction following survives |
| MAIN, FedDQC, Hindsight | pair *quality* / alignment scores | aligned pairs are better data |

Verified from the sources: Kung & Peng train T5-large on NatInst-V2 and corrupt
the in-prompt demonstration, never the supervised target. Hewitt et al.'s arms are
IT / response tuning / single-task tuning / a rule-based adapter; An et al.'s are
IT / RT. **Neither has a mismatched-pair arm.** None of these holds the prompt and
response marginals fixed and decorrelates **the supervised pair itself**, and none
contrasts *wrong* against *absent* correspondence.

A useful incidental finding: the two mother papers do not even implement the same
control. Hewitt et al. replace the instruction string with the empty string,
keeping the `<|user|>` scaffolding; An et al. drop the user turn entirely. "RT" is
therefore not a well-defined correspondence-free condition, which is precisely the
gap D_mask was built to close — and E01 shows the two differ by +1.91 pp
[-1.66, +5.42] against a budget-matched control.

## 5. Strongest reviewer compression

> "You shuffled the training data and the model got worse. Garbage in, garbage
> out. MAIN and FedDQC already said alignment matters."

## 6. Surviving contribution

The compression does not survive the **D_mask arm**. Garbage-in-garbage-out
predicts that removing the information hurts too; it does not predict that
removing it is nearly free (−1.85 pp, no collapse) while contradicting it is
catastrophic (−14.97 pp, total collapse). Those two arms have identical prompt
tokens, identical positions, identical loss-token counts and identical steps.
The claim is therefore about the **sign of the supervision's dependence
structure**, not about data quality.

It also makes a prediction the quality framing does not: a dataset of *useless*
pairs should be far safer than a dataset of *actively mismatched* pairs at equal
size — the harm is not proportional to the good data displaced.

## 7. What would make it Main-level — the missing conditional law

The asymmetry alone is a phenotype. The paper needs **what sets the size of the
damage**, and there are two mechanisms with different predictions:

- **Structure-destruction:** the collapse is the erasure of specific pretrained
  `x→y` bindings. Then breaking correspondence on pairs the base model *already
  binds strongly* (high `NLL(y) − NLL(y|x)`, FedDQC's IRA-like quantity, not ours
  and not claimed as novelty) should hurt disproportionately.
- **Global policy shift:** the collapse is the model learning a blanket "the
  prompt does not predict the response" policy. Then damage depends only on the
  *fraction* of pairs broken, and is indifferent to which ones.

These are cleanly separable by an **intervention**, which is what the original
README asked C2 to be: at a fixed breaking budget, break high-association versus
low-association pairs, matched on response NLL, response length, prompt length
and source task. This is not the item-level correlation the README warned
against.

## 8. New successful-result inference

If structure-destruction wins: *post-training erases pretrained conditional
structure in proportion to how strongly that structure was held* — which says
alignment quality matters most exactly where the model needed it least, and
reverses the MAIN/FedDQC intuition that high-alignment pairs are the valuable
ones.

If policy-shift wins: *a small amount of decorrelated supervision can switch off
prompt conditioning globally* — a threshold/contagion effect, and the practical
consequence is that a few percent of mismatched data is disproportionately
dangerous.

Either outcome is a statement about what post-training does to pretrained
structure, which is the repository's stated search target. Neither requires the
unmeasurable `Delta_pair`.

## 9. Feasibility and resolution

This is the decisive argument for the pivot: the load-bearing effect is ~13 pp
instead of ~2 pp, i.e. roughly an order of magnitude above the noise floor that
killed the original estimand. The same 541-prompt IFEval that cannot resolve
`Delta_pair` resolves `Delta_wrong` with a CI that excludes zero by 8.8 pp.

Cost, reusing all E01 infrastructure unchanged:

- a dose–response pass to find where damage is *partial* rather than saturated
  (breaking fraction α ∈ {0, 10, 25, 50, 100}%), ~5 runs, ~5 h wall on 4 GPUs;
- the stratified intervention at the sensitive α, high- vs low-association with
  matched difficulty, 2 conditions x 3 seeds, ~6 h wall.

The base-model association scores are being computed now purely as a feasibility
check for §7 (is the distribution wide enough to stratify, and can high/low
halves be matched on length and response NLL?).

## 10. Risks that could still kill this

- **Floor effects.** If any nonzero α collapses the model, the stratified
  comparison has no dynamic range. The dose–response pass exists to find that out
  cheaply, and a saturated dose–response is itself a kill condition.
- **Association is confounded with difficulty.** High-IRA pairs may simply be
  short/formulaic. If matching on response NLL, length and source cannot separate
  them, the intervention is not identified and the route stops.
- **The asymmetry may be Alpaca-specific.** One dataset and one 2B model.
  Breadth would be required before any Main claim, though not before selection.
- **Scope drift.** The practical reading ("filter mismatched data") is explicitly
  out of scope per the candidate's §10 guard. The claim must stay a causal
  statement about pretrained structure, not a data-curation method.

## 11. Requested verdict

`PASS` to a **bounded C2 pilot** (dose–response, then one stratified
intervention), or `NO-GO` if the asymmetry is judged too close to
garbage-in-garbage-out to survive review even with the D_mask control.

Recommendation: **PASS**, conditional on the dose–response showing a partial-damage
regime. The pivot keeps the original scientific family, discards the
unmeasurable quantity, and moves the load-bearing effect an order of magnitude
above the noise floor — which is exactly the failure E01 was authorized to detect
and has now detected.
