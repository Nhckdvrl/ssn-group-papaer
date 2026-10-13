# 阅读深度债与优先任务（非固定周计划）

以下不是机械阅读 checklist；任务顺序随新证据/高信息量实验主动改变。已在 [PAPER_LEDGER](PAPER_LEDGER.md) 标 P0/P1/P2 的论文都**不能假装完成了完整精读**。

## A 高度靠近 NPC 本体（优先深读和实码）
- KNUDGE EMNLP2024：quest schema、NPC 已知/未知信息、角色图谱、评价和真实语料许可，完整原文/附录。
- CDT ACL2026：tree 的 scene-action 数据、算法校验、泛化/角色/场景拆分、对比强基线，构树 API 成本及动作解释。
- PCSP 2026 arXiv：InfoNCE 监督链、actor 接收梯度关系、独立 action/state Big-Five probe、语义行为量表有效性和异常审计。真实阅读代码的测试脚本；不可简单宣称重发现。
- FAIRGAMER ACL2026：公平性是输出趋同吗？控制改变了什么？哪些选择属于角色影响哪些是不合理社会偏见？独立 ground truth。
- NCP-Bench ICML2026：对 100 题做事实/剧情承诺、玩家输入冲突率的裁判机制与同 judge 对照；可替代剧情路径的合法性。

## B 扩展近邻但不要挤占全部算力
- Collab-Overcooked、CollabBench、Decrypto：玩家/NPC 动作、partner update 与真实协作必要性；最强 baseline/成本。
- Generative Agents、SOTOPIA、RoleKE、动态 persona/ArcANE、ThinkPersona、AIIDE structured knowledge trees；防止声称早已存在的动态角色或博弈机制。
- 游戏引擎/实际玩家体验的论文中，抽样验证“语言流畅≠游戏质量”最重要的客观/真人指标。

## C 最新 NeurIPS2026 定位
- TALES：继续对照实验表、Simon Says 变量、自然 Jericho zero-shot vs budget，代码执行和失败案例。
- Population-Aligned Persona Generation、How to Interpret Agent Behavior、Personalize-then-Store：逐一核实正式版本、接受 track、方法、数据和代码。
- From [官方目录](https://neurips.cc/Downloads/2026) 扩展 Game/ToM/Memory/Narrative/Persona/Action 的可解释性和 eval 方向，不止检索关键词 NPC。特殊 tracks 绝不与主会论文混写。
- 每轮补新近邻时写**被谁占了的主张**及**我们更新了哪个判断**，避免沉迷造一个无贡献的 PDF 摘要库。

阅读任何论文产生的具体知识卡、假设、反例、实码实验设计均写在这个 workbench 的 knowledge/ 内。
