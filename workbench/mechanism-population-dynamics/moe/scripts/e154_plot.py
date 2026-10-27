"""E154 complete public-lineage profiles; no selected operating points."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT=Path(__file__).resolve().parents[1]/"results/e154"


def main():
    s=json.loads((OUT/"summary.json").read_text())
    assert s["status"]=="complete"
    full=s["scopes"]["full"]["profiles"]
    tail=s["scopes"]["suffix"]["profiles"]
    plt.rcParams.update({"font.size":9,"axes.spines.top":False,"axes.spines.right":False,"pdf.fonttype":42})
    fig,axes=plt.subplots(2,3,figsize=(11.8,6.7),dpi=160)
    records=[
        ("A  Full native quality","Native NLL",lambda x:full[x]["conditions"]["native"]["NLL"]),
        ("B  Routed branch dependence","All R zero: NLL penalty",lambda x:full[x]["conditions"]["routed_zero"]["delta_NLL"]),
        ("C  Shared branch dependence","All S zero: NLL penalty",lambda x:full[x]["conditions"]["shared_zero"]["delta_NLL"]),
        ("D  Own prefix restriction","Suffix NLL penalty",lambda x:tail[x]["conditions"]["own_prefix"]["delta_NLL"]),
        ("E  Fixed random restrictions","Mean suffix NLL penalty",lambda x:tail[x]["random_mean"]["delta_NLL"]),
        ("F  Useful input selection","Random minus own-prefix NLL",lambda x:tail[x]["own_prefix_selection_advantage"]["NLL"]),
    ]
    for ax,(title,ylabel,get) in zip(axes.flat,records):
        for i,(label,color) in enumerate((("P","#666666"),("A","#2166AC"),("B","#B2182B"))):
            row=get(label)
            lo,hi=row["input_file_ci95"]
            ax.vlines(i,lo,hi,color=color,linewidth=1.3)
            ax.plot(i,row["point"],"o",color=color,markersize=5)
        ax.set(title=title,ylabel=ylabel,xticks=range(3),xticklabels=("Parent P","Standard A","Pool B"))
        ax.grid(axis="y",alpha=.15)
        ax.axhline(0,color="#BBBBBB",linewidth=.6)
    fig.tight_layout(rect=(0,.09,1,1),w_pad=2,h_pad=2)
    fig.text(.5,.015,"One author-declared 1T parent and two 50B annealing endpoints; unchanged architecture and text inputs.\n"
             "20 paired input-file CIs, not training seeds. Zeroing costs are nonadditive dependencies; three snapshots are not full dynamics.",ha="center",fontsize=8,color="#666666")
    out=OUT/"figures"
    out.mkdir(exist_ok=True)
    for suffix in ("png","pdf"):
        fig.savefig(out/("public_parent_dependence_profiles."+suffix),bbox_inches="tight")
    print(out/"public_parent_dependence_profiles.png")


if __name__=="__main__":
    main()
