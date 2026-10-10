# Just-in-time and Distributed Task Representations（预印本）[v3主文§2–5]

[v3正文](https://arxiv.org/html/2509.04466v3)，[v3 PDF](https://arxiv.org/pdf/2509.04466v3)，Li / Campbell / Chan / Lampinen；venue corpus列ICLR2026 Reject，未以该状态作科学判决。2026-10-10补读v3 PDF主文§2–5；HTML503后下载PDF并转文本，未把v1当最新全文。

1. **形态：** 表示动态与迁移范围的解释。
2. **压力：** 任务向量有效，不意味着它随示例稳定累积、持续存在或代表完整任务。
3. **改变前提：** 可解码任务身份、可迁移任务状态、可支持的语义范围要分别测。
4. **idea来源：** RECONSTRUCTED；从已有任务向量跨query恢复，追问其形成与作用范围。
5. **距离：** Hendel/Todd、Xiong与跨提示任务表示；贡献是时间/语义局部性。
6. **操作：** dummy query抽取残差，在50-query开发集选层，迁移到zero-shot新query；增加示例、变抽取token、比较单任务/重复/复合输出。主文Gemma3预训练4/12/27B，v3报告附录Qwen3 4/8/14B复现。14简单任务中v3仅两项count任务明确列hard-to-transfer；此前v1读数不能直接沿用。§4.2还做跨token交换：输入前Q冒号→答案前冒号可部分恢复，功能和身份表征有部分重叠，非严格二分。
7. **边界：** 覆盖残差覆盖式迁移接口；部分任务表现提高而迁移不提高，不证明没有其它分布式实现。输入前Q冒号也被测试，不可把“输入前提取状态”本身当新意。
8. **研究动作：** 先改变任务作用范围，再检验原表示解释能否预测；保留接口失败的替代解释。
9. **对ICES：** E66在single/mixed均失败，只限制该KV/遮挡接口。新研究应明确迁移的是Source地址、criterion含义还是答案倾向；不能仅再找一个有作用的位置。

## E88定位

v3已覆盖输入前状态部分迁移、Qwen家族、任务范围局部性。本次候选的具体增量是同来源姓名、改变其从demo推断的标准、保留recipient示例，让标准相关信号与原有证据竞争；第一次阳性仍兼容criterion-conditioned retrieval。没有因新的近邻撤回E85或自动判定ICES价值。
