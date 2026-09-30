# Research Library — 按题材组织的素材库

**重组：** 2026-09-30（按题材；内容迁移/索引，未改写）。旧的按来源组织方式（academic / industry / open-artifacts）保留在 `deep/` 作为长篇原文，并在每个题材页里建立了章节级索引。

这里是可复用的知识层：谱系、关键论文、精读卡、开源资产、热度数据与来源入口。**它不是候选题目清单。**

## 题材索引

| 题材 | 目录 | 对应组内偏好 / workbench |
|---|---|---|
| 多智能体与大小模型协作 | [`themes/multi-agent-collaboration/`](themes/multi-agent-collaboration/README.md) | 偏好第一条；territory 扫描推荐（待人确认） |
| 推理与测试时计算 | [`themes/reasoning-test-time/`](themes/reasoning-test-time/README.md) | 推理 |
| 训练：预训练、SFT、蒸馏与 RL 后训练 | [`themes/training-post-training/`](themes/training-post-training/README.md) | |
| 可解释性与表征分析 | [`themes/interpretability-representation/`](themes/interpretability-representation/README.md) | 表征分析、可解释性；`workbench/mechanism-population-dynamics/` |
| 理解与生成 / 多模态 | [`themes/unified-multimodal/`](themes/unified-multimodal/README.md) | 理解与生成 |
| 游戏 NPC 与社会智能体 | [`themes/game-npc-social/`](themes/game-npc-social/README.md) | 游戏 NPC；`workbench/npc-*` |
| 智能体、工具与交互 | [`themes/agents-tools/`](themes/agents-tools/README.md) | |
| 语音、全模态与实时交互 | [`themes/speech-omni-realtime/`](themes/speech-omni-realtime/README.md) | `workbench/realtime-*`、`omni-recon` |
| 视频生成与世界模型 | [`themes/video-world-models/`](themes/video-world-models/README.md) | 当前主线 `workbench/video-world-model-temporal-interfaces/` |
| VLA 与具身智能 | [`themes/vla-embodied/`](themes/vla-embodied/README.md) | |
| 架构、记忆与长上下文 | [`themes/architecture-memory/`](themes/architecture-memory/README.md) | `workbench/shape-olmo/`、`hybrid-adaptation/` |
| MoE 与路由 | [`themes/moe-routing/`](themes/moe-routing/README.md) | `workbench/moe-route-preference/` |
| 跨语言能力形成 | [`themes/multilingual/`](themes/multilingual/README.md) | `workbench/cross-lingual-acquisition-regimes/` |
| 科学基础模型与 AI4Quant | [`themes/scientific-fm-ai4quant/`](themes/scientific-fm-ai4quant/README.md) | `workbench/ai4quant/` |
| 研究方法、测量与选题技艺 | [`themes/research-craft/`](themes/research-craft/README.md) | 选题流程、再归因、负结果 |

每个题材页的结构相同：
1. **热度**（`tools/venue_corpus` 计算的顶会接收数与 ICLR 切片接收率）；
2. **Territory 笔记**（原 `TERRITORY_BANK.md`）；
3. **关键论文**（原 `KEY_PAPERS.md` 按 ID 前缀拆出）与本题材的精读卡；
4. **深读材料**：`deep/` 长篇原文中与本题材相关的章节列表；
5. **博客 / 报告**；
6. **最新 arXiv 入口**（awesome 列表）；
7. **本仓库相关 workbench / 历史**。

## 其他入口
- [`KEY_PAPERS.md`](KEY_PAPERS.md) — ID 前缀 → 题材文件的索引（新增条目写进题材目录）。
- [`TERRITORY_BANK.md`](TERRITORY_BANK.md) — T01–T14 → 题材目录的索引。
- [`sources/AWESOME_LISTS.md`](sources/AWESOME_LISTS.md) — awesome 列表（标注是否仍在更新）、daily-arXiv 镜像、顶会名单数据源、PaperNotes。
- [`sources/BLOGS_REPORTS.md`](sources/BLOGS_REPORTS.md) — 博客与报告（B01–B23）。
- [`deep/`](deep/) — 长篇谱系原文（academic / industry / open-artifacts），通过题材页的章节索引进入。
- [`../tools/venue_corpus/`](../tools/venue_corpus/README.md) — 顶会接收 + 拒稿语料库。

## 怎么用

新方向出现时：
1. 找到对应题材页，先看热度与谱系；
2. 读题材页列出的关键论文与精读卡；
3. 用 `tools/venue_corpus` 查近邻（接收 + near-miss 拒稿）；
4. 用 `sources/AWESOME_LISTS.md` 的入口看最新 arXiv；
5. 需要选主线时，按 `../search/README.md` §2 填 territory 卡。

## 读论文：为想法的来源与距离而读

精读模板见 `../search/README.md` §4.1 与 [`../templates/paper_card.md`](../templates/paper_card.md)（论文卡）。除了问题、方法、结果，更要重建：

- **parent baseline / belief** — 之前最强的做法或共识；
- **pressure** — 什么具体困难让它不够用；
- **changed premise** — 这篇论文不再接受哪条假设；
- **revealing experiment** — 在最终方法出现之前，什么分析能暴露问题；
- **与最近邻的距离** — 它相对 3–5 个近邻的增量是什么、怎样论证的（**找自己增量时最重要的参考**）；
- **证据强度** — 几个模型、几个 benchmark、有无消融/理论；
- **可迁移的研究动作** — 我们该模仿的是哪一步。

### Documented vs reconstructed genesis
不要虚构作者的历史。标注 **DOCUMENTED**（作者博客/演讲/附录/代码历史明确说过）或 **RECONSTRUCTED**（根据论文与相关工作重建的合理路径）。后者用于训练研究品味，不当作传记事实。

### 值得反复学习的生长模式（原文保留）
- **强基线改变问题**（ResNet Strikes Back）：提出新架构前，先问基线是不是还按它那个年代的方式在训练。
- **方法动物园 → 显式设计空间**（EDM）：技巧很多、相互作用时，分解本身就能暴露哪些假设在承重。
- **复杂流水线 → 改变数学对象**（DPO）：瓶颈有时不是容量，而是优化问题的表示方式。
- **规模暴露表示瓶颈**（FAST）：成功的系统抽象会在规模/频率变化后成为下一个瓶颈。
- **成功的训练配方 → 分解学习信号在哪里**（RLVR 分析）：一个配方有效时，问名义学习信号里究竟哪一部分在起作用。
- **命名的失败模式 + 最小修复**（Dr. MAS、AT-GRPO、Dr. MAMR）：在强框架上真实跑出的失败，配最小修复，是多智能体方向最常见的接收形态。

## 什么该放进来
有复用价值才加：基础原语、改变的前提、强负结果/再归因、基线或训练配方、研究技艺、可用于实验的开源资产。不要把每篇新 arXiv 都加进来；候选相关的近邻放在 workbench 或 candidate 包里。

## 条目标签
**ANCHOR**（长期基础）· **BRIDGE**（改变对一条谱系的理解）· **FRONTIER**（近期，下结论前复查）· **ARTIFACT**（可用于实验的代码/权重/数据）· **CRAFT**（研究/实验实践）· **NEGATIVE**（有价值的局限/再归因）。
