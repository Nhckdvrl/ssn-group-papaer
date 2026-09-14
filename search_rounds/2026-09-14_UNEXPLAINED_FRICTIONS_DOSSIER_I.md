# 2026-09-14 — Unexplained Frictions Dossier I

**Mode:** FRICTION MINING INSIDE ESTABLISHED STANDING PROBLEMS  
**Candidate generation:** **OFF**  
**L-series / K-series:** **NO CHANGES**  
**Input:** multi-year immersion in WALL-A/B/C/D  
**Admission rule:** a friction must come from an actual contradiction, failed prediction, instability, identification limit, or unresolved construct split in the literature. “Authors list future work” is not enough.

The purpose of this file is to collect the equivalent of a strong researcher’s:

> **things that keep bothering me because the current story does not quite add up.**

No item below is a research question yet.

---

# 1. WALL-A frictions — reusable abstractions

## A-FR1 — A causal abstraction can become vacuous if the alignment map is too expressive

**Evidence.** Sutter, Minder, Hofmann & Pimentel, NeurIPS 2025, _The Non-Linear Representation Dilemma: Is Causal Abstraction Enough for Mechanistic Interpretability?_ argues that if alignment maps are allowed to be arbitrarily powerful, then under reasonable assumptions essentially any neural network can be mapped onto any algorithm. The unrestricted abstraction relation therefore becomes uninformative. Existing practical work often avoids this by assuming linear or otherwise restricted alignments.

Source: https://mlanthology.org/neurips/2025/sutter2025neurips-nonlinear/

### Why this is a real friction

Causal abstraction was introduced to make the statement “network implements algorithm H” precise. But the conclusion depends on the **complexity class allowed for the map from low-level states to high-level variables**.

This creates an unavoidable scientific tradeoff:

> alignment too weak → miss real nonlinear/distributed abstractions;  
> alignment too strong → every desired abstraction becomes recoverable and the explanation says nothing.

This is not a missing benchmark. It is a construct-validity problem for mechanistic evidence itself.

### What it invalidates

- “high IIA means we found the true abstraction” without accounting for alignment flexibility;
- treating linearity as merely an implementation convenience;
- comparing abstraction scores across hypotheses with different mapping complexity as if the scores were commensurate.

**Friction strength: VERY HIGH.**

---

## A-FR2 — A high-level algorithm can be faithful only on part of the input space

**Evidence.** Pîslar, Magliacane & Geiger (CLeaR 2025), _Combining Causal Models for More Accurate Abstractions of Neural Networks_, finds that a single high-level model often only partially captures network reasoning and models the network as occupying different computational states. Li et al. (2026), _Bucketing the Good Apples_, explicitly partitions inputs into well-interpreted and under-interpreted regions and uses failures to discover missing distinctions/intermediate variables.

Sources:
- https://proceedings.mlr.press/v275/pislar25a.html
- https://arxiv.org/abs/2605.02234

### Why this is a real friction

The strongest linguistic interpretation papers often talk as though a construction or relation has an abstract mechanism. Yet causal faithfulness itself may be **conditional on input regime**.

The unresolved scientific object is not just whether abstraction H exists, but what determines its **domain of validity**.

### What it invalidates

- averaging interchange-intervention accuracy over all inputs and treating the mean as a property of the model;
- assuming the same high-level mechanism is active whenever the same linguistic label applies;
- explaining failures as mere noise before asking whether the model changed computational state.

**Friction strength: VERY HIGH.**

---

## A-FR3 — The framework tests a proposed theory better than it discovers which theory deserves to be proposed

**Evidence.** The causal-abstraction lineage itself notes that one must select alignment/high-level hypotheses to test; the hypothesis space is enormous. DAS improves alignment search but does not solve the upstream scientific problem of choosing a meaningful high-level causal model.

Sources:
- Stanford SAIL causal-abstraction discussion: https://sail.stanford.edu/blog/causal-abstraction/
- Geiger et al. CLeaR 2024: https://proceedings.mlr.press/v236/geiger24a.html

### Why this is a real friction

A high IIA result is conditional on **the theorist’s ontology**. A powerful search procedure can test whether a network can be aligned with a theory, but theory selection remains external.

This matters especially for NLP because linguistic theories can posit rival decompositions that predict similar behavior.

