# Technical appendix: source-evidence formation and use

2026-10-12. This preserves the complete interfaces and functional readouts supporting the main manuscript. Primary definitions and experiment-card links remain unchanged.

## A. Complete criterion–convention functional response

### A.1 Separating criterion from private output convention

A learned association can change a classifier's confidence without specifying a complete criterion for a new input. We test this distinction with comments containing independently balanced food and service sentiment. Source A's demonstrations establish a food criterion. Source B can evaluate either food or service, under an output convention agreeing with or opposite to A's. The criteria are inferred from demonstrations rather than stated in the multi-source prompt (E117/E118).

The four B worlds are constructed by bijectively reassigning inputs to fixed demonstration positions. A's raw demonstrations, B's output stream, source names, positions, and input multiset remain unchanged. Eight novel queries cover all four sentiment combinations. Every interface is evaluated on the same queries: complete native histories, histories whose queries cannot read B positions, A-label cache interchange into one recipient, and historical B-answer messages consumed during A-label formation. Separate-output label donors test the effect of output coding during formation while restoring the shared-output recipient for querying.

Let \(f_q,s_q\in\{-1,+1\}\) be food and service polarity, oriented to A's private convention. For criterion \(t\), define \(\delta_t(q)=\frac{1}{2}[z_{t,+}(q)-z_{t,-}(q)]\), the response to changing B's convention. The context-level matrix

\[
M_c=\begin{pmatrix}
\mathbb E_q[\delta_{food}(q)f_q] & \mathbb E_q[\delta_{food}(q)s_q]\\
\mathbb E_q[\delta_{service}(q)f_q] & \mathbb E_q[\delta_{service}(q)s_q]
\end{pmatrix}
\]

separates the two criteria's effects on the two aspects. Bias and food–service interaction are also retained. These are B-relation effects while A is requested, not B's own accuracy or a gain in correctly isolating A.

### A.2 Association magnitude and criterion selectivity give different answers

Across three model families, E117 confirmation finds that changing B's pairing alters both food and service sensitivity through A-label caches. A positive service response alone therefore cannot establish transport of B's service criterion. E118 independently crosses criterion with B's convention and preserves the entire response matrix. Full native histories show more criterion selectivity than local label interchanges in several settings, with substantial family variation. The mean criterion–feature interaction is positive in all three families, but Qwen3-8B's interaction mainly reflects service selectivity; unequal gains along one common direction can also produce a positive mean interaction.

![Full criterion response matrices across three families](results/figs/fig_criterion_code_responses.png)

*Figure 4. New-material confirmation, 32 contexts per family. Rows vary B's inferred criterion; columns measure the induced food/service response under independent B-convention reversal. The requested source remains A. Full matrices avoid equating one positive aspect response with complete criterion transfer.*

Separating B's output namespace during formation can lower both aspect responses without appreciably changing their mean selectivity contrast. In Llama, food-criterion responses decrease by .267/.243 nats on food/service, and service-criterion responses by .110/.079; all four paired intervals are negative. Namespace effects on evidence formation thus include a change in relational influence magnitude, not only which aspect dominates.

### A.3 A prospective functional-direction test in Qwen3-14B

Before any E119 scores, we freeze an additional observer: the determinant of each context's response matrix and its normalized determinant, \(\det(M_c)/(\|M_{c,food}\|\|M_{c,service}\|)\). If the two criteria merely rescale a common functional direction, each determinant is zero. These quantities are computed within context before averaging. A row norm of at most .001 nats sets the normalized statistic to zero while retaining the context; no confirmation context meets this threshold.

Qwen3-14B confirms criterion-specific native responses: food selectivity is .282 [.199, .371] nats and service selectivity .404 [.294, .528]. Native signed determinant is .568 [.408, .751] nats² and normalized determinant .410 [.330, .493]. When every query position is prohibited from reading B, the A cache still formed from the full history yields .0289 [.0032, .0553] and .190 [.073, .310]. Thus criterion-related history can have distinct functional effects through the remaining computation.

