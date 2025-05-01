import unittest
from feature_1.keyword_demand import KeywordDemand
from model import Issue, Event
from datetime import datetime
from collections import Counter
from unittest.mock import patch
import matplotlib



matplotlib.use("Agg")


class TestKeywordDemand(unittest.TestCase):

    def setUp(self):
        issue1 = Issue()
        issue1.title = "Fix virtualenv bug"
        issue1.text = "Something is broken in virtualenv"
        issue1.labels = ["bug"]
        issue1.created_date = datetime(2024, 1, 10)
        issue1.events = [Event({"event_type": "comment"})]

        issue2 = Issue()
        issue2.title = "Improve poetry docs"
        issue2.text = "Add pipx usage"
        issue2.labels = ["documentation"]
        issue2.created_date = datetime(2024, 2, 15)
        issue2.events = [Event({"event_type": "closed"})]

        self.issues = [issue1, issue2]

    @patch("feature_1.keyword_demand.config.get_parameter", return_value="virtualenv")
    def test_keyword_filtering(self, mock_config):
        kd = KeywordDemand()
        matched = [
            i for i in self.issues
            if kd.keyword in (i.title or "").lower() or kd.keyword in (i.text or "").lower()
        ]
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0].title, "Fix virtualenv bug")

    def test_comment_count(self):
        count = sum(len([e for e in i.events if e.event_type == "comment"]) for i in self.issues)
        self.assertEqual(count, 1)

    def test_label_count(self):
        label_counter = Counter()
        for issue in self.issues:
            for label in issue.labels:
                label_counter[label] += 1
        self.assertEqual(label_counter["bug"], 1)
        self.assertEqual(label_counter["documentation"], 1)

    @patch("feature_1.keyword_demand.config.get_parameter", return_value="virtualenv")
    def test_monthly_keyword_count(self, mock_config):
        kd = KeywordDemand()
        matched = [
            i for i in self.issues
            if kd.keyword in (i.title or "").lower() or kd.keyword in (i.text or "").lower()
        ]
        month_counts = Counter()
        for i in matched:
            month = i.created_date.strftime("%Y-%m")
            month_counts[month] += 1
        self.assertEqual(month_counts["2024-01"], 1)

    @patch("matplotlib.pyplot.show")
    @patch("feature_1.keyword_demand.config.get_parameter", return_value="virtualenv")
    def test_analyze_and_plot_runs_without_crash(self, mock_config, mock_show):
        kd = KeywordDemand()
        kd.analyze_and_plot(self.issues)
        mock_show.assert_called()

    @patch("feature_1.keyword_demand.DataLoader.get_issues")
    @patch("matplotlib.pyplot.show")
    @patch("feature_1.keyword_demand.config.get_parameter", return_value="virtualenv")
    def test_run_method_with_mocked_loader(self, mock_config, mock_show, mock_get_issues):
        mock_get_issues.return_value = self.issues
        kd = KeywordDemand()
        kd.run()
        mock_show.assert_called()

    @patch("feature_1.keyword_demand.DataLoader.get_issues", return_value=[])
    @patch("feature_1.keyword_demand.config.get_parameter", return_value="")
    @patch("builtins.print")
    def test_run_empty_keyword(self, mock_print, mock_config, mock_loader):
        kd = KeywordDemand()
        kd.run()
        mock_print.assert_called_with("Please input the keyword as --keyword")


if __name__ == "__main__":
    unittest.main()
