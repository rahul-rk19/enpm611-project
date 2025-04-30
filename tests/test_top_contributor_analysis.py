import unittest
from unittest.mock import patch, mock_open
import json
from feature_3.top_contributor_analysis import TopContributorAnalysis

# ----------- MOCK DATA -----------

MOCK_DATA_VALID_EVENTS = json.dumps([
    {
        "creator": "alice",
        "events": [
            {"event_type": "commented", "author": "bob"},
            {"event_type": "closed", "author": "carol"},
            {"event_type": "labeled", "author": "alice"},
            {"event_type": "reopened", "author": "carol"}
        ]
    }
])

MOCK_DATA_MISSING_EVENT_TYPES = json.dumps([
    {
        "creator": "eve",
        "events": [
            {"event_type": "mentioned", "author": "frank"},
            {"event_type": "subscribed", "author": "grace"},
            {"event_type": "referenced", "author": "heidi"}
        ]
    }
])

MOCK_DATA_EMPTY = json.dumps([])

MOCK_DATA_EVENT_WITHOUT_AUTHOR = json.dumps([
    {
        "creator": "leo",
        "events": [
            {"event_type": "commented"},  # no author
            {"event_type": "closed", "author": "leo"}
        ]
    }
])

# ----------- TEST CLASS -----------

class TestTopContributorAnalysis(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data=MOCK_DATA_VALID_EVENTS)
    @patch("config.get_parameter", return_value="dummy_path.json")
    def test_run_valid_events(self, mock_config, mock_file):
        tca = TopContributorAnalysis()
        with patch("matplotlib.pyplot.show"):
            contributors = tca.run()
            self.assertEqual(contributors["alice"], 2)  # creator + labeled
            self.assertEqual(contributors["bob"], 1)    # commented
            self.assertEqual(contributors["carol"], 2)  # closed + reopened

    @patch("builtins.open", new_callable=mock_open, read_data=MOCK_DATA_MISSING_EVENT_TYPES)
    @patch("config.get_parameter", return_value="dummy_path.json")
    def test_run_missing_event_types_should_count(self, mock_config, mock_file):
        tca = TopContributorAnalysis()
        with patch("matplotlib.pyplot.show"):
            contributors = tca.run()
            self.assertEqual(contributors["eve"], 1)  
            self.assertEqual(contributors["frank"], 1)   
            self.assertEqual(contributors["grace"], 1)   
            self.assertEqual(contributors["heidi"], 1)  

    @patch("builtins.open", new_callable=mock_open, read_data=MOCK_DATA_EMPTY)
    @patch("config.get_parameter", return_value="dummy_path.json")
    def test_run_empty_data(self, mock_config, mock_file):
        tca = TopContributorAnalysis()
        with patch("builtins.print") as mock_print, patch("matplotlib.pyplot.show") as mock_show:
            contributors = tca.run()
            mock_print.assert_called_with("No issues found in dataset.")
            self.assertEqual(contributors, {})
            mock_show.assert_not_called()

    @patch("builtins.open", new_callable=mock_open, read_data=MOCK_DATA_EVENT_WITHOUT_AUTHOR)
    @patch("config.get_parameter", return_value="dummy_path.json")
    def test_event_missing_author_field(self, mock_config, mock_file):
        tca = TopContributorAnalysis()
        with patch("matplotlib.pyplot.show"):
            contributors = tca.run()
            self.assertEqual(contributors["leo"], 2) 

# ----------- RUN TESTS -----------

if __name__ == "__main__":
    unittest.main()
