# Graded Expectations (SCiL2026)

来源：[primary](https://aclanthology.org/2026.scil-main.46/)；公开评审/分数未核对。

1. **论文形态 / 阅读证据：** 全文正文和refs已读；未获得原code/data，不能声称复现。
2. **背景与压力：** 二分类lie准确率可混淆底层预测与assistant决策；人类对欺骗有graded期待。
3. **改变前提 / idea来源：** Base/思考/指令的continuation概率与human completion比例对齐；来源DOCUMENTED：人类lie/truth续写。
4. **方法 / 数据 / 证据：** 76对照narratives，40有44human completions；Qwen3 .6/1.7/4/8B与instruct/thinking/2507；base4B Pearson .838、Spearman .892。Eq4 q(c|x)∝m(c)exp(mean_logprob(c|x))。
5. **短板与校对：** 测量null待审：若所有score相同且候选仅L/T，m(c)权重本身可完全重建human L/(L+T)；含ambiguous时仍引入目标相关prior。这是公式层可识别性风险，未用原数据证实；不能指控paper错误或把推理当finding。
6. **最近邻与claim ownership：** Base比instruct更像人已有ownership。需count-only、context-free、leave-human-out候选验证，不能把已有human label频率再次嵌入model预测。
7. **可迁移研究动作：** reproduce → 同材料条件切片 → readout/知识check控制 → 跨model/stage。新颖性只做定位。
8. **对本workbench：** 与Hu/Levy、Wavelength、ALTPRAG/PaCE的距离按测量对象和证据区分，不能把这些parent的已有结论改个名字当贡献。
9. **阅读边界：** 上列已读部分明确，未读附录/原code不以PDF下载代替。
