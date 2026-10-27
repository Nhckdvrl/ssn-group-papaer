"""E153 full matrix plots; every fixed source case and selector is retained."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]/"results/e153"
CASES=("AAAA","ABAA","BABB","BBBB")
POLICIES=(("full","#4D4D4D","s"),("selectorA32","#2166AC","o"),("selectorB32","#B2182B","^"))
SUBJECTS=(None,"high_school_biology","high_school_mathematics")


def value(row,subject):
    if subject is None:
        return row["point"],row["question_ci95"]
    d=row["per_subject"][subject]
    return d["point"],d["ci95"]


def main():
    s=json.loads((ROOT/"summary.json").read_text())
    assert s["status"]=="complete"
    plt.rcParams.update({"font.size":9,"axes.spines.top":False,"axes.spines.right":False,"pdf.fonttype":42})
    fig,axes=plt.subplots(2,3,figsize=(13.2,7.1),dpi=160)
    for col,subject in enumerate(SUBJECTS):
        for row,metric in enumerate(("raw_accuracy","choice_CE")):
            ax=axes[row,col]
            scale=100 if metric=="raw_accuracy" else 1
            for p,(policy,color,marker) in enumerate(POLICIES):
                xs=[i+(p-1)*.18 for i in range(4)]
                for i,name in enumerate(CASES):
                    point,ci=value(s["cases"][name][policy][metric],subject)
                    ax.vlines(xs[i],scale*ci[0],scale*ci[1],color=color,linewidth=1)
                    ax.plot(xs[i],scale*point,marker,color=color,markersize=4,label=policy if i==0 else None)
            ax.set_xticks(range(4),CASES)
            ax.grid(axis="y",alpha=.15)
            if row==0:
                ax.set_title(("Fixed-subject macro","Biology (64 questions)","Mathematics (64 questions)")[col])
                ax.set_ylim(0,100)
                ax.axhline(25,color="#BBBBBB",linestyle=":",linewidth=.7)
            if col==0:
                ax.set_ylabel(("Raw RC accuracy (%)","Correct-choice CE (four scores)")[row])
            if row==0 and col==0:
                ax.legend(frameon=False,fontsize=8)
    fig.tight_layout(rect=(0,.09,1,1),w_pad=2,h_pad=2)
    fig.text(.5,.015,"G x non-router body: AAAA, B-gate-only ABAA, B-body-with-A-gate BABB, BBBB. Shared slot is retained.\n"
             "Native validation-selected masks are fixed for all hybrids. Question-paired 95% CIs; two subjects, not model seeds or whole MMLU.",ha="center",fontsize=8,color="#666666")
    out=ROOT/"figures"
    out.mkdir(exist_ok=True)
    for suffix in ("png","pdf"):
        fig.savefig(out/("task_source_transfer."+suffix),bbox_inches="tight")
    print(out/"task_source_transfer.png")


if __name__=="__main__":
    main()
