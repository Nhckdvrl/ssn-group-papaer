# 本轮主图与第15批发现结果呈现独立校对

结论：当前呈现通过。Figure2的20点/60个均值及CI端点、Figure3的72点/216个均值及CI端点，与已封E123/E125确认结果误差均为0；附录M新增25个打印数字及范围与第15批独立raw封签一致。没有重算旧science或GPU重跑。

最终绑定主文 `70799115a741f7df451419fedfd75cab36c9502290492e2dc12af16c5c0b4d6d`、附录 `2d6c867c4ea8a29d8b0e487ffae399c5ac74ee5830026b41e3840f6ea0a81d43`、PDF `adeb070e098f9f20d6a09b27472088879bea7894a6519d6944cfeb785d63b741`；详细脚本、CSV、manifest、sealed来源及图资产SHA见JSON。PDF正文8页，Limitations在P9页首，共32页；主文3图3表、附录13图27表。最终LaTeX warning/undefined/Overfull均0；日志仍有Underfull排版提示，所查看页面没有剪切。

Figure2仅展示既有n32确认：shared的三形成政策full-vocabulary均值与95%context-bootstrapCI，以及far/all-cross形成的candidate/full差；两Actor均值不是joint，两panel均为full-source query。Figure3保留三checkpoint×三公共表×四F/R条件×两readout全部72点，caption明确定义00/10/01/11。实看P3/6/7/8/9/18/24/29，主图模型名、图例、坐标与误差棒清楚。旧六政策E123图已补回附录F，当前浮动排在P24；全量表也仍保留。

附录M的70B function仍是n16发现：shared full86.72→98.44%，paired+11.72[8.01,15.43]pp；A/B与same/opposite保留，targeted−all+23.44[21.88,25.00]pp，query-only+10.55[5.66,15.04]pp。mean与joint97.27%区分；far/all-cross candidate99.02%/full51.17%/joint3.91%及other-word48.24%保留。single私有方向范围95.31–100%，不是原子满分；三项固定确认仍pending，没有把空canonical fence当行为或阴性。

相对`3d0c6c3b`，Abstract与Related Work逐字保持，22个原始工作链接和24个bib身份保留，全部16行主表字节保持。Intro删重复概述但保留三递进认识、固定A/query反事实、系数一接口预测、fixed-word关系内容、形成/读取政策区别与公共关系/等价背景，以及32B同链确认。没有增加完整criterion程序、唯一算法、普遍最优政策或因果容量律。

本轮只读改动呈现、sealed数值与实际PDF；旧744单元、全历史raw和独立GPU未重做。原数值/配置/写作审计保存原snapshot。本报告不改claims/grade/state，不设新科学门槛。
