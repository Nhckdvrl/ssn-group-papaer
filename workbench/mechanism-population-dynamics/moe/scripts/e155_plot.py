"""Task branch-dependence profiles, with all R x S conditions retained."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT=Path(__file__).resolve().parents[1]/"results/e155"
SOURCES=("P","A","B")
CONDITIONS=("native","routed_zero","shared_zero","all_moe_zero")
COLORS=("#555555","#2166AC","#B2182B","#7B3294")
MARKERS=("s","o","^","x")


def main():
    s=json.loads((OUT/"summary.json").read_text())
    assert s["status"]=="complete"
    plt.rcParams.update({"font.size":9,"axes.spines.top":False,"axes.spines.right":False,"pdf.fonttype":42})
    fig,axes=plt.subplots(2,2,figsize=(11,7),dpi=160)
    for panel,field in enumerate(("raw_accuracy","per_char_accuracy","choice_CE","first_answer_token_KL")):
        ax=axes.flat[panel]
        scale=100 if "accuracy" in field else 1
        for c,name in enumerate(CONDITIONS):
            for i,source in enumerate(SOURCES):
                row=s["sources"][source][name][field]
                x=i+(c-1.5)*.13
                lo,hi=row["question_ci95"]
                ax.vlines(x,scale*lo,scale*hi,color=COLORS[c],linewidth=1)
                ax.plot(x,scale*row["point"],MARKERS[c],color=COLORS[c],markersize=4,label=name if i==0 else None)
        ax.set_xticks(range(3),("Parent P","Standard A","Pool B"))
        ax.set_ylabel(("Raw RC accuracy (%)","Per-character accuracy (%)","Correct-choice CE","First-answer full-vocabulary KL")[panel])
        ax.set_title(("A  Task correctness","B  Length-normalized diagnostic","C  Correct-answer preference","D  Predictive effect of branch removal")[panel])
        ax.grid(axis="y",alpha=.15)
        if "accuracy" in field:
            ax.set_ylim(0,100)
            ax.axhline(25,color="#BBBBBB",linestyle=":",linewidth=.7)
        if panel==0:
            ax.legend(frameon=False,fontsize=8)
    fig.tight_layout(rect=(0,.09,1,1),w_pad=2,h_pad=2)
    fig.text(.5,.015,"R-zero retains D+S; S-zero retains D+R; all-MoE-zero retains D. Same fixed 128 questions and pretrained checkpoints.\n"
             "Paired question CIs within two fixed subjects. Removal effects are nonadditive dependencies, not fractions of stored knowledge.",ha="center",fontsize=8,color="#666666")
    figures=OUT/"figures"
    figures.mkdir(exist_ok=True)
    for ext in ("png","pdf"):
        fig.savefig(figures/("task_branch_dependence."+ext),bbox_inches="tight")
    print(figures/"task_branch_dependence.png")


if __name__=="__main__":
    main()
