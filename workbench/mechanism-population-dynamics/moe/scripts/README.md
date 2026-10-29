# 代码入口

从本workbench根目录运行，使用已有`~/.venvs/mechpop/bin/python`。日常入口只有下列几项：

| 文件 | 用途 |
|---|---|
| [reproduce.py](reproduce.py) | 已完成实验的CPU统计、独立校验及作图；不做模型前向、训练或下载 |
| [moe_paper_figures.py](moe_paper_figures.py) | 五幅论文主图；73项估计/共同成功计数逐项绑定JSON路径与SHA |
| [moe_paper_patterns.py](moe_paper_patterns.py) | E166完整逐学科模式和cal的POST-HOC描述，无新推断或模型运行 |
| [moe_native_geometry_posthoc.py](moe_native_geometry_posthoc.py) | 既有E163 native几何的描述性汇总 |
| [source_snapshot.py](source_snapshot.py) / [frozen_sources.json](frozen_sources.json) | 固定历史源码的离线查阅、导出与临时原路径恢复 |

## 复核结果

```bash
~/.venvs/mechpop/bin/python -B moe/scripts/reproduce.py spine verify
~/.venvs/mechpop/bin/python -B moe/scripts/reproduce.py E166 all
```

`spine`保持原四项E156/E159/E162/E163；单项支持E156及E158–E166。`stats`从raw重算，`verify`使用原独立实现，`plots`重绘，`all`依次执行；`--show-commands`先列实际命令。未完成结果会拒绝。E165/E166的plots生成当前五幅论文图，原实验自身的图仍可按其他条目复算。

## 查阅冻结实现

原229份MoE及170份头线执行/分析源码保留在固定Git版本`d581ed4b9636319da8e8467930f716ab651f38c4`，不再平铺为当前入口。

```bash
python3 -B moe/scripts/reproduce.py sources
python3 -B moe/scripts/reproduce.py sources --name e166_core.py
python3 -B moe/scripts/reproduce.py sources --export /tmp/mechpop-frozen-source
```

查阅命令给出原路径、Git链接、SHA与大小；导出需放在当前仓库之外。关键实现包括`e163_geometry.py`（消息接口）、`e164_routing.py`（真实路由）、`e166_core.py`（增益）及各实验analyze/verify。旧训练、资产准备、失败恢复与封存工具均能按名字找到。

复算时，入口持有跨节点共享锁，临时将**原字节恢复到原路径**，执行原程序，最后只收回自己创建且SHA未变的文件。已有冲突文件不会覆盖。这样保留`__file__`、动态import和冻结源码guard的契约，数值程序不做目录迁移或改写；仅替换了日常入口的组织方式。历史训练程序不会自动执行。

若是浅克隆缺少该Git对象，先取得上述固定版本；封存包是另一精确恢复来源。历史完整环境/GPU程序按[ASSETS](../ASSETS.md)和原卡在独立checkout恢复；旧源中的准备命令不是当前实验队列。
