# How Shared Outputs Shape Source-Specific Evidence in In-Context Learning

Manuscript draft, 2026-10-12. The linked appendix and experiment records contain complete conditions, controls, and reconstruction targets. This is a research manuscript; formal candidate status remains unchanged.

## Abstract

When several sources demonstrate different rules using the same output vocabulary, how does a language model form and use evidence for the requested source? We distinguish the source positions accessed by a query from the origin of the learned relations influencing its answer. Earlier demonstrations can alter another source's evidence before the query is processed. Causal message interchanges identify an output-dependent pathway from historical answers to later label states, and a frozen reconstruction predicts namespace counterfactuals in new contexts. Removing the corresponding native operation reduces cross-source relational influence across model families. With output words fixed, the messages also transfer part of a learned input–label association. This formation account predicts a constructive distinction: selectively limiting cross-source answer formation can improve source-conditioned judgments while retaining other contextual access paths, whereas isolating all cross-source formation can worsen them. Query-stage isolation has different effects across models. On real sentiment text, the same formation mechanism holds with reliable private-rule controls, and selective formation improves shared-word judgments by 5.4–9.5 percentage points; criterion–convention counterfactuals further distinguish association transfer from full criterion-related responses. Information-equivalent public backgrounds can also produce private caches whose joint use differs, including when both sources share identical output words. The results connect evidence provenance, historical formation, and source-conditioned use, explaining why attention to the requested source alone is an incomplete account of evidence selection.

## 1. Introduction

A context can contain several legitimate rules. Two annotators may assign different labels to the same kind of comment, or judge different aspects of it, while sharing the words `yes` and `no`. A new query specifies whose demonstrations should govern its answer. The model must infer and use the relevant input–output relation, while retaining useful information from the surrounding context. This is a computational question both when its answer is correct and when the conventions interfere.

Mechanistic studies have established input encoding, merging at label positions, retrieval, and aggregation in ICL. Cross-demonstration contextualization is also important: examples can acquire task information from earlier examples before a query uses them. What remains to establish in the multi-source setting is how this process organizes **the provenance of learned relations**. Source A's token positions belong to A, but their contextualized representations may have been shaped by B's rule. The output vocabulary can influence that formation process, as well as the final answer.

This changes the object of explanation. A model attending to the requested source has selected positions, not necessarily isolated that source's supervision. Conversely, cross-source information is not uniformly harmful: removing it can discard information that helps the model use either rule. A computational account must explain which relations enter the available evidence and how the reading process uses that evidence.

We develop this account through three connected findings:

1. **Output coding affects evidence formation before retrieval.** Source-position access and relational provenance can be causally separated. A fixed historical answer-to-label intervention predicts output-namespace counterfactuals, and native operation removal establishes a functional contribution.
2. **The historical messages carry learned associations.** Counterfactuals preserving label words, positions, and input multisets distinguish relational content from a static output signal. These effects remain under full-source reading and on real sentiment text.
3. **Formation and reading impose different functional constraints.** A prospective comparison of selective formation, complete source separation, and query-only isolation produces different outcomes for two source-specific rules. Public source–output relations can also improve their joint use through formation while private histories remain isolated; direct query access gives different results. Equivalent public backgrounds yield different joint cache compatibility, including under identical output words. Criterion–convention counterfactuals show why association transfer does not by itself specify a full criterion program.

Our contribution builds on existing contextualization mechanisms. The increment is a tested account of output-dependent relational provenance and its consequences for source-conditioned evidence use. It does not rely on future models continuing to fail the task.

![Tested formation and reading interfaces](results/figs/fig_source_evidence_overview.png)

*Figure 1. Historical formation creates contextualized evidence for both sources. Changing B can affect evidence at A positions, while full-source reading can also access B-position caches. Arrows denote tested causal interfaces and information access.*

## 2. Measuring which source's relations influence a prediction

### 2.1 Sources, rules, and materials

