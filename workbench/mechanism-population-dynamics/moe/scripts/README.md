# 代码入口与冻结边界

从工作台根`workbench/mechanism-population-dynamics/`使用已有环境：

```
~/.venvs/mechpop/bin/python -B moe/scripts/reproduce.py E160 all
```

同一入口支持E158、E159、E160、E161、E162的`stats`、`verify`、`plots`、`all`；`--show-commands`显示实际命令。只复算已完成结果，不加载模型做新前向、不训练、不下载。E162未完成时会拒绝。E150–E157及更早阶段的精确入口仍在原实验卡；不要因文件编号旧而删除其传递依赖。

当前少量职责边界：

| 职责 | 入口 |
|---|---|
| 科学说明、证据与停点 | `../README.md`、`../../CLAIMS.md`、`../../AGENTS.md` |
| 完整结果CPU复现 | `reproduce.py`；各`eNNN_analyze.py`及`results/*_independent_audit/` |
| 已完成E162批次 | `e162_finish_batch.py`：原完整资产→准备plan→单卡评测→CPU统计/校验；保留原入口 |
| 新授权E163 | `e163_run.py prepare/run --group PAB/F`；先CPU装载/hash再占单卡。`e163_analyze.py analyze`、`e163_verify.py verify`从raw复算。plan/SHA与CPU预检见`results/e163/` |
| 第四端点公开权重与校验 | `full_course_assets.py`、`stage_full_course.py`；固定HF pin/LFS SHA，原数据不变 |
| 通用耐久退出记录 | `supervised_process.py` |
| 冻结运行源码 | 原`eNNN_run.py`、原生模型/干预/helper；SHA在对应plan/manifest，保持以便复查 |

E160的正式结果在`results/e160/retry_1/`；父目录budget保存中断事实，不用于冒充完整结果。旧恢复器冻结版本的audit包装有接口错误，当前统一入口使用独立auditor的`--root`入口，未修改其GPU数值程序。

整理时先查import、实验卡、冻结source SHA与图的生成来源，再删无用入口。原始模型、inputs、raw和唯一训练checkpoint在耐久缓存，路径/恢复见`../ASSETS.md`；这不是应塞进Git或盲删的内容。

若收尾清理了fvcrc20的P/A/B临时模型，未来确需GPU重放时，在该节点运行`restore_mature_staging.py --receipt ~/mechpop_cache/pab_restore_NEW_ID.json`。它仍用原始公开pin和SHA复制、独立复核，原冻结staging manifest不改写；新receipt必须不存在。CPU结果复算不需要这些临时权重。F评测器在临时执行副本不存在时可用已核验的耐久HF缓存。
