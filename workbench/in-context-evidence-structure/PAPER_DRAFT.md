# How Shared Outputs Shape Source-Specific Evidence in In-Context Learning

Core manuscript draft, 2026-10-11. This version organizes the completed experimental evidence; it is not a submission-ready manuscript. Experiment IDs provide links to reproducible records and can be removed during manuscript preparation.

## Abstract

When several sources provide demonstrations using the same output vocabulary, how does a language model form and use evidence specific to the requested source? We distinguish the source positions accessed by a query from the functional origin of the relations used in its prediction. Restricting a query to one source's positions does not ensure that its predictions depend only on that source's associations: historical demonstrations can already have altered the evidence stored at those positions. Causal interventions identify an output-dependent formation pathway from earlier answer regions to the requested source's label states. Without fitting coefficients or selecting heads, this pathway approximately reconstructs namespace counterfactuals in new contexts and a second model family. Counterfactuals that preserve output words and positions show that answer messages also transfer part of a learned input–label association. Finally, full-source prediction remains sensitive to this formation history, with confirmed interactions between the requested source's cached evidence and the other source's cached environment. These results connect shared outputs to the formation and use of source-specific evidence, and show why positional source selection alone is an incomplete measure of functional evidence provenance.

## 1. Introduction

In-context learning often combines demonstrations from different annotators, users, or task conventions. Two annotators can use the same words while assigning them differently: one may label favorable restaurant comments `yes`, while another uses the inverse convention. A new query names the annotator whose examples should constrain its answer. Understanding this computation matters both when the model succeeds and when it confuses the conventions.

Existing mechanistic accounts identify label positions as carriers of input information, retrieval pathways that aggregate demonstrations, and contextualization between demonstrations. These accounts make it plausible that source-conditioned retrieval acts on contextualized evidence. They do not, by themselves, establish how shared output identities shape the functional provenance of evidence assigned to an individual source, or how that formation process contributes to subsequent source-conditioned prediction.

Our starting observation is that sharing output words can reduce the distinction between different annotators' judgments. However, this internal distinction need not produce a large accuracy loss in practical prediction settings. We therefore study the computation that organizes source-specific evidence, rather than defining the project around a persistent inability to answer correctly.

The key distinction is between **where evidence is read** and **which relations influenced its formation**. An attention mask selecting source A's positions controls the first quantity. It does not retroactively remove information from B that entered those positions while the prefix was processed. We first establish this distinction through functional counterfactuals, then intervene on the historical messages forming A's labels. We test both changes in output namespace and changes in association with output words fixed. Finally, we reconnect these interventions to full-source prediction.

The resulting contribution is a bounded causal account of how shared outputs shape source-specific relational evidence. It extends the application and measurement of contextualization to a source-provenance question; it does not claim to discover contextualization, label carriers, or the general distinction between attention routing and values.

## 2. Distinguishing positional selection from functional provenance

Let \(D_A,D_B\) denote the two sources' raw demonstrations and \(H_A,H_B\) their contextualized prefix states. A useful description is

\[
H_A=F_A(D_A,D_B),\qquad z=R(q,H_A,H_B).
\]

These symbols summarize interventions, not independent neural modules. In particular, \(H_B\) can also contain information from A.

We change B's input–label association while holding A's raw demonstrations and labels fixed. A query-time mask prevents every query position from attending to B's prefix positions. If the query's answer still changes, the association has a functional effect through the remaining computational graph. This does not establish that all such sharing is undesirable, or that the states encode an abstract rule in isolation.

In independent contexts, changing B's rule alters 17.6% [12.1, 23.8] of A's answers even under this restriction (E90). Separating B's output vocabulary also reduces this inherited dependence (E91). Thus neither the source of the attended token nor successful source selection alone identifies the source of the relational information being used. Earlier native source interventions remain relevant: source identity does influence the model, so these results do not imply that the model ignores source names.

## 3. An output-dependent pathway during evidence formation

### 3.1 Intervention and frozen effect prediction

We compare prefixes in which A's demonstrations and output words remain identical, while B either shares A's output vocabulary or uses a separate vocabulary. We extract donor K/V states from the counterfactual prefix. During recipient prefix processing, we replace B's answer-region K, V, or both **only in the attention messages received at A's label positions**. All layers participate; no head, layer, strength, or coefficient is selected using the outcomes. The query then consumes the resulting A-label cache interchange in an otherwise pristine prefix cache.

