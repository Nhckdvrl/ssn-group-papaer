# Accommodation and Epistemic Vigilance — ACL2026 main

[出版页](https://aclanthology.org/2026.acl-long.736/) · [原代码](https://github.com/myracheng/accommodation)，commit5d5c9696d906564184726f01fb76559a639131b8。

- **已读范围：** 正文§1–8与limitations；AppA–E方法/关键控制、TableA1/A3与末尾FPR表已读，所有后部图表未逐项抄核；README、生成例、Cancer与NFP judge实现已读，未运行闭源API。
- **来源 DOCUMENTED：** 人类accommodation/vigilance的QUD/at-issueness、presupposition和source reliability→重新解释医药误信与sycophancy跨域失败。理论统一已有自然压力，再用控制和轻干预检验，是顶会尺度参照。
- **设置：** 6models，包括Qwen3Next80B/Llama8/70与三API。Study0原16场景翻译→64prompt，趋势不显著。Cancer585→GPT4o改写三形式1755，SAGE104facts×8原模板，ELEPHANT两个各500及OEQ；医疗内容原有expert metadata，当前不作医疗建议。
- **已拥有：** at-issue易纠错、presupposed难纠错、unreliable提示与其交互；wait-a-minute与explicit控制，150NFP及SafetyOK false positives；PCR−FPR、safety−FPR。不能claim首次hit/FA并看、首次帮助vs脑补/纠错的边界，也不能把本territory改名vigilance便称新。
- **重要边界：** WAIT在SAGE经FPR控制无总体显著提升；Gemini出现prefill截断/乱码（AppE）；Llama几乎拒绝医药提问。explicit在framing上过度挑战。这些失败与收益同报。两轮pushback更容易accommodate，已经拥有多轮norm pressure，不能泛称首次撤回失灵。
- **数据/评分风险：** 改写30人工抽检、embedding相似.97并不证明所有语义保留；SAGE encoding与长度混杂，作者主动不混作主因果分析；3API judges/Vertex source为重评依赖，源code顶层MODEL_ID等配置缺口不能直接作为本地objective scorer。公共repo只有两改写CSV与生成/judge例，没有Study0完整资产或所有response cache。
- **与我们距离：** factual challenging/规范行为与implicit q posterior不同；若拓展安全行为，须确认facts、请求和候选q，不能跨不同gold相加。可能增量是同一谱系下来源/知识/QUD怎样改变候选解释，再联系行为；目前没有novel claim。