| Qwen3-14B interface, n=32 | Mean interaction J, nats [95% CI] | Signed determinant, nats² [95% CI] | Normalized determinant [95% CI] |
|---|---:|---:|---:|
| Complete native histories | .343 [.265, .433] | .568 [.408, .751] | .410 [.330, .493] |
| Full history, A-only query | .058 [.029, .089] | .0289 [.0032, .0553] | .190 [.073, .310] |
| A-label interchange | −.0238 [−.0478, −.0025] | −.0201 [−.0374, −.0052] | .006 [−.121, .140] |
| A-label interchange, A-only query | .038 [.012, .068] | .0074 [−.0106, .0271] | .124 [.017, .242] |
| Historical answer KV at formation | .0060 [.0029, .0093] | .00068 [.00012, .00130] | .085 [−.042, .214] |
| Historical answer KV, A-only query | .0126 [.0076, .0188] | .00194 [.00031, .00474] | .072 [−.040, .190] |
| Separate-output label donor | −.0192 [−.0348, −.0060] | .00192 [−.00123, .00556] | .011 [−.145, .164] |

The local label interface does not reproduce the full native responses. Its negative signed determinant also rules out describing every formation interface as a common-direction gain; the gated label interface has a small positive normalized response. The signed and normalized statistics weight contexts differently, so both are reported. Nonzero determinants reject the restricted functional common-direction account, not every nonlinear latent representation or an alternative retrieval policy.

Historical answer KV only partially predicts the actual criterion-label counterfactuals: native/gated raw correlations are .668/.665, RMSE .646/.878, compared with zero-prediction RMSE .746/1.018. This is a functional boundary of the formation reconstruction, not a reason to discard its successful namespace prediction. Local association transfer, whole-history criterion dependence, and source-conditioned use are different causal questions.

![Stronger-model functional responses and all frozen observers](results/figs/fig_stronger_model_functional_responses.png)

*Figure 5. Qwen3-14B confirmation. Matrix means summarize functional responses; determinant intervals use determinants computed separately within each context. All seven predefined interfaces, including reverse and weak effects, are retained. Different cache interfaces do not establish different hidden algorithms.*

## B. Exact serialization, interchanges, and audit scope

Experiments use frozen Qwen3-8B and Qwen3-14B (both post-trained hybrid models), Mistral-7B-v0.3 base, and Llama-3.1-8B base, FP32 eager attention, PyTorch 2.8.0 and Transformers 4.57.6. The controlled sentiment task contains eight demonstrations from each source and eight new queries per context. Source names, private output direction, and demonstration order vary; the two private directions are balanced in confirmation. Shared outputs are `no/yes`; separate B outputs are `pass/flag`. A's outputs remain unchanged. Models process the serialized task as a continuation, without adding a chat template or generating reasoning. Qwen3-14B is a same-family size comparison; training data and recipes are not controlled between sizes. The two-aspect templates always mention food before service, so this experiment measures functional aspect distinctions under fixed order and does not separate semantic identity from position selection.

The actual serialized token stream is part of the method. Blocks, answer words, and separators are encoded separately. For Mistral, this introduces fixed extra spaces relative to literal whole-string encoding: the first native confirmation context has 351 rather than 335 tokens. Its B answer-message region includes the answer word plus three separator tokens per demonstration, totaling 32 sender positions; Qwen uses 16. Paired token positions and boundaries remain identical across the relevant manipulations. Native controls validate the actual stream, not a claimed equivalent whole-string encoding. Source code and independent tokenizer reconstruction preserve this disclosure.

Effects use 10,000 context-bootstrap resamples, seed 910; reconstruction intervals follow the frozen E109 analysis. Queries within a context are not treated as independent observations. Raw logits, full-vocabulary argmax, binary candidate-label accuracy, all conditions, and failed controls are retained. Confirmation uses new word/template pools; discovery-to-confirmation text overlap is zero for E113 and the Qwen E114 batches, but vocabulary/templates recur across contexts within a pool.

