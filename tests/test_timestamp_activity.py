import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, time
from dateutil import tz
from collections import defaultdict
from feature_2.timestamp_activity import TimestampActivityAnalysis
from model import Event, Issue

class TestTimestampActivity(unittest.TestCase):
    def setUp(self):
        # Create test data that matches actual model structure
        self.sample_issue = self.create_mock_issue(
            created_date=datetime(2023, 1, 1, 12, 0, tzinfo=tz.UTC),
            updated_date=datetime(2023, 1, 2, 14, 0, tzinfo=tz.UTC),
            events=[
                self.create_mock_event(datetime(2023, 1, 1, 13, 0, tzinfo=tz.UTC)),
                self.create_mock_event(datetime(2023, 1, 2, 15, 0, tzinfo=tz.UTC))
            ]
        )
        
        # For testing datetime conversion
        self.naive_datetime = datetime(2023, 1, 1, 12, 0)
        self.aware_datetime = datetime(2023, 1, 1, 12, 0, tzinfo=tz.UTC)

    def create_mock_event(self, event_date):
        """Create an Event object with the correct structure"""
        return Event({
            'event_type': 'test_event',
            'event_date': event_date.isoformat() if event_date else None,
            'author': 'test_author'
        })

    def create_mock_issue(self, created_date=None, updated_date=None, events=None):
        """Create an Issue object with the correct structure"""
        return Issue({
            'created_date': created_date.isoformat() if created_date else None,
            'updated_date': updated_date.isoformat() if updated_date else None,
            'events': [e.__dict__ for e in events] if events else [],
            'state': 'open',
            'title': 'Test Issue',
            'creator': 'test_user'
        })

    def test_make_tz_aware(self):
        """Test timezone awareness conversion"""
        analysis = TimestampActivityAnalysis()
        result = analysis.make_tz_aware(self.naive_datetime)
        self.assertIsNotNone(result.tzinfo)
        self.assertEqual(analysis.make_tz_aware(self.aware_datetime).tzinfo, tz.UTC)
        self.assertIsNone(analysis.make_tz_aware(None))

    def test_is_within_date_range_no_filters(self):
        """Test date range check with no filters"""
        analysis = TimestampActivityAnalysis()
        self.assertTrue(analysis.is_within_date_range(self.aware_datetime))
        self.assertTrue(analysis.is_within_date_range(self.naive_datetime))
        self.assertFalse(analysis.is_within_date_range(None))

    @patch('config.get_parameter')
    def test_is_within_date_range_with_filters(self, mock_get_parameter):
        """Test date range check with filters"""
        mock_get_parameter.side_effect = lambda x: '2023-01-01' if x == 'start_date' else '2023-01-31'
        analysis = TimestampActivityAnalysis()
        test_dt = datetime(2023, 1, 15, 12, 0, tzinfo=tz.UTC)
        self.assertTrue(analysis.is_within_date_range(test_dt))
        self.assertFalse(analysis.is_within_date_range(datetime(2022, 12, 31, tzinfo=tz.UTC)))

    def test_format_heatmap_number(self):
        """Test number formatting for heatmap labels"""
        analysis = TimestampActivityAnalysis()
        self.assertEqual(analysis.format_heatmap_number(500), "500")
        self.assertEqual(analysis.format_heatmap_number(1500), "1.5K")
        self.assertEqual(analysis.format_heatmap_number(1500000), "1.5M")

    def test_count_hours(self):
        """Test hour counting functionality"""
        analysis = TimestampActivityAnalysis()
        hours = [1, 1, 2, 3, 3, 3, 23]
        expected = [0]*24
        expected[1], expected[2], expected[3], expected[23] = 2, 1, 3, 1
        self.assertEqual(analysis.count_hours(hours), expected)

    @patch('data_loader.DataLoader')
    @patch('matplotlib.pyplot.show')
    def test_run_no_filters(self, mock_show, mock_data_loader):
        """Test main run method with no date filters"""
        mock_data_loader.return_value.get_issues.return_value = [self.sample_issue]
        analysis = TimestampActivityAnalysis()
        analysis.run()
        mock_show.assert_called_once()

    @patch('data_loader.DataLoader')
    @patch('matplotlib.pyplot.show')
    @patch('config.get_parameter')
    def test_run_with_filters(self, mock_get_parameter, mock_show, mock_data_loader):
        """Test main run method with date filters"""
        mock_data_loader.return_value.get_issues.return_value = [self.sample_issue]
        mock_get_parameter.side_effect = lambda x: '2023-01-01' if x == 'start_date' else '2023-01-31'
        analysis = TimestampActivityAnalysis()
        analysis.run()
        mock_show.assert_called_once()

    @patch('data_loader.DataLoader')
    @patch('matplotlib.pyplot.show')
    def test_run_with_null_dates(self, mock_show, mock_data_loader):
        """Test handling of issues/events with null dates"""
        mock_data_loader.return_value.get_issues.return_value = [
            self.create_mock_issue(
                created_date=None,
                updated_date=None,
                events=[self.create_mock_event(None)]
        )]
        analysis = TimestampActivityAnalysis()
        analysis.run()
        mock_show.assert_called_once()

if __name__ == '__main__':
    unittest.main()