The prediction uses coefficient one: the intervention's logit change predicts the actual counterfactual change at the specified interface. We report raw effects and rule double contrasts. The latter compare the namespace effect between the original and changed B-association worlds, helping distinguish relation-dependent effects from a shared output bias. The predictor uses actual donor activations; it is a causal reconstruction, not a donor-free algorithm for unseen behavior.

### 3.2 Confirmation across contexts, model families, and materials

In 32 new contexts for each of Qwen3-8B and Mistral-7B-v0.3, answer-key interchange approximately reconstructs the namespace effect on the specified A-label interface. The same frozen namespace intervention remains predictive in a separate controlled sentiment task for Qwen (E109/E111/E112).

| Frozen rule-double-contrast reconstruction | Qwen / MHS | Mistral / MHS | Qwen / sentiment |
|---|---:|---:|---:|
| Answer K: correlation / RMSE | .969 / .810 | .966 / .265 | .907 / 1.599 |
| Answer KV: correlation / RMSE | .985 / .562 | .977 / .225 | .958 / 1.097 |
| Answer V: correlation / RMSE | .642 / 2.527 | .508 / .754 | .707 / 2.645 |
| Zero-prediction RMSE | 3.267 | .865 | 3.731 |

The observed combinations are three model–task pairs, rather than a full factorial grid. MHS contexts are independently sampled but can reuse comments. All predefined predictors, including weak controls, remain in the results. K-only interchange does not directly replace V on the intervened edge; subsequent recipient states still evolve. Approximate reconstruction establishes a sufficient partial pathway for the measured effect, not its unique or necessary mediator.

![Formation-path reconstruction and association evidence](results/figs/fig_evidence_formation.png)

*Figure 1. Completed confirmation results for output-dependent evidence formation. Prediction uses the frozen causal intervention, without a fitted regression line. The accompanying data and scripts retain all channels and controls.*

## 4. Does the pathway carry associations when output identities stay fixed?

A namespace manipulation alone could reflect output identity without identifying learned relational content. We therefore retain B's label words, source names, token positions, and input multiset, and swap comments across opposite sentiment classes. A control swaps comments within the same sentiment class, changing the same number of positions. A's demonstrations and new queries remain fixed. Token geometry and boundaries are matched before running the models.

This creates competing explanations for the answer-region messages. If their effect is only a static label signal, the fixed-word association manipulation should not produce an additional relation-dependent effect. If the contextualized messages carry association information, changing the pairing can affect A's evidence even when the eventual query cannot read B directly. Within-class swaps control for part of the disturbance caused by moving inputs; they do not make every semantic property invariant.

For each intervention world \(w\), we first compute the context-level signed effect \(E_c(w)=\operatorname{mean}_q g_q(z_w-z_{origin})\). The reported excess effect is \(\operatorname{mean}_c[|E_c(cross)|-|E_c(within)|]\). Signed effects and per-query changes are also retained; this magnitude contrast is not a claim that every query changes in the same direction.

Confirmation uses new sentiment words and sentence templates. Historical answer KV produces a cross-minus-within effect of .618 [.446, .813] nats in Qwen and .404 [.313, .499] in Mistral (E111/E113). V interventions are substantially stronger than K for this contrast. The complete A-label interchange has a larger effect, so the answer-region pathway carries part of the relation rather than reproducing all of it.

An earlier long-comment version did not adequately distinguish relation change from within-class movement (E110). Its result is retained as a limit on that design; the simpler sentiment experiment answers a narrower, identifiable question. Neither experiment proves a transferable abstract criterion or a complete source-specific program.

## 5. Connecting formation to full-source prediction

### 5.1 Crossing cached formation states and reading environments

The preceding restriction isolates inherited information. It does not establish that the same pathway matters when the query can read all sources. We therefore cross the namespace history of A's complete prefix cache with that of B's complete prefix cache, while allowing normal attention to every prefix position (E114).

Let \(f\) select A-position caches formed in shared or separate-output prefixes, and \(r\) select B-position caches from those prefixes. Both caches are contextualized; \(r\) is not a fixed reader, and changing it can affect later query states and attention. The 00 and 11 corners correspond to coherent full-source endpoints. Mixed corners are diagnostic cache interchanges.