Self interchanges produce zero error. Cached versus full-token native query scoring differs by at most 4.96e−5 in Qwen and 7.63e−6 in Mistral confirmation. Cache fingerprints, layer consumption, and matched token geometry are checked. An independent session reconstructs the token layouts and recomputes 559 numerical checks from raw records before reading author summaries, with maximum discrepancy 4.77e−15. Separate bootstrap resampling confirms the signed interactions; it is not represented as an independent GPU rerun.

The earlier E113/E114 package comprises five runs and 36,736 scores. The completed E115–E119 expansion comprises 24 discovery/confirmation runs, 576 contexts, 181,632 scores, and 2.393 recorded GPU-hours. Independent raw reviews recompute 36,750 numerical quantities (maximum discrepancy 1.13e−14), reconstruct actual token layouts, and check recorded all-layer consumption. This is independent analysis, not an independent GPU rerun. The E120/E121 native-operation and real-text additions comprise 16 runs, 384 contexts, 164,352 scores, and 2.540 recorded GPU-hours. Their independent raw audits recompute 18,064 scalars (maximum discrepancy 5.00e−15), reconstruct 2,112 actual token streams, and verify the recorded masks and reachable edges. No weights are trained. All model/seed/channel results remain available. Cards specify revisions, script hashes, and rebuilding commands; small summaries, figures, code, and audits are versioned, while raw JSONL and models remain at the [documented asset paths](README.md).


## C. All formation/query policies and functional controls

Policy results average the two source requests, four B worlds, and eight queries within each context. Candidate accuracy and full-vocabulary argmax remain separate in raw records. `normal`, `answer_cross_off`, and `all_cross_off` use no trained parameters; the generated source ownership determines the mask. Both actors consume the same prefix cache.

| Model, confirmation n=32 | Native | Answer formation | All cross formation | Query only | Answer + query | All formation + query |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3-8B | 71.58 [69.43, 73.44] | 74.51 [72.66, 76.17] | 62.60 [61.62, 63.67] | 70.46 [67.87, 73.05] | 73.78 [71.58, 75.73] | 73.29 [70.80, 75.68] |
| Mistral-7B-v0.3 | 69.14 [67.63, 70.65] | 72.56 [70.31, 74.85] | 62.74 [60.99, 64.55] | 70.85 [69.14, 72.46] | 71.97 [69.87, 74.12] | 73.54 [71.04, 75.88] |
| Llama-3.1-8B | 73.83 [72.22, 75.44] | 81.20 [79.10, 83.25] | 68.55 [66.75, 70.26] | 85.89 [84.08, 87.74] | 86.77 [85.11, 88.53] | 84.18 [81.30, 86.87] |
| Qwen3-14B | 78.12 [75.68, 80.76] | 80.91 [78.86, 82.86] | 67.58 [66.02, 69.19] | 84.23 [81.64, 86.82] | 83.30 [80.81, 85.69] | 82.91 [80.22, 85.64] |

All entries are accuracy percentages with context-bootstrap95%CI. Separate A/B, agreeing/disagreeing correct labels, all four criterion/convention worlds, single functions, one-sentence instructions, Food/Service/bias/FS responses, and all signed contrasts are in `results/e122/*_confirmation/analysis.json` and the [independent raw audit](results/e122/independent_review_2026-10-12.md). The single-aspect SST ability does not establish perfect dual-aspect primitive mastery.

| Model, n=32 | Single A | Single B service/same | Single B service/opposite | Single B food/same | Single B food/opposite |
|---|---:|---:|---:|---:|---:|
| Qwen3-8B | 67.97 [64.06, 71.88] | 83.59 [79.69, 87.50] | 80.08 [76.17, 83.98] | 70.70 [67.58, 73.44] | 72.66 [69.14, 75.78] |
| Mistral-7B-v0.3 | 72.66 [69.53, 75.39] | 72.27 [68.36, 75.78] | 75.78 [72.27, 79.30] | 76.95 [73.83, 80.08] | 76.56 [73.44, 79.69] |
| Llama-3.1-8B | 79.30 [75.00, 83.59] | 87.11 [83.59, 90.62] | 86.33 [82.03, 90.62] | 82.42 [78.12, 86.72] | 81.64 [76.95, 85.94] |
| Qwen3-14B | 82.42 [78.91, 85.94] | 85.55 [81.64, 89.45] | 88.67 [84.77, 92.58] | 83.59 [80.08, 87.11] | 84.77 [80.86, 88.67] |

