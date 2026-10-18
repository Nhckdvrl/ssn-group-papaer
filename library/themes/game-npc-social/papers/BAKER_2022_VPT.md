# Video PreTraining (VPT): Learning to Act by Watching Unlabeled Online Videos

规范记录：`baker_2022_vpt`；NeurIPS 2022。实际版本：Official proceedings PDF; standalone supplements unavailable in downloaded file。

**实际阅读范围：** Complete main text §§1–5, PDF pages 1–10; separate Appendices A–I and videos not read/viewed

[原文](https://papers.neurips.cc/paper_files/paper/2022/file/9c7008aff45b5d8f0973b23e1a22ada0-Paper-Conference.pdf) · [发表／主源信息](https://proceedings.neurips.cc/paper_files/paper/2022/hash/9c7008aff45b5d8f0973b23e1a22ada0-Abstract-Conference.html)

**稳定 ID：** `baker_2022_vpt`。NeurIPS 2022 正式会议 PDF。**实际阅读：** 完整主文 §§1–5（PDF 1–10）；所下载正式 PDF 不含正文引用的独立附录，故未读附录 A–I；视频未观看。

VPT 处理可学行动数据缺口：互联网游戏视频通常只有图像，没有按键标签。先用 1,962 小时带操作记录的承包者数据训练可观察前后帧的逆动力学模型，再给约 7 万小时筛选后的 Minecraft 生存视频产生伪动作标签，训练只看过去帧的行为克隆模型。逆动力学只需推断环境如何变化，相比预测人的意图更省标注。平台使用 20 Hz 原生键鼠和背包拖放界面，这与调用 craft API 的 Minecraft agent 是不同控制问题。

基础模型 0.5B 参数、30 epoch，约 720 V100 九天；评估通常在新生存世界运行 60 分钟，图 4 为 2,500 回合。基础模型能造工作台，但平均每小时 0.19 张，承包者 5.44 张，不能从“会造”推出可靠能力。行为克隆聚焦早期游戏后增强技能；进一步用手工科技树奖励、约 140 亿帧 PPG 和对预训练策略的 KL 约束，最强三阶段模型在 10 分钟内造铁镐 >80%、取钻石约 20%、造钻石镐 2.5%。同任务人类对应 57%、15%、12%；只有部分中间技能达到该人类基线，最终目标明显低于人类。去掉 KL 后学习停留在初级物品，说明预训练的稀有技能可能在尚未兑现价值前遗忘。

这是一条把示范变为探索先验的有效路线，且清楚展示监督损失、零样本行为和微调潜能可能不一致。数据规模消融的较小点用 71M 模型，最大点用 0.5B，不能把整条曲线视为纯数据因素。基础策略在主要实验中不接受任务指令；其“general”是宽行为先验，非自主制定目标或通用指令遵循。它能帮助构建执行技能，但未测 NPC 人格、玩家体验或合作。知识库应明确区分基础模型、行为克隆微调和 RL 后模型，避免把最强专门微调结果归给开箱基础模型。

**主源：** https://proceedings.neurips.cc/paper_files/paper/2022/hash/9c7008aff45b5d8f0973b23e1a22ada0-Abstract-Conference.html ； https://openai.com/index/vpt/

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Scaling Instructable Agents Across Many Simulated Worlds](SIMA_2024.md) | VPT 主文以 Minecraft 视频预训练和特定目标微调为主；SIMA 将语言指令与多个不同游戏的原生控制连接。 |
| [SIMA 2: A Generalist Embodied Agent for Virtual Worlds](SIMA2_2025.md) | SIMA 2 在预训练语言模型上追加具身数据与可验证奖励学习；VPT 的核心是逆动力学补标签再行为克隆。 |
| [DeepMimic: Example-Guided Deep Reinforcement Learning of Physics-Based Character Skills](PENG_2018_DEEPMIMIC.md) | VPT 面对外部游戏像素与键鼠界面，DeepMimic 则能直接读取身体状态并向关节 PD 控制器输出目标。 |
