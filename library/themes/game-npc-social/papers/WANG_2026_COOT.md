# CooT: Learning to Coordinate In-Context with Coordination Transformers

规范记录：`wang_2026_coot`；ICML 2026, PMLR 306:125587–125625; official proceedings identity verified。实际版本：Official PMLR ICML 2026 PDF, 39 pages。

**实际阅读范围：** Complete main text §§1–6, PDF pp.1–9; all main quantitative tables and adaptation results; Appendices A–C pp.14–25; human study D.1–D.3 and coding tables/comments pp.25–28; Appendices E–I pp.34–39, including added PACE/GAMMA/PLASTIC and sparse-reward baselines, algorithms, theoretical interpretation; remaining comment tables/interfaces pp.29–33 not fully read

[原文](https://raw.githubusercontent.com/mlresearch/v306/main/assets/wang26ag/wang26ag.pdf) · [发表／主源信息](https://proceedings.mlr.press/v306/wang26ag.html)

**稳定 ID：** `wang_2026_coot`。ICML 2026，PMLR 306:125587–125625正式39页PDF。**实际阅读：** 完整正文§§1–6（1–9）；A–C（14–25）、D实验/编码及部分原评论（25–28）、E–I（34–39）；29–33剩余评论/界面未全读。

CooT以“针对伙伴的最佳响应”作为监督目标。先从带事件偏好奖励的伙伴及其已训练最佳响应收集轨迹，用小型GPT-2结构（4层、128维，**不是商业语言模型**）读最近五回合状态/己方动作/奖励和当前查询状态，输出响应动作；测试无初始示范，完成一回合才更新跨回合context，无梯度更新。关键不是把轨迹塞进任意模型，而是将伙伴行为到互补响应的映射专门训练。附录B.1给36伙伴组成15 MEP+21 HSP，200/250轨迹每伙伴，主要315k查询训练例；每布局每种子19 GPU小时不含既有伙伴/BR训练。

五Overcooked布局、10伙伴（多配方15）、每伙伴连续50轮，3训练种子；GRF三攻一防含守门员，另10对伙伴。总体BR-prox 0.57，对HSP 0.44；多配方Coord Ring回报45.96对29.35，Counter 28.28对21.37，而普通Coord Ring 38.30低于HSP 41.10，Asymm也非最高。GRF表2“goal rate”是200步内平均进球数2.50对HSP1.46，不是成功概率。真人N=36（7有实际Overcooked经验），每人四伙伴各8轮、每轮200步，双盲随机顺序；18/36首选CooT，回报63.5对最佳其他53.0，合作评分4.0、适应3.1。突换三类伙伴六种方向，达到新伙伴不切换回报需1–6回合，不是瞬时恢复。后半套实验并未测新游戏布局。

消融包括BC/RNN、HSP在线微调、HSP-meta/PACE改编、GAMMA（两图）、PLASTIC（一图）、context长度/打乱；本体稀疏奖励不能消除其依赖预训练BR动作示范的监督优势。文中“旧context过时”是解释假说，伙伴固定时也可能是己方分布变化；不能当已辨识因果机制。正式稿还存在可复现性欠账：§4.2/G声称查询状态独立于context，算法1第22行却从context采样；§5.1称只评最终检查点，B.6又纳入早期；主文全HSP与附录混合池描述不同。记录这些具体不一致，并据更细附录报告配置，不自行裁定代码实际执行情况。

与ICRL4AHT合读可见正结果有明确适用面：明确的BR监督、相同环境下偏好伙伴外推、跨回合连续交互，能产生人可感知的适应；尚不能推出一般序列模型能理解任意伙伴。论文附录借用DPT遗憾界解释收敛，本轮未核该定理全部假设，不将其当CooT实际任务最优保证。

**主源：** https://proceedings.mlr.press/v306/wang26ag.html ； https://raw.githubusercontent.com/mlresearch/v306/main/assets/wang26ag/wang26ag.pdf

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Learning Zero-Shot Cooperation with Humans, Assuming Humans Are Biased](YU_2023_HSP.md) | CooT 用伙伴最佳响应轨迹训练条件动作预测器；HSP 本身不依赖跨回合 Transformer 上下文来在线改变响应。 |
| [Benchmarking the Limits of In-Context Reinforcement Learning for Ad-Hoc Teamwork](JING_2026_ICRL4AHT.md) | 两者正负结果来自不同观察、伙伴分布和监督数据；ICRL4AHT 的局部视野与新配方不是 CooT 原实验的同条件复测。 |
| [ZSC-Eval: An Evaluation Toolkit and Benchmark for Multi-agent Zero-shot Coordination](WANG_2024_ZSC_EVAL.md) | CooT 使用 BR-Prox 检验相对伙伴可达表现；ZSC-Eval 更关注评价池是否要求有差异的最佳响应。 |
