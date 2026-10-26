"""Standalone E150 prediction, restricted-compute and pairing figures; all cases."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]/"results/e150"
BLUE,RED,GRAY="#2166AC","#B2182B","#666666"


def point(ax,x,row,color,marker="o",offset=0,label=None):
    low,high=row["input_file_ci95"]
    ax.vlines(x+offset,low,high,color=color,linewidth=.9)
    ax.plot(x+offset,row["point"],marker,color=color,markersize=4,label=label)


def main():
    d=json.loads((ROOT/"summary.json").read_text())
    if d["status"]!="complete":raise ValueError("Complete source cube required")
    plt.rcParams.update({"font.size":9,"axes.spines.top":False,"axes.spines.right":False,"pdf.fonttype":42})
    names=list(d["cases"])
    fig,axes=plt.subplots(2,2,figsize=(13,8),dpi=150)
    ax=axes[0,0]
    for i,name in enumerate(names):point(ax,i,d["cases"][name]["nll_minus_AAAA"],BLUE if name=="AAAA" else RED if name=="BBBB" else GRAY)
    ax.set(title="A  Full-model source composition",ylabel="NLL minus AAAA (nats / token)")
    ax=axes[0,1]
    for p,(selector,color,offset) in enumerate((("A",BLUE,-.1),("B",RED,.1))):
        for i,name in enumerate(names):
            row=d["restriction"]["selectors"][selector]["cases"][name]["pruning_delta_nll"]
            point(ax,i,row,color,offset=offset,label=f"Native {selector} prefix selector" if i==0 else None)
    ax.set(title="B  Fixed 32-slot compute on unseen suffix",ylabel="Restricted minus same full hybrid NLL")
    ax.legend(frameon=False,fontsize=8)
    for ax in axes[0]:
        ax.set_xticks(range(16),names,rotation=60,fontsize=8)
        ax.set_xlabel("Sources: dense / router / routed experts / shared experts")
    ax=axes[1,0]
    factors=("dense_backbone","all_routers","routed_experts","shared_experts")
    for selector,color,offset in (("A",BLUE,-.12),("B",RED,.12)):
        for i,factor in enumerate(factors):
            row=d["restriction"]["selectors"][selector]["factor_effect_on_pruning_penalty"][factor+"_B_minus_A"]
            point(ax,i,row,color,offset=offset,label=f"Selector {selector}" if i==0 else None)
    ax.set(xticks=range(4),xticklabels=["Dense","Routers","Routed","Shared"],title="C  Source effects on restricted-compute cost",ylabel="B minus A source, mean over 8 backgrounds")
    ax.legend(frameon=False,fontsize=8)
    ax=axes[1,1]
    for selector,color,offset in (("A",BLUE,-.12),("B",RED,.12)):
        rows=d["restriction"]["selectors"][selector]["factor_effect_on_full_to_restricted_KL"]
        for i,factor in enumerate(factors):
            row=rows[factor+"_B_minus_A"]
            point(ax,i,row,color,offset=offset,label=f"Selector {selector}" if i==0 else None)
    ax.set(xticks=range(4),xticklabels=["Dense","Routers","Routed","Shared"],title="D  Source effects on predictive sensitivity",ylabel="B minus A source: full-to-restricted KL")
    ax.legend(frameon=False,fontsize=8)
    for ax in axes.flat:ax.axhline(0,color="#BBBBBB",linewidth=.7);ax.grid(axis="y",alpha=.15)
    fig.tight_layout(rect=(0,.09,1,1),w_pad=2,h_pad=2)
    fig.text(.5,.015,"One published protocol-package pair with a declared common parent; no new training.\n"
        "All 16 source cells, both fixed prefix selectors; 20 input-file cluster CIs, not training seeds. Language-window diagnostic, not a semantic-module benchmark.",ha="center",fontsize=8,color=GRAY)
    out=ROOT/"figures";out.mkdir(exist_ok=True)
    for suffix in ("png","pdf"):fig.savefig(out/("mature_source_and_restricted_compute."+suffix),bbox_inches="tight")
    fig,axes=plt.subplots(1,2,figsize=(11,4),dpi=150)
    for selector,color in (("A",BLUE),("B",RED)):
        rows=d["restriction"]["selectors"][selector]["cases"]
        for ax,field,title in ((axes[0],"mean_layer_routed_top7_support_retained","Original routed Top-7 support"),
                               (axes[1],"mean_layer_inverse_retained_probability","Full-softmax denominator scale")):
            x=[rows[k][field]["point"] for k in names]
            y=[rows[k]["pruning_delta_nll"]["point"] for k in names]
            ax.scatter(x,y,color=color,s=18,alpha=.75,label=f"Selector {selector}")
            for k in ("AAAA","BBBB"):
                i=names.index(k);ax.annotate(k,(x[i],y[i]),xytext=(3,3),textcoords="offset points",fontsize=7,color=color)
            ax.set(title=title,xlabel="Mean Top-7 fraction kept" if ax==axes[0] else "Mean inverse retained routed probability",ylabel="Pruning NLL cost")
    for ax in axes:ax.legend(frameon=False,fontsize=8);ax.grid(alpha=.15)
    fig.tight_layout(rect=(0,.1,1,1),w_pad=3)
    fig.text(.5,.015,"Descriptive pathways across source interventions; no regression or causal responsibility percentage.\n"
        "Normalizer mass uses full FP32 routed softmax before BF16 cast; shared expert is retained with native weight 1.",ha="center",fontsize=8,color=GRAY)
    for suffix in ("png","pdf"):fig.savefig(out/("support_and_normalizer_paths."+suffix),bbox_inches="tight")
    print(out/"mature_source_and_restricted_compute.png")


if __name__=="__main__":main()
