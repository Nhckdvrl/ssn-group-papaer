# CacheBlend：为什么独立KV块不能总是直接组合

- 主来源：[2405.16444v2正文](https://arxiv.org/html/2405.16444v2)，2026-10-12读§3.3/4.1–4.3与实验说明；此处未另核会议版本，未复跑代码。
- idea来源（论文论证重构）：缓存服务可纠正位置，但非prefix块在预计算时没有读取前面的块，位置纠正不恢复缺失的上下文化。用跨文档比较两个球员进球数暴露joint查询的失效，再把full/独立cache的KV与forward attention差异转为选择性重计算问题。
- 方法：KV/attention deviation定义不同，逐层选择高偏差token、利用跨层相关性逐渐过滤；不是新bindingID解释。其系统收益和多benchmark是效率/质量验证。
- ICES距离：一般“块独立形成后组合不够”已有；不能把E123/E126输出失败单独说成首次记忆不组合。ICES的私人规则都合法，问哪些来源配对应隔离、哪些公共关系可共享。E126保留Source-private关系/global位置/公共事实，配对coherent/mixed衡量相同语义结构下形成背景的joint非加性交互，与删除全部cross-attention不同；这个具体设计差异仍需实际结果而非自动novelty。
