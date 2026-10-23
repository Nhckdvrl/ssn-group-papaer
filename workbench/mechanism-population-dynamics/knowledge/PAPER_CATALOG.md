# 论文精读卡目录（2026-10-23 重建）

按主题列出 `papers/` 下的全部卡片。除 [FLAGGED_ABSTRACT_ONLY](papers/FLAGGED_ABSTRACT_ONLY_2026-10-17.md) 列出的条目外，都是正文精读。研究背景见 [研究总档](../RESEARCH_HISTORY.md)。

## 1. 跨训练的普适性、组件对应与对称
| 卡片 | 一句话 |
|---|---|
| [LI_CONVERGENT_LEARNING_2016](papers/LI_CONVERGENT_LEARNING_2016.md) | CNN 神经元很少一一对应，子空间共享 |
| [GURNEE_UNIVERSAL_NEURONS_2024](papers/GURNEE_UNIVERSAL_NEURONS_2024.md) | GPT-2 五个种子中 1–5% 神经元普适 |
| [CHUGHTAI_TOY_UNIVERSALITY_2023](papers/CHUGHTAI_TOY_UNIVERSALITY_2023.md) | 算法族普适，具体表示与顺序部分任意 |
| [ZHONG_CLOCK_PIZZA_2023](papers/ZHONG_CLOCK_PIZZA_2023.md) | 同一任务多个可行算法，由超参数选择 |
| [BALI_2026](papers/BALI_2026.md) | 头跨训练稳定性（注意力最佳匹配，中层最不稳定） |
| [SPECTRAL_PROBE_CIRCUITS_2026](papers/SPECTRAL_PROBE_CIRCUITS_2026.md) | 不同种子用不同的头、甚至不同的层 |
| [TIGGES_2024](papers/TIGGES_2024.md) | 电路算法跨训练与规模稳定，组件更换 |
| [TROTT_2025](papers/TROTT_2025.md) | 机制解释的可推广性理论（位置维度） |
| [DFA_2026](papers/DFA_2026.md) | 可微的跨模型电路迁移 |
| [SYMMETRY_BREAKING_THEORY_2026](papers/SYMMETRY_BREAKING_THEORY_2026.md) | 头专业化的对称破缺理论 |
| [WANG_RLLC_2025](papers/WANG_RLLC_2025.md) | 用 refined LLC 看头的分化 |

## 2. 模式连通与模型对齐
| 卡片 | 一句话 |
|---|---|
| [FRANKLE_LMC_2020](papers/FRANKLE_LMC_2020.md) | 分叉后何时线性连通（不稳定性分析） |
| [ENTEZARI_PERMUTATION_2022](papers/ENTEZARI_PERMUTATION_2022.md) | 置换对齐后多数解在同一盆地的猜想 |
| [GIT_REBASIN_2023](papers/GIT_REBASIN_2023.md) | 权重 / 激活匹配后合并 |
| [LUBANA_MMC_2023](papers/LUBANA_MMC_2023.md) | 机制模式连通：不连通 → 机制不同 |
| [THEUS_GLMC_2025](papers/THEUS_GLMC_2025.md) | Transformer 的广义线性模式连通 |
| [VERMA_MERGING_2024](papers/VERMA_MERGING_2024.md) | 不同初始化的文本 Transformer 合并 |

## 3. MoE 专家分工
| 卡片 | 一句话 |
|---|---|
| [MOE_DIVISION_OF_LABOR_2026-10-23](papers/MOE_DIVISION_OF_LABOR_2026-10-23.md) | Equifinality、LMC-MoE、Myth of Specialization、Routers Learn Geometry 等 |
| [MOE_SPECIALIZATION_SEEDS_2026](papers/MOE_SPECIALIZATION_SEEDS_2026.md) | 视觉 MoE：划分结构跨种子重现、身份不重现 |

## 4. 电路、因果读数与测量
| 卡片 | 一句话 |
|---|---|
| [OLSSON_2022](papers/OLSSON_2022.md) | induction 头与 ICL |
| [SINGH_2024](papers/SINGH_2024.md) | induction 头形成所需条件（训练期钳制） |
| [YIN_2025](papers/YIN_2025.md) | ICL 更依赖 function-vector 头 |
| [SAHIN_HAPAX_2025](papers/SAHIN_HAPAX_2025.md) | 不靠复制的 ICL |
| [MERULLO_2024](papers/MERULLO_2024.md) | 电路组件跨任务复用 |
| [ALL_CIRCUITS_2026](papers/ALL_CIRCUITS_2026.md) | 同一计算有多个忠实电路 |
| [MANY_CIRCUITS_2026](papers/MANY_CIRCUITS_2026.md) | 多电路、一个机制 |
| [SHENG_2026](papers/SHENG_2026.md) | 电路结论依赖抽取与比较方式 |
| [MELoux_2026](papers/MELoux_2026.md) | 机制解释作为统计估计 |
| [MDA_2026](papers/MDA_2026.md) | 训练数据归因到 induction 形成 |
| [ACTIVE_DORMANT_2024](papers/ACTIVE_DORMANT_2024.md) | 注意力汇与休眠头 |
| [FROZEN_QK_2025](papers/FROZEN_QK_2025.md) | 随机注意力是否足够 |

