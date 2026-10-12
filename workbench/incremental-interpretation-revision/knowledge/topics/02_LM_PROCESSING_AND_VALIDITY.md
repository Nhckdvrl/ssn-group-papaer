# 专题二｜LM究竟是在加工句子，还是在完成一个人为构造的阅读测试？

> 本文不是一篇泛泛“自报不能说明理解”的综述，而是整理一条**测量失败→调整评估对象→验证自然/正式基线→检查功能后果**的研究演化路径。[全库索引](../PAPER_ATLAS.md)。

## 1. 四种输出任务不是同一条能力轴

**分辨表**（每项只能指向所定义的对象）：

| 任务/仪器 | 观察 | 强竞争解释 | 不能推的结论 |
|---|---|---|---|
| 词 surprisal / 人的RT | 这个词在现有prefix下是否出乎意料/多费时 | 词频、句末wrap-up、错误先验、结构阻塞 | 人/模型最终事件图是否正确 |
| 目标词补全概率 | 既定字符串的生成偏好 | 表面词频、训练先验、词位与语义都有贡献 | 内部已建立完整 parse，亦不等于自然自由生成 |
| “旧角色对吗？”二元QA | 此格式诱发的答案 | 不理解题、old关系语用可推、积极否认old但不知道new | 新语义完整、old内存存在 |
| 正确新关系的开放陈述 | 模型在可选表达中具体承诺什么 | 含糊、避答、被模板暗示、命名不稳定 | 另一用途一定正确，或闭合全部关系 |
| 反身/后续句/新问题 | 正确依赖在另一操作里是否发挥功能 | 问句/任务额外成本、同一句其它信息路径 | 唯一中间表示变量已确认 |

这不是说问答无效；任何测量必须服务特定科学构念。[Hu & Levy EMNLP 2023](../hu2023-metalinguistic-measurement.md)比较概率与meta语言提示，[Hu & Frank COLM 2024](../hu-frank2024-task-demands.md)更具体地提出**资源×辅助任务需求**交互：测量差异可能随着模型的大小/训练而变化，不能用一个简单“哪种测试更可靠”盖过它。[Han ICLR2025](../han2025-causal-comprehension.md)比较语义改变、表面改变的因果估计代理；它的proxy同样不保证严格保持文本全部意义。

## 2. 从Jurayj/Li到Amouyal的可检验问题如何变化？

[Jurayj et al.2022](https://aclanthology.org/2022.blackboxnlp-1.25/) 用局部surprisal与表示几何观察暂时歧义；更关心加工**过程**，并非证明完整句子含什么依赖。

[Li et al.2024](https://arxiv.org/abs/2405.16042) 增加分块reading与initial-proposition comprehension，试图从disambiguation处的预测冲击移向最终理解；但很多最终关系只是预检，词概率变化、Yes/No内容和attention解释仍未形成同一严格因果指标。[原卡](../li-2024-incremental-comprehension.md)。

[Amouyal et al.2025 ACL](https://aclanthology.org/2025.acl-long.403/) 跨模型与人类用结构、plausibility、动词类别对照，并关联复述/视觉任务；科学进步之一是**问初始句法误读是否真的反映一个可观测且跨测试存在的现象**。它并非每一种问句语义都可在三值逻辑下无争议。

[Amouyal et al.2026 ACL](https://aclanthology.org/2026.acl-long.1040/) 进一步将四种GP与三种非GP在统一任务里比较，重点从“某个GP能否答对”变成“**人类与模型的困难次序在不同结构下是否相似**”。真人RSVP 400ms/词+100ms空屏、5秒答题，5380条回答；LM31模型/五族与8个prompt平均，thinking设置用一个prompt。这种统一工程可以提高描述可比性，却不能把 human temporal parser 与 autoregressive LM 的*实现机制*等同。表中GPT-5 GP46.8%而非GP93.7%是指定非高思考设置，**不是2026全部推理配置的最新能力**。[原卡](../amouyal-2026-processing-difficulties.md)。

该论文“GP需扔掉先前解释”的说法是尚待实验的机制**猜想**。科学问题在于若人机同样表现不佳，究竟是同一个困难操作，还是不同流程碰巧导致同样分数？这一点可反过来解释我们过去为获得人机同型曲线而投入的不足之处。

## 3. 纵向轨迹不是因果LM“重写了早token”

[Madureira et al. ACL2024](../madureira2024-restart-incrementality.md)分析restart-incremental的双向架构；同一token随新增前缀通过**重新编码**获得新的contextual state。[Storer & Zimmerman 2026](../storer2026-incremental-contextual-trajectories.md)同样在RoBERTa等encoder每增加token后再次前向得到早token新的CWE，轨迹分类可高分，但critical region first-word外部holdout降至≈54.9%。需要注意，time shuffle损伤可能因为顺序/位置破坏，不唯一支持某个“重分析轨迹”。

**对因果decoder而言**，合法KV缓存使早token的历史状态不原地变化，然而后到token可以读过去证据并在自己位置构造新的语义内容。仅仅把同一tokens的prefill拆分为两次，无论结果如何都没有形成“先错误理解过”和“一次看完整输入”的两个不同可识别处理条件（见[构念审计](../02_CONSTRUCT_AND_MEASUREMENT.md)）。切勿把encoder复读机制和causal decoder的依赖绑定在同一图的纵轴上。

## 4. 类别/任务 × 信息证据的交互，比继续增加模型数更值得知道

模型可能使用三类捷径来完成“理解题”：
- 语法许可与语义蕴含（我们真正要问的）；
- 世界合理性和noisy-channel修正（源没有说的也可能被补全）；
- meta问句与解码偏好（工具/格式学会了就变分）。

两条反例告诉我们不应靠题型成功就选故事：E11把“完整subject span”加入元语言问题就显著恢复部分无歧义延长条件答案，因此早期一些role下降属于**instrument artifact**；E09正式SAP自然题仍存在GP×cue差异，因而也不能反过来说“全部GP失败都是我们问句造的”。这意味着真正有解释力的研究必须给这两种相反证据一个共同模型，而不是挑一边。

## 5. 从学习原文得来的实验方法，而非照抄实验菜单

- **对象一致**：预先给每个源定义完整事件和独立用途的必要关系。不要把英文句法的old No、新闻事实的反驳、新的belief update当一种“revision”合格标签。
- **信息透明**：自然来源、前置阅读目标、外加正确frame属于不同信息处理。把oracle作为可实现性上界，不能与原生来源混计。
- **有判别力的反结果**：同样correct old No但new dependency全错，说明单No指标根本没有覆盖目标；如Q/Options次序效应受mapping控制而不稳，先撤回task-order大机制。
- **独立后果**：条件有真实语义差异，才值得用另一个未参与拟合的用途测试“修订”是否真正发挥作用。大样本有价值，但必须是正确测量的来源聚合。

当前工作不自动“补一个更大的benchmark”。旧E卡最大的知识价值之一正是告诉我们，有些漂亮的数字其实不对应自然修订对象。