The current sentiment and dual-aspect experiments contain eight demonstrations from each source and eight novel queries. In shared-word conditions both sources use `no/yes`, with private label polarity balanced across contexts; separate-word conditions keep A’s words and give B `pass/flag`; earlier Measuring Hate Speech experiments use `safe/toxic`. A's raw examples and labels are held fixed; paired counterfactuals change B. A single-aspect sentiment task separates association from output naming. A dual-aspect task independently varies food and service sentiment, B's inferred criterion, and its private output convention. Original SST5 reviews supply a natural-text test with independently sampled demonstrations and official held-out queries.

All models are frozen: Qwen3-8B, Qwen3-14B, and Qwen3-32B post-trained hybrid checkpoints, Mistral-7B-v0.3 base, and Llama-3.1-8B base. We score the serialized task as a continuation using FP32 eager attention. Confirmation uses new materials after discovery, without selecting models, contexts, or seeds by correctness. Model revisions, actual token streams, and complete split rules are recorded in the [appendix](PAPER_APPENDIX.md).

### 2.2 Positional access and functional provenance

Write the contextualized source caches and prediction as

\[
H_A=F_A(D_A,D_B),\qquad H_B=F_B(D_A,D_B),\qquad z=R(q,H_A,H_B).
\]

Here \(z\) is the difference between the two output-label logits (`yes` minus `no` in the current sentiment experiments). The notation describes intervenable quantities rather than separate neural modules. To measure B-relation dependence, we change B's input–label pairing while fixing A and the query. We also prevent **every query position** from accessing B positions. Any remaining B-rule effect must reach the prediction through the remaining contextualized graph.

Under this restriction, changing B's rule changes 17.6% [12.1, 23.8] of A's answers in 32 independent Qwen3-8B Measuring Hate Speech contexts (E90). Separating B's output vocabulary reduces the inherited effect even though A's raw demonstrations and labels are unchanged. Source identity also has native causal effects in earlier interventions. Thus the result concerns the provenance of contextualized evidence, rather than a model completely ignoring source names.

## 3. How output identities shape historical evidence

### 3.1 A frozen formation-path prediction

We compare shared-output and separate-output prefixes, keeping A's examples and output words identical. Counterfactual donor states replace historical B-answer-region K, V, or KV **only in messages consumed at A's label positions** during prefix processing. Subsequent states evolve normally. Interchanging the resulting A-label caches into one otherwise pristine recipient tests the specified formation interface.

The prediction has coefficient one: the message-intervention effect predicts the actual namespace counterfactual at that interface. No head, layer, strength, or regression coefficient is selected. We report raw effects and rule double contrasts, which subtract the namespace effect between two B-association worlds. This separates relation-dependent naming effects from a common output shift.

In new contexts, K reconstruction gives rule-double-contrast correlations .969 and .966 for Qwen3-8B and Mistral on the controlled Measuring Hate Speech task; KV gives .985 and .977. The same frozen mechanism remains predictive on controlled sentiment and real SST5 text. These are actual-donor causal reconstructions: their target is a specified interface effect, and residuals are measured against the coefficient-one identity prediction.

### 3.2 Testing the native operation

Reconstruction alone does not establish native contribution. We therefore block historical B-answer access at A-label receivers during ordinary prefix processing, using the same fixed mask at every layer. There is no donor activation. A complementary test blocks all B-to-A prefix access, then reopens only the historical answer-to-label path. Within-A answer removal and single-source private functions control for disturbance to general historical learning.

| Model, n=32 | Full-source operation removal | A-only restricted restoration | Full-source restricted restoration |
|---|---:|---:|---:|
| Qwen3-8B | 1.649 [1.108, 2.250] | 1.455 [0.999, 1.945] | -0.806 [-1.365, -0.266] |
| Mistral-7B-v0.3 | 1.054 [0.886, 1.227] | 0.647 [0.463, 0.835] | 0.140 [0.053, 0.231] |
| Llama-3.1-8B | 0.808 [0.517, 1.109] | 0.958 [0.635, 1.276] | -0.233 [-0.336, -0.122] |
| Qwen3-14B | 1.329 [0.967, 1.717] | 1.120 [0.673, 1.646] | 0.039 [-0.217, 0.287] |


