"""Plot the complete, audited E03 learning curves without selecting snapshots."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def main():
    report = json.loads((ROOT / "results/e03_train_analysis_seed17.json").read_text())
    fig, axes = plt.subplots(1,2,figsize=(10,4),sharey=True,constrained_layout=True)
    for ax,split,title in zip(axes,("en_test","de_test"),("English task learning","German transfer")):
        for condition,label,color in (("baseline","FWB","#18765b"),("monoweb","MWB","#b43e43"),
                                      ("onlyparallel","MWB+P","#326ba8")):
            rows = [r for r in report["table"] if r["condition"]==condition and r["split"]==split and r["metric"]=="f1"]
            assert [r["updates"] for r in rows]==[0,128,512,1024]
            x = [r["updates"]*16 for r in rows]
            ax.plot(x,[r["mean"]*100 for r in rows],"o-",color=color,label=label)
            ax.fill_between(x,[r["context_cluster_bootstrap95"][0]*100 for r in rows],
                              [r["context_cluster_bootstrap95"][1]*100 for r in rows],color=color,alpha=.12)
        ax.set(title=title,xlabel="English supervised examples",ylim=(0,100),xticks=(0,2048,8192,16384))
        ax.grid(axis="y",alpha=.2)
        ax.spines[["top","right"]].set_visible(False)
    axes[0].set_ylabel("Official generation F1 (%)")
    axes[1].legend(frameon=False)
    fig.suptitle("One adaptation seed; bands: context-cluster intervals",fontsize=11)
    path = ROOT / "results/qa_learning_curves.png"
    fig.savefig(path,dpi=160)
    print(path)


if __name__ == "__main__":
    main()
