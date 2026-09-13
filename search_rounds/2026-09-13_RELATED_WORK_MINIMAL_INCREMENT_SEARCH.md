# 2026-09-13 — Related-Work Minimal-Increment Search

Purpose: persistent anti-resurrection log for the search mode that reverse-engineers strong ACL/EMNLP/NAACL papers and asks only for the smallest consequential sentence still missing after their closest related work. This is a search log, not a candidate list. L32 has its own selection record and is not duplicated here.

Rule: strong/weird result -> closest 3–5 owners/successors -> ask what one inference remains -> if Prior A+B+C already makes the strongest expected answer natural, DROP immediately. Only fully selected PILOT-AUTHORIZED topics become candidates.

## Hook A — ExPO: does preference tuning learn the right direction early and only scale magnitude later?

Status: DROP / reviewer-compressible.

ACL 2025 ExPO shows that extrapolating an early DPO checkpoint farther along its learned weight delta can outperform the fully trained DPO model. The tempting follow-up is to decompose training into direction vs magnitude and ask when the alignment direction stabilizes. But the functional premise of ExPO already requires the early direction to remain useful under extrapolation, and 2026 trajectory-aware preference-optimization work further crowds the training-path interpretation. A result that early and final directions are highly aligned would read as a geometric restatement of ExPO rather than a new Main-level inference. Do not reopen unless independent evidence shows the later orthogonal component is systematically harmful or serves a distinct scientific function.

## Hook B — Train-then-revert > freeze-then-train: temporary parameters as optimization scaffolding

Status: DROP / old optimization explanation too strong.

Multiple lines report that allowing parameters to move during adaptation and reverting some updates afterward can outperform freezing those parameters from the start. The attractive RQ is whether some parameter changes are useful only transiently during learning. However, the strongest expected conclusion compresses to a mature overparameterization/optimization principle: extra degrees of freedom can ease optimization even if the final constrained solution does not retain them. Without a sharper LLM-specific contradiction, this is not enough for Main.

## Hook C — Wrong/negative examples help without corrective rationales

Status: DROP / parent + successor own the mechanism space.

EMNLP 2025 shows incorrect answers can help ICL more when explicit corrective rationales are removed; ACL 2026 and related work on negative reasoning trajectories already connect negative examples to training dynamics, policy entropy, and generalization. Asking why mistakes help is now an occupied parent, not an unexplained anomaly.

## Hook D — Formal-language pre-pretraining: what property of a synthetic language creates transferable bias?

Status: DROP / successor already violates and rewrites the original explanation.

ACL 2025 argued that pre-pretraining on formal languages can impart useful linguistic biases, with an explanation tied partly to hierarchical structure and architectural computability. ACL 2026 already demonstrates a formal language that violates the earlier load-bearing computational-bound condition yet transfers better, and shifts the explanation toward dependency accessibility/ambiguity. The desired move—find a counterexample to the parent explanation and rewrite the law—has already been made.

## Hook E — Training longer makes models harder to quantize

Status: DROP / direct 2026 mechanism successor.

The anomaly is attractive: longer pretraining can improve dense loss while making post-training quantization substantially worse. But 2026 follow-up work directly implicates learning-rate decay/training dynamics rather than token exposure per se and trains controlled models to intervene on that factor. Do not reopen generic `why does more training hurt quantization?`.

## Hook F — TrimLLM: why can domain-adapted models lose 50–60% of layers without losing domain accuracy?

Status: DROP / mother already favors pre-existing task-layer redundancy.

The tempting distinction is whether adaptation compresses domain capability into a few layers or the pretrained model already needs only a subset for the domain. TrimLLM reports that layer-importance patterns measured before fine-tuning correlate strongly with which layers survive iterative dropping and uses this fact operationally. Appendix results also show task-specific drop patterns already present. A base/adapted transplant would mostly complete an inference the mother paper already strongly implies.

## Hook G — Mamba and Transformers show similar ICL behavior but different intervention responses

Status: DROP / mature mechanism family.

ACL 2026 reports that Mamba2 does not respond to Transformer-style function-vector interventions in the same way despite comparable ICL behavior. This is a nice `same behavior, different computation` mother, but 2024–2026 theory already explains Mamba ICL through online-gradient-style computation, convolution/Laplacian smoothing, gating-based feature extraction, and outlier suppression. Asking what replaces a Transformer function vector would mostly map those established SSM mechanisms onto another diagnostic.

## Hook H — One-shot critique fine-tuning generalizes from one math problem

