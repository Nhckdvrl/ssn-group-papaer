# Probing Good-Enough Processing in Large Language Models with a Paraphrasing Task（KJELL 2026） `[证据级别：正式完整主文]`

来源：[期刊DOI](https://doi.org/10.15738/kjell.26..202601.127)，publisher公开PDF `http://journal.kasell.or.kr/xml/48116/48116.pdf`；读§1–5页127–138全部，参考文献不算精读，图精确比例仅用作者正文说明。Korea/Dongguk，一月刊，不是最新顶会；依直接相关性读。未核对评审分数/仓库实现。

1. **形态/压力：** 跨测量验证。同一初始误读问句可能诱发错误，不能把Yes误答自动说潜在理解失败。
2. **前提/来源：** DOCUMENTED：Lee&Shin2025 QA偏差＋Patson2009人类自由复述→GPT3.5/4整句改写。RECONSTRUCTED：把人类测量对策迁到LLM以回答模式是否跨任务保持，非新生成算法。
3. **距离：** Christianson2001/Patson2009已有正确新关系与错误旧关系共存；Lee&Shin2025已有GPT QA；Amouyal是多模型GP比较；这里只换输出方式及OT/RAT比较。跨用途差异/复述错误整体叙事有现成ownership，但不足自动否定更深因果研究。
4. **方法/数据：** 单一OpenAI族GPT3.5/4-0613；原Patson24句12OT/12RAT，GP/cue只差逗号，每S零样本重置上下文10次。单prompt要求同义改写、不照抄，无一句恢复/内部干预；failed/partial/full/other，full作correct、GLMM items随机效应。temperature/完整评分员协议主文未明确，仓库未核对。
5. **结果与保留：** GPT4 GP OT/RAT完整重析约35%，先前QA0/20%；cue近100%。partial是旧verb对象+新verb主语同时保留，failed很少。OT与RAT相似，但“RAT强制自身所以无语用影响”依赖实际配价理解，作者承认这个竞争解释。QA/复述来自不同研究，不是逐生成配对；不能将相似结果直接称同一因果机制。
6. **限制：** 同词串copy/synonym替换可能给看似正确复述，作者讨论但未做因果测试。无白盒不能从输出推断attention聚焦/过度优化。这些是论文解释，非已观察机制。重复10次不是24×10独立词汇样本。
7. **可借动作：** 让两个输出考验同一可校验关系，区分failed和partial、排除只读最终关系就正确的松读数。研究对策的创新要有独特后果，不能仅再跑强新模型替代旧GPT。
8. **对我们：** E53是必要科学地图而非单独novelty：570源/3独立族/格式与一句恢复完善范围。E63/E64共源因果、更细源消费位置，以及E65/E66撤销旧关系/新关系建立入口不对称是可能增量；目前不存在一致充分证据，不把覆盖问题变成桌面关闭。

2026-10-08主文重读／Fig1视觉核（不是新增论文）：已读正式稿SHAe9f5c3068b4222fbda4f1f0bee5f8f79d716dad54f32337d018436b4f4012d5c；旧卡完整保留。对I08更具体的边界：一般question诱导/任务深度与overoptimization已有讨论；E99新增的是同一提前目标使QA成功且明确角色错的联合比例升高，旧QA仍forced-choice，E98须actual用途支持。不能用多模型复跑自由复述单独占novel，也不据局部相似关闭线。
