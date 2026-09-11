# L16 — Same World, Different Partitions

## Do LLM beliefs change when we redraw the hypothesis space?

**Status:** **PILOT-AUTHORIZED — bounded E01/E02 only (2026-09-11)**  
**Paper mainline:** NOT APPROVED  
**Target:** ACL / EMNLP / NAACL Main

> **Plain example**  
> These are the same seven possible days and the same event: **Sunday is the hottest day next week**.  
> One prompt makes the salient partition `{Sunday} | {not Sunday}`; another makes it `{Sunday}|{Monday}|...|{Saturday}`.  
> No evidence about the weather has changed. A coherent belief about the same event should not be manufactured by how the other possibilities are grouped.

## Locked research question

> **Holding the atomic hypotheses, evidence, target proposition, wording inventory, and normal reasoning budget fixed, does arbitrary refinement/coarsening of the displayed hypothesis space systematically pull an LLM's elicited credence toward the uniform mass over displayed cells (`1/M`), and can that representationally induced credence shift survive explicit recognition that the partitions are informationally equivalent?**

The project is **not** generic prompt sensitivity, generic confidence calibration, option-count bias, multiple-choice order effects, record/evidence grouping, distractor generation, or a replication of a human cognitive bias for its own sake.

## Why this is a Main-level question if the signature exists

Modern LLM systems increasingly expose or consume confidence in forecasting, abstention, routing, diagnosis, search, agent planning, and decision support. Recent work also shows that confidence can causally govern abstention behavior. If the same evidence about the same proposition yields systematically different credences merely because the *unchanged hypothesis space is redrawn*, then a list/tree/schema of possibilities is not a neutral interface: it acts as an epistemic prior.

The interesting result is therefore not "LLMs show partition bias." It is:

> **Representation of the hypothesis space can create a directional prior in LLM uncertainty even when it adds no information.**

The stronger mechanistic signature is:

> **The model correctly states that two partitions encode the same possibilities and evidence, yet its own credence moves toward the partition-specific ignorance prior.**

That would expose a concrete gap between extensional equivalence and uncertainty construction.

## Classic parent

The parent phenomenon is **partition dependence / partition priming** in human probability judgment.

- Fox & Rottenstreich (2003), *Partition Priming in Judgment Under Uncertainty*: case vs class formulations of the same event prime ignorance priors such as `1/2` versus `1/7`.
- Fox & Clemen (2005), *Subjective Probability Assessment in Decision Analysis*: judgments are biased toward a uniform distribution over the presented partition; the effect occurs for discrete/continuous spaces and even trained experts.
- See, Fox & Rottenstreich (2006), *Between Ignorance and Truth*: learned evidence and the partition-specific ignorance prior combine; stronger knowledge attenuates the bias.
- Ding & Feldman (2025), Registered Report: mostly successful replication, N=603, with public materials/data/code (`https://osf.io/g9czs/`).

The human phenomenon is established enough to give us a principled hypothesis and public anchor materials. It is not our novelty claim.

## Current ownership verdict

**Plausible independent contribution after expanded direct audit.**

No direct owner was found for the locked five-part LLM object:

1. the same atomic hypotheses are present in every condition;
2. only their arbitrary grouping/refinement changes;
3. the target proposition and evidence are identical;
4. the predicted effect is directional toward the partition-specific `1/M` ignorance prior, not merely "prompt changed -> confidence changed";
5. equivalence knowledge and downstream credence are measured separately.

The strongest current compression and collision fences are recorded in [RELATED_WORK_AND_NOVELTY.md](RELATED_WORK_AND_NOVELTY.md).

## Locked accounts

### A — Extensional belief / partition invariance
The model's credence is a function of the proposition and evidence. If the atomic possibilities and evidence are unchanged, regrouping alternatives is representational only and `P(target)` remains stable.

### B — Partition-induced ignorance prior
The displayed partition supplies an implicit prior over cells. Under weak information, the target credence is pulled toward `1/M`, where `M` is the number of salient mutually exclusive cells. Thus the same target can move systematically as the space is redrawn.

### C — Generic surface/prompt sensitivity
Grouping changes output, but not with the directional `1/M` law, not consistently across regroupings, and/or without the predicted attenuation under stronger evidence. This is already too close to generic semantic-invariance work and **does not rescue L16**.

### D — Alternative availability / lexical exposure
The effect is caused by adding/removing or repeating alternatives. Primary stimuli rule this down by keeping **exactly the same atomic alternatives in exactly the same order** across conditions.

### E — Verbalized-number artifact
Only the requested numeric confidence shifts; another confidence/decision readout is invariant. If so, the broad "LLM belief" story is not licensed. The current paper identity must be killed or explicitly reconstructed after a fresh novelty audit.

## Paper-shaped development path — preregistered before compute

### C1 — Same world, different partition
Content-matched `M=2`, `M=3`, `M=9`, and flat presentations. Test whether the same target credence changes systematically under normal reasoning.

### C2 — Is it an ignorance-prior law rather than generic prompt sensitivity?
If C1 lives, test the signed pull toward `1/M`, random regroupings, explicit informational-equivalence recognition, and attenuation as evidence strengthens. These were selected before seeing model outputs.

### C3 — Does representational partitioning change behavior?
**Not authorized until post-pilot re-selection.** If C1/C2 survive, test fixed decision/abstention thresholds under equivalent partitions. This remains the same paper identity: representation-induced credence -> consequential decision. Recent causal work on LLM confidence and abstention motivates the consequence but does not own the partition manipulation.

No hidden-state search, training method, generic debiasing method, RAG extension, or model zoo is authorized before re-selection.

## Data / gold

Primary pilot gold is **partition invariance**, which is exact and independent of the evaluated model: the proposition, atomic hypotheses, and evidence are held fixed; arbitrary braces/group labels add no world information.

Mechanism gold/expectation is a preregistered directional signature from the classic parent: if Account B holds, credence should move toward `1/M`, with larger partition effects under weaker evidence.

The pilot uses two tiers:

- **published anchor materials** from Fox & Rottenstreich / Ding & Feldman where license/access permits;
- **lexically matched diagnostic items** whose only manipulated field is the partition map over a fixed ordered list of atomic alternatives.

See [DATA_AND_GOLD.md](DATA_AND_GOLD.md).

## Authorized pilot

Only:

- **E01:** content-matched partition curve under normal reasoning;
- **E02:** directional `1/M` signature + equivalence-awareness / grouping controls.

Primary mode is normal reasoning / CoT. A phenomenon that exists only when reasoning is blocked is a kill signal, not a rescue route.

See [PILOT_CARD.md](PILOT_CARD.md).

## Hard kill / mutation rule

Kill the current route if any of the following holds:

- both capable model families are approximately invariant under CoT;
- an apparent effect disappears once atomic alternatives and their lexical order are matched;
- shifts are not directional with partition granularity and reduce to generic prompt sensitivity;
- the effect exists only in direct/no-reasoning mode;
- the effect is confined to one weaker model family;
- the model does not recognize that the matched partitions are informationally equivalent, so the claimed dissociation cannot be established;
- a direct owner of the locked hypothesis-partition computation is found.

If the result mutates into option ordering, distractor count, record grouping, prompt calibration, candidate omission, response-scale design, or another neighboring paper identity: **stop before the next experiment and return to selection.**

> **Evidence survives claim mutation; authorization does not.**

# Current verdict

# **PILOT-AUTHORIZED — E01/E02 ONLY**

This package has already passed the pre-pilot ownership/data/development audit. It is ready for a bounded kill-oriented pilot; no additional literature-search gate is required before E01.