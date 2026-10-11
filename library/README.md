# Research Library — 按题材组织的素材库

**重组：** 2026-09-30（按题材；内容迁移/索引，未改写）。旧的按来源组织方式（academic / industry / open-artifacts）保留在 `deep/` 作为长篇原文，并在每个题材页里建立了章节级索引。

这里是可复用的知识层：谱系、关键论文、精读卡、开源资产、热度数据与来源入口。**它不是候选题目清单。**

## 题材索引（18 个主题，唯一入口）

2026-10-09 精简：不再保留已明确放弃的 AI4Quant 题材壳；真正可复用的分析记录在其他题材中，不另建“废弃研究资料”目录。

这里按**科学对象/研究问题**组织，而不是按某次研究的活跃状态；`library` 的题材页负责领域背景和文献，**项目是否还在推进只以 [workbench 登记表](../workbench/README.md) 与用户最新决定为准**。历史文献画像不能代替实时研究状态。

| 主题 | 入口 | 适合先找什么 |
|---|---|---|
| AI Agent / 工具使用 | [agents-tools](themes/agents-tools/README.md) | Agent harness、工具、长程交互 |
| 多智能体协作 | [multi-agent-collaboration](themes/multi-agent-collaboration/README.md) | 大小模型协作、团队训练、交叉配对 |
| NPC / 社会智能体 | [game-npc-social](themes/game-npc-social/README.md) | Persona、行为、可调查的欺骗与游戏世界 |
| 推理与 Test-time Compute | [reasoning-test-time](themes/reasoning-test-time/README.md) | CoT、搜索、验证与计算分配 |
| 训练与后训练 | [training-post-training](themes/training-post-training/README.md) | 数据、SFT、RL、蒸馏与 RSI 文献 |
| 架构、记忆与长上下文 | [architecture-memory](themes/architecture-memory/README.md) | Transformer/SSM、状态、KV 与长上下文 |
| 可解释性与表征 | [interpretability-representation](themes/interpretability-representation/README.md) | 机制、因果有效性、模型差分测量 |
| ICL 证据结构 | [in-context-evidence-structure](themes/in-context-evidence-structure/README.md) | 漂移、噪声、示例聚合、输出身份 |
| 增量语言理解 | [incremental-language-processing](themes/incremental-language-processing/README.md) | 重解析、证据修订；含逐篇阅读卡 |
| 语用推理 | [pragmatic-inference](themes/pragmatic-inference/README.md) | 语义/语用、信念更新；含逐篇阅读卡 |
| 跨语言学习 | [multilingual](themes/multilingual/README.md) | 多语训练、迁移、翻译桥接和数据混合 |
| MoE 路由 | [moe-routing](themes/moe-routing/README.md) | 专家路由、偏好与实际 Top-K |
| 语音与实时交互 | [speech-omni-realtime](themes/speech-omni-realtime/README.md) | 全双工、流式语音、实时 Agent |
| 多模态理解与生成 | [unified-multimodal](themes/unified-multimodal/README.md) | VLM、多模态表示、理解生成统一 |
| 视频与世界模型 | [video-world-models](themes/video-world-models/README.md) | 生成式交互世界模型、causalization |
| 紧凑隐空间世界模型 | [latent-world-models](themes/latent-world-models/README.md) | JEPA/LeWM、latent planning、规划代价 |
| VLA 与具身 | [vla-embodied](themes/vla-embodied/README.md) | 动作表示、具身训练与控制 |
| 研究方法与研究品味 | [research-craft](themes/research-craft/README.md) | 谱系、反归因、实验有效性、选题 |

**阅读顺序：** 题材 `README.md`（问题地图）→ `KEY_PAPERS.md` 或 `PAPER_CARDS.md`（可复用论文）→ 必要时查 `deep/`（大篇幅史料）→ 到 `workbench/` 查看本项目实验和实时状态。题材目录的文件结构因历史来源不同，不应为了形式一致而移动/改写几百份阅读卡。

## 其他入口
- [本次知识库审计](LIBRARY_AUDIT_2026-10-09.md) — 目录完整性、历史引用与编号问题的修复记录。
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
