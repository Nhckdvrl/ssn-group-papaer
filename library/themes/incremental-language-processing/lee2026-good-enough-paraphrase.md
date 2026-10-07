# Probing Good-Enough Processing with a Paraphrasing Task（2026期刊）

`[正式主文全部精读]` [DOI](https://doi.org/10.15738/kjell.26..202601.127)，Lee/Shin，Korea University Sejong/Dongguk；官方公开PDF15页，SHAe9f5c3068b4222fbda4f1f0bee5f8f79d716dad54f32337d018436b4f4012d5c。Main1–5及limitations pp1–12全部，Fig1 p7视觉核；refs仅定位。DOI公共HTTP出版站可读，HTTPS握手失败，未绕私有权限。代码链接存在但本轮未读/复现。

- **idea来源（RECONSTRUCTED）：** 旧GPT的GP误答可能被直接问题诱导，Patson人类paraphrase范式让读者自己外化关系→迁移GPT3.5/4看错误是否仍在→再用OT/RAT词类区分一般合理性与语法修订。最近邻是作者2025 QA及Patson2009，不是全新paraphrase评测。
- **方法与规模：** 两个0613 GPT版本，24经典句（OT/RAT各12）及comma cue，每项10次零样本独立上下文；四类full/partial/failed/others，full=正确；chi-square和item随机GLMM。标注执行者/独立一致率、完整decoding参数未从主文核对到，不能据“10次”推10独立词汇样本。
- **结果：** GPT4 GP两词类full均约35%，GPT3.5约7%/15%；cue较高。GPT4比作者旧QA0%/20%改善，但任务/版本/条件比较不是当前prefix匹配因果干预。partial包含既主句correct又加初始wrong关系，与我们T4明确GP可共存定义相近。
- **机制距离：** 文中推测question聚焦局部词、freeP逼整句处理，并讨论task over-optimization；闭源内部未操纵，所以这是假说，不是证明继承人类机制。RAT语用/反身约束需词汇个案，不能把所有OT/RAT原No都自动当显式矛盾（P13）。
- **I08定位：** “题型导致理解表现不同”“直接问句可能污染解释”“只追即时回答会忽略更深语义”已有明确owner；单纯多三模型或多词类不能作核心novel。E99新增具体干预：同一提前目标改善QA却增加QA成功/自由P明确错关系的联合比例；E98需actual用途证据和一条恢复边界，不把本论文一般讨论当精确撞车，也不桌面关闭I08。
- **借鉴：** 自由输出区分partial与未形成主体关系，保留多读数；不沿两题型反复证明“LLM也good-enough”，应问何时目标成功掩盖哪个修订操作、有哪些有价值的后果。
