# E160 独立 CPU 校对

正式raw尚未完成。CPU完整汇总集成fixture发现并修复独立比较器的一处符号错：准确率的matching cost按预定定义为对角减非对角，loss为非对角减对角。原冻结作者统计与模型driver未改。`check_integration.py`单独导入作者统计生成合成汇总，`audit.py`仍以独立公式计算；3828数字/3565计数匹配（≤4.45e−16），故意损坏点、CI、计数、空学科None均被拒绝。`integration_test.json`记录源码SHA；该CPU测试没有读取正式干预数组。

对应 C14、E160 固定共享信号实验卡。独立实现消费者×生产者九格、共享支撑、固定生产信号后的受控 R 支撑、自然参照、固定生产者及固定消费者对比、固定 P 信号与自然伙伴效应差、非对角减对角完整质量、R 删除时保留生产信号的恢复量。四种指标均保留；全部题目按两学科各 64 道等权、学科内成对 bootstrap 1000 次，seed 160001。

次分析在九格完整结果均 raw 正确的题上，输出点值/计数和全部 8 模式及固定生产者/消费者转移；学科为空时宏平均为 null。S-replay-only 使用 R 存在时产生的 S 轨迹，不是自然 S 独立能力。受控 R 支撑不是 R 总知识量；恢复量不是唯一中介比例或无需 R 计算的部署证明。

```sh
~/.venvs/mechpop/bin/python -B moe/results/e160_independent_audit/audit.py --self-test
```

合成自检覆盖轴与符号、固定信号和自然对比、八模式、空学科、预算拒绝。未读取新 E160 科学原始数据、未加载模型或运行 GPU。正式输入/继承哈希校验及无数值 summary 比较器已接入；正式运行加 `--audit --summary <summary.json> --output <report.json>`。当前尚未读取正式数据，未声称独立校对通过。
