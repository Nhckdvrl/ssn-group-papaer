# E158 独立 CPU 审计器

依据预注册卡、封存数据接口和此前静态审阅独立重算；不是盲法设计审计。未调用作者统计函数、未读取成熟raw或运行模型。

重算内容包括所有来源/场景/路径/层的source排名特异性、对照赔率、source/target LP、命中及KL；固定国家成对bootstrap（seed158001、1000次）、等权关系与16层均值、历史差及实体/属性S−R差。另核同层匹配移除的target NLL/top1/KL、层均值、历史与S−R对比；共同成功集只报告各关系点估计与计数。baseline-only不生成patch值，检查native和最后residual正控。

真实raw仅在预算、manifest 和 plan/data/raw SHA 校验通过后人工调用。v3 只接受累计预算中完整保留的先前 cached 失败和一个已完成的 full-forward 尝试，并校验失败记录 SHA。已按主agent提供的无数值summary结构实现自动逐项比较；合成比较器差异检测通过。真实结果尚未读取或审计。首token KL只保存标量，不保存词表分布，因此可核汇总与CI，不能从分布重算。

```sh
~/.venvs/mechpop/bin/python -B moe/results/e158_independent_audit/audit.py --self-test
```

真实结果完成后人工调用：

```sh
~/.venvs/mechpop/bin/python -B moe/results/e158_independent_audit/audit.py \
  --raw "$HOME/mechpop_cache/e158_factual_role_interchange/full_forward/scores.npz" \
  --data "$HOME/mechpop_cache/e158_factual_role_interchange/data.npz" \
  --summary moe/results/e158/full_forward/summary.json \
  --manifest moe/results/e158/full_forward/manifest.json \
  --plan moe/results/e158/full_forward/plan.json \
  --budget moe/results/e158/budget.json
```

v3 的 `uncached_*` 与 `cache_KL` 是兼容字段名：分别记录完整词表读出和仅最后位置读出的原生全前缀对照，不使用 KV cache。先前 cached 预检失败单独保留。