**Friction strength: HIGH.**

---

## A-FR4 — Causal mediation, systematic generalization, and abstraction reuse are not the same quantity

**Evidence.** EMNLP 2025 filler–gap work gives strong evidence for causal sharing across constructions, while ICML 2025 variable-binding work shows a systematic addressable-memory mechanism emerging after heuristic phases. But neither result establishes a general equivalence between:

1. variable causally mediates behavior;
2. variable transfers under a prescribed interchange;
3. computation productively generalizes to novel combinations;
4. same algorithm remains active across distribution/training shifts.

Sources:
- https://aclanthology.org/2025.emnlp-main.1271/
- https://proceedings.mlr.press/v267/wu25j.html

### Why this is a real friction

Mechanistic papers routinely use “causal,” “abstract,” “systematic,” and “reusable” in nearby rhetorical space, but they are distinct estimands.

**Friction strength: HIGH, but requires discipline not to create another generic readout/representation parent.**

---

# 2. WALL-B frictions — formation of inductive bias

## B-FR1 — Linguistic acquisition trajectories can be globally stable while final OOD generalization is locally unstable

**Evidence on stability.** Choshen et al., ACL 2022, _The Grammar-Learning Trajectories of Neural Language Models_, reports that models with different seeds, sizes, architectures, and corpora acquire many English grammatical phenomena in nearly the same order.

**Evidence on instability.** Bhaskar, Friedman & Chen, ACL 2024, _The Heuristic Core_, begins from prior observations that fine-tuned pretrained LMs with different random seeds can achieve similar in-domain performance but very different syntactic OOD generalization. Within one model, multiple subnetworks can also match in-domain performance while generalizing very differently.

Sources:
- ACL 2022 trajectory summary: https://borgr.github.io/papers/the-grammar-learning-trajectories-of-neural-language-models/
- https://aclanthology.org/2024.acl-long.774/

### Why this is a real friction

There is no single answer to:

> “Are linguistic inductive biases stable across training randomness?”

Stability appears to depend on **which level and stage is measured**:

- order in which broad grammatical abilities emerge;
- exact probability distribution learned;
- downstream fine-tuning solution;
- OOD generalization mechanism.

This means “bias” is an overloaded scientific quantity.

**Friction strength: VERY HIGH.**

---

## B-FR2 — Similar in-domain solutions can contain very different generalization potential, but the simple “competing algorithms” story also fails

**Evidence.** _The Heuristic Core_ directly tests a grokking-style account where subnetworks instantiate competing algorithms and the model eventually selects the generalizing one. Instead, both generalizing and non-generalizing subnetworks share an early shallow heuristic core; generalization comes from additional heads building higher-level features on top of that shared heuristic computation.

Source: https://aclanthology.org/2024.acl-long.774/

### Why this is a real friction

A common story says:

> heuristic and rule are competing solutions; learning chooses one.

The evidence here suggests a compositional developmental story:

> general algorithm may **reuse** the heuristic computation rather than replace it.

That changes how we should think about “bias toward heuristic vs rule.”

**Friction strength: VERY HIGH.**

---

## B-FR3 — “Architecture’s inductive bias” becomes ill-defined after substantial prior learning

**Evidence.** Mueller & Linzen 2023 show architecture depth and input genre both affect hierarchical bias. Papadimitriou & Jurafsky 2023 and Hu et al. ACL 2025 show prior artificial/formal learning can deliberately install biases that alter later natural-language acquisition; ACL 2025 further finds transferred attention machinery remains causally relevant.

Sources:
- https://aclanthology.org/2023.acl-long.629/
- https://aclanthology.org/2023.findings-emnlp.563/
- https://aclanthology.org/2025.acl-long.478/

### Why this is a real friction

For a pretrained foundation model, “the prior” is itself the result of a huge previous learning process. Architecture, optimizer, pretraining data, and learned circuitry are layered causes.

Statements like:

> “Transformers have bias X”

can therefore collapse several distinct causal claims.

**Friction strength: HIGH.**

---

## B-FR4 — Model success on a syntactic dependency does not establish that realistic input is sufficient for human acquisition

