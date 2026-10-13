# 文献账本：当前问题锚点、逐篇资产、历史初筛

2026-10-13第三轮。P0=题目/来源入口，P1=官方摘要，P2=指定正文/附录或源码已读，P3=充分正文/关键附录及代码核查，P4=实际复算。会议身份与阅读深度是两件事。**本地模型复现P4目前为零。** 以下没有把旧索引的36篇全部升级成精读。

## 1. 当前重要性与研究尺度锚点

| 来源 | 身份核验 | 本轮实际范围 | 当前作用 |
|---|---|---|---|
| [LIGHT](https://aclanthology.org/D19-1062/) / [项目](https://parl.ai/projects/light/) | EMNLP-IJCNLP2019 main | 项目数据/论文身份、引擎README/graph/play_map源码；P2 asset | 原生角色任务谱系，尚未安装 |
| [How to Motivate Your Dragon](https://aclanthology.org/2021.naacl-main.64/) | NAACL2021 main | 正文任务/方法/数据、相关附录入口；P2 paper | 角色动机、语言与行动后果，不冒认长程已解决 |
| [Direct Behavior Specification](https://proceedings.mlr.press/v162/roy22a.html) | ICML2022 main | 动机、§4–6及实验图/机构，P2 | 制作人员的行为控制问题及贡献尺度 |
| [GAMMA](https://proceedings.neurips.cc/paper_files/paper/2024/hash/6e9f99809b6df59e8fe5c9ffe269bf40-Abstract-Conference.html) | NeurIPS2024 main | 方法概览、实现/成本/真人附录与README；P2 | 伙伴分布、人类迁移、非LLM参照 |
| [Hypothetical Minds](https://proceedings.iclr.cc/paper_files/paper/2025/hash/12f483f624b378f9f3058d8ecd3c7ff5-Abstract-Conference.html) | ICLR2025 main | 方法结构、消融、局限与成本表、README；P2 | 伙伴策略的预测/修正；有本地分支仍须计成本 |
| [Proact-VL](https://openreview.net/forum?id=k9PKgV0L4C) | ICML2026 main | v4任务/实现/评价与资源发布README；P2 | 主动视频伙伴；资源已发布但主裁判含API |
| [Dynamic Persona Coherence](https://aclanthology.org/2026.acl-long.1336/) | ACL2026 main | 本轮官方摘要/身份P1，未假称全文 | 稳定身份与动态状态的已研究对象 |
| [Interactive Drama](https://aclanthology.org/2025.acl-long.546/) | ACL2025 main | 正文引言/构念/评价入口P2 | 沉浸与能动性的证据要求 |
| [AI for Games in the Foundation Model Era](https://arxiv.org/html/2609.16679) | 2026预印本 | NPC/运行期角色/体验/开放问题相关部分P2 | 领域导航，非原研究证据或main保证 |

详见[RESEARCH_CALIBRATION](RESEARCH_CALIBRATION.md)；行业一手来源另见[INDUSTRY_EVIDENCE](INDUSTRY_EVIDENCE.md)。本轮新源码blob与尚未运行的边界见[BASELINES](../BASELINES.md)。

## 2. 前轮逐篇资产（完整保留，不等于当前优先题）

| 文献 | 已有阅读位置 | 使用边界 |
|---|---|---|
| [KNUDGE / EMNLP2024](https://aclanthology.org/2024.emnlp-main.520/) | [卡](papers/KNUDGE_2024.md) | 前轮指定正文/关键附录；authoring，不是完整执行引擎 |
| [CDT / ACL2026](https://aclanthology.org/2026.acl-long.568/) | [卡](papers/CDT_2026.md) | 前轮方法、D/E和源码；保留其多轮证据，不冒认原生游戏动作闭环 |
| [NCP / ICML2026](https://proceedings.mlr.press/v306/ma26ap.html) | [卡](papers/NCP_2026.md) | 前轮正文/指定附录与指标源码；已有审计/人类控制，非本地模型复现 |
| [PCSP / arXiv2026](https://arxiv.org/abs/2605.23652) | [卡](papers/PCSP_2026.md) | 方法部分与作者独立行为审计；未确认主会，不冒领结果 |
| [CPDC 2025](papers/CPDC_2025.md) | 官方任务、技术报告、公开sample的前轮卡 | **仅历史技术参考；用户已否定其作为当前科研入口** |

## 3. 继承的初筛索引：供发现近邻，不是本轮已核主会/全文清单

以下保存初始链接与对象，不重复保证每个会场/版本。需要用于实际研究时，返回原文核验；未查到的不能编补。其更早标记与数值在Git历史可追溯。

| 文献来源 | 初筛对象/当前用途 |
|---|---|
| [Generative Agents](https://arxiv.org/abs/2304.03442) | 社会记忆/反思谱系 |
| [SOTOPIA](https://proceedings.iclr.cc/paper_files/paper/2024/hash/b3075b88e583a0e98d8b24338a613060-Abstract-Conference.html) | 社会角色与目标互动 |
| [SOTOPIA-π](https://aclanthology.org/2024.acl-long.698/) | 社会互动后训练 |
| [Collaborative Quest Completion in Minecraft](https://arxiv.org/abs/2407.03460) | 人与NPC的游戏任务 |
| [Collab-Overcooked](https://aclanthology.org/2025.emnlp-main.249/) | 必要协作，前轮README/部分阅读保留 |
| [RoleKE](https://aclanthology.org/2025.emnlp-main.1689/) | 角色知识错误 |
| [R-CHAR](https://aclanthology.org/2025.emnlp-main.1372/) | 社会角色推断 |
| [FAIRGAMER](https://aclanthology.org/2026.acl-long.2015/) | 特定游戏决策/偏差评价 |
| [ThinkPersona](https://aclanthology.org/2026.acl-long.449/) | 人物知识结构 |
| [Trait Activation in Silicon](https://aclanthology.org/2026.acl-long.1792/) | 情境化人格 |
| [ArcANE](https://arxiv.org/abs/2606.05553) | 角色剧情阶段 |
| [CollabBench](https://proceedings.mlr.press/v306/qian26c.html) | 协作与伙伴 |
| [Decrypto](https://proceedings.mlr.press/v306/lupu26a.html) | 信息不对称游戏 |
| [CoopEval](https://proceedings.mlr.press/v306/tewolde26a.html) | 合作博弈 |
| [ReactiveGWM](https://arxiv.org/abs/2605.15256) | 世界模型中NPC控制 |
| [WorldMind](https://arxiv.org/abs/2608.21439) | 状态感知NPC/world model |
| [Lies We Can See](https://arxiv.org/abs/2608.30428) | 言语/非言语社会行为 |
| [ClueGen](https://doi.org/10.1609/aiide.v12i2.12896) | 侦探游戏/可追踪事件的旧谱系 |
| [Structured Knowledge Trees](https://arxiv.org/abs/2609.23043) | 侦探NPC知识结构 |
| [Talk Less, Call Right](https://arxiv.org/html/2509.00482v1) | 特定角色/工具切片；非当前中心 |
| [Deflanderization](https://arxiv.org/html/2510.13586v1) | 人物表现与任务对话；非当前中心 |
| [Do Role-Playing Agents Practice What They Preach?](https://arxiv.org/html/2507.02197v1) | 自报信念/Trust Game行为 |
| [TALES](https://arxiv.org/html/2504.14128) | 玩家游戏底座，非NPC等价物 |
| [Population-Aligned Persona Generation](https://arxiv.org/abs/2509.10127) | 人口层面人物设定 |
| [How to Interpret Agent Behavior](https://arxiv.org/abs/2605.13625) | 行为解释 |
| [Personalize-then-Store](https://arxiv.org/abs/2605.25535) | 个性化长期记忆 |
| [Perception, Not Reasoning, Limits Visual Theory of Mind](https://neurips.cc/Downloads/2026) | 仅标题入口，track/正文待核 |
| [Task Success Is Not Enough](https://neurips.cc/Downloads/2026) | 仅标题入口，track/正文待核 |
| [LLM-Based NPCs in Video Games: Mapping Study](https://doi.org/10.1109/TG.2026.3733302) | 初筛综述，本轮未重新核验全部元数据 |
| [Narrative and Dialogue Generation: Mapping](https://doi.org/10.1016/j.engappai.2026.115041) | 初筛综述，本轮未重新核验全部元数据 |
| [CharacterBench](https://ojs.aaai.org/index.php/AAAI/article/view/34806) | 人物对话，不代表动作执行 |
| [AMemGym](https://proceedings.iclr.cc/paper_files/paper/2026/hash/0856bc553d3e3b9827e5140d0ad3bf8d-Abstract-Conference.html) | 记忆近邻；本轮未补全文 |
| [lmgame-Bench](https://proceedings.iclr.cc/paper_files/paper/2026/hash/83a4ea71b13bc86308a2bd0b5e07fb61-Abstract-Conference.html) | 游戏玩家代理；本轮未补全文 |

NeurIPS2026下载目录可能包含不同track；本轮没有逐篇完成确认，不能从以上历史归类声称它们全是主会接收。重要性、近邻新颖性与本地可复现性分别核验，未完成项见[READING_QUEUE](READING_QUEUE.md)。
