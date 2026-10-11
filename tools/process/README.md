# tools/process — 让流程可执行、可检查

纯 Python 标准库，在仓库任意位置运行。

| 命令 | 作用 |
|---|---|
| `python3 tools/process/check.py [--today YYYY-MM-DD] [--strict]` | 检查登记表（`workbench/README.md` §9）、容量规则、ACTIVE 线的主张账本 / 痛点日志 / 人审记录 / README 长度、实验卡与 idea 卡的必填字段、`CLAIMS.md` 的证据等级与引用、K254 起的关闭记录是否写明证据类别。**不做任何日程检查。**有 ERROR 时退出码为 1 |
| `python3 tools/process/new.py workbench <名字>` | 按 `templates/` 新建 workbench（README、CLAIMS、PAIN_LOG、experiments/、ideas/、logs/、results/）；不自动登记，登记与改状态由人决定 |
| `python3 tools/process/new.py experiment <workbench> <slug>` | 新建实验卡，编号从该 workbench 已用的最大 E## 继续 |
| `python3 tools/process/new.py idea <workbench> <slug>` | 新建 idea 卡（I##） |
| `python3 tools/process/review.py <workbench> [--since YYYY-MM-DD] [--write]` | 在决策点生成人审骨架：**自上次人审以来**的主张变化、实验与 EXPLORE 占比、idea 状态、新痛点、漂移信号（按实验张数计，不按天数）；`--write` 写到 `logs/review-<日期>.md` |

约定（工具依赖这些格式）：
- 登记表的表头以 `| workbench |` 开头，列包括 `状态`、`目标会议`、`截稿`、`主张账本`、`上次人审`；状态只能是 `ACTIVE-MAIN / ACTIVE-EXPLORE / PROPOSED / PAUSED / CLOSED`。
- 卡片字段写成 `- **字段名：** 值`（与 `templates/` 一致）；选项类字段（状态、类型）把模板里的 `A / B / C` 改成一个值。
- `CLAIMS.md` 第一个含 `ID` 与 `等级` 的表格是主张表；等级写 `L0`–`L5`；日期写 `YYYY-MM-DD`。
- 痛点日志每条以 `- P## · YYYY-MM-DD ·` 开头。
- 实验卡的实际算力写在 `**实际：** <数字>`（GPU·时），`review.py` 用它计算 EXPLORE 占比。
