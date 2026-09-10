# L12 Adversarial Main-Paper Audit

**Date:** 2026-09-10  
**Reference bar:** ACL/EMNLP/NAACL Main, with Outstanding/strong mechanistic papers as structural comparators

## Bottom Line

The paper now has a Main-scale narrative and evidence chain. Its strongest form is
not "reasoning traces affect answers" and not "reasoning models calculate EV."
It is:

> Reasoning-oriented computation reallocates causal decision control toward an
> evidence-bearing trajectory and its state, producing selective invariance to
> form rather than general insensitivity.

No new experiment is justified by this audit. The remaining risks are primarily
claim wording, chronology, and explanation in the manuscript. They are addressed
below and must remain visible during LaTeX conversion.

## Load-Bearing Reviewer Attacks

### R1. "This is just Mind the DH Gap plus activation patching."

**Severity:** critical if the paper opens with methods or layer results.  
**Why compression fails:** the parent owns behavioral invariance but not the causal
route. L12 independently crosses prompt and natural trajectory, follows the effect
into a text-free state, and then orthogonalizes form from evidence prospectively.
The selective-sensitivity result changes the interpretation of the parent
phenomenon.  
**Required manuscript action:** keep the E18 failure and E20 decomposition in the
abstract/introduction; never headline a layer or probe.

### R2. "Reasoning models are merely better at averaging 20 numbers."

**Severity:** high.  
**Why it is plausible:** empirical EV direction is arithmetic, and standard models
often fail to follow it.  
**Why it does not compress the paper:** E20 holds the exact payoff multiset fixed
across raw and summary forms; the same selective behavior appears with both forms.
E20-C then fixes the prompt while changing evidence carried by a natural trajectory,
and E21 transfers evidence through a donor state without donor text. The claim is
not a new arithmetic capability but a change in causal architecture that explains
when invariance appears and breaks.  
**Required manuscript action:** state this objection explicitly in Discussion.
Avoid universal claims beyond decisions with independently measurable evidence.

### R3. "Inserted trajectories are just long, recent prompts."

**Severity:** high.  
**Current answer:** the same donor strings are crossed with prompts and scored
under matched regimes; short arithmetic snippets fail to reproduce the effect;
terminal stripping removes explicit commitment; direction-specific residual-state
substitution transfers the choice without donor text.  
**Residual boundary:** text insertion is not a natural indirect effect.  
**Required manuscript action:** define `Delta_P` and `Delta_R` as interventional
control indices and pair every text claim with state evidence.

### R4. "The three model comparisons are not commensurate."

**Severity:** high.  
**Current answer:** they are deliberately complementary, not pooled as equivalent
treatments. OLMo provides common-base sibling association and checkpoint
persistence; Qwen fixes weights but changes native route/channel; Llama/DeepSeek
provides external replication only.  
**Required manuscript action:** include an identification table early. Use
"reasoning-regime-associated" for the shared computation and reserve causal
language for prompt/trajectory/state interventions.

### R5. "E20 is a post-hoc rescue after E18 failed."

**Severity:** high.  
**Current answer:** the exploratory E18 analysis only generated the hypothesis.
E20 froze new history IDs, form/evidence cells, metrics, selection, regimes, and
analysis before model scoring. The 137 problem identities come from previously
used CPC18 pools, so they must not be called heldout decisions.  
**Required manuscript action:** show the chronology exactly: E18 result ->
model-independent construct audit -> E20 freeze -> scoring. Say "previously
unscored histories/cells," never "previously unseen decisions."

### R6. "Selective sensitivity is an arbitrary difference of two metrics."

**Severity:** high.  
**Current answer:** report both components before their difference. Form sensitivity
is an absolute within-evidence contrast; evidence sensitivity is a signed within-
form contrast; both are averaged within order and base decision. The joint metric
encodes the account-discrimination prediction rather than replacing components.
The trajectory factorial and state donor factorial reproduce the same distinction
with different estimands.  
**Required manuscript action:** Figure 4 must show the two-dimensional sensitivity
plane, not only a selective-score bar.

### R7. "Invalid reasoning generations drive the result."

**Severity:** high for OLMo.  
**Current answer:** E20 has exact execution coverage and reports conditional choice
plus sharp assignment. Qwen and external component directions are robust. OLMo's
joint selective difference remains positive under sharp assignment, but its
form-only component does not.  
**Required manuscript action:** report OLMo Think validity (0.704) beside the main
table and phrase the OLMo form decrease as conditional; let the joint selective
contrast carry the unconditional claim.

### R8. "State substitution trivially overwrites the answer."

**Severity:** medium-high.  
**Current answer:** target/donor share decision and order while evidence direction
varies; both patch directions are used; early layers are null; the effect develops
into a sustained late profile; donor evidence and donor form are independently
crossed in E21.  
**Residual boundary:** causal sufficiency under substitution is not complete
natural mediation.  
**Required manuscript action:** emphasize directional factorial content and the
early-to-late profile, not flip rate or a single final layer.

### R9. "The E21 subset is selected on successful reasoning."

**Severity:** medium.  
**Current answer:** eligibility requires valid natural traces that follow both
evidence directions, because direction-specific donor states otherwise do not
exist. Selection is blind to states, margins, layers, and patch results and is
stratified over evidence strength.  
**Required manuscript action:** make the conditional population explicit. E19's
48-decision state breadth supplies the broader carrier result; E21 identifies the
carrier's content within eligible trajectories.

### R10. "This is one narrow risky-choice domain."

**Severity:** medium.  
**Current answer:** the domain is a strength for identification: form can be made
exactly information-equivalent, evidence direction has independent gold, and real
human histories avoid an artificial benchmark. Breadth comes from 36 controlled
and 195 natural decision units, not from many loosely matched tasks.  
**Required manuscript action:** do not claim universal reasoning architecture.
Explain why a clean domain is necessary for the mechanism question and state
cross-domain generalization as future work.

## Main-Level Depth Check

| Comparator | Its progression | L12 progression | Audit |
|---|---|---|---|
| *Mind the (DH) Gap!* | broad phenomenon, humans, rational baseline | parent phenomenon -> causal explanation | L12 should not compete on raw model count |
| *Racing Thoughts* | hypothesis -> correlation -> causality -> intervention | erasure constraint -> trajectory process -> state causality -> construct consequence | aligned |
| *The LLM Language Network* | localization -> causal ablation -> 18-model breadth | probe constraint -> state substitution -> three complementary axes | aligned, with narrower but more controlled breadth |
| *What Makes a Good Reasoning Chain?* | structure -> failure -> practical use | trajectory control -> heldout failure -> form/evidence reconceptualization | consequence is conceptual/evaluative, not a new method |
| *Persistent Latent Policy States* | dynamics -> state intervention -> tasks/scales -> inference-time use | decision content -> state intervention -> selective behavior/control | distinct identity; weaker scale breadth, stronger construct identification |

## Claim Budget

The paper should contain exactly three major claims:

1. Trajectories progressively construct and consolidate decisions.
2. Reasoning reallocates causal control toward trajectory/state.
3. The reallocation is selectively sensitive to evidence rather than form.

Checkpoint persistence, Qwen, DeepSeek, probes, layer profiles, history length,
and parser audits are supporting evidence. Promoting any of them into extra claims
would weaken the story.

## Decision

**GO to full paper drafting.** The audit does not reveal a missing experiment that
would deepen the central explanation more than it would expand scope. The next
high-value work is manuscript compression, figure/table integration, and an
independent citation/number audit.