![Complete policy accuracy](results/figs/fig_source_function_formation.png)

Bars show the source-average primary; black circle/triangle show A/B means. These are not joint both-correct rates. Each paired contrast uses its context-level difference, not differences between separately constructed intervals.

| Model | Selective-minus-native A, pp | B, pp | Agreeing golds, pp | Disagreeing golds, pp | Selective-minus-all formation, pp |
|---|---:|---:|---:|---:|---:|
| Qwen3-8B | 1.37 [-0.68, 3.32] | 4.49 [2.15, 6.84] | -2.34 [-4.00, -0.78] | 8.20 [5.86, 10.45] | 11.91 [10.25, 13.53] |
| Mistral-7B-v0.3 | 5.66 [2.54, 9.08] | 1.17 [-1.27, 3.52] | -1.95 [-4.98, 0.88] | 8.79 [6.15, 11.62] | 9.81 [6.74, 13.04] |
| Llama-3.1-8B | 8.01 [4.79, 11.33] | 6.74 [4.49, 8.89] | -1.86 [-4.30, 0.39] | 16.60 [13.87, 19.43] | 12.65 [10.40, 15.04] |
| Qwen3-14B | 2.83 [0.00, 5.47] | 2.73 [0.10, 5.37] | -3.61 [-5.86, -1.56] | 9.18 [6.15, 12.30] | 13.33 [11.33, 15.38] |

## D. Native operation and real-text completeness

| Model, n=32 | Full-source operation removal | A-only restricted restoration | Full-source restricted restoration |
|---|---:|---:|---:|
| Qwen3-8B | 1.649 [1.108, 2.250] | 1.455 [0.999, 1.945] | -0.806 [-1.365, -0.266] |
| Mistral-7B-v0.3 | 1.054 [0.886, 1.227] | 0.647 [0.463, 0.835] | 0.140 [0.053, 0.231] |
| Llama-3.1-8B | 0.808 [0.517, 1.109] | 0.958 [0.635, 1.276] | -0.233 [-0.336, -0.122] |
| Qwen3-14B | 1.329 [0.967, 1.717] | 1.120 [0.673, 1.646] | 0.039 [-0.217, 0.287] |

Paired signed B-rule-response differences in nats with95%CI. The operation acts at every prefix layer, masks strict historical senders, preserves self attention, and renormalizes the remaining attention. The restricted restoration opens only the historical answer→label edges; it does not restore original numerical messages or all native paths. E120 single within-answer-off controls, far-namespace effects, residuals, and signed/magnitude contrasts are in the card/results.

| Model, n=32 | Single-source positive / inverted accuracy, % | Native A-formation magnitude, nats [95% CI] | KV rule r / RMSE / zero RMSE |
|---|---:|---:|---:|
| Qwen3-8B | 98.4 / 88.3 | 2.151 [1.487, 2.895] | 0.931 / 1.363 / 3.658 |
| Mistral-7B-v0.3 | 99.2 / 96.9 | 1.091 [0.925, 1.258] | 0.948 / 0.336 / 1.048 |
| Llama-3.1-8B | 97.7 / 99.2 | 0.689 [0.488, 0.901] | 0.930 / 0.309 / 0.840 |
| Qwen3-14B | 99.2 / 93.8 | 1.678 [1.340, 2.052] | 0.966 / 0.519 / 1.949 |

Each SST private direction has n16contexts; natural-text pool/split/source provenance is independently audited. The word-plus-separator sender regions differ by tokenizer. Llama fixed-word association signed effects are negative; all K/KV/V raw/rule reconstructions and zero predictions remain in the summaries.

