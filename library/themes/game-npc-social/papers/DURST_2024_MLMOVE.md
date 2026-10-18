# Learning to Move Like Professional Counter-Strike Players

规范记录：`durst_2024_mlmove`；Computer Graphics Forum 43(8), e15173 / SCA 2024; DOI verified。实际版本：Author-hosted final typeset PDF, 2024。

**实际阅读范围：** Complete main text §§1–7, PDF pages 1–11; Tables 1–3 and human evaluation; separate Supplemental Material and videos not read/viewed

[原文](https://davidbdurst.com/mlmove/Learning%20to%20Move%20Like%20Professional%20Counter-Strike%20Players.pdf) · [发表／主源信息](https://doi.org/10.1111/cgf.15173)

**稳定 ID：** `durst_2024_mlmove`。Computer Graphics Forum 43(8) / SCA 2024，DOI 10.1111/cgf.15173；作者正式排版 PDF。**实际阅读：** 完整主文 §§1–7（PDF 1–11），表1–3与人类评估；主文引用的独立 Supplemental Material 未下载通读，视频未观看。

MLMove 以实际游戏部署的控制预算为约束：固定 Dust2 地图、CS:GO Retakes 模式，5.4M参数Transformer读至多10名玩家的当前结构状态，生成97类移动选项（方向×速度×跳跃及静止），瞄准、射击和动作转换交给规则。每125ms推理约8ms，平均到每个游戏tick约0.5ms；这是摊销成本，非单次推理0.5ms。小模型在固定地图、缩短预测时间及排除多余输入后达到CPU预算，揭示接口/任务分解对实用性的作用。

CSKnow从1,156小时职业赛日志筛出炸弹安放后的123小时、17k余回合、2292位不同玩家；按回合80/20划分防止邻帧跨集。训练约1.5小时单4090。1430个保留Retakes初态各重复5轮，与真人原轨迹、开发数月的RuleMove及原生GameBot比较；MLMove站位、击杀位置、包抄/分散配置频率更接近人类，但存活时间指标GameBot更接近。15名评审对8组共32段鸟瞰透视视频盲排，MLMove比两基线更似人，真正人类仍最好。TrueSkill相对高16%–59%不是“人类相似度提高相同比例”的直观量尺。

论文目标是匹配专家行动，非赢率最大化；明确角色训练伙伴与替补队友潜力。但主要测试由同类bot控制双方全部成员，输入聚合所有玩家位置，不能直接外推分散、部分观察的人机合作。实际真人与bot混合游玩探索结果不确定，因为玩家忙于游戏难以判断他人移动；不能写成已验证队友体验更好。只在一地图一模式且无手雷、同武器，仍有被动、反复清角、转弯受限等问题。领域价值在以游戏专家术语构造可测协作站位，并把风格、团队结构和毫秒预算连接；迁移到新地图/游戏需新数据和接口。

**主源：** https://davidbdurst.com/mlmove/ ； https://doi.org/10.1111/cgf.15173

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Human-level performance in 3D multiplayer games with population-based reinforcement learning](JADERBERG_2019_QUAKE.md) | MLMove 优化专业移动分布及实时 CPU 成本；FTW 主要优化赢率和跨随机地图战术，并依赖大规模训练。 |
| [Generating Personas for Games with Multimodal Adversarial Imitation Learning](MULTIGAIL_2023.md) | MultiGAIL 允许风格权重混合；MLMove 没有同样的显式个性调节接口，而强调站位、掩体与队形统计。 |
| [Adaptive Game AI with Dynamic Scripting](SPRONCK_2006_DYNAMIC_SCRIPTING.md) | MLMove 的策略主要离线模仿，dynamic scripting 在战斗间更新规则权重；二者都保留人工确定的控制边界。 |