Status: DROP / error-type generalization already supplies the natural answer.

EMNLP 2025 reports large cross-problem gains from critique data generated from a single seed math question. The obvious mystery is what can transfer when almost no new mathematical content is introduced. The paper's diversity ablations already point toward broad error-pattern coverage, while ACL 2025 Self-Error-Instruct and related error-grounded augmentation explicitly extract, cluster, and train on transferable error types. Strongest reviewer compression: diverse critiques + known error-type generalization. Do not reopen as `what does one-example CFT learn?`.

## Hook I — More SFT data hurts factual knowledge / most updates can be reverted

Status: DROP + overlaps hard-ban.

EMNLP 2025 shows more SFT samples can hurt closed-book QA and that large fractions of parameter updates can be restored without hurting, sometimes improving, knowledge performance. The paper already links the effect to data mastery, logit divergence, unnecessary/harmful updates, and restoration. Any fallback to `knowledge remains but readout/access changed` overlaps the Temporal Forgetting / latent-access hard ban. Do not reopen.

## Hook J — Tiny SFT warm-up unlocks DPO reasoning

Status: DROP / generic post-training decomposition + portfolio overlap.

ACL 2025 reports that a small fraction of SFT before DPO yields large mathematical-reasoning gains. The parent already frames the problem as a distribution/support mismatch between the base policy and step-by-step reasoning targets. Further decomposition into format/support/capability rapidly becomes generic SFT-vs-DPO analysis and overlaps L30's supervision-structure territory.

## Hook K — Later generated tokens require fewer layers

Status: DROP / SkipDecode already states the explanation.

ACL 2025 D3 exploits a position-dependent law: later generated tokens have lower perplexity and tolerate shallower execution. The appealing follow-up is whether earlier prefix computation is progressively reused so later tokens need less depth. SkipDecode 2023 already explains later-token compute reduction via growing context, increasing predictability, and faster hidden-state saturation across layers. Exact causal tests would refine an existing account, not create a new parent.

## Hook L — Attention/FFN update-direction correlation (DiffSkip)

Status: DROP / weak mother + architectural common cause.

Reported attention/FFN differential-vector alignment is mainly established on one Llama-3-8B setting and is naturally explained by both sublayers responding to the same token difficulty / residual-stream direction. It lacks the hard repeated mother needed for a mechanism paper and does not justify selection merely because a cheap layer-skipping experiment exists.

## Hook M — Linear weight interpolation causes a sharp Instruct→Thinking phase transition

Status: DROP / token-triggered reasoning-mode owner makes strongest result too predictable.

ACL 2026 shows a sharp jump in Think Ratio around intermediate interpolation coefficients, and module ablations suggest FFNs are load-bearing for the transition. The tempting RQ is whether a genuine internal reasoning computation appears discontinuously or whether interpolation merely pushes an autoregressive mode-switch token over a decoding threshold. Mid-Think (2026) already shows Qwen3 thinking/non-thinking behavior can be strongly induced or suppressed by a few token-level triggers, while Qwen3 officially exposes think/no-think mode controls. Reviewer compression: interpolation moves trigger logits across a threshold; token trigger then self-maintains the mode. Exact force/suppress experiments are not enough novelty.

## Hook N — Multi-turn dialogue sharply degrades reasoning

Status: DROP / parent already has stronger owner and mitigation trajectory.

ACL 2026 BOULDER finds a large, consistent isolated-vs-dialogue reasoning gap and identifies multi-turn interaction as the main burden. But ICLR 2026 `LLMs Get Lost In Multi-Turn Conversation` already establishes a ~39% average degradation across models, decomposes it into small aptitude loss plus large unreliability, and traces failures to early assumptions / premature solutions that models fail to recover from. A June-2026 memory-augmented RL follow-up further shows that compact rolling memory mitigates fragmented-context degradation. Asking generically why dialogue hurts reasoning is already occupied.

## Search lesson from this round

The useful discovery move is not `find a weird result and invent three accounts`. It is:

> weird result -> read the parent's own explanation carefully -> read successors -> identify exactly one missing inference -> ask whether that inference would still surprise a reviewer who knows the component papers.

Most apparently attractive anomalies above died because the abstract sounded mysterious while the body/successor literature had already supplied the next sentence. L32 remains a useful positive template because the parent owns a very large mother effect but does not determine the causal sequence phase through which the learned sparse embedding deltas act, and the decisive split can be done on the same learned checkpoint rather than by retraining multiple models.