For each context, the signed B-rule response is the query mean of A-correct-label-oriented margins, D = mean[g_A(q)(z_cross(q) − z_origin(q))]. Removal reports D_native − D_blocked; restricted restoration reports D_restore − D_all-B-off. The targeted native removal reduces B-rule influence in every checkpoint. Reopening the path in the restricted graph increases influence under A-only reading, but has negative, positive, or uncertain effects under full-source reading. Thus its function depends on the subsequent evidence environment. Masks renormalize attention and later states remain live; the experiment identifies the operation's conditional contribution rather than a fixed additive message fraction. In Mistral, removing its own answer history also impairs its private function, and Qwen's cross-versus-within specificity interval includes zero. Complete controls remain in the appendix.


## 4. The messages transmit relationships, not only label identity

Namespace changes might alter output-related signals without changing learned relational content. We therefore hold B's label stream, source names, positions, and input multiset fixed, and reassign comments across opposite sentiment classes. A matched within-class reassignment moves the same number of inputs without reversing the association. A's raw evidence and novel queries stay fixed; paired token geometry is matched before model scoring.

For each world, we measure the correct-label-oriented query effect, then compare its magnitude between cross-class and within-class reassignment. Historical answer KV has an excess effect of .618 [.446, .813] nats in Qwen and .404 [.313, .499] in Mistral under A-only reading. V carries substantial content, while the namespace reconstruction is more accurately reproduced through K/KV. This dissociates the intervention's relation content from its output-identity effect without assuming independent internal components.

The relation effect also holds when queries can read both sources. Moreover, crossing A-position caches formed under shared/separate namespaces with B-position caches from the same backgrounds changes native B-rule dependence. The signed interaction is positive in the three smaller checkpoints and negative in Qwen3-14B (−.686 [−1.133, −.237] nats). The model therefore consumes jointly formed evidence; its source caches are not independent stores whose effects can be assumed additive.

The answer-region pathway reproduces part of the relation effect. Full label interchanges have additional effects, and the signed relation contrasts vary by model. These distinctions motivate measuring complete functional behavior in the next experiment, rather than equating a message effect with a fully transferred rule.

## 5. A constructive test: preserve relations while retaining context

### 5.1 Competing formation and reading policies

The formation account predicts different consequences for three operations: selectively limiting other sources' answer messages, removing all cross-source formation, and restricting only query access. The first tests whether limiting answer sharing protects private mappings while retaining other contextual paths; the second can also remove useful shared information; the third acts on evidence already formed.

We fix three prefix policies—native, symmetric other-source answer removal at label receivers, and all cross-source removal—and two whole-query scopes. Both source requests use the same prefix. On dual-aspect comments, B's food/service criterion and same/opposite private convention vary independently. The primary averages two-candidate accuracy over both sources, worlds, and queries within each context. Single-source functions and a one-sentence instruction are evaluated separately.

### 5.2 Independent functional confirmation

Selective formation improves mean accuracy by 2.93 [1.42, 4.35], 3.42 [1.17, 5.76], 7.37 [5.37, 9.43], and 2.78 [0.49, 4.79] points in Qwen3-8B, Mistral, Llama, and Qwen3-14B. It outperforms complete cross-source formation removal in every checkpoint. Gains concentrate on conflicting correct labels; agreeing-label cases lose 2.34 [0.78, 4.00] points in Qwen3-8B and 3.61 [1.56, 5.86] in Qwen3-14B. Individual-source gains are not uniformly confirmed. Query-only isolation gives larger gains in Llama and Qwen3-14B, so selective formation is not a universally optimal policy.

Formation isolation and query isolation control different routes: complete formation isolation can increase convention influence when the query reads both sources, whereas combining it with source-only reading gives the graph-required zero B-world effect on A. These are constructive policy tests with known source ownership. Masks remove unequal edge sets, renormalize attention, and leave subsequent states live; the comparison measures functional consequences rather than an equal-mass isolated component. Appendix C retains every policy, source, agreement tradeoff, and private-function control.

