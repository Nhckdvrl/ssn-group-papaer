# Fake Player: Imitating Real Player to Distill Data for LLM-based NPC Training（ICLR 2026 投稿）

**证据范围：已读原 PDF 的索引正文片段，不是全文精读完成。** 主源：[投稿 PDF](https://openreview.net/pdf?id=nfMzqKhobR)、[原文版本链接](https://openreview.net/pdf/2e26df077644bbbe3df13f485ea6433e09764b7b.pdf)、[论坛](https://openreview.net/forum?id=nfMzqKhobR)。原文直链/公开版本返回 browser challenge/403，停止抓取；通过主源搜索索引实际读到第2页方法动机/三 agent 描述、第9页 Table2/结论。关键附录、完整 §3–6、提示全文及真实日志来源尚未获取，不能以摘要代替这些部分。

1. **状态与形态：** 本地 venue corpus 记录 ICLR2026 Reject、平均4.5；这只作定位，不据此否定实质。形态为玩家侧数据生成方法＋训练前质量评价及下游验证。
2. **问题与 Idea 来源：** DOCUMENTED：NPC 数据需兼顾角色回复与玩家输入；普通 role-playing 玩家易冗长、失真。作者把界面表达约束引入模拟玩家。RECONSTRUCTED：玩家消息的生成过程本身是影响 NPC 评价的重要环境条件。
3. **已核方法：** Inner Monologue agent 生成想法，Intent Analysis agent 维护意图栈，Typing agent 把当前意图变成简洁玩家文本。这里已看到的是消息接口；没有据此确认它控制原生角色动作或库存。
4. **已核评价：** Distill Bench 在简介中定义话题相关、人类相似、数据多样三维；Table2 比较 ICL/Role-Playing Agent/Fake Player 数据训练的 Qwen2.5-7B 与 Hunyuan-7B，并列出 TR/CC/CP/EA/CI/CR 等角色对话维度。没有把角色互动分数当物理任务完成。
5. **待核内容：** 真实玩家日志的游戏、来源/授权/分割、蒸馏与评测重叠、完整 prompt/裁判程序、下游训练细节及实体动作接口。未确认作者代码/数据入口；本地元数据 `github` 为空、附附件ZIP名不等于代码不存在。不能据局部阅读声称已经验证工业部署或真实玩家行为保真。
6. **对整体研究的距离：** 值得继承“别把合成玩家当真实人类”的压力：我们的小闭环只声称特定可见信息与权限下的响应者效应。当前读到的文本数据质量与角色回复评价，尚不覆盖人设、自身目标、原生前提与实际资源去向的联合因果问题；不因此缩小完整研究主张，也不为阅读它开训练/新平台。
7. **下一研究动作启发：** 响应者应有角色信息边界、有限表达和真实可兑现行动；若没有真实玩家验证，不声称模拟器代表真实玩家分布。响应帮助修复等待也不能直接读成玩家体验提升。

本地元数据核读：`tools/venue_corpus/data/raw/iclr2026.json` 的 `id=nfMzqKhobR`，作者字段为 `Junbao Huang;MinghaoChen`，补充附件 `/attachment/cfb392c52cc1545616019140a4c67026a23c2169.zip`。未下载附件、不推断其内容，未新增 GPU/API 调用。
