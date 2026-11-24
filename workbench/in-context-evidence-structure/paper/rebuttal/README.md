# Rebuttal 工作区（ARR，2026-11）

## 时间与规则（2026-11-24 查询，以 OpenReview 本轮页面为准）
- **作者回复窗口：** ARR 2026 年 10 月轮次为 **11 月 24–30 日**（ARR 官方日期表；第三方指南一致）。具体截止时刻以 OpenReview 上本篇的页面为准，**待核对**。
- **篇幅：** 一份总回复（general response，面向全部审稿人）+ 每位审稿人一份回复，**每份 ≤ 5,000 字符**。
- **格式：** 只能纯文本；**不得包含任何外部链接**（违反可能被直接拒稿，匿名代码也不能用链接指向）。
- **新结果：** 只允许作为对审稿人具体问题的直接回答，且应是对已有实验的小补充（一个消融、一个超参数、一个基线）；不得主动追加，也不得出现显示投稿后有大量新工作的内容。
- 来源：ARR 作者指南 https://aclrollingreview.org/authors 、ARR 日期表（GitHub acl-org/aclrollingreview `dates.md`）。

## 流程
1. 把每位审稿人的意见原文贴进 `reviews/R1.md`、`R2.md`……（Meta-review 若已出，贴进 `reviews/meta.md`）。
2. 对每条意见先分类：误解（正文/附录已有答案）、可用已有证据回答、需要小补充实验、需要承认的局限。
3. 逐条起草 `responses/R1.md`……与 `responses/general.md`；每条回答先给结论和数字，再指出正文/附录位置。
4. `python3 count_chars.py responses/*.md` 检查字符数（≤ 5,000）和是否含链接。
5. 小补充实验只为审稿人明确提出的问题而做，先写实验卡（R3），结果进实验卡与 `results/`，回复里只报数字。
6. 投稿正本 `../main.tex` 在 rebuttal 期间不改；承诺的修改记在 `revision_plan.md`，供 camera-ready / 下一轮使用。

## 文件
- [`EVIDENCE_MAP.md`](EVIDENCE_MAP.md)：论文每项主张 → 数字 → 正文/附录位置 → 实验卡与结果目录 → 已知限定。
- [`ANTICIPATED.md`](ANTICIPATED.md)：预期问题、回答要点与可调用的证据（含论文之外的已有实验）。
- `count_chars.py`：字符数与链接检查。
- `reviews/`、`responses/`：收到意见后创建。