**Evidence.** Lan, Chemla & Katzir, _Large Language Models and the Argument from the Poverty of the Stimulus_ (Linguistic Inquiry 2026), argues that current LMs do not support the strong conclusion that a linguistically neutral learner can acquire the relevant wh-movement knowledge from realistic corpora. Enriching the training corpus with limited instances improves the tested model, implicating evidence availability as part of the failure.

Source: https://doi.org/10.1162/ling_a_00533

### Why this is a real friction

LM acquisition work can fail in **both directions** as evidence about humans:

- success may reflect unrealistic data/scale/architecture;
- failure may reflect model limitations rather than poverty of the human stimulus.

The missing object is the linking inference, not another success/failure benchmark.

**Friction strength: HIGH.**

---

## B-FR5 — Random-seed distributions themselves undergo structured convergence → divergence → reconvergence

**Evidence.** Fehlauer, Mahowald & Pimentel, EMNLP 2025, trains LMs under different random seeds and finds a four-phase distributional trajectory: initial uniformity, sharp convergence, sharp divergence, and slow reconvergence. Larger models reconverge more strongly; smaller ones may not.

Source: https://aclanthology.org/2025.emnlp-main.1675/

### Why this is a real friction

Seed variability is not simply “noise around the same learner.” Training can systematically **increase** between-seed disagreement after an initial convergence phase.

That makes endpoint seed variance hard to interpret as a static property of the architecture or data.

**Friction strength: MEDIUM-HIGH.**

---

# 3. WALL-C frictions — selection among representable algorithms

## C-FR1 — We now have local selection laws, but they do not yet form a general theory

**Evidence.** Several papers supply different quantities governing learned computation in restricted settings:

- Hahn & Rofin 2024: input sensitivity ↔ isolated/sharp loss-landscape solutions and low-sensitivity learning bias;
- Kawata et al., NeurIPS 2025: sufficient data diversity, characterized by a distance-based ratio, drives transition from positional shortcut to induction head;
- Huang, Liang & Yang, ICML 2025: two-stage GD dynamics with attention feature formation then max-margin linear separation;
- Zhao, ACL Findings 2026: weight-norm complexity collapse accompanies grokking into a succinct counting circuit.

Sources:
- https://aclanthology.org/2024.acl-long.800/
- https://proceedings.neurips.cc/paper_files/paper/2025/hash/6499b639e8a4b5c9a780d9b88c09722f-Abstract-Conference.html
- https://proceedings.mlr.press/v267/huang25s.html
- https://aclanthology.org/2026.findings-acl.1301/

### Why this is a real friction

The standing problem is **not untouched**. There are genuine algorithm-selection laws — but each governs a narrow regime using a different scientific quantity.

What remains unclear is whether these are:

- manifestations of a common implicit-complexity principle;
- genuinely different regimes with no common scalar law;
- artifacts of simplified task/architecture assumptions.

**Friction strength: VERY HIGH.**

This observation prevents us from naively proposing “study why GD selects algorithm X.” That parent is already an active theory program.

---

## C-FR2 — The appearance of a “generalization circuit” and behavioral generalization can dissociate

**Evidence.** He et al., ACL Findings 2026, _Is Grokking Worthwhile?_ reports that grokked and non-grokked models can use the same inference paths on in-distribution compositional queries; high unseen-case accuracy and formation of a certain reasoning path can occur independently under particular data regimes; even mature circuits have limited transfer when integrating new knowledge.

Source: https://aclanthology.org/2026.findings-acl.1697/

### Why this is a real friction

A mechanistic transition, a behavioral OOD transition, and acquisition of a reusable algorithm need not happen at the same moment — or at all.

This undermines a common narrative:

> circuit appears → algorithm acquired → generalization follows.

**Friction strength: VERY HIGH.**

---

## C-FR3 — A generalizable computation can be built on top of a heuristic rather than replacing it

**Evidence.** _The Heuristic Core_ finds a shared early heuristic core in both generalizing and non-generalizing subnetworks; generalizing subnetworks add higher-level heads that depend on this core.

Source: https://aclanthology.org/2024.acl-long.774/

### Why this is a real friction

Many theoretical stories model shortcut and algorithm as mutually exclusive minima. Real trained networks may instead **compose** shallow and abstract computations.

This complicates any simple “which of two algorithms was selected?” account.

**Friction strength: HIGH.**