### 5.3 Association influence and criterion-related function

Source-conditioned use also depends on what a learned association does to a new input. To test this, we independently reverse B's private convention under food and service criteria, holding A fixed. Responses are projected onto food, service, bias, and their interaction. The resulting two-by-two criterion–feature matrix distinguishes changing the amount of influence from changing its functional direction.

In Qwen3-14B, native food and service selectivity are .282 [.199, .371] and .404 [.294, .528] nats. A prospective within-context normalized determinant is .410 [.330, .493], rejecting a restricted account in which both criteria only rescale one common functional direction. With the query prohibited from reading B, it is still .190 [.073, .310]. Local label and answer-message interfaces yield different responses. Historical answer KV only partially reconstructs the **actual label-interface** criterion counterfactual (r=.668, RMSE=.646, zero RMSE=.746).

Thus association transfer, full-history criterion dependence, and correct source-conditioned use are distinct measurable properties. The complete response matrices and negative effects are retained in the appendix; a positive aspect response alone is not sufficient evidence for a complete abstract criterion program.

## 6. Natural-text formation with usable private rules

### 6.1 Mechanistic replication with reliable private conventions

We repeat the frozen 43-condition engine on original extreme-polarity SST5 reviews. Demonstration pools are disjoint text-hash partitions of training; discovery and confirmation queries use official validation and test splits. Gold sentiment and token geometry determine construction, without screening model outputs. Positive and inverted private conventions have single-source accuracies of 88.3–99.2% across the four checkpoints (Appendix D).

The same coefficient-one KV formation reconstruction gives rule correlations .931/.948/.930/.966 in Qwen3-8B, Mistral, Llama, and Qwen3-14B, respectively. Fixed-output association excess magnitudes are positive in every family. Llama's signed relation contrast is negative (−.109 [−.194, −.024] nats): transmitted content is not uniformly a correction of the requested rule. SST5 provides a functionally usable natural-text replication; these constructed conventions do not recover individual human preferences.

### 6.2 A prospective test of real-text source-function use

We next test the functional policy prediction on new SST5 contexts. A and B infer the same sentiment criterion but can adopt opposite private conventions. Origin and cross-convention worlds receive equal primary weight; a within-class movement remains a separate control. The same three formation policies and two query scopes are evaluated for both sources from each common prefix. A keeps `no/yes`; B uses either those shared words or `pass/flag`. Single functions and one-sentence source instructions are retained in all 85 conditions.

| Model, confirmation n=32 | Shared native accuracy, % | Selective formation, % | Selective-minus-native, pp [95% CI] | Query-only-minus-native, pp [95% CI] |
|---|---:|---:|---:|---:|
| Qwen3-8B | 84.86 | 92.19 | 7.32 [5.37, 9.28] | -0.39 [-3.12, 2.44] |
| Mistral-7B-v0.3 | 88.77 | 94.14 | 5.37 [2.93, 7.71] | 5.96 [3.22, 8.59] |
| Llama-3.1-8B | 81.25 | 90.72 | 9.47 [7.52, 11.52] | 16.70 [14.36, 19.04] |
| Qwen3-14B | 89.94 | 97.36 | 7.42 [5.57, 9.38] | 3.81 [1.27, 6.25] |

Selective formation improves the shared-word primary in all four checkpoints, with independently positive A and B gains. Candidate and full-vocabulary primary scores coincide here. Benefits concentrate on opposite conventions; same-convention effects are small and uncertain. The predefined B-convention response also decreases under selective formation while A's output words remain fixed (Appendix F), connecting the accuracy change to relational influence. Query-only isolation remains more effective in Llama and less effective in the two Qwen checkpoints; Mistral's point ordering is uncertain.

