# L10 — Related Work and Paper-Level Novelty

**Candidate:** Success Teaches, Failure Doesn't?

---

## 1. Direct parent — ImplicitMemBench (ACL 2026)

Qin et al., **“ImplicitMemBench: Measuring Unconscious Behavioral Adaptation in Large Language Models”**:
- introduces implicit-memory evaluation;
- covers procedural memory, priming, and classical conditioning;
- uses Learning/Priming–Interfere–Test with first-attempt scoring;
- 300 items;
- 17 models;
- reports inhibition 17.6% vs preference 75.0%.

Source:
- https://aclanthology.org/2026.acl-long.1301/

What it owns:
- implicit behavioral adaptation benchmark;
- the success/preference vs inhibition asymmetry as a reported phenomenon;
- broad claim that current models have an inhibition bottleneck.

We cannot claim:
- LLMs struggle with inhibition;
- implicit memory is under-evaluated;
- first-action behavior is a new metric.

## 2. Natural interactive parent — EscapeBench (ACL 2025)

EscapeBench includes an error type **Useless Repetition**:
> model repeats the same action despite receiving explicit negative environment feedback.

Source:
- https://aclanthology.org/2025.acl-long.39/

This owns:
- natural examples of repeated failure;
- reflection/foresight as a method for improving creative agents.

It does not compare matched positive and negative experience formation or locate the asymmetry stage.

## 3. Failure reflection / self-evolution — BenchTrace

BenchTrace (2026 preprint):
- 1,821 annotated episodes across six tasks;
- reflection evaluation for failure identification;
- evolution evaluation for whether failure experience becomes avoidance;
- reports diagnosis as a bottleneck and studies failure-avoidance rate.

Source:
- https://arxiv.org/abs/2605.29225

Collision:
- “can agents learn from failures?” is already too close.

Surviving axis:
> BenchTrace studies the failure side; it does not explain why a matched success signal produces much stronger adaptation than a matched failure signal.

## 4. Experience-learning methods

**Training Language Agents to Learn from Experience** (2026):
- trains reflector models from experience;
- studies reusable lessons across unseen tasks.

Source:
- https://arxiv.org/abs/2605.20477

Older methods such as ExpeL/Reflexion also use success/failure trajectories to improve agents.

These own:
- engineering systems for learning from experience.

They do not own:
> the scientific decomposition of positive-vs-negative behavioral adaptation.

## 5. Negative constraint mechanism neighbor

**“Semantic Gravity Wells: Why Negative Constraints Backfire”** (2026 preprint) studies explicit instructions like “do not use word X” and finds mechanistic failure modes including priming and late-layer override.

Source:
- https://arxiv.org/abs/2601.08070

This is a dangerous neighbor.

It owns:
- explicit linguistic negative constraints;
- mechanistic analysis of prohibition failure.

It does not own:
- experiential failure;
- success-vs-failure asymmetry;
- outcome memory/credit assignment before the prohibition stage.

Our study should use negative-constraint behavior as one **account**, not as the entire story.

## 6. What part is new

The paper must own:

1. behavior asymmetry is already established externally;
2. construct matched positive and negative experience pairs;
3. decompose experience→action into observable stages:
   - outcome memory;
   - causal attribution;
   - policy knowledge;
   - first action;
4. manipulate attribution and action framing;
5. identify where positive and negative learning diverge;
6. validate the mechanism on natural interactive failure trajectories.

This is not a benchmark contribution.

## 7. Reviewer compression

### Attack 1
> “ImplicitMemBench + probes.”

Fatal without stage-wise intervention.

### Attack 2
> “BenchTrace with a positive control.”

Rebuttal:
> positive experience is not merely a control; the scientific quantity is the **valence asymmetry** and the location where two otherwise matched learning processes diverge.

### Attack 3
> “Negative constraints in an agent setting.”

Rebuttal:
> explicit prohibition is only the final possible stage. The model may fail earlier at memory or attribution.

## 8. Kill-level collision definition

KILL if a paper already:
- uses matched success/failure experiences;
- measures outcome recall, causal attribution, policy knowledge, and action;
- performs targeted interventions at these stages;
- and identifies the same positive-vs-negative asymmetry mechanism.

Generic failure reflection, avoidance benchmarks, or explicit “do not X” work do not kill.

## 9. Top-conference alignment

This candidate matches a strong Main scientific pattern:
> award/Main-established behavior → simple explanation question → controlled decomposition → causal repair → system consequence.

The topic becomes weak if it drifts toward cognitive terminology or another memory benchmark.

## 10. Current verdict

**SERIOUS / A-.**

The strongest identity is:
> **Where does success/failure behavioral learning become asymmetric?**
