# 代码使用：从三个结果到复算

从工作台根`workbench/mechanism-population-dynamics/`使用已有`~/.venvs/mechpop`环境。复核三条核心结果的统一入口：

```bash
~/.venvs/mechpop/bin/python -B moe/scripts/reproduce.py spine verify
```

`spine`依次覆盖E156（性质来源）、E159（伙伴作用）、E162（成熟路径分担）、E163（消息几何/重用）。`verify`执行原有独立公式校验；`stats`从raw重算统计，`plots`重绘，`all`依次执行三项；`--show-commands`列出实际命令。只复算已完成结果，不加载模型前向、训练或下载；任一manifest未完成会拒绝。

单实验还支持E156、E158–E165，例如`reproduce.py E156 stats`、`reproduce.py E165 all`。E165的plots生成论文四图，E164保持原图入口；现有`spine`仍是四项原核心证据，不因新实验改变旧复核组成。E150–E155/E157和早期窗口的精确入口保留在各原卡；[结果导航](../results/README.md)给出当前证据路径。

## 当前少量使用入口

| 用途 | 入口/边界 |
|---|---|
| 所有当前论证的CPU复核 | `reproduce.py spine verify`；原审计器不变，不提高证据等级 |
| 本轮论文关键图 | `moe_paper_figures.py`；57项既有估计/共同成功计数的四幅图，逐项来源在`paper/figures/figure_sources.json`；无新检验，英文论证在`paper/main.tex` |
| E165数值与复核 | `e165_run.py`及18份原源码冻结0fb295d6；`e165_local_adapter.py`只改已核SHA的NVMe路径。耐久链全部exit0，`reproduce.py E165 all`不运行模型 |
| E166当前执行 | `e166_run.py`与`e166_finish.py`；27份数值/辅助源码冻结ef8f58c8。两谱系顺序单卡、plan累计cap4GPU时；完成目录不可覆盖，不以中途格更新科学结论 |
| 论文总览图 | `moe_research_spine.py`；只组织E156/E159/E163已有估计及原CI，sidecar给来源SHA和JSON路径 |
| E164当前数值程序 | `e164_run.py`的prepare/preflight/run、`e164_routing.py`及统计/校验；21份源码冻结43aee97a，plan/source不随运行修改。CPU入口只读完整结果，真实GPU任务由`e164_finish.py`的耐久链监督且已exit0；不得覆盖完成目录 |
| E163原始数值程序 | `e163_run.py`、`e163_geometry.py`、`e163_metrics.py`等20文件冻结c31e4b0e；不以目录整理改数值代码 |
| E163实际续跑 | `e163_cross_resume.py`调用`e163_resource_wait.py`，只转换轨迹指纹键并有检查地继承native块；原worker终态未得与fresh范围见原卡 |
| 成熟权重/源码恢复 | [ASSETS](../ASSETS.md)；`full_course_assets.py`、`restore_mature_staging.py`，固定HF pin/SHA |
| 耐久监督 | `supervised_process.py`；监督退出码、心跳、费用账本，进程消失不等于成功 |

## 为什么保留旧脚本

2026-10-29整理快照中的198个Python文件，有88个被当时plan/manifest/封存来源直接引用；随后新增E164的研究、复核与封存入口。其他还包括生成、作图、失败方案与传递依赖。[目录核查](../results/directory_cleanup_2026-10-29.json)记录逐文件SHA、直接引用及本地imports。引用数不是自动删文件的判据；以日期搬动或删除会破坏动态import和旧source恢复。日常从上表进入，无需逐个浏览全部文件。

E160正式结果在`results/e160/retry_1/`，统一入口使用独立auditor的正确`--root`接口；旧恢复器的audit包装错误保留为历史，不改GPU数值程序。E158只有`whole_path/`完成；旧单层扫描/原失败入口不能当有结果的复现路线。

确需GPU重放时，先读[AGENTS](../../AGENTS.md)、原卡和新鲜资源状态，最多4卡；现有完成目录和凭证不可覆盖。大权重、raw、唯一checkpoint和失败记录按ASSETS恢复，源码封存包内的旧文档是当时快照。