Separate words expose a further distinction. Complete cross-source formation isolation retains about 94–97% own-word candidate accuracy, yet full-vocabulary accuracy falls to about 51–54%: the model frequently outputs the other source's word. Thus learning within a label space and using that convention jointly require separate measurements. Native separate-word candidate accuracy is already high, so its smaller selective gains also reflect headroom and word priors. Mistral loses 1.27 [0.20, 2.44] full-output points under selective formation despite unchanged candidate accuracy. Appendix F preserves every namespace, private direction, source, actual output, and instruction control.

![Real-text policies and output-space use](results/figs/fig_natural_source_function_policies.png)

*Figure 2. All formation/query policies on independently confirmed real-text private functions. Colored circles score within the requested source’s two words; black crosses score the actual full-vocabulary output. The separate-word condition reveals failures hidden by candidate restriction.*

### 6.3 Sharing identities while keeping supervision private

What can be shared without exchanging private supervision? With cross-source demonstration formation blocked, we cross access to an unlabeled source-name list during formation and whole-query reading, using unrelated names as control. Qwen3-8B has a formation-specific full-output gain of 4.59 [2.73, 6.64] points, with uncertain candidate gain; Mistral's effect is negative and Llama's uncertain (Appendix G). Names alone therefore provide a partial, model-dependent account of the missing shared information.

### 6.4 Sharing an output schema before private rule learning

We next share a source-to-word-set table before independent formation, for example Alex: no, yes; Sam: pass, flag. It specifies output spaces, without review–label pairs or private polarity. An unrelated-name table has the same words and structure; a swapped table reverses the real sources' word assignments. Formation and query access are crossed while all private cross-source formation remains blocked.

True-minus-unrelated formation-only gains in full-vocabulary accuracy are 26.66 [23.05, 30.47], 7.71 [5.08, 10.45], and 8.30 [6.05, 10.84] points in Qwen3-8B, Mistral, and Llama. Direct reading-only contrasts include zero in all three. Public relational information therefore affects jointly usable private evidence through formation, even when no query position can read it.

Literal table routing is insufficient: correct tables outperform swapped tables, but swapped tables themselves improve full accuracy and reduce other-source outputs in every checkpoint. Qwen's candidate accuracy also falls, and some source-specific gains remain uncertain (Appendix H). The result identifies useful shared formation structure, with costs; the next test asks whether information-equivalent structures form equally compatible evidence.

![Public schemas during formation and reading](results/figs/fig_public_source_schema_coordination.png)

*Figure 3. Public source–word-set access with private historical supervision isolated. Solid curves score the actual full-vocabulary output; dashed curves score within the requested source's candidates. Correct and swapped relations both help through formation, but their magnitudes differ.*

### 6.5 Common formation backgrounds constrain joint rule use

We keep every public relation and private demonstration fixed, reversing only the two rows of the correct schema. Private cross-source formation remains blocked, and no query position can read the table. Each ordering supplies the same facts but forms its own pair of source caches. We combine A and B caches from one ordering (00 or 11), or from different orderings (01 or 10), interchanging all private K/V states at unchanged global positions.

With separate word sets, coherent composition improves full-output use much more than within-source candidate judgments (E126; Appendix I). A post-hoc diagnosis finds that most wrong-source words also match that other source's private convention. This motivates a prospective test with identical output words: a model must select the appropriate learned mapping even though the words themselves cannot identify a source.

E127 fixes four checkpoints and both shared/separate namespaces before scoring. Its primary uses shared words and opposite private conventions, where the two sources require different answers. The coherent-minus-mixed contrast averages 00 and 11 against 01 and 10. It cancels additive differences in individual-cache quality, while retaining the joint reader's nonlinear behavior.

Coherent composition improves shared-word, opposite-convention accuracy by 8.89 [6.64, 11.13], 5.86 [4.10, 7.71], 0.78 [0.10, 1.56], and 9.38 [7.32, 11.52] points in Qwen3-8B, Mistral, Llama, and Qwen3-14B. The source-conditioned margin also increases in each checkpoint (Appendix J).

The same dependence therefore extends beyond selecting a distinguishable word set. The paired source-conditioned margin is one half of the gold-A-oriented difference between A and B requests. A single request-independent output shift cancels in this difference and cannot explain its positive change. This is an equivalent projection of the two-source margins, not an additional independent mechanism measure.

