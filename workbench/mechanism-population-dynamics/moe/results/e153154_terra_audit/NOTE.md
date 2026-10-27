# E153/E154 独立 CPU 复算（C14/P32）

- E153 的 12 条 raw/per-char 正确率与首答案 token KL 点值与作者汇总一致；例如 BBBB/selectorB32 raw=0.3750 [0.2967, 0.4533]。BABB 的 A/B selector 首 token KL=0.2751/0.2519。
- E154 全目标 B−P：routed-zero ΔNLL=−3.157944 [−3.754613,−2.588519]，shared-zero ΔNLL=+2.231770 [1.971234,2.509166]。后代−父状态各条件 ΔNLL 与作者表点及区间最大差 8.9e−16。
- E153 固定两个学科、各 64 题，按学科分层配对 bootstrap 1000 次；作者与本复算同 seed 但随机数顺序不同，已核对项 CI 端点最大差 0.01196。E154 以 20 个 (source,file_id) 簇为单位重采样并按各簇原序列数加权；区间均是输入抽样区间，不是训练种子总体区间。
- E153 真实答案文本作为 continuation，目标位置从 prompt 长度减一处起逐 token 评分，计数与记录的答案 token 数核对；测试题 question+choices 哈希与 calibration 集交集为 0。dev 五例共享为上下文，不能据此排除预训练污染。
- 四格顺序为 D/G/R/S：AAAA、ABAA、BABB、BBBB；body 包含 D/R/S，因此改变隐藏状态及其后路由，不能当作隔离的专家权重效应。两个 native task selector 在所有 hybrid 上固定，不对 hybrid 重选。
- E154 的 P 是公开 Preanneal，A/B 为两封存成熟后代；后代 native/零化/随机取 E151，两个固定 prefix 取 E150，mask 与 P 一致。公开谱系声明不等于已核验逐 batch/optimizer 的因果链。
- BF16：P 的两条 calibration FP32→BF16 KL 为 0.000665/0.000343；重复和全槽精确。A/B 有各自 preflight。推理前后参数及 buffer 哈希不变为运行记录与代码证据，本审计没有重新执行模型或复核全部权重字节。
- 交互、加减恒等式及观察到的依赖差异不能单独证明训练形成机制或跨初始化普遍性；上述具体读数仍有效于所测输入和固定模型。
- 过程检查 0 error、33 个既有 warning。本审计未修改主张等级，未重跑 GPU；可执行复算与完整结果见同目录 script.py、report.json。
- 补充复算 192 项（12 条件五项指标、六种来源对比及相对同格 full 的变化）：作者预定 subject-major bootstrap 的点值与 CI 端点最大误差 2.22e−16。report 保留 subject-major 和 replicate-major 两种区间；后者的有限次重采样差异不是数值 bug。
- 例如 AAAA/full 的 choice CE=3.9182 [2.9334,4.9676]、正确答案 token NLL=1.9877 [1.7767,2.2239]。selectorA 下平均 gate/body 来源的同格 full 相对 choice CE 变化分别 +0.4517 [0.1257,0.8096] / −3.7441 [−5.1513,−2.4495]；body 效应包含 H 与实际 routing 的变化，不能归因于单一组件。
