# When Should Models Change Their Minds? Contextual Belief Management in LLMs（EMNLP2026 main）

[arXiv v2](https://arxiv.org/abs/2605.30219v2)，[正文](https://arxiv.org/html/2605.30219v2)。读取§1–5.1、方法定义/主表；§6机制与附录未完整读。accepted身份来自arXiv作者声明，不称已核对会议proceedings。

- **形态与来源：** closed-world精确测量+训练/提示干预。把更新、保持、不相关信息隔离分成可符号验证的轨迹；来自多轮上下文不稳定与belief dependencies压力。
- **资产：** Rule Discovery（Wason triples）与Circuit Diagnosis；固定有限hypothesis空间，每步完整candidate-set gold。corrected evidence替换先前观测，non-evidential noise不得改变oracle。
- **重要读数：** k次trajectory任一次失败就算sample失败，主表高失败率不能直接当平均per-turn准确率；训练按Jaccard state reward，不是普通QA。
- **已拥有：** Failed Stay/Update/Isolation，以及prompt有限、RL改善。我们不能把“更新且保护无关事实”或“记忆正确但操作失败”当全新故事。
- **与I01距离：** 我们测正常语言中predicate/episode触发的患者关联，当前没有显式belief-set更新任务，未知是否真正修订完成。若以后研究scope覆盖，必须有语言关系/事件指向的具体增量与竞争解释，不改挂泛泛belief management benchmark。

当前HTML读取，PDF尚未缓存；代码与数据未下载审计，不把网页可见当license/hash资产完成。