---

## C-FR4 — Expressive restrictions and learnability restrictions are not ordered along one capacity axis

**Evidence.** Li & Cotterell ACL 2026 show local and global attention are expressively complementary under their formalization; a restriction introduced for efficiency provides a distinct temporal operator. Borenstein et al. ACL 2024 find empirical learnability depends on probabilistic-language rank/expected length with architecture-specific patterns.

Sources:
- https://aclanthology.org/2026.acl-long.1739/
- https://aclanthology.org/2024.acl-long.807/

### Why this is a real friction

The intuition “more access / more representational power → easier learning → better generalization” is not a valid one-dimensional ordering.

**Friction strength: HIGH.**

---

## C-FR5 — Clean algorithm identification currently trades off against natural-language relevance

**Evidence pattern.** The strongest theoretical selection results use tightly controlled tasks (parity/even-pairs, trigger-copy, counting, variable binding), because the rival algorithms and solution classes can be specified exactly. Natural-language models offer scientific relevance but make the candidate algorithm space vastly less identifiable.

### Why this is a real friction

This is not merely “synthetic data is bad.” It is a structural tension:

> precise algorithm-level science requires restricting the task enough to know what algorithms are possible;  
> NLP significance requires preserving enough natural structure that the conclusion matters for language models.

**Friction strength: VERY HIGH for project design.**

---

# 4. WALL-D frictions — structure from resource constraints

## D-FR1 — A unified memory/prediction computational model can predict the interaction qualitatively yet miss its empirical time course

**Evidence.** Oltrogge, Veríssimo, Patil & Lago, Journal of Memory and Language 2025, experimentally tests a cue-based model connecting memory retrieval and prediction. Human eye-tracking supports interaction between prediction and memory interference, but the novel determiner condition’s time course differs from the computational prediction. The model needs an additional process motivated by the semantics of indefinite determiners.

Sources:
- https://doi.org/10.1016/j.jml.2025.104651
- University of Lisbon summary: https://researchportal.ulisboa.pt/en/publications/memory-retrieval-and-prediction-interact-in-sentence-comprehensio/

### Why this is a real friction

A broad resource/memory principle can get the direction of an interaction right while missing **when and how the process unfolds**. Linguistic semantics can alter the processing algorithm rather than merely shift a scalar resource parameter.

This is exactly the kind of model failure strong research lineages learn from.

**Friction strength: VERY HIGH.**

---

## D-FR2 — Domain-general strategic resource allocation shows substantial cross-linguistic variability

**Evidence.** Xu & Futrell 2026 derive Strategic Resource Allocation as a domain-general memory-efficiency principle, but their empirical results show considerable cross-linguistic variability and explicitly motivate closer study of interaction with language-specific phrase structures.

Source: https://doi.org/10.1016/j.jml.2025.104706

### Why this is a real friction

If the optimization principle is domain-general, why should its behavioral signature vary strongly across language structures?

Several possibilities remain:

- the same principle operates but language statistics change the optimum;
- phrase structure changes what information is valuable;
- the measured locality effect mixes encoding and retrieval;
- the proposed objective/resource is incomplete.

**Friction strength: VERY HIGH.**

---

## D-FR3 — Encoding limitation and retrieval limitation can mimic one another behaviorally

**Evidence.** Lossy-context/resource-rational work places the key limitation in the quality/retention of memory representations. Cue-based retrieval theories instead locate important limitations in content-addressable retrieval/interference. ACL 2025 work on attention as a cognitive memory-retrieval model further argues for structure-sensitive retrieval representations. ACL 2026 memory-efficiency work explicitly points to a dissociation between retrieval mechanisms and underlying memory representations.

Sources:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC7065005/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC8459291/
- https://aclanthology.org/2025.acl-long.483/
- https://aclanthology.org/2026.acl-long.1550/

### Why this is a real friction

A reading-time/locality effect does not by itself identify whether the bottleneck happened while **encoding**, **retaining**, or **retrieving** information.

This is a mature rival-account problem, not a generic “representation vs readout” story: the processes are independently defined in psycholinguistic memory theories.

**Friction strength: VERY HIGH.**

---

## D-FR4 — Resource-rational accounts require specifying both the resource and the objective; neither is automatically given by “bounded cognition”

