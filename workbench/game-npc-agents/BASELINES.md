# 本地研究资产与真实可用性｜2026-10-13 第三轮

**没有完整模型 baseline 被本地复现。** 下表区分研究对象、公开资产和仍未解决的本地问题。CPDC已撤出优先入口；E01源码测试不构成模型/游戏复现。

## 1. 当前优先核查与备用入口

| 系统 | 对象与价值 | 本轮查到了什么 | 尚须核查，不能跳过 |
|---|---|---|---|
| [LIGHT](https://github.com/facebookresearch/LIGHT) / [quests项目](https://parl.ai/projects/light/) | 有身份/动机的角色、对话及真实游戏行动；优先原生NPC研究底座候选 | README、graph说明、play_map.py；OOGraph/GraphEvent/Soul，模型之外可有规则角色 | 旧依赖/模型迁移、数据和权重各自许可、真实quest能否载入当前引擎、现代本地代理；未安装 |
| [Hypothetical Minds](https://github.com/locross93/Hypothetical-Minds) | 伙伴策略推断与协同/竞争；第二分支强LLM近邻 | 官方README有本地vLLM/Llama3路径，不只是API | 指定MeltingPot fork、实际客户端、模型规模/提示/调用成本；未运行，不按GPT默认命令启动 |
| [GAMMA](https://github.com/lych1233/GAMMA-human-ai-collaboration) | 人类配合的强非LLM政策参照；不是剧情角色 | README有政策数据/检查点入口、训练与human-proxy流程 | checkpoint字节/许可/配置匹配未核查；安装说明承认有缺失依赖；全量训练成本高 |
| [Collab-Overcooked](https://github.com/YusaeMeow/Collab-Overcooked) | 行动协作与过程测量，可作备用底座 | 前轮核查README与评估入口，支持本地服务 | 旧Python/MPI依赖、与原版Overcooked不同、参考轨迹评分的范围；本轮未重新安装 |
| [Proact-VL](https://github.com/microsoft/AnthropomorphicIntelligence/tree/main/Proact-VL) | 实时解说/指导伙伴，主动性近邻，不是有行动身体的NPC | 当前README已链接权重/训练与测试数据、推理训练和评估脚本 | GPT质量/PAUC裁判、本地替代的效度、视频IO和Ego4D等数据许可；不默认完整重训 |

## 2. 保留的角色/叙事研究近邻，不冒充默认执行底座

[KNUDGE](https://github.com/nweir127/KNUDGE)：作者侧专业RPG对话图与知识使用。自然语料有价值，不意味着有完整在线世界。

[CDT](https://github.com/KomeijiForce/Codified_Decision_Tree)：情境化人物规则与行动文本；构树、语义判断、评估的模型调用均入账，不能直接执行其默认外部API示例。

[NCP](https://github.com/NLP2CT/NCP-Bench)：narrator长程承诺；世界更新/审核含LLM，原文有多种验证，不能误称纯规则世界或缺所有对照。

[PCSP](https://github.com/yoosunghong/pcsp)：共享政策/真实动作的重要预印本近邻；作者已有独立行为probe审计，不是本项目发现。先核研究层，不默认装全套UE。

TALES是玩家式agent；FAIRGAMER有专门评价目标；CPDC是本次撤出中心的竞赛。它们可提供局部知识，不决定整个NPC研究的目标函数。已有详细材料见[旧阅读入口](knowledge/CORE_NOTES.md)，当前优先级以本页及[问题谱系](knowledge/PROBLEM_GENEALOGY.md)为准。

## 3. 本轮真实源码核验记录

| 仓库文件 | 已读Git blob SHA | 实际结论 |
|---|---|---|
| facebookresearch/LIGHT README.md | ecc5717608ada580fffc24ed2ac2c5fd375b7812 | 声明MIT代码、引擎与Soul接口；模型迁移/部署说明仍有TODO |
| facebookresearch/LIGHT light/graph/README.md | 6fa39500950bf40083634ec8fb207bc9e4362150 | 图的状态、节点/边、GraphEvent与序列化；尚未跑测试 |
| facebookresearch/LIGHT scripts/examples/play_map.py | 4dada31b28619d227dc4086341f02c7e6fb31e78 | Hydra配置、规则/模型Soul分支；并非已成功运行命令 |
| locross93/Hypothetical-Minds README.md | c72e23ff68ee6414e745b432046a3bef3a1e8e00 | 指定MeltingPot fork、本地vLLM启动与llama3选择分支 |
| lych1233/GAMMA-human-ai-collaboration README.md | c6a7bedef8a7b1f98e8cad5178d6ae48c88311eb | 有本地训练/模型入口，但环境依赖不完整承诺、checkpoint未下载验证 |

这些是**文件blob不是整个repo的commit pin**。正式运行必须另外固定每个上游commit、模型revision、数据hash，不能凭本表声称全依赖已冻结。

LIGHT的README仍示例 --load-map，而本轮源码docstring使用Hydra的 builder.load_map=...；源码还残留 /checkpoint/... 默认路径。因此不复制旧README命令当一键复现说明。应在隔离环境核查入口及无模型依赖路径，不把该差异包装为科学发现。

## 4. 全链路本地化与复现身份

执行规范见[LOCAL_FIRST.md](LOCAL_FIRST.md)。本地替换云端模型后的结果叫受控改造/新基线，不叫作者原成绩复现。代码MIT不意味着所有数据/模型都MIT；网页列出模型不意味着权重与脚本已逐字匹配。核心实验不依赖付费API，也不要求新造大型游戏引擎。

对动作/规则主张优先真实状态反馈；对叙事/心理/体验问题需要相应的人类或经验证测量，**独立符号引擎不是所有NPC论文的唯一资格**。本地优先是降低研究耦合和成本，不是把科学问题缩成最容易写断言的任务。