## 5. 训练动力学、涌现与种子差异
| 卡片 | 一句话 |
|---|---|
| [DATADECIDE_2025](papers/DATADECIDE_2025.md) | 25 语料 × 14 尺寸 × 3 种子套件 |
| [CHEN_SAPHRA_2024](papers/CHEN_SAPHRA_2024.md) | 语法习得的损失骤降 |
| [HOOGLAND_2025](papers/HOOGLAND_2025.md) | 损失地形退化与分阶段发育 |
| [ATTN_CIRCUITS_FORM_2026](papers/ATTN_CIRCUITS_FORM_2026.md) | 1B 级三种架构的能力与注意力汇发育 |
| [SINGH_TRANSIENCE_2023_2025](papers/SINGH_TRANSIENCE_2023_2025.md) | ICL 的暂时性与策略竞合 |
| [ZHAO_SAPHRA_2026](papers/ZHAO_SAPHRA_2026.md) | 涌现能力的随机尺度 |
| [BAHERWANI_2026](papers/BAHERWANI_2026.md) | 能力随机出现于稀疏注意力学习 |
| [DAHIYA_2026](papers/DAHIYA_2026.md) | 训练中低于随机的下探 |
| [PLASTICITY_SCALE_2026](papers/PLASTICITY_SCALE_2026.md) | 规模与可塑性丧失 |

## 6. 自修复、损伤与再分配
| 卡片 | 一句话 |
|---|---|
| [HYDRA_2023](papers/HYDRA_2023.md) | 推理时的自修复 |
| [RUSHING_NANDA_2024](papers/RUSHING_NANDA_2024.md) | 自修复的探索 |
| [CONDITIONAL_COABLATION_2026](papers/CONDITIONAL_COABLATION_2026.md) | 条件共消融找回替补 |
| [SCHALLON_2026](papers/SCHALLON_2026.md) | 塌缩注意力头的手术修复 |
| [MIAO_DOBS_2025](papers/MIAO_DOBS_2025.md) | 竞争性重训中的功能再分配 |
| [PRAKASH_2024](papers/PRAKASH_2024.md) | 微调增强已有机制 |
| [JAIN_2024](papers/JAIN_2024.md) | 微调只加包装层 |

## 7. 遗忘与重学
| 卡片 | 一句话 |
|---|---|
| [RELEARNING_REVERSIBILITY_2024_2026](papers/RELEARNING_REVERSIBILITY_2024_2026.md) | 近邻综述：遗忘后能力为何回来 |
| [DEEB_ROGER_2024](papers/DEEB_ROGER_2024.md) | 遗忘方法是否真的移除信息 |
| [HU_BENIGN_RELEARNING_2025](papers/HU_BENIGN_RELEARNING_2025.md) | 良性重学唤回遗忘 |
| [QI_FINETUNING_SAFETY_2024](papers/QI_FINETUNING_SAFETY_2024.md) | 良性微调破坏安全对齐 |
| [UNLEARNING_ISNT_DELETION_2025](papers/UNLEARNING_ISNT_DELETION_2025.md) | 遗忘的可逆性 |
| [GUO_MECH_UNLEARNING_2024](papers/GUO_MECH_UNLEARNING_2024.md) | 机制定位的遗忘 |
| [SIDDIQUI_2025](papers/SIDDIQUI_2025.md) | 权重空间正则的抗篡改遗忘 |
| [UNDO_LEE_2025](papers/UNDO_LEE_2025.md) | 蒸馏使遗忘稳健 |
| [SAM_UNLEARNING_2025](papers/SAM_UNLEARNING_2025.md) | 锐度感知的抗重学遗忘 |
| [LAYERED_UNLEARNING_2025](papers/LAYERED_UNLEARNING_2025.md) | 分层遗忘 |
| [TAR_2024](papers/TAR_2024.md) | 开放权重的抗篡改防护 |
| [ADAPTIVE_RMU_2025](papers/ADAPTIVE_RMU_2025.md) | 自适应 RMU |
