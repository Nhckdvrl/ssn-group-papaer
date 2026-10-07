# ABBEL: Learning Natural-Language Belief States for Memory-Efficient Interaction（作者v2，2026-06-04，venue未核对）

`[证据级别：主文精读＋指定附录]` [arXiv2512.20111v2](https://arxiv.org/abs/2512.20111v2)。Berkeley/GeorgiaTech；官方NeurIPS2026已缓存题名未找到精确ABBEL匹配，不由此判质量/关线。PDF30页，SHA7038f14b9af481e4b96ccecc895d4cf957324f2e20ff1632ded9e88c92ea00e4。

1. **论文形态：** 诊断＋训练接口方法＋性能/内存前沿。
2. **背景与压力：** 递归摘要比完整历史弱，却难在memory和reasoning混合文本中评价信息。将每步分成belief更新与action选择，使belief可单独监督。
3. **改变的前提：** 不把摘要当任意中间轨迹，而使内容/长度成为能各自训练的对象。domain-specific grading与reconstruction grading作用不同，不能混报。
4. **idea来源（RECONSTRUCTED）：** MEM1压缩但信息缺失/错更新→将belief从推理分离→识别既有prior错误传播与过长状态→辅助GRPO采样同一context的belief组＋peak长度惩罚。科学距离在训练接口/具体reward，非发明Bayesian belief或一般summary。
5. **最近邻距离：** MEM1、Arumugam/Griffiths2026自然语言状态、context compression、外部memory；多调用引入额外compute，不是无成本同接口改进。拆更新/使用已为邻 work拥有，但可借对照和方法生长尺度。
6. **数据与实验：** frontier五环境，每环境40任务、3模型；3个RL域、主Qwen2.5-7B，lock另14B。lock三seed、ColBench五seed、QA三seed；ColBench user由Gemma3-27B持隐藏测试/reference模拟，10次提问、10tests，非真实用户。QA训练2目标/6steps→16目标/20steps，有horizon泛化，未测试>20步。40%提升/67%内存为特定16目标相对MEM1，不是所有域统一结果。
7. **方法细读：** Eq5重建的是**最新观察ot**，条件同时含新belief、旧belief、last action，绝非要求重建旧belief。Eq6的Bayes同joint解释不能自动从两个不同排列的chat prompt保证，要实际核查。Algorithm4把观测token logP求和后max(score,−.9)；是否code也使用sum/该cap未核对。PBP主文Eq4与AppD2 batch-centering叙述不完全相同，记录而不凭文字宣告实现错。
8. **证据范围与边界：** 已读Main1–7 pp1–12全、AppD训练/lock22–24、D2/3与Algorithm4 pp27–30全；Table1/2 p10视觉核对。AppendixA/B/C及剩余D pp16–21/25–26未全读，代码未读。所谓memory为peak input+output token代理，未量实际VRAM；frontier部分reasoning只summary估计，不能当实际完整cost。训练4×A100 PCI总时长12–30小时/配置，不外推成单小时全RL复现。
9. **对我们／开放压力：** 借先定位真实信息错误再选择内容reward，而非一串提示。I06源抑制/正论元未完全重建，提示我们反问**重建原观察的奖励是否能分清忠实解释与语义错接？** 此为新探索猜想；不能凭逻辑可能性宣告ABBEL失效，须在固定自然Source/完整已标输出上测reward与语义保真的配对。已有E70原子盲审可复用，0新原数据审计；这比继续frame-source层位网格更有信息量。
