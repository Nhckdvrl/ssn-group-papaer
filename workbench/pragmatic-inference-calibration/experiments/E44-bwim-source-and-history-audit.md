# E44：BWIM原材料与history审计

- **状态：** DONE
- **类型：** REPRO / D1，CPU源码/材料审计
- **对应：** C02/P09
- **问题（一句话）：** 原互动基线在本地无需API的confidence协议迁移中，材料、partner可靠性、episode history与客观verifier是否可重建？
- **设置：** ltl-uva/build_what_i_mean固定commit6384a1a5122df14374f2aa766c626ba09aa2d834；两原CSV与BuildingGameTask原生成器，源码全读。64rows、24相同sentence/start但target不同a/b对，四原seed0–3，不造新语句。paper全文/附录A–C已读。
- **读数：** 原64坐标合法/unique、fully16/under48、a/b同prompt；每episode40、每partner8fully/12under、literal8a4b/pragmatic12b；完整nativehistory包括source system。原code的QA与paper confidence实现不同，明确不能数字parity。
- **阳性对照：** 原target可通过whole coordinates/rating parser，重复source生成SHA一致；跨speaker原无歧义保持同任务；各model gold-history token长度与上下文限制核对。
- **噪声地板 + MIE：** CPU确定性，0sampling；原4seed是材料/顺序而非trainingseed，没有科学效应阈值。
- **混杂审计：** 原QA固定gpt4o-mini答案，不以dummy Yellow替代；本卡仅confidence迁移，不能推question-action gap。原QA code四seed共享session，不能冒称30独立confidence会话。发布CSV两lists不是paper全部8lists。a/b取目标diff不能强标所有literal下pragmatic选择为false alarm。
- **决策表（跑之前写）：** A完整源和history/坐标门通过→另卡有界confidence pilot；B源字段/坐标/version不符→只资产限制；C必要API/缺人类norm→不替换judge制造parity；D超context或native system丢失→入口不可用，不解释语用。
- **算力预算：** CPU原资产与五完整tokenizer，0GPU，repo小数据，不安装AgentBeats服务或调用API。

## 结果
CPU gate进行中；不产生能力finding。

2026-10-03 CPU gates完成：64原rows、24相同sentence/start的a/b target pairs；四seeds各40trial与两partner8fully/12under、a/b配比、所有坐标合法通过。五官方完整tokenizer的gold-history max15909–16797tokens，低于各checkpoint32768/40960；实际model history逐turn仍核查。source/code/data SHA见 results/E44-bwim-source-preflight.json。不复现原QA API，也未取得原逐trial human。
