"""Regression coverage for a domain workbench with one nested research ledger."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import check
import common
import new
import review


class ResearchPathsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.wb = self.root / "workbench"
        self.domain = self.wb / "npc"
        self.research = self.domain / "mine-a"
        for name in ("experiments", "ideas", "logs"):
            (self.research / name).mkdir(parents=True)
        (self.domain / "README.md").write_text("# Domain\n")
        (self.wb / "README.md").write_text(
            "| workbench | 状态 | 目标会议 | 截稿 | 主张账本 | 上次人审 |\n"
            "|---|---|---|---|---|---|\n"
            "| `npc` | PROPOSED | — | — | `mine-a/CLAIMS.md` | 2026-10-17 |\n"
        )
        (self.research / "CLAIMS.md").write_text(
            "| ID | 主张 | 等级 | 证据 | 更新 |\n|---|---|---|---|---|\n"
            "| C01 | Actual evidence | L2 | E01 | 2026-10-17 |\n"
        )
        (self.research / "PAIN_LOG.md").write_text("# Pain\n")
        self.card = self.research / "experiments/E01-source.md"
        self.card.write_text("# E01\n- **状态：** DONE\n- **类型：** REPRO\n")
        (self.research / "ideas/I01-source.md").write_text(
            "# I01\n- **状态：** SEED\n- **来源：** P01 actual observation\n"
        )
        for module in (common, check, new, review):
            for name, value in (("WB", self.wb), ("ROOT", self.root)):
                ctx = patch.object(module, name, value)
                ctx.start()
                self.addCleanup(ctx.stop)

    def test_default_and_nested_ledger(self):
        self.assertEqual(common.research_dir({"name": "npc"}), self.domain)
        row = common.registry()[1][0]
        self.assertEqual(common.research_dir(row), self.research)
        self.assertEqual(common.ledger_path(row), self.research / "CLAIMS.md")

    def test_checker_reads_nested_cards_and_claims(self):
        output = io.StringIO()
        with patch("sys.argv", ["check.py"]), contextlib.redirect_stdout(output):
            with self.assertRaises(SystemExit) as result:
                check.main()
        self.assertEqual(result.exception.code, 0)
        self.assertIn("npc/mine-a/experiments/E01-source.md", output.getvalue())
        self.assertIn("实验卡缺少字段", output.getvalue())
        rep = check.Report()
        check.check_claims(rep, common.ledger_path(common.registry()[1][0]))
        self.assertEqual(rep.items, [])

    def test_new_card_uses_nested_numbering_without_outer_copy(self):
        with patch("sys.argv", ["new.py", "experiment", "npc", "next"]):
            with contextlib.redirect_stdout(io.StringIO()):
                new.main()
        self.assertTrue((self.research / "experiments/E02-next.md").exists())
        self.assertFalse((self.domain / "experiments").exists())

    def test_review_reads_nested_ledger_cards_and_ideas(self):
        touched = {str(self.card.relative_to(self.root))}
        output = io.StringIO()
        with patch("sys.argv", ["review.py", "npc"]), patch.object(
            review, "git_touched", return_value=([], touched)
        ), contextlib.redirect_stdout(output):
            review.main()
        self.assertIn("L2:1", output.getvalue())
        self.assertIn("涉及 1 张实验卡", output.getvalue())
        self.assertIn("idea 组合：** 1 个", output.getvalue())
        self.assertFalse(list(self.research.glob("logs/review-*.md")))


if __name__ == "__main__":
    unittest.main()
