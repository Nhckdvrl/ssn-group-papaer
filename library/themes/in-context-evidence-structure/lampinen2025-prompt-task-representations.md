# Do different prompting methods yield a common task representation in language models?（预印本）[当前HTML§2–3.1、5.1]

[原文](https://arxiv.org/html/2505.12075)。2026-10-11读方法、主文首项结果与限制；其它结果按所读摘要/图注区分，未核接收状态。

1. **形态：** 任务表示提取方法与接口比较。
2. **压力：** 相同任务的instruction/demo都能成功，不意味着能由同组头提取通用任务向量。
3. **改变前提：** 分开头localizer、激活来源、接收者条件，做交叉组合。
4. **idea来源：** RECONSTRUCTED：先确认两种FV各自有效，再检查共同性；非发现时间线。
5. **距离：** Todd FV的扩展；不同提示产生不同功能接口已经被研究。
6. **方法：** 每头task-conditioned mean，shuffle或匹配长度/概率的非任务文本为基线；100均值例、25因果打分例、20头。instruction从模型生成候选中选5强项；只保留成功prompt并省略弱任务，这个选择在我们设计中不能照搬为无筛选确认。
7. **证据边界：** demo FV用shuffled10-shot，instruction FV用0-shot，接收场景本来不同；作者做mismatched/localizer对照。通用表示没有找到不证明不存在，限制中明确承认。我们的Goal比较不能仅凭接口差异就声称新模块。
8. **研究动作：** 区分“哪个组件可被修改”与“该组件当前生成什么信息”；交叉localizer和内容，而不是为每个失败重新挑层。
9. **对ICES：** 私人Goal/criterion Goal差异值得解释，但宽泛Goal-dependent task-state或跨接口迁移失败不是新意。具体目标仍是共享标准如何与私人映射组合，先看E97冻结结果，不抢先铺开神经层扫描。
