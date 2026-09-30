#!/usr/bin/env python3
"""Generate the human-review skeleton for a workbench (templates/review.md).

  python3 tools/process/review.py <workbench> [--since YYYY-MM-DD] [--today YYYY-MM-DD] [--write]

Reviews are triggered by decision points (EXECUTION.md §9), not by the calendar. The window is
"since the last review": the latest logs/review-*.md, else the registry's 上次人审, else all history.
Auto-fills claim changes, experiments and ideas touched, new pain-log entries and drift signals
(EXECUTION.md §8, counted in experiments, not days). The human fills the rest.
"""
import argparse
import re
import subprocess
import sys

from common import LEVELS, ROOT, WB, choice, claims, field, parse_date, registry, today

DRIFT_CARDS = 5  # completed experiment cards without any claim change


def last_review(d, row):
    dates = [parse_date(f.name) for f in (d / "logs").glob("review-*.md")] if (d / "logs").is_dir() else []
    dates = [x for x in dates if x]
    return max(dates) if dates else parse_date(row.get("上次人审"))


def git_touched(path, since):
    cmd = ["git", "log", "--name-only", "--pretty=format:%h %ad %s", "--date=short"]
    if since:
        cmd.append(f"--since={since.isoformat()}")
    out = subprocess.run(cmd + ["--", str(path)], cwd=ROOT, capture_output=True, text=True).stdout
    is_commit = lambda l: re.match(r"^[0-9a-f]{7,} \d{4}-", l)
    commits = [l for l in out.splitlines() if is_commit(l)]
    files = {l.strip() for l in out.splitlines() if l.strip() and not is_commit(l)}
    return commits, files


def gpu_hours(text):
    m = re.search(r"\*\*实际：\*\*\s*([\d.]+)", text)
    return float(m.group(1)) if m else 0.0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("workbench")
    ap.add_argument("--since")
    ap.add_argument("--today")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    now = today(args.today)
    d = WB / args.workbench
    if not d.is_dir():
        sys.exit(f"workbench 不存在：{args.workbench}")
    row = next((r for r in registry()[1] if r["name"] == args.workbench), {})
    since = parse_date(args.since) if args.since else last_review(d, row)
    rel = d.relative_to(ROOT).as_posix()
    commits, touched = git_touched(d, since)
    window = f"自 {since} 上次人审以来" if since else "全部历史（尚无人审记录）"
    out = [f"# 人审 — {args.workbench} — {now}（{window}）", "",
           "**触发原因：** ＿（D1–D6 交付 / pilot 要选分支 / 主张升降级 / 漂移信号 / 开关线、转向、进候选、投稿之前）", ""]

    ledger = d / (re.sub(r"`", "", row.get("主张账本", "")).strip() or "CLAIMS.md")
    rows = [c for c in claims(ledger) if next((v for k, v in c.items() if "主张" in k), "").strip()]
    by_level, changed = {lv: 0 for lv in LEVELS}, []
    for c in rows:
        lv = next((v for k, v in c.items() if "等级" in k), "").strip()
        by_level[lv] = by_level.get(lv, 0) + 1
        upd = parse_date(next((v for k, v in c.items() if "更新" in k), ""))
        if upd and (since is None or upd >= since):
            changed.append(f"{c.get('ID')}（{lv}）")
    dist = " · ".join(f"{k}:{v}" for k, v in by_level.items() if v) or "账本为空或非表格格式"
    out.append(f"1. **主张：** 分布 {dist}；本窗口内更新：{', '.join(changed) or '无'}。")

    exp_lines, total, explore, no_plan, done = [], 0.0, 0.0, [], 0
    for card in sorted((d / "experiments").glob("E*.md")) if (d / "experiments").is_dir() else []:
        if f"{rel}/experiments/{card.name}" not in touched:
            continue
        text = card.read_text()
        st = choice(field(text, "状态"), ["PLANNED", "RUNNING", "DONE", "VOID"]) or "?"
        ty = choice(field(text, "类型"), ["CLAIM", "PILOT", "REPRO", "EXPLORE"]) or "?"
        h = gpu_hours(text)
        total += h
        explore += h if ty == "EXPLORE" else 0
        done += st == "DONE"
        if re.fullmatch(r"结果 A → ；结果 B → ；不确定 →\s*", field(text, "决策表（跑之前写）") or ""):
            no_plan.append(card.stem)
        exp_lines.append(f"   - {card.stem}：{st} · {ty} · {h:g} GPU·时")
    share = f"{explore / total:.0%}" if total else "—"
    out.append(f"2. **实验：** 本窗口内涉及 {len(exp_lines)} 张实验卡（完成 {done}）；EXPLORE 占 GPU·时 {share}。")
    out += exp_lines

    idea_lines = []
    for card in sorted((d / "ideas").glob("I*.md")) if (d / "ideas").is_dir() else []:
        st = choice(field(card.read_text(), "状态"), ["SEED", "PILOT", "PROMISING", "CLAIM", "PARKED", "REFUTED"]) or "?"
        mark = "（本窗口内更新）" if f"{rel}/ideas/{card.name}" in touched else ""
        idea_lines.append(f"   - {card.stem}：{st}{mark}")
    out.append(f"3. **idea 组合：** {len(idea_lines)} 个。排序前 2 与接下来的决定性 pilot：＿")
    out += idea_lines

    pains = []
    if (d / "PAIN_LOG.md").exists():
        for line in (d / "PAIN_LOG.md").read_text().splitlines():
            dd = parse_date(line)
            if line.lstrip().startswith("- P") and dd and (since is None or dd >= since):
                pains.append("   " + line.strip()[:160])
    out.append(f"4. **痛点：** 新增 {len(pains)} 条。")
    out += pains
    out.append("5. **定位：** 新近邻（`tools/venue_corpus/query.py nearest` + 最新 arXiv；主旨改变或主张升到 L2 时必做）：＿")

    drift = []
    if done >= DRIFT_CARDS and not changed:
        drift.append(f"完成 {done} 张实验卡，但没有任何主张变化")
    if total and explore / total > 0.3:
        drift.append(f"EXPLORE 占 {explore / total:.0%} > 30%")
    if no_plan:
        drift.append(f"决策表为空：{', '.join(no_plan)}")
    out.append(f"6. **漂移信号：** {'；'.join(drift) or '未检测到（仍请人工确认 EXECUTION.md §8）'}。")
    out += ["7. **形态卡：** 一句话主旨是否更简单了？＿",
            f"8. **目标会议：** {row.get('目标会议', '未登记')}——截稿时够不够投？不够就改投哪个会？＿",
            "9. **需要人决定的事：** ＿", "10. **人的品味输入：** ＿",
            "11. **决定（人签字）：** 继续 / 同领域内转向 / 暂停 ＿", "", f"<!-- 本窗口内提交 {len(commits)} 个 -->"]
    text = "\n".join(out) + "\n"
    if args.write:
        path = d / "logs" / f"review-{now}.md"
        path.parent.mkdir(exist_ok=True)
        if path.exists():
            sys.exit(f"已存在：{path.relative_to(ROOT)}")
        path.write_text(text)
        print(f"created {path.relative_to(ROOT)}")
    else:
        print(text)


if __name__ == "__main__":
    main()
