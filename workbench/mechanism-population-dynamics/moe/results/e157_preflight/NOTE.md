# E157 静态预检

未发现阻止冻结的实质代码问题。每层沿旧mask选择31个donor R、其余R及gate取P，shared独立取P/A/B；12新full格与3个native重放的轴与统计schema一致。

代码按两个固定题分别核对empty/all与旧full、on-domain masked部分组与整bank同算子及旧E156读数；所有题的native LL与首token KL重放。参数、buffer、原生cal、输入、mask和冻结源码均有哈希或逐位校验；off-domain masked未测。

上述为只读静态推断；真实GPU的身份、hook恢复、数值、内存与执行结果尚待正式运行。两题masked结构控制不等于重新测量全部题；gate参数固定不保证隐藏态或实际路由固定。