![Real-text formation and private functions](results/figs/fig_natural_text_formation.png)

## E. Registered evidence map

| Manuscript claim | Records |
|---|---|
| Positional access does not isolate relation dependence | [E90](experiments/E90-source-isolation-before-and-after.md), [E91](experiments/E91-label-namespace-and-inherited-rule.md) |
| Output-dependent formation reconstruction, C21 | [E109](experiments/E109-foreign-messages-at-label-formation.md), [E111](experiments/E111-polarity-relation-versus-namespace.md), [E112](experiments/E112-formation-mechanism-mistral-family.md), [first independent audit](results/e109/independent_review_2026-10-11.md) |
| Fixed-label partial association content, C22 | [E111](experiments/E111-polarity-relation-versus-namespace.md), [E113](experiments/E113-relation-content-mistral.md), [E114](experiments/E114-native-formation-reading-crossing.md) |
| Native operation contribution and restricted restoration | [E120](experiments/E120-operation-necessity.md), [independent operation audit](results/e120/independent_review_2026-10-12.md) |
| Reliable private functions and formation on natural text | [E121](experiments/E121-natural-sentiment-mechanism.md), [independent data and mechanism audit](results/e121/independent_review_2026-10-12.md) |
| Native conditional effects and interaction, C23 | [E114](experiments/E114-native-formation-reading-crossing.md), [new independent audit](results/e114/independent_review_2026-10-11.md) |
| Functional criterion response and its formation-interface boundary, C24 | [E117](experiments/E117-criterion-feature-formation.md), [E118](experiments/E118-criterion-code-feature-crossing.md), [E119](experiments/E119-stronger-model-formation-criterion.md), [E118 audit](results/e118/independent_review_2026-10-11.md), [E119 audit](results/e119/independent_review_2026-10-11.md) |
| Llama, larger checkpoint, and real-text coverage | [E115](experiments/E115-llama-frozen-native-mechanism.md), [E116](experiments/E116-native-mhs-formation-reading.md), E119; [wave audit](results/e117/independent_review_2026-10-11.md) |
| Limits and failed functional interfaces | E50–E52, E99, E107, [E110](experiments/E110-learned-relation-fixed-label-stream.md); full ledger in [CLAIMS](CLAIMS.md) |
| Joint source-function formation and query policies | [E122](experiments/E122-source-preserving-formation.md), [independent raw audit](results/e122/independent_review_2026-10-12.md) |


## F. Real-text function policies and complete output readouts

Primary accuracy averages origin/cross worlds, two requested sources, and eight queries within each context. Within-class movement is reported separately. The original primary is candidate accuracy; full-vocabulary output and word-space diagnostics are separate secondary readouts. Shared-word candidate/full-vocabulary aggregates coincide in all six confirmation policies. Private polarity is balanced across contexts; source-specific conventions are inferred from examples, not provided as explicit rules.

| Model / output words, n=32 | Native candidate / full, % | Selective candidate / full | All formation off candidate / full | Query-only candidate / full | Answer + query candidate / full | All formation + query candidate / full |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3-8B / shared | 84.86 / 84.86 | 92.19 / 92.19 | 75.00 / 75.00 | 84.47 / 84.47 | 93.85 / 93.85 | 94.34 / 94.34 |
| Qwen3-8B / far | 94.24 / 92.09 | 94.34 / 92.09 | 94.34 / 51.46 | 94.34 / 94.34 | 94.63 / 94.63 | 93.16 / 93.16 |
| Mistral-7B-v0.3 / shared | 88.77 / 88.77 | 94.14 / 94.14 | 73.54 / 73.54 | 94.73 / 94.73 | 96.39 / 96.39 | 93.16 / 93.16 |
| Mistral-7B-v0.3 / far | 98.05 / 96.00 | 98.05 / 94.73 | 95.21 / 53.71 | 97.27 / 97.27 | 97.46 / 97.46 | 95.61 / 95.61 |
| Llama-3.1-8B / shared | 81.25 / 81.25 | 90.72 / 90.72 | 75.20 / 75.20 | 97.95 / 97.95 | 99.12 / 99.12 | 99.12 / 99.12 |
| Llama-3.1-8B / far | 97.95 / 95.41 | 98.54 / 95.12 | 94.82 / 53.81 | 96.58 / 96.58 | 96.97 / 96.97 | 95.31 / 95.31 |
| Qwen3-14B / shared | 89.94 / 89.94 | 97.36 / 97.36 | 75.00 / 75.00 | 93.75 / 93.75 | 97.27 / 97.27 | 98.05 / 98.05 |
| Qwen3-14B / far | 95.90 / 95.80 | 97.27 / 97.07 | 96.68 / 52.83 | 92.97 / 92.97 | 94.63 / 94.63 | 96.68 / 96.68 |

