"""Recompute the mother paper's Table 1 aggregates. Input numbers are transcribed from
ACL Anthology 2025.emnlp-main.522 Table 1 (see data/mother_paper.txt)."""
BENCH=["MMLU","BBH","LAMBADA","GSM8K","MATH","MBPP","HumanEval","OBQA","PIQA"]
SHORT={"UltraChat":[61.50,61.00,64.44,54.69,17.28,39.20,32.92,74.40,75.24],
       "Tulu-v2":  [61.37,61.50,64.20,62.50,16.42,51.20,49.39,74.40,76.33]}
LONG={"LongAlpaca":[62.11,61.29,68.84,68.75,16.70,46.20,48.78,74.40,76.77],
      "LongMIT":   [62.65,61.80,71.51,59.38,18.22,50.20,54.27,74.20,68.28],
      "ChatQA2":   [62.80,63.79,70.11,68.75,18.06,46.20,44.51,74.20,76.61]}
avg=lambda v:sum(v)/len(v)
if __name__=="__main__":
    sa=[avg(v) for v in SHORT.values()]; la=[avg(v) for v in LONG.values()]
    print(f"condition gap (macro)      {avg(la)-avg(sa):+.2f}")
    print(f"within-SHORT spread        {max(sa)-min(sa):+.2f}")
    print(f"within-LONG  spread        {max(la)-min(la):+.2f}\n")
    print(f"{'bench':10s}{'short':>8s}{'long':>8s}{'gap':>8s}{'shortSpread':>13s}")
    for i,b in enumerate(BENCH):
        s=[SHORT[k][i] for k in SHORT]; l=[LONG[k][i] for k in LONG]
        print(f"{b:10s}{avg(s):8.2f}{avg(l):8.2f}{avg(l)-avg(s):+8.2f}{max(s)-min(s):13.2f}")
    n=sum(1 for i in range(9) if max(SHORT[k][i] for k in SHORT)>min(LONG[k][i] for k in LONG))
    print(f"\nbenchmarks where best-SHORT dataset > worst-LONG dataset: {n}/9")
