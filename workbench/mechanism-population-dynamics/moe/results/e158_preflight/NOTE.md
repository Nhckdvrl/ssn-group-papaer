# E158 静态预检

- 未发现必须修复的数值逻辑错误；CPU测试及成熟GPU验证的实际状态以运行结果为准，不构成L3设计审计。
- 每步深复制prefix KV，最后位置设length−1；逐query逐层核对fast/native MLP输出与cached预测位相同。
- R/S为原生加权专家输出直接tap；固定q0/q48逐层以原生S-zero、R-zero和both-zero核验，R+S逐位重构。固定query同源替换及所有source的final-residual正控覆盖预设条件。
- target、三类source与匹配对照从封存data索引取值；control保留source标签频数，不用模型读数选择。
- 内容数组3×3×3×16×2×24×38，移除3×3×16×2×24×38；循环各格填一次，共27648行。baseline gate失败时不分配虚假patch/removal数组。
- budget与设备锁在CUDA张量分配前进入；临时forward与hook使用finally恢复，结束核对参数/buffer哈希。
- 精度边界：成熟每步只核原cache长度，原cache字节hash只在CPU tiny测试；不能称成熟逐次cache字节已核对。统计和schema核对详见report.json。
