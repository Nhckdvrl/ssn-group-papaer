# independent pure-python check: exit rate on re-test from binomial noise alone, no learning
from math import comb, lgamma, exp, log
def bpdf(p,a,b): return exp((a-1)*log(p)+(b-1)*log(1-p)+lgamma(a+b)-lgamma(a)-lgamma(b))
def pin(k,p,lo,hi): return sum(comb(k,j)*p**j*(1-p)**(k-j) for j in range(k+1) if lo<=j/k<=hi)
def run(a,b,k,lo,hi,N=4000):
    num=den=tin=0.0
    for i in range(N):
        p=(i+0.5)/N; w=bpdf(p,a,b); ad=pin(k,p,lo,hi)
        den+=w*ad; num+=w*ad*(1-pin(k,p,lo,hi)); tin+=w*ad*(lo<=p<=hi)
    return num/den, tin/den
for (a,b) in [(0.5,0.5),(1,1),(2,2)]:
    for k in [8,10,16,32]:
        for lo,hi in [(0.3,0.7),(0.3,0.8),(0.2,0.8)]:
            e,t=run(a,b,k,lo,hi); print(f"Beta({a},{b}) k={k} band=[{lo},{hi}] exit={e:.2f} trueInBand={t:.2f}")
