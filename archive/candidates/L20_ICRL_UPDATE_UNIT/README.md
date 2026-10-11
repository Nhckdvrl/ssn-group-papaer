# L20 — What Does an LLM Learn From a Rewarded Trajectory?

**Status:** **NO-GO / ARCHIVED**  
**Date:** 2026-09-12  
**Target considered:** ACL / EMNLP / NAACL Main

## Research question

> When a fixed pretrained LLM sees a multi-step attempt followed by scalar reward, does its next policy preferentially update the actions that causally earned the outcome, or mainly treat the whole rewarded trajectory as a good/bad demonstration?

## Why we cannot do it

The question is natural, but the surviving paper identity is not strong enough relative to its experimental burden.

1. **The novelty remainder is too narrow.** ICLR 2026 *Reward Is Enough* already establishes fixed-weight improvement from response/reward history; NeurIPS 2025 self-generated-trajectory work establishes whole-trajectory in-context reuse; 2026 credit-assignment work directly studies whether trajectory steps causally deserve credit. Measuring future policy shift rather than retrospective step score is a real estimand difference, but the strongest reviewer compression remains “credit assignment / trajectory reuse, measured through ICRL prompting.”

2. **The successful-result test is asymmetric.** The genuinely strong result is that scalar terminal reward induces nontrivial local causal credit in an ordinary pretrained LLM. If instead actions are broadly reused according to whole-trajectory success/failure, that is compatible with coarse trajectory-return learning or reward-conditioned imitation and is not by itself a strong Main-level correction to existing ICRL claims. If reward removal preserves the effect, the reward-mediated story collapses. The route therefore again depends too heavily on one interesting positive phenomenon.

3. **Independent local-quality gold is expensive and awkward.** In realistic agent environments, local causal contribution requires executed replay / policy-supported counterfactuals. Recent replay auditing shows that causal contribution is sparse and sometimes not measurable for a substantial fraction of decision points, with measurability itself depending on the policy. A cheap symbolic domain such as Game of 24 could provide exact local labels, but then the result risks becoming a puzzle-specific context-conditioning result and would still need a second realistic sequential domain for the intended general claim.

4. **Full-study burden is poor relative to expected contribution.** Even without gradient training, a credible study would require reproducing the mother ICRL effect, constructing outcome × local-quality conflicts, counterfactual replay, matched pre/post policy measurements, reward/no-reward/dense-reward controls, and enough independent states across more than one model/domain. The expensive part is not policy optimization; it is obtaining and validating the causal units needed to support the claim.

5. **Venue identity is not ideal for the target.** The strongest version is fundamentally an ICRL / RL credit-assignment paper. It could be relevant to NLP agents, but it is less naturally centered on an ACL/EMNLP/NAACL scientific object than cleaner language, measurement, or LLM-mechanism candidates.

## Decision

**KILL L20 CURRENT FORM. Do not pilot.**

Do not rescue it by shrinking to a cheap Game-of-24-only experiment: that changes the paper identity and weakens the intended claim. Any future low-cost symbolic reformulation must return to topic selection as a new candidate and pass a fresh novelty / successful-result / Main-level audit.
