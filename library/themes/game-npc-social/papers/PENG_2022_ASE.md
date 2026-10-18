# ASE: Large-Scale Reusable Adversarial Skill Embeddings for Physically Simulated Characters

规范记录：`peng_2022_ase`；ACM TOG 41(4), Article 94 / SIGGRAPH 2022。实际版本：arXiv v2, 2022-05-05。

**实际阅读范围：** Complete main text §§1–11, PDF pages 1–14; task definitions, table 1, coverage and recovery metrics; appendix hyperparameters and videos not read/viewed; Critical evidence table visually verified on rendered PDF page 12

[原文](https://arxiv.org/pdf/2205.01906) · [发表／主源信息](https://xbpeng.github.io/projects/ASE/)

**稳定 ID：** `peng_2022_ase`。TOG 41(4), Article 94 / SIGGRAPH 2022；arXiv v2（2022-05-05）。**实际阅读：** 完整主文 §§1–11（PDF 1–14），方法、任务奖励、表 1 与覆盖/恢复测量；附录超参数未通读，演示视频未观看。

ASE 正面补 AMP 的重复训练问题：先用动作判别器与互信息技能发现目标，训练输入连续潜变量的通用低层策略；之后冻结低层和判别器，为每个新任务训练高层策略。球面潜空间控制无界输入造成的分布外动作，训练中不断换潜变量提升响应性；多样性正则避免忽略输入。低层在 10% 回合从随机摔倒状态开始，故恢复策略能够随技能一起复用。高层以 6 Hz 给潜变量，低层以 30 Hz 给关节目标；任务目标仍是由研究者定义的坐标、速度、朝向和击倒物体奖励。

一名持剑盾的 37 自由度人形从 187 段、约 30 分钟动作资料中学习，预训练超过 100 亿样本，约十年模拟时间、单 V100 十天；不能把模拟年数当真实训练时长或人类数据量。五类下游任务比较从零训练及去除技能发现/多样性消融，每配置 3 个低层模型、各 4096 评估回合。技能发现对覆盖与下游表现关键；多样性项提高可观察技能转移密度，却未大幅改善这组任务分数。纯任务从零策略在多数任务奖励更高但动作怪异，再次说明效率与自然度不是同一指标。500 次随机扰动后均恢复，平均 0.31 秒，但“恢复”由骨盆/头部高度阈值定义，且作者承认会有夸张旋转，并非玩家认可度测量。

重要进展是可复用、可引导的技能层和物理恢复；真实未知包括更复杂环境下组合、覆盖全部动作、稳定自然的恢复与样本效率。现有技能转移统计只呈现最常匹配的 50 段，约 10% 可能转移被观察到，不能写成自由组合所有技能。它适合知识库“角色身体能力与上层目标接口”，与语言规划相连接时还需明确目标怎样落到坐标/动作、失败反馈怎样返回；论文本身未研究 NPC 动机或玩家合作。

**主源：** https://xbpeng.github.io/projects/ASE/ ； https://doi.org/10.1145/3528223.3530110

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [AMP: Adversarial Motion Priors for Stylized Physics-Based Character Control](PENG_2021_AMP.md) | ASE 的冻结低层控制器使高层可在新任务选择风格技能，AMP 原形式的负样本分布依赖当前任务策略。 |
| [DeepMimic: Example-Guided Deep Reinforcement Learning of Physics-Based Character Skills](PENG_2018_DEEPMIMIC.md) | DeepMimic 展示较精确参考动作控制；ASE 更重视规模、组合与恢复，但并不保证所有技能间任意转移。 |
| [Video PreTraining (VPT): Learning to Act by Watching Unlabeled Online Videos](BAKER_2022_VPT.md) | ASE 从动作捕捉和完整身体状态学关节控制；VPT 从人类游戏视频与少量动作标签学键鼠操作，数据与动作接口不同。 |
