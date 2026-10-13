# 2026-10-13 定向前沿复核：不再用标题目录代替阅读

本次覆盖所选“角色目标承诺与计划适应”的直接近邻和跨方向参照；不是宣称穷尽NeurIPS2026或所有NPC论文。会议身份、阅读深度、开源可用性分别登记。官方[NeurIPS目录](https://neurips.cc/Downloads/2026)混有不同track，题目命中NPC也可能是医学缩写。

## 可用于本次决策的来源

| 工作 | 身份证据 | 本轮实际阅读 | 对选择的影响 |
|---|---|---|---|
| alem: Benchmarking Open-Ended Multi-Agent Coordination | [作者公告](https://www.kaleabtessera.com/news/)明确 NeurIPS2026 Evaluations & Datasets Track；不写main | [全文](https://arxiv.org/html/2606.08340v1) §1–3的任务/接口和协作要求、评估设计部分；非全45页逐字核验 | 环境要证明真的需要协作；不能把单体能力弱解释为互动控制弱；不因此把NPC转成新MARL总榜 |
| NARRA-Gym | [作者主页](https://jackwwj619.github.io/)与[LMU公告](https://www.som.lmu.de/ai/en/update/news-overview/news/5-papers-accepted-at-neurips-2026-7c6c1c03.html)列NeurIPS2026；具体track未单独确认 | [全文](https://arxiv.org/html/2605.08503v1)框架、实验/评价、误差分析与局限；未声称本地复现 | 叙事与用户体验多维，judge和人类中间排序会不同；不能用自然语言流畅当行为成功 |
| Behavioral Foundation Models for Quality Diversity | [论文](https://arxiv.org/abs/2609.35615)及官方题目目录；track未确认 | 摘要与方法概览，非完整深读 | 行为多样性已可在预训练行为空间搜索；不是我们选择的语言NPC执行底座 |
| Proact-VL | [ICML2026论文入口](https://openreview.net/forum?id=k9PKgV0L4C)及前轮源码记录 | 沿用前轮正文/资源审查，本轮不虚记新深读 | 时机/内容联合研究已有先例；不做视频IO和云端judge主链 |
| A Behavioural and Representational Evaluation of Goal-Directedness | [arXiv](https://arxiv.org/html/2602.08964v1)；OpenReview浏览器验证未能确认会场 | §3–5及关键变换/工具性目标/探针证据 | 无用钥匙、内部地图与动作一致性已有直接近邻，更新切口的增量要求 |
| Evaluating Goal-Directedness (Everitt等) | [arXiv](https://arxiv.org/html/2504.11844v1)；不从ICML模板推断接受 | §1–4与局限，能力分解与受扰执行 | 强制加入变化后快照的能力对照，不把失败当缺目标 |
| Evaluating Goal Drift | [全文](https://arxiv.org/html/2505.02709v1)和[AIES论文入口](https://ojs.aaai.org/index.php/AIES/article/download/36541/38679/40616) | 正文、历史控制和局限，PDF Figure1截图核查 | 目标切换/模式延续本身不新；NPC状态后果需带来真实解释增量 |
| Bayesian Partner Modelling | [arXiv摘要](https://arxiv.org/abs/2608.18490)，接受未核实 | 摘要已核；v1 HTML/PDF尝试失败，旧笔记不冒充本轮全文 | 已占belief–action gap和矛盾触发重规划，保守地按强近邻纳入而非忽略 |

## 两篇新NeurIPS参照究竟教会什么

**alem。** DOCUMENTED：传统多代理环境常把交互困难、单体任务难度与固定协作套路混在一起；它保留世界布局，操控依赖、交接、同步要求，并提供原生文本动作接口。RECONSTRUCTED：先让协作压力成为环境中真实可变的因果对象，再研究失败，而不是通过增加代理数制造复杂度。注意一个难度参数同时改变多项机制，不可自动当作单因子因果结果。本项目借用“相同世界、可核实的依赖变化”的设计尺度，不重训其十亿步MARL。

**NARRA-Gym。** DOCUMENTED：交互叙事需要持续角色、记忆和响应用户，而不是一次性故事文本；采用控制的模型×persona评估及人类体验。RECONSTRUCTED：把“故事写得好”拆开为不同、可不一致的使用维度，借人类评价核对自动量表。其9模型×8persona、3judge的设计不意味着64或72是任何任务的充分样本量；新NPC主张以源任务的变异度决定。我们不继承它的体验结论，也不复制三云端judge成本。

## 隔离而不填空

目录中的“Constraint Retrieval Is Not Constraint Enforcement”等题目，未找到可充分核验的原文时只作继续检索线索，**不据标题归纳机制或说某主张已被完整解决**。NARRA/BFM的track不确定不影响它们作为研究近邻，但不拿来冒充主会地位证明选题。

本轮已完成对所选切口的必要正反定位；Bayesian全文取得、LIGHT归档字节与模型实际运行仍是具体未解决项。新结果准备声明novelty时必须重新扫描；这不是要求本地agent机械重读整个列表才能开始建设。