| Model | Selective shared gain A, pp | B, pp | Opposite conventions, pp | Same conventions, pp | Shared-minus-separate gain, pp |
|---|---:|---:|---:|---:|---:|
| Qwen3-8B | 4.49 [1.56, 7.03] | 10.16 [6.05, 14.26] | 15.23 [11.91, 18.75] | -0.59 [-2.15, 0.98] | 7.23 [5.08, 9.47] |
| Mistral-7B-v0.3 | 4.49 [0.98, 8.20] | 6.25 [3.32, 9.38] | 12.11 [8.20, 16.21] | -1.37 [-3.71, 0.20] | 5.37 [2.73, 7.81] |
| Llama-3.1-8B | 7.42 [4.69, 10.16] | 11.52 [8.20, 14.65] | 19.14 [15.04, 23.24] | -0.20 [-0.59, 0.00] | 8.89 [6.84, 10.94] |
| Qwen3-14B | 4.88 [2.15, 8.20] | 9.96 [6.05, 14.06] | 15.23 [11.52, 19.14] | -0.39 [-1.37, 0.59] | 6.05 [4.30, 7.91] |

These are paired context-bootstrap95%CI. The namespace contrast is not headroom matched; word meanings/priors also differ. No layer, head, intervention strength or context is selected to improve these results.

| Model | Far/all-formation-off full accuracy A, % | B, % | Other-source word output A, % | B, % |
|---|---:|---:|---:|---:|
| Qwen3-8B | 48.24 [40.43, 56.05] | 54.69 [45.70, 63.48] | 51.17 [43.36, 58.98] | 42.58 [33.40, 51.76] |
| Mistral-7B-v0.3 | 30.86 [21.68, 40.62] | 76.56 [68.75, 83.98] | 66.99 [56.84, 76.76] | 22.27 [14.84, 30.08] |
| Llama-3.1-8B | 64.65 [58.01, 71.29] | 42.97 [34.96, 50.98] | 34.96 [28.32, 41.60] | 55.27 [47.46, 63.28] |
| Qwen3-14B | 46.09 [39.65, 52.34] | 59.57 [53.52, 66.02] | 53.71 [47.46, 60.16] | 38.48 [32.03, 44.73] |

This classification uses the actual argmax token and the other source’s two word IDs. The average other-source-word rates are 44.6–46.9%, but their A/B composition differs. In the shared-word case, surface words cannot identify their source: recording zero identifiable other-space words is not evidence of provenance isolation.

| Model | Single A, % | B opposite shared | B same shared | B opposite far | B same far |
|---|---:|---:|---:|---:|---:|
| Qwen3-8B | 95.31 [92.58, 97.66] | 94.14 [90.62, 97.27] | 97.27 [94.92, 99.22] | 92.97 [88.28, 96.88] | 94.14 [90.23, 97.66] |
| Mistral-7B-v0.3 | 98.83 [97.27, 100.00] | 98.05 [94.92, 100.00] | 98.44 [96.88, 99.61] | 98.83 [97.66, 100.00] | 98.05 [96.48, 99.61] |
| Llama-3.1-8B | 98.44 [96.88, 99.61] | 99.22 [98.05, 100.00] | 99.61 [98.83, 100.00] | 94.14 [89.84, 97.66] | 89.06 [83.58, 94.14] |
| Qwen3-14B | 98.05 [96.48, 99.61] | 96.88 [93.75, 99.22] | 98.44 [96.48, 100.00] | 95.70 [93.75, 97.66] | 96.48 [92.97, 99.22] |

