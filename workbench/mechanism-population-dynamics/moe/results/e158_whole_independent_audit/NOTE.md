# E158 v4 完整路径独立 CPU 校对

对应 C14、E158 v4。基于实验卡与原独立审计公式实现，未读取作者 v4 统计器、未读取 v4 新数据或加载模型。`audit.py --self-test` 使用合成读数校验排名平局、国家配对、关系等权、模型/路径轴、S−R 和历史对比以及预算拒绝条件。

实际运行仅在主实验进程退出且预算记账完成后：

```sh
~/.venvs/mechpop/bin/python -B moe/results/e158_whole_independent_audit/audit.py --audit --output moe/results/e158_whole_independent_audit/recomputed.json
```

读取科学 raw 前核预算原样保留两次失败及第三次完成、累计 ≤14400 秒、plan/manifest/源码/数据及引用 SHA、参数/buffer/cal 身份、旧完整原生预检、执行方式与地板；核输入映射、baseline 引用、共同 top10 门槛及阳性残差身份。门槛未通过时只输出 baseline；通过时输出全部四路径和三场景的八项指标、固定国家配对 bootstrap 及所有预定对比、共同成功集点值计数和匹配移除。R/S 单独身份仅两个固定查询，所有查询检验的是联合 RS 和 A；不声称全查询单独 R/S 身份。

`cache_*` 兼容字段实际为继承 v3 的完整 head 与 keep=1 原生读取对照，不使用 KV cache。KL 只封存完整词表 KL 标量，不能从已保存数据重建词表分布。输出无层轴，也无层均值；完整路径非定位与知识比例。主汇总结构尚未提供，目前尚无自动比较器，亦未宣称正式独立校对通过。
