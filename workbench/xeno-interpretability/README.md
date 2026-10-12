# Xeno-Interpretability — 解释的边界与模型原生表征

**状态：PROPOSED**（用户 2026-10-12 明确批准创建独立 workbench；不改变其他 ACTIVE 状态）
**源论文：** [Pierucci et al., Xeno-Interpretability](https://arxiv.org/abs/2609.20408)，2026 arXiv 概念性论文。
**科学兴趣：** 当一个表征可识别、可预测、可干预，却难以归入现有人类概念时，究竟是概念体系不充分、解释器不充分，还是实验对象根本不对？
**论文主旨 / 目标会议：** 均未确定；**零个已验证实验结果**，`CLAIMS.md` 主张全部 L0。

## 入口（所有本项目专属文献资产都在 knowledge/）
- [知识库索引与规范](knowledge/README.md)（从这里开始读）
- [精读笔记：谱系、方法、数值、反证、idea 来源](knowledge/papers/CORE_READS.md)（当前核心资产）
- [领域地图与可检验的解释压力](knowledge/LITERATURE_MAP.md)
- [精读进度与待读近邻](knowledge/READING_QUEUE.md)
- [Xeno 源论文卡](knowledge/papers/PIERUCCI_2026_XENO.md)

## 研究纪律
1. **先综述、后顶会、再前沿预印本。** 最新 NeurIPS 2026 优先扫描，但会议身份、全文与版本须逐条核验。
2. **不追零近邻。** 寻找重要、自然且仍有解释空白的问题；精读须重建 parent → 研究压力 → 思路来源（标记 RECONSTRUCTED / DOCUMENTED）→ 区分性实验 → 相对最近邻的实质增量。
3. **不先指定最终 idea。** 强 baseline / 可复现测量 / 竞争假设 / 高信息量实验驱动方向；可以推翻早期猜想，不为保故事拼方法。
4. **证据分层。** 好看的自然语言标签 ≠ 可靠预测；激活相关 ≠ 因果功能；成功 steering ≠ 自然模型实际使用该机制；描述失败 ≠ 原则上存在不可描述“外星语义”。
5. **只维护紧凑的本地知识库。** 论文信息更新原卡，集中保存谱系、数字、错误与读数。不复制成长流程宣言或不断添加空目录。

## 现有科研文件与决策
- [CLAIMS.md](CLAIMS.md)：L0 假设；[PAIN_LOG.md](PAIN_LOG.md)：只有跑出真实 baseline 痛点才追加。
- `experiments/`、`ideas/`、`results/`、`logs/`：执行资产，不与 literature 知识混写。
- **2026-10-12**：用户决定建立独立 xeno workbench，知识库必须在工作台内部；继续深读并压缩重复材料。
- 算力：尚未启动新实验、未占用 GPU。后续优先单卡 / 单节点可重复的强开放基线。