The private positive/inverted halves, actual full-vocabulary controls, all one-sentence instructions, complete A convention-response/signed/within movement readouts, and all 85 condition statistics remain in the experiment summaries and independent audit. Aggregate private functions are usable but not uniformly perfect; the distinct words also have asymmetric direction priors. Formation masks remove unequal sets of edges, renormalize attention, and allow states to evolve. Consequently the result identifies functional consequences of fixed policies, not isolated representation components or a tuned performance method.

![B convention response on fixed A words](results/figs/fig_natural_source_provenance.png)

The observer is the absolute context mean of the A-gold-oriented half contrast between B conventions, computed in A’s fixed output space. It is not attention-based source ranking. Signed and matched within-class movement remain alongside it.

E123 freezes the scientific source at91374879 before the first score. Four checkpoints each execute discovery16 and confirmation32, totaling192contexts/130560scores. Scientific inputs, masks, full-output tokens, and small report data are independently checked; see [E123](experiments/E123-natural-source-function-policy.md) and its [raw audit](results/e123/independent_review_2026-10-12.md). The pinned SST downloader reproduces all three Arrow files and the Llama32 confirmation contexts byte-for-byte in the recorded environment, without modifying the frozen scientific modules.


## G. Shared identities and independent private supervision

E124 isolates both sources' private demonstration histories at every layer, retains original global positions, and places a public names-only list after the generic header but before all supervision. F controls demonstration access to the list; R controls every query position's direct access. All generic public tokens precede the list, preventing an indirect public relay when F is off. No output words, criterion or private convention are provided. True and unrelated lists have equal token length; numerical cache and full-output no-ops establish their complete invisibility under F0R0.

The primary is full-vocabulary accuracy, averaged uniformly over worlds, sources, and eight queries within each context. Identity-specific formation gain is [true F1R0−true F0R0]−[unrelated F1R0−unrelated F0R0]; reading gain substitutes F0R1. It is not a comparison to the shorter no-list prefix.

| Model, n32 | Formation identity gain, pp | Reading identity gain, pp | true F0R0 full/candidate, % | true F1R0 full/candidate, % |
|---|---:|---:|---:|---:|
| Qwen3-8B | 4.59 [2.73, 6.64] | 0.29 [-0.78, 1.46] | 52.73/93.16 | 58.98/93.65 |
| Mistral-7B-v0.3 | -1.07 [-2.05, -0.20] | 0.49 [0.10, 0.98] | 53.32/91.41 | 52.83/92.97 |
| Llama-3.1-8B | -0.68 [-1.95, 0.49] | -0.20 [-0.88, 0.39] | 53.22/93.95 | 54.59/93.95 |

Qwen's formation identity gain is positive for A and B and both private directions. Mistral's true formation-only operation has opposite effects on A and B; Llama's positive candidate identity contrast does not transfer to the full-output primary. Mistral's reading identity contrast is positive but small. All 47 conditions, instructions, single-source functions, private directions, signed/absolute B-convention responses, and F×R contrasts are retained in [the complete report](results/e124/report.md) and its summaries. There is no equivalence conclusion from a confidence interval crossing zero.

![Shared identities at formation and reading](results/figs/fig_source_identity_coordination.png)

Three checkpoints each execute 16 discovery and 32 confirmation contexts, changing Alex/Sam to Robin/Jordan in confirmation. The 54,144 scores undergo [independent numerical, token and graph review](results/e124/independent_review_2026-10-12.md); 11,742 numerical comparisons match exactly. Whole-query mask consumption is checked in every layer. Independent review is not an independent GPU rerun. The names-only public context is not a full entity–attribute binding construction, and its partial/negative effects do not refute all binding mechanisms.
