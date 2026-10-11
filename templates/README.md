# Templates — 全流程卡片模板

复制后填写；`python3 tools/process/new.py` 会自动从这里生成 workbench / 实验卡 / idea 卡。字段可以写“未知”，但不能删。

| 阶段 | 模板 | 放在哪里 |
|---|---|---|
| 找题 | [`territory_card.md`](territory_card.md) | `search/<通道>/` |
| 读论文 | [`paper_card.md`](paper_card.md) | `library/themes/<题材>/` |
| 驻留 | [`workbench_readme.md`](workbench_readme.md) | `workbench/<名字>/README.md` |
| 驻留 | [`pain_log.md`](pain_log.md) | `workbench/<名字>/PAIN_LOG.md` |
| 探索 idea | [`idea_card.md`](idea_card.md) | `workbench/<名字>/ideas/I##-<slug>.md` |
| 执行 | [`experiment_card.md`](experiment_card.md) | `workbench/<名字>/experiments/E##-<slug>.md` |
| 执行 | [`claims.md`](claims.md) | `workbench/<名字>/CLAIMS.md` |
| 定位 | [`positioning.md`](positioning.md) | workbench README 或 `POSITIONING.md` |
| 人审（决策点触发） | [`review.md`](review.md) | `workbench/<名字>/logs/review-YYYY-MM-DD.md`（`tools/process/review.py` 生成骨架） |
| 论文形态 | [`paper_shape.md`](paper_shape.md) | workbench README（每次人审更新） |
| 关闭 / 暂停 | [`close_record.md`](close_record.md) | workbench README 末尾；跨项目有用的再复制到 `failed/` |
| 候选 | [`candidate_readme.md`](candidate_readme.md) | `candidates/<名字>/README.md` |
| 模拟审稿 | [`mock_review.md`](mock_review.md) | `candidates/<名字>/MOCK_REVIEW.md` |
