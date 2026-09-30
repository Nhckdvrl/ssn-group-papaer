#!/usr/bin/env python3
"""Generate the weekly human-review skeleton for a workbench (templates/weekly_review.md).

  python3 tools/process/weekly.py <workbench> [--days 7] [--today YYYY-MM-DD] [--write]

Auto-fills: countdown and expected phase, experiments and ideas touched in the window,
claim levels, new pain-log entries, drift signals (EXECUTION.md §8). The human fills the rest.
"""
import argparse
import datetime as dt
import re
import subprocess
import sys

from common import LEVELS, ROOT, WB, choice, claims, field, parse_date, registry, today

PHASES = [(12, "驻留 D1–D6；形态卡初稿"), (10, "主旨主张 ≥ L2；定位表完整；决定是否改投"),
          (8, "进入 candidate；主图草图；引言初稿"), (6, "泛化与消融（≥ L3）；方法与实验初稿"),
          (4, "全文初稿；模拟审稿"), (1, "修复、校对、复现清单"), (0, "投稿")]


def git_touched(path, since):
    out = subprocess.run(["git", "log", f"--since={since.isoformat()}", "--name-only", "--pretty=format:%h %ad %s",
                          "--date=short", "--", str(path)], cwd=ROOT, capture_output=True, text=True).stdout
    commits = [l for l in out.splitlines() if re.match(r"^[0-9a-f]{7,} \d{4}-", l)]
    files = {l.strip() for l in out.splitlines() if l.strip() and not re.match(r"^[0-9a-f]{7,} \d{4}-", l)}
    return commits, files


def gpu_hours(text):
    m = re.search(r"\*\*实际：\*\*\s*([\d.]+)", text)
    return float(m.group(1)) if m else 0.0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("workbench")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--today")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    now = today(args.today)
    since = now - dt.timedelta(days=args.days)
    d = WB / args.workbench
    if not d.is_dir():
        sys.exit(f"workbench 不存在：{args.workbench}")
    row = next((r for r in registry()[1] if r["name"] == args.workbench), {})
    rel = d.relative_to(ROOT).as_posix()
    commits, touched = git_touched(d, since)
    out = [f"# 每周人审 — {args.workbench} — {now}（窗口：{since} → {now}）", ""]

    deadline = parse_date(row.get("截稿"))
    if deadline:
        days = (deadline - now).days
        phase = next((p for w, p in PHASES if days >= w * 7), PHASES[-1][1])
        out.append(f"1. **倒计时：** 距 {row.get('目标会议')} 截稿 {days} 天（T−{days // 7} 周）；按倒排应处于：{phase}。")
    else:
        out.append(f"1. **倒计时：** 截稿日未定（登记表：{row.get('目标会议', '未登记')}）。")

    ledger = d / (re.sub(r"`", "", row.get("主张账本", "")).strip() or "CLAIMS.md")
    rows = [c for c in claims(ledger) if next((v for k, v in c.items() if "主张" in k), "").strip()]
    by_level = {lv: 0 for lv in LEVELS}
    recent, last_update = [], None
    for c in rows:
        lv = next((v for k, v in c.items() if "等级" in k), "").strip()
        if lv in by_level:
            by_level[lv] += 1
        upd = parse_date(next((v for k, v in c.items() if "更新" in k), ""))
        if upd:
            last_update = max(last_update or upd, upd)
            if upd >= since:
                recent.append(f"{c.get('ID')}（{lv}）")
    dist = " · ".join(f"{k}:{v}" for k, v in by_level.items() if v) or "账本为空或非表格格式"
    out.append(f"2. **主张：** 分布 {dist}；本周更新：{', '.join(recent) or '无'}。")

    exp_lines, total, explore, no_plan = [], 0.0, 0.0, []
    for card in sorted((d / "experiments").glob("E*.md")) if (d / "experiments").is_dir() else []:
        if f"{rel}/experiments/{card.name}" not in touched:
            continue
        text = card.read_text()
        st = choice(field(text, "状态"), ["PLANNED", "RUNNING", "DONE", "VOID"]) or "?"
        ty = choice(field(text, "类型"), ["CLAIM", "PILOT", "REPRO", "EXPLORE"]) or "?"
        h = gpu_hours(text)
        total += h
        explore += h if ty == "EXPLORE" else 0
        if re.fullmatch(r"结果 A → ；结果 B → ；不确定 →\s*", field(text, "决策表（跑之前写）") or ""):
            no_plan.append(card.stem)
        exp_lines.append(f"   - {card.stem}：{st} · {ty} · {h:g} GPU·时")
    share = f"{explore / total:.0%}" if total else "—"
    out.append(f"3. **实验：** 本周涉及 {len(exp_lines)} 张实验卡；EXPLORE 占 GPU·时 {share}。")
    out += exp_lines

    idea_lines = []
    for card in sorted((d / "ideas").glob("I*.md")) if (d / "ideas").is_dir() else []:
        st = choice(field(card.read_text(), "状态"), ["SEED", "PILOT", "PROMISING", "CLAIM", "PARKED", "REFUTED"]) or "?"
        mark = "（本周更新）" if f"{rel}/ideas/{card.name}" in touched else ""
        idea_lines.append(f"   - {card.stem}：{st}{mark}")
    out.append(f"4. **idea 组合：** {len(idea_lines)} 个。排序前 2 与下周的决定性 pilot：＿")
    out += idea_lines

    pains = []
    if (d / "PAIN_LOG.md").exists():
        for line in (d / "PAIN_LOG.md").read_text().splitlines():
            dd = parse_date(line)
            if line.lstrip().startswith("- P") and dd and dd >= since:
                pains.append("   " + line.strip()[:160])
    out.append(f"5. **痛点：** 本周新增 {len(pains)} 条。")
    out += pains
    out.append("6. **定位：** 新近邻（两周一次，`tools/venue_corpus/query.py nearest` + 最新 arXiv）：＿")

    drift = []
    if last_update and (now - last_update).days >= 14:
        drift.append(f"主张账本 {(now - last_update).days} 天没有更新")
    if total and explore / total > 0.3:
        drift.append(f"EXPLORE 占 {explore / total:.0%} > 30%")
    if no_plan:
        drift.append(f"决策表为空：{', '.join(no_plan)}")
    if not commits:
        drift.append("本周没有提交")
    out.append(f"7. **漂移信号：** {'；'.join(drift) or '未检测到（仍请人工确认 EXECUTION.md §8）'}。")
    out += ["8. **形态卡：** 一句话主旨是否更简单了？＿", "9. **需要人决定的事：** ＿",
            "10. **人的品味输入：** ＿", "11. **决定（人签字）：** 继续 / 同领域内转向 / 暂停 ＿", "",
            f"<!-- 本周提交 {len(commits)} 个 -->"]
    text = "\n".join(out) + "\n"
    if args.write:
        path = d / "logs" / f"weekly-{now}.md"
        path.parent.mkdir(exist_ok=True)
        if path.exists():
            sys.exit(f"已存在：{path.relative_to(ROOT)}")
        path.write_text(text)
        print(f"created {path.relative_to(ROOT)}")
    else:
        print(text)


if __name__ == "__main__":
    main()