For each context, define the signed rule response

\[
D_{fr}=\operatorname{mean}_q g_q\big(z_{fr}^{cross}(q)-z_{fr}^{origin}(q)\big),
\]

where \(z\) is the `yes` minus `no` logit margin and \(g_q\) is the sign of A's correct private label. We report both signed and absolute conditional effects. Nonadditivity is tested using the signed interaction \(D_{11}-D_{10}-D_{01}+D_{00}\), rather than inferred solely from nonlinear absolute-value summaries.

### 5.2 Native conditional effects and frozen predictions

Independent confirmation includes 32 new contexts per model family. Changing A's formation history has a clear effect in both B-cache environments. The signed interaction is positive in both models.

| Confirmed effect, nats [95% CI] | Qwen3-8B | Mistral-7B-v0.3 |
|---|---:|---:|
| A formation: decrease in rule magnitude, B shared | 2.098 [1.344, 2.892] | 1.238 [1.037, 1.464] |
| A formation: decrease in rule magnitude, B separate | .759 [.269, 1.269] | .684 [.461, .896] |
| B environment: decrease in rule magnitude, A shared | 3.757 [2.645, 4.840] | 1.902 [1.246, 2.534] |
| B environment: decrease in rule magnitude, A separate | 2.418 [1.596, 3.308] | 1.348 [.815, 1.871] |
| Signed interaction | .775 [.113, 1.440] | .321 [.187, .454] |

The historical answer KV intervention also predicts native A-label namespace effects: rule-double-contrast correlations are .899/.930 for Qwen and .959/.968 for Mistral under the two B environments. Corresponding RMSEs are 1.560/.868 and .388/.396, below zero-prediction RMSEs of 3.388/2.316 and 1.360/1.324. Effects on the full A cache and every predefined channel are reported separately.

The fixed-label relation contrast persists under full-source reading, at .241 [.149, .348] and .263 [.198, .329] nats. V and KV are not interchangeable: native Mistral shows a larger V effect, and Qwen also has a signed channel difference. Results from independently sampled gated and native runs are not treated as a matched causal estimate of removing the gate.

![Native conditional effects and frozen prediction](results/figs/fig_native_evidence_use.png)

*Figure 2. Top: signed rule responses across A/B cache backgrounds and confirmed interaction. Bottom: actual-donor, coefficient-one answer-KV predictions of the native A-label interface under both B backgrounds. Identity lines indicate exact reconstruction; residuals are retained.*

![Association transfer across model families and interfaces](results/figs/fig_relation_transfer_interfaces.png)

*Figure 3. Partial fixed-label association transfer in both families, under gated and full-source query interfaces. These bars summarize independently sampled runs and do not isolate the gate as a single changed variable.*

## 6. Relation to existing explanations

