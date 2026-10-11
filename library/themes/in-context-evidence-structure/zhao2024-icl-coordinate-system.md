# EMNLP2024：认任务与相似示例的解释竞争

[Zhao et al.主会](https://aclanthology.org/2024.emnlp-main.689/)，[2407.17011v2正文](https://arxiv.org/html/2407.17011)§2–3/5–6。2026-10-12读指定段落，未重跑。

- **idea来源（RECONSTRUCTED）：** 标签扰动有时伤害、有时不伤害，单靠“类似样本复制”或“已有任务识别”都不充分，转为两个不同预测变量。
- **关键动作：** 同一测试输入当最高相似示例但改其label；用label位置logit-lens的代表任务词峰值rank衡量识别；多象限比较。默认准确率用完整词表，不只指定candidate。
- **方法范围：** PIR依赖代表任务词和层最大值；任务可读出不保证后续deploy。semantic-vs-lexical、同输入错label与预训练prior不都是独立参数，因此不能从框架直接断言所有任务采用唯一算法。
- **与ICES距离：** 已拥有prior/task识别与类似demo作用的共同解释，full输出指标也非首次。ICES保护raw A、正交B私人配对/命名后测形成来源；E124/125公共关系仅是解释竞争把手，不把关键词readout当天然绑定证据。借鉴主旨是一组现有解释的具体矛盾，而非无限扩dataset/细节规范。