**Evidence.** Across the lineage, different papers constrain:

- retention / lossy context;
- representational precision;
- retrieval/search computation;
- predictive information / excess entropy.

They optimize different downstream quantities and operate at different explanatory scales.

### Why this is a real friction

“Resource rationality” is a framework, not one empirical theory. With enough freedom in the cost function and resource definition, many behaviors could be rationalized after the fact.

A strong explanation therefore needs independently justified resource and objective before seeing the target phenomenon.

**Friction strength: HIGH.**

---

## D-FR5 — The same bottleneck idea is being used at three explanatory scales that need not share one optimum

**Evidence.** The lineage spans:

1. online sentence-processing difficulty;
2. neural encoding geometry under memory precision constraints;
3. emergence of systematic language structure under sequential-information bottlenecks.

Sources:
- https://doi.org/10.1111/cogs.12814
- https://aclanthology.org/2026.acl-long.1550/
- https://www.nature.com/articles/s41562-025-02336-w

### Why this is a real friction

An efficiency pressure that predicts an individual processor’s representation need not be identical to the pressure shaping a population’s language over generations.

The same mathematical quantity appearing at multiple scales is suggestive, but does not itself establish a shared causal explanation.

**Friction strength: MEDIUM-HIGH.**

---

# 5. Frictions that are already too close to active owner programs

To prevent the dossier itself becoming a successor generator, the following are marked **SCIENTIFICALLY REAL BUT OWNER-DENSE**:

- “Where does causal abstraction work/fail across the input space?” — directly active in 2025–2026 causal-abstraction diagnostics.
- “Does data diversity choose shortcut vs induction head?” — direct NeurIPS 2025 owner.
- “Does regularization make transformers find succinct circuits?” — direct ACL 2026 owner and previous K250 boundary.
- “Can prior formal-language training install syntactic bias?” — direct ACL 2025 Outstanding owner.
- “Does memory precision induce categorical representations?” — direct ACL 2026 Best owner.

These facts update our standing model but are **not available project parents**.

---

# 6. Frictions that are most valuable for research intimacy

No topic generation is authorized, but four frictions deserve to remain mentally active because they are broader than their current owners and expose genuine scientific disagreement:

### FI-1 — Stability of an abstraction is conditional

A mechanistic interpretation can be causal and still hold only on a subset of inputs / computational states. “The model implements H” needs a domain-of-validity theory.

### FI-2 — A learned bias is a developmental object

Global acquisition order can be reproducible while OOD generalization varies across seeds and subnetworks. Bias cannot be summarized by one endpoint preference.

### FI-3 — Mechanism and generalization are not locked together

A circuit/algorithm may appear before, after, or independently of behavioral OOD generalization; heuristic computation can remain inside the generalizing solution.

### FI-4 — Resource theories face a real encoding–retrieval identification problem

The same processing signature may reflect what information was stored versus how it was retrieved. The distinction comes from mature cognitive theory, not from generic interpretability vocabulary.

These are **frictions**, not RQs.

---

# 7. Searcher lesson from this pass

The difference between a fake pressure and a real friction is now clearer.

### Fake pressure

> Paper A says X; Paper B says Y; nobody tested X × Y.

### Real friction

> The field has a working explanatory story. A concrete result, failed prediction, or formal limitation shows that the story cannot be literally true in its current form — yet the replacement account is not known.

The four strongest examples above satisfy this criterion:

- causal abstraction becomes trivial if mappings are unconstrained, but restrictive mappings risk missing real abstractions;
- linguistic learning can be globally reproducible yet locally generalization-unstable;
- a putative generalization mechanism can dissociate from generalization itself;
- a memory/prediction model can capture the broad interaction yet fail the empirical time course, revealing a missing process.

This is much closer to the “failures I don’t understand” state described by strong researchers than the repository’s previous paper-gap search.

---

# 8. Current decision

**Still no candidate generation.**  
**New L-series: 0.**  
**New kill IDs: 0.**  
**Pilot: none.**

The next useful step is a second friction pass with a different goal:

> **look for replication disputes, theory failures, and contradictory results that the originating authors themselves discuss or that later papers explicitly challenge.**

Only after this has enough density should we decide whether one standing problem has accumulated enough real pressure to permit question generation.