The caches retain strong requested-source-only functions, yet coherent joint-reading mean accuracy under conflicting conventions is only 53–65%. The small Llama effect and nonuniform private-direction gains remain reported. With food/service criteria instead of opposing codes, coherent formation yields a smaller gain: Qwen3-14B improves by 2.93 [0.59, 5.47] points, while the other accuracy intervals touch or cross zero; joint-reading mean accuracy is about 50–53% (Appendix K).

These comparisons show that local private-function accuracy does not determine joint usability. The shared-word result exceeds a word-set-only explanation, and the source-request margin excludes a single request-independent output shift. It remains compatible with contextual binding and competitive retrieval. Whole-cache interchanges do not identify a new binding ID or a complete abstract criterion program; all cache pairs, common shifts, and private controls remain in Appendices I–K.

### 6.6 The same formation and operation chain in a larger model

We repeat the fixed formation, native-operation, and real-text function tests in Qwen3-32B, with a fresh Qwen3-8B confirmation anchor. The two sizes receive byte-identical contexts within each stage. All 43/64/85 conditions, K/KV/V channels, reading backgrounds, private directions, and instructions are retained. Discovery uses n16 and confirmation n32 without selecting by discovery effects. Full FP32 weights and eager attention are kept, with no fitted head, layer, intervention strength, or reconstruction coefficient.

| Qwen3, matched confirmation n32 | A-formation signed, nats | Native operation removal, nats | Selective-minus-native full, pp | Query-only-minus-native full, pp |
|---|---:|---:|---:|---:|
| 8B | 2.351 [1.857, 2.837] | 1.762 [1.264, 2.294] | 7.62 [5.18, 9.96] | −2.54 [−6.54, 1.46] |
| 32B | 2.676 [2.266, 3.096] | 1.972 [1.467, 2.500] | 7.71 [5.76, 9.57] | 5.86 [4.20, 7.52] |

The 32B formation batch has 100% single-source accuracy under both private directions, while the historical relation-formation effect remains. Coefficient-one label-interface KV reconstruction has raw r=.883 and rule-double-contrast r=.922, with raw RMSE .864 versus zero-prediction RMSE 1.857. Native restricted restoration is positive under A-only reading (+.775 [.321, 1.284] nats) and negative under full-source reading (−.544 [−.833, −.276]), as in the fresh 8B anchor. The same formation operation therefore contributes in the larger model, with its function depending on the subsequent reading environment.

On real-text shared-word functions, 32B native full accuracy is 87.99%, rising to 95.70% with selective formation; its advantage over complete cross-source formation removal is 20.41 [18.16, 22.36] points. The paired selective-gain difference is .10 [−3.22, 3.32] points, while the query-only gain differs by 8.40 [3.81, 13.09]. Formation and reading contributions can thus vary separately across these checkpoints. Their training recipes also differ, so the paired comparison characterizes computation across sizes rather than estimating a parameter-count scaling law. Both requested-source gains, agreement tradeoffs, separate-word output failures, and all reconstruction targets are retained in Appendix M.

## 7. Related work and positioning

[Cho's circuit](https://arxiv.org/html/2410.04468v3), [information removal](https://arxiv.org/abs/2509.21012), [Contextualize-then-Aggregate](https://arxiv.org/html/2504.00132v2), and [How Few-Shot Examples Add Up](https://arxiv.org/html/2605.16591v2) establish input merging, information selection, contextualization, and QK/V contributions. [Sun et al.](https://aclanthology.org/2025.acl-long.196/) trace input–label mappings, including 70B/72B checks. These explain important components of our setting. We add a measurement of whose learned relations enter evidence, an output-dependent formation prediction, and its native and functional consequences.

[Local task vectors](https://aclanthology.org/2026.findings-acl.314/) and [just-in-time representations](https://arxiv.org/html/2509.04466v3) establish heterogeneous task states. [Feng and Steinhardt](https://arxiv.org/html/2310.17191v2), [Dai et al.](https://aclanthology.org/2024.emnlp-main.967/), and [Mixing Mechanisms](https://arxiv.org/html/2510.06182v2) explain binding, ordering, and competing retrieval mechanisms; [Test, then Route](https://arxiv.org/html/2608.04183v1) separates predicate testing from token-dependent routing. Our relational-content and compatibility tests do not establish a new binding component. [Parallel Context Windows](https://aclanthology.org/2023.acl-long.352/) and [CacheBlend](https://arxiv.org/abs/2405.16444) already address independently computed prefixes and KV context dependence. Our counterfactual fixes public facts and private positions, blocks private supervision exchange, and tests joint function under equivalent formation backgrounds.

[Task recognition/learning](https://arxiv.org/html/2509.24164v2) separates label-space alignment from within-space mappings; [Li et al.](https://aclanthology.org/2024.acl-long.669/) test task composition and label remapping. [Demonstration Conflict](https://arxiv.org/html/2603.04464v1) studies corrupted demonstrations, and [Jurisdiction](https://arxiv.org/html/2609.27603v1) studies contextual authority over prior knowledge. Here both inferred source rules are legitimate; this motivates our question without establishing novelty by setup alone. [Yu and Ananiadou](https://aclanthology.org/2024.emnlp-main.192/), [Crosbie and Shutova](https://aclanthology.org/2025.findings-naacl.283/), and [Racing Thoughts](https://aclanthology.org/2025.naacl-long.155/) motivate operation-specific causal tests. [Lepori et al.](https://aclanthology.org/2026.acl-long.676/) and [CoSToM](https://aclanthology.org/2026.acl-long.421/) separate internal information from deployment; our frozen-model functional tests do not claim this general distinction first.

## 8. Reproducibility

Intervals use 10,000 context-bootstrap samples; queries within a context are not independent units. All predefined conditions, private directions, negative results, and reconstruction channels remain reported. We check actual token/mask consumption, full-token/cached scores, self interventions, graph-zero controls, and pristine caches. Independent sessions recompute raw quantities and graph/gold layouts before reading author summaries; these are independent analyses, not GPU reruns. Cards, script hashes, revisions, small summaries, figures, and audits are versioned. Raw JSONL and weights remain at the [documented asset paths](README.md); complete interfaces and serialization are in the appendix.

## 9. Discussion

Source-conditioned ICL reads evidence whose relations were formed across a contextual history. Selecting the requested source's positions therefore does not establish the provenance of the supervision influencing its answer. Shared output identities shape this historical formation: the pathway transmits learned relations, predicts namespace counterfactuals, and contributes to ordinary predictions. Its functional contribution changes with subsequent reading, including in the larger checkpoint.

This account produces constructive predictions. Selectively limiting answer-level sharing can preserve private judgments, while removing all historical sharing can impair joint use. Public source–output relations help through formation even when private supervision cannot cross sources and the query cannot read the public table. Information-equivalent formation backgrounds also change compatibility under shared output words. Thus understanding relevant evidence requires explaining both the formation of private associations and their coordination during reading. The question remains meaningful when a model answers correctly.

## Limitations

The experiments cover three families, including 14B and 32B same-family checkpoints. They do not isolate parameter count from training recipe. Dual-aspect templates fix food before service; their responses do not establish a position-independent criterion program. Pre-input source-cue transfer does not reliably deploy both criteria despite usable private functions (Appendix L); small responses and other native task-state routes remain possible.

Cache interchanges and renormalized masks test specified interfaces with unmodeled paths; policy masks remove unequal edge sets. Reconstructions use actual donor activations. Intervals are not corrected for all comparisons. Private conventions are constructed, and SST5 sentiment may occur in pretraining. Earlier practical evaluations found limited accuracy consequences of source mixing. These constraints preserve the demonstrated formation and use results while limiting applications and full-algorithm claims. The [technical appendix](PAPER_APPENDIX.md) retains all controls and the [claim ledger](CLAIMS.md) records registered scope.
