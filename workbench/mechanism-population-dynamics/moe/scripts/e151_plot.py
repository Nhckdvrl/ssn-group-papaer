"""E151 global necessity and all random-budget probes, with paired prefix costs."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

WB=Path(__file__).resolve().parents[1]
ROOT=WB/"results/e151"


def point(ax,x,row,color,offset=0,marker="o",label=None):
    lo,hi=row["input_file_ci95"]
    ax.vlines(x+offset,lo,hi,color=color,linewidth=1)
    ax.plot(x+offset,row["point"],marker,color=color,markersize=5,label=label)


def main():
    d=json.loads((ROOT/"summary.json").read_text());old=json.loads((WB/"results/e150/summary.json").read_text())
    assert d["status"]=="complete"
    plt.rcParams.update({"font.size":9,"axes.spines.top":False,"axes.spines.right":False,"pdf.fonttype":42})
    fig,axes=plt.subplots(2,2,figsize=(11.5,7.5),dpi=150)
    for source,color,offset,native in (("A","#2166AC",-.1,"AAAA"),("B","#B2182B",.1,"BBBB")):
        row=d["sources"][source]
        for i,condition in enumerate(("routed_zero","shared_zero")):
            point(axes[0,0],i,row["conditions"][condition]["full_delta_NLL"],color,offset,label=source if i==0 else None)
            point(axes[0,1],i,row["conditions"][condition]["full_KL"],color,offset,label=source if i==0 else None)
        for i,selector in enumerate("AB"):
            value=old["restriction"]["selectors"][selector]["cases"][native]["pruning_delta_nll"]
            point(axes[1,0],i,value,color,offset,label=source if i==0 else None)
        for i,condition in enumerate(("random0","random1","random2"),start=2):
            point(axes[1,0],i,row["conditions"][condition]["suffix_delta_NLL"],color,offset)
        point(axes[1,0],5,row["random_mean"]["suffix_delta_NLL"],color,offset,marker="s")
        for i,selector in enumerate("AB"):
            for j,(field,marker) in enumerate((("random_mean_minus_prefix_NLL","o"),("random_mean_minus_prefix_KL","^"))):
                value=row["random_vs_prefix"][selector][field]
                point(axes[1,1],i,value,color,offset+(j-.5)*.08,marker,label=f"{source}, {'NLL' if j==0 else 'KL'}" if i==0 else None)
    for ax in axes[0]:ax.set_xticks([0,1],["All routed experts zero","All shared experts zero"]);ax.legend(frameon=False)
    axes[0,0].set(title="A  Global computation necessity",ylabel="Perturbed minus native NLL (all targets)")
    axes[0,1].set(title="B  Native to zeroed predictor",ylabel="Full-vocabulary KL (all targets)")
    axes[1,0].set(title="C  Every fixed 32-slot budget",ylabel="Pruning NLL cost (suffix only)",xticks=range(6),
                   xticklabels=["Prefix A","Prefix B","Random 0","Random 1","Random 2","Random mean"])
    axes[1,0].tick_params(axis="x",rotation=35)
    axes[1,0].legend(frameon=False)
    axes[1,1].set(title="D  Selection benefit at the same budget",ylabel="Random mean minus selected-prefix cost",xticks=[0,1],xticklabels=["Prefix selector A","Prefix selector B"])
    axes[1,1].legend(frameon=False,fontsize=8)
    for ax in axes.flat:ax.axhline(0,color="#BBBBBB",linewidth=.7);ax.grid(axis="y",alpha=.15)
    fig.tight_layout(rect=(0,.09,1,1),w_pad=2,h_pad=2)
    fig.text(.5,.015,"Same mature public pair and language inputs as E150; no new training. Global zeroing is a necessity perturbation.\n"
        "Three fixed random-mask probes are not seeds; intervals resample 20 input files. Budget masks retain 31 routed + 1 shared slots.",ha="center",fontsize=8,color="#666666")
    out=ROOT/"figures";out.mkdir(exist_ok=True)
    for suffix in ("png","pdf"):fig.savefig(out/("native_necessity_and_selection."+suffix),bbox_inches="tight")
    print(out/"native_necessity_and_selection.png")


if __name__=="__main__":main()
