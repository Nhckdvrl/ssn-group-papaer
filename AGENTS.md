# AGENTS.md — 在本仓库工作的 AI agent 必读

适用于 Codex、Claude、GPT 等所有在本仓库执行任务的 agent。本仓库是**研究流程仓库**（找题 → 驻留探索 → 执行 → 候选 → 投稿），不是软件项目。
**你的角色：执行者、测量者、起草者。人负责品味与决策。** 流程总图见 [`README.md`](README.md)。

## 1. 每次会话开始
1. 读 `README.md` 与 `workbench/README.md` §9 登记表：当前主线 / 探索线、状态、截稿日。
2. 进入你负责的 workbench：读状态页、论文形态卡、`CLAIMS.md`、`PAIN_LOG.md`、最近的实验卡与 `logs/`。
3. 运行 `python3 tools/process/check.py`，有 ERROR 先修。
4. 写下本次会话要推进的**主张 C##、idea I## 或痛点 P##**。说不出来 → 先做每周人审骨架（`python3 tools/process/weekly.py <workbench>`）或问人。

## 2. 硬规则（违反即停，回到本文件）
- **R1 不在桌面上判死。** 不能以“有人做过 / 已成 program / 一小块被碰过 / 天花板不够 / 审稿人会说你不就是 ___”为理由关闭 territory、workbench 或 idea。你能做的是：写定位表（近邻 + 增量）、调整增量、把 idea 标为 PARKED 并写重开条件。撞车的定义与处理见 `search/README.md` §3。
- **R2 开线、关线、暂停、改状态只由人决定。** 你可以用 `templates/close_record.md` 提议，证据类别只能是 A（实验）或 C（可行性）。
- **R3 先写实验卡再运行**（`python3 tools/process/new.py experiment <workbench> <slug>`）：对应的主张 / idea / 痛点、读数、阳性对照、噪声地板、决策表、算力。事后补写的标 POST-HOC。
- **R4 主张升级必须引用实验卡和结果文件**；证据等级按 `workbench/EXECUTION.md` §3；升到 L2 前过混杂审计（§4），升到 L3 前做独立校对（§5）。
- **R5 不筛幸存种子，不在看到结果后改读数**；作废和降级写进 `CLAIMS.md` 的作废记录，和正结果一样汇报。
- **R6 新颖性检查只输出定位，不输出判决**：`python3 tools/venue_corpus/query.py nearest "<主旨>"` + 最新 arXiv → 定位表的行。热度是数字，不是判决。
- **R7 容量**：ACTIVE-MAIN 与 ACTIVE-EXPLORE 各最多 1 条；不自行新建 workbench（可以在 `search/` 写 territory 卡提议）。
- **R8 提示词行为探针不能单独作为能力证据**，必须有“一句指令能否恢复”的对照。
- **R9 文档从简**：workbench README ≤ 200 行；过程写进实验卡、`logs/` 或 `results/`；不建过程堆积目录；不把 idea 孵化放进 `candidates/`。
- **R10 不参考 EACL，不投 Findings。**

## 3. 鼓励你主动做的
- 在强基线上修真实出现的痛点（方法从驻留第一周起允许，但要对应一个 P##）。
- 从痛点和测量异常出发，用研究动作写 idea 卡（`workbench/IDEA_EXPLORATION.md` §2），并设计最便宜的决定性 pilot。
- 发现混杂或伪影时，立刻写校对备注，降级受影响的主张。
- 每两周为 ACTIVE 线扫描新近邻（venue corpus + awesome 列表 + daily-arXiv 镜像，入口见 `library/sources/AWESOME_LISTS.md`），更新定位表。
- 读论文时写论文卡（`templates/paper_card.md`），重点写“idea 来源”和“与最近邻的距离”，放进 `library/themes/<题材>/`。

## 4. 汇报
- 每次会话结束：在 workbench 的 `logs/YYYY-MM-DD.md` 追加一条——做了什么（实验卡 ID）→ 数字与置信区间 → 哪条主张升 / 降级 → 下一步 → 需要人决定的事。
- 面向组员的状态页与汇报用中文；论文草稿用英文。先说结论和数字，再说过程。
- 不确定的地方直接写“不确定 / 未核对”，不要用措辞掩盖。

## 5. 提交
- 小步提交，提交信息写“做了什么 + 为什么”。
- 大文件（checkpoint、rollout、原始数据）不进 git；在 README“资产位置”写路径与下载方式。
- `tools/venue_corpus/data/` 是本地缓存（已 git-ignore），用 `tools/venue_corpus/fetch.sh` + `build.py` 重建。
