"""Standalone plots of all fixed masks under both E152 denominator rules."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]/"results/e152"
MASKS=("prefixA","prefixB","random0","random1","random2")


def point(ax,x,row,color,marker,offset=0,label=None):
    lo,hi=row["input_file_ci95"];ax.vlines(x+offset,lo,hi,color=color,linewidth=1)
    ax.plot(x+offset,row["point"],marker,color=color,markersize=4,label=label)


def main():
    d=json.loads((ROOT/"summary.json").read_text());assert d["status"]=="complete"
    plt.rcParams.update({"font.size":9,"axes.spines.top":False,"axes.spines.right":False,"pdf.fonttype":42})
    fig,axes=plt.subplots(2,2,figsize=(11.5,7.5),dpi=150)
    for source,color,shift in (("A","#2166AC",-.12),("B","#B2182B",.12)):
        for r,(rule,marker) in enumerate((("pool","o"),("full","^"))):
            offset=shift+(r-.5)*.07
            for j,mask in enumerate(MASKS):
                row=d["sources"][source]["masks"][mask][rule]
                label=f"{source}, {rule}" if j==0 else None
                point(axes[0,0],j,row["delta_NLL"],color,marker,offset,label)
                point(axes[0,1],j,row["native_to_variant_KL"],color,marker,offset,label)
                point(axes[1,0],j,row["applied_R_mass"],color,marker,offset,label)
    for r,(rule,color,marker) in enumerate((("pool","#2166AC","o"),("full","#B2182B","^"))):
        for j,mask in enumerate(MASKS):
            point(axes[1,1],j,d["B_minus_A"][mask][rule]["delta_NLL"],color,marker,(r-.5)*.12,rule if j==0 else None)
    axes[0,0].set(title="A  Fixed-mask prediction cost",ylabel="Variant minus native suffix NLL")
    axes[0,1].set(title="B  Native to variant",ylabel="Full-vocabulary KL on suffix")
    axes[1,0].set(title="C  Actual routed gate mass",ylabel="Applied Top-7 weights, mean over layers")
    axes[1,1].set(title="D  B minus A budget cost",ylabel="B minus A NLL penalty (paired inputs)")
    for ax in axes.flat:
        ax.set_xticks(range(5),MASKS);ax.legend(frameon=False,fontsize=8)
        ax.axhline(0,color="#BBBBBB",linewidth=.7);ax.grid(axis="y",alpha=.15)
    fig.tight_layout(rect=(0,.09,1,1),w_pad=2,h_pad=2)
    fig.text(.5,.015,"Same five masks, source endpoints and texts; only the denominator policy changes. Shared expert remains at weight 1.\n"
        "Later hidden states/routes may respond to upstream scaling. 20 input-file CIs, not model seeds or semantic-unit evidence.",ha="center",fontsize=8,color="#666666")
    out=ROOT/"figures";out.mkdir(exist_ok=True)
    for suffix in ("png","pdf"):fig.savefig(out/("fixed_mask_denominator_counterfactual."+suffix),bbox_inches="tight")
    print(out/"fixed_mask_denominator_counterfactual.png")


if __name__=="__main__":main()