[Cho's ICL circuit account](https://arxiv.org/html/2410.04468v3) connects input encoding, merging at labels, retrieval, and bypasses. [Task-oriented information removal](https://arxiv.org/abs/2509.21012) supplies an additional view of how demonstrations select useful information. We use these as existing accounts of label formation and information selection; our contribution is not that labels contain input information.

[Contextualize-then-Aggregate](https://arxiv.org/html/2504.00132v2) causally establishes cross-demonstration contextualization, including functional effects of changed mappings. Our results are compatible with that framework. The specific addition is a source-provenance measurement and an explanation of how output coding changes cross-source relation dependence during formation and subsequent native prediction.

[How Few-Shot Examples Add Up](https://arxiv.org/html/2605.16591v2) distinguishes contextualized QK routing and V effects on function-vector aggregation. Its factorial design motivates retaining conditional effects under both backgrounds. We do not claim QK/V separation or nonadditivity as a new general principle; our interventions target historical formation of source-specific labels and the full-source predictions that consume them.

[CoSToM](https://aclanthology.org/2026.acl-long.421/) connects an internal activation interface to downstream use after supervised steering. It provides a research-design example of moving from internal information to functional deployment. Here the models remain frozen, and the functional connection is tested through cache/message interchanges rather than a trained repair. Entity-binding and task-representation accounts also remain relevant alternatives for other portions of source-conditioned computation.

## 7. Methods and reproducibility

Experiments use frozen Qwen3-8B and Mistral-7B-v0.3 base, FP32 eager attention, PyTorch 2.8.0 and Transformers 4.57.6. The controlled sentiment task contains eight demonstrations from each source and eight new queries per context. Source names, private output direction, and demonstration order vary; the two private directions are balanced in confirmation. Shared outputs are `no/yes`; separate B outputs are `pass/flag`. A's outputs remain unchanged. Models process the serialized task as a continuation, without adding a chat template.

The actual serialized token stream is part of the method. Blocks, answer words, and separators are encoded separately. For Mistral, this introduces fixed extra spaces relative to literal whole-string encoding: the first native confirmation context has 351 rather than 335 tokens. Its B answer-message region includes the answer word plus three separator tokens per demonstration, totaling 32 sender positions; Qwen uses 16. Paired token positions and boundaries remain identical across the relevant manipulations. Native controls validate the actual stream, not a claimed equivalent whole-string encoding. Source code and independent tokenizer reconstruction preserve this disclosure.

Effects use 10,000 context-bootstrap resamples, seed 910; reconstruction intervals follow the frozen E109 analysis. Queries within a context are not treated as independent observations. Raw logits, full-vocabulary argmax, binary candidate-label accuracy, all conditions, and failed controls are retained. Confirmation uses new word/template pools; discovery-to-confirmation text overlap is zero for E113 and the Qwen E114 batches, but vocabulary/templates recur across contexts within a pool.

Self interchanges produce zero error. Cached versus full-token native query scoring differs by at most 4.96e−5 in Qwen and 7.63e−6 in Mistral confirmation. Cache fingerprints, layer consumption, and matched token geometry are checked. An independent session reconstructs the token layouts and recomputes 559 numerical checks from raw records before reading author summaries, with maximum discrepancy 4.77e−15. Separate bootstrap resampling confirms the signed interactions; it is not represented as an independent GPU rerun.

The final E113/E114 package comprises five runs, 36,736 scores, and .353 recorded GPU-hours. No weights are trained. Cards specify seeds, model revisions, script hashes, and rebuilding commands. Small summaries, figures, code, and audits are versioned; raw JSONL and model assets remain at the paths documented in [README](README.md).

## 8. Scope and implications

The strongest formation reconstruction covers three model–task pairs. Fixed-label content and the native factorial confirmation cover two model families on one controlled sentiment task. We do not infer a complete cross-task native theory, a unique pathway, or a donor-free prediction algorithm. Mixed cache states are diagnostic interventions, and the full relational effect exceeds the reconstructed pathway.

Historical dependence also need not be a computational error. Sharing information can be useful, and earlier practical evaluations did not show uniformly large accuracy costs. Stronger models can perform related tasks successfully. Our explanation concerns the causal organization of evidence, rather than a limitation that all future models must retain.

The practical scientific implication is a change in measurement: evaluating source-conditioned computation requires asking which source's associations influenced the available evidence, alongside which positions the query reads. In these settings, output coding changes that formation process, and formation history interacts with the cached evidence available during native reading. This provides a specific, testable account within existing contextualization theories rather than requiring a new universal ICL circuit.

## Evidence map

| Manuscript claim | Records |
|---|---|
| Positional access does not isolate relation dependence | [E90](experiments/E90-source-isolation-before-and-after.md), [E91](experiments/E91-label-namespace-and-inherited-rule.md) |
| Output-dependent formation reconstruction, C21 | [E109](experiments/E109-foreign-messages-at-label-formation.md), [E111](experiments/E111-polarity-relation-versus-namespace.md), [E112](experiments/E112-formation-mechanism-mistral-family.md), [first independent audit](results/e109/independent_review_2026-10-11.md) |
| Fixed-label partial association content, C22 | [E111](experiments/E111-polarity-relation-versus-namespace.md), [E113](experiments/E113-relation-content-mistral.md), [E114](experiments/E114-native-formation-reading-crossing.md) |
| Native conditional effects and interaction, C23 | [E114](experiments/E114-native-formation-reading-crossing.md), [new independent audit](results/e114/independent_review_2026-10-11.md) |
| Limits and failed functional interfaces | E50–E52, E99, E107, [E110](experiments/E110-learned-relation-fixed-label-stream.md); full ledger in [CLAIMS](CLAIMS.md) |
