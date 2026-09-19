# Academic Genealogy Library Index

这是 `academic/` 的**导航页**，不重复详细 autopsy。每条 lineage 的完整 parent→successor reconstruction 在 `GENEALOGIES_01...04.md`。

> 用法：先用本页定位 lineage 与 saturation，再读对应 genealogy；不要把表格里的 “move” 当 idea generator。

| ID | Lineage | Frontier movement（极简） | 当前高风险 surface | 详见 |
|---|---|---|---|---|
| G01 | RLVR learning signal | scalable RL → token/sign/unit/calibration semantics | generic entropy weighting、another GRPO variant | GENEALOGIES_01 |
| G02 | Test-time scaling | more paths → search state → compute policy → local leverage | generic best-of-N / adaptive compute | GENEALOGIES_01 |
| G03 | ICL mechanism | behavior/circuit → task representation → new explanatory decomposition | another head/vector/probe | GENEALOGIES_01 |
| G04 | Diffusion fast sampling | solver → schedule → design-space attribution → local heterogeneity | another solver/cache/adaptive timestep | GENEALOGIES_01 |
| G05 | VLA action representation | single action → chunk/token interface → representation/latency bottleneck | generic chunk/tokenization | GENEALOGIES_01 |
| G06 | Pretraining scaling | N/D/C → mixture/exposure/recipe as structured variables | another scaling fit / giant sweep | GENEALOGIES_02 |
| G07 | SFT & knowledge | behavior adaptation → model-state-relative supervision/update | generic forgetting / checkpoint biography | GENEALOGIES_02 |
| G08 | Distillation | teacher quality → teacher–student–state relation | generic curriculum/key-step/student-aware KD | GENEALOGIES_02 |
| G09 | Architecture / inductive bias | stack → iterative compute; generic tokens → task geometry/physics | module invention without structural pressure | GENEALOGIES_02 |
| G10 | VLM token lifecycle | connector → token explosion → dynamic/future utility | generic visual-token pruning | GENEALOGIES_03 |
| G11 | Latent multimodal reasoning | verbal/explicit intermediate → latent visual computation | “latent token” itself | GENEALOGIES_03 |
| G12 | Full-duplex speech | turn pipeline → synchronized concurrent streams | full-duplex/streaming as label | GENEALOGIES_03 |
| G13 | Negative / limits | measured effect → attribution audit | another stress test/judge/perturbation | GENEALOGIES_03 |
| G14 | Optimization / SAM | endpoint flatness → trajectory dynamics/objective reformulation | another SAM/optimizer acronym | GENEALOGIES_03 |
| G15 | Multimodal objectives | contrastive vs generative → capability relations | generic unified/self-reward | GENEALOGIES_04 |
| G16 | Speech tokenization | acoustic/semantic codes → downstream/deployment-aware representation | another codebook/teacher signal | GENEALOGIES_04 |
| G17 | CoT faithfulness | plausible rationale → causal target/identification refinement | another faithfulness metric | GENEALOGIES_04 |
| G18 | Video/world models | visual generation → action-conditioned transition/dynamics | “world model” label / giant unified system | GENEALOGIES_04 |

## 文件分布

- `GENEALOGIES_01.md`：G01–G05
- `GENEALOGIES_02.md`：G06–G09
- `GENEALOGIES_03.md`：G10–G14
- `GENEALOGIES_04.md`：G15–G18
- `LITERATURE_MAP.md`：跨会议 landscape、coverage 与 density
- `PAPER_AUTOPSIES.md`：第一轮逐篇阅读记录

## Same surface ≠ same genealogy

这些词跨很多领域反复出现，但本身没有 novelty：

| Surface | 可能对应的真实 pressure |
|---|---|
| adaptive | compute marginal value、integration error、student state、token relevance |
| selective | branching decision、instructional leverage、redundancy、harmful update |
| latent | computation depth、visual reasoning carrier、dynamics state、task representation |
| unified | objective compatibility、information allocation、modality interface、system integration |
| mismatch | train/test、teacher/student、objective/metric、representation/modality、deployment/kernel |
| dynamic | decoder state、physical time、optimization trajectory、world state |

正式迁移前必须回目标领域验证：

> state 是什么？quantity 是什么？旧 assumption 是什么？decisive evidence 是什么？

## Coverage boundary

当前 academic library 已覆盖 training、inference、architecture、multimodal、generation、embodied、speech、optimization/theory、negative/limits。

仍相对薄的方向包括：

- MoE/routing
- long-context beyond KV efficiency
- code/program synthesis
- continual learning/model editing
- 3D/geometry
- causal representation learning
- scientific ML

这些不是“待填空白”。若未来 candidate 落在这些领域，先补对应 genealogy，再正式审题。

## Scope

本索引只维护 academic evidence。

- industry：`../industry/README.md`
- startup/HF：`../startup_hf/README.md`
- candidate 状态：`../topics/README.md`
- canonical workflow：`../SEARCH_GUIDE_ZH.md`
