from datetime import datetime, time
from typing import List, Optional
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import config
from data_loader import DataLoader
from model import Issue, Event
from dateutil import tz

class TimestampActivityAnalysis:
    def __init__(self):
        """
        Constructor with date filtering and validation
        """
        try:
            # Get and validate date parameters
            self.start_date, self.end_date = self.validateDates(
                config.get_parameter('start_date'),
                config.get_parameter('end_date')
            )
        except ValueError as e:
            print(f"\nERROR: {str(e)}")
            print("Please provide dates in YYYY-MM-DD format with valid values")
            print("Example valid dates: 2023-01-15, 2024-12-31")
            raise SystemExit(1)  # Exit the program with error code

    def validateDates(self, start_date_str: Optional[str], end_date_str: Optional[str]) -> tuple:
        """Validate and parse date strings with comprehensive checks"""
        def parseDate(date_str: str) -> datetime:
            try:
                # First check the format is correct
                dt = datetime.strptime(date_str, '%Y-%m-%d')
                
                # Validate month range
                if not 1 <= dt.month <= 12:
                    raise ValueError(f"Month must be between 01-12 (got {dt.month})")
                
                # Validate day range
                if not 1 <= dt.day <= 31:
                    raise ValueError(f"Day must be between 01-31 (got {dt.day})")
                
                # Validate specific month-day combinations
                if dt.month in [4,6,9,11] and dt.day > 30:
                    raise ValueError(f"Month {dt.month} only has 30 days")
                if dt.month == 2:
                    # Simple leap year check (may not cover all edge cases)
                    leap_year = dt.year % 4 == 0 and (dt.year % 100 != 0 or dt.year % 400 == 0)
                    max_day = 29 if leap_year else 28
                    if dt.day > max_day:
                        raise ValueError(f"February {dt.year} only has {max_day} days")
                
                return dt.replace(tzinfo=tz.UTC)
            except ValueError as e:
                raise ValueError(f"Invalid date '{date_str}'. {str(e)}")

        start_date = None
        end_date = None

        if start_date_str:
            start_date = parseDate(start_date_str)
        if end_date_str:
            end_date = datetime.combine(
                parseDate(end_date_str),
                time.max
            ).replace(tzinfo=tz.UTC)

        # Validate date range if both dates exist
        if start_date and end_date and start_date > end_date:
            raise ValueError(
                f"Date range error: Start date ({start_date.date()}) "
                f"cannot be after end date ({end_date.date()})"
            )

        return start_date, end_date

    def makeTzAware(self, dt: datetime) -> datetime:
        """Ensure datetime is timezone-aware (UTC)"""
        if dt and not dt.tzinfo:
            return dt.replace(tzinfo=tz.UTC)
        return dt

    def isWithinDateRange(self, dt: datetime) -> bool:
        """Check if datetime falls within filter range"""
        if not dt:
            return False
            
        dt = self.makeTzAware(dt)
        
        if self.start_date and dt < self.start_date:
            return False
        if self.end_date and dt > self.end_date:
            return False
        return True

    def formatHeatmapNumber(self, num: int) -> str:
        """Format numbers with 1 decimal K/M (e.g. 41100 → 41.1K)"""
        if num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        if num >= 1_000:
            return f"{num/1_000:.1f}K"
        return str(num)

    def countHours(self, hour_list: List[int]) -> List[int]:
        """Count occurrences by hour"""
        counts = defaultdict(int)
        for hour in hour_list:
            counts[hour] += 1
        return [counts[h] for h in range(24)]

    def run(self):
        issues = DataLoader().get_issues()
        issue_hours, event_hours = [], []
        stats = {
            'total_issues': len(issues),
            'filtered_issues': 0,
            'total_events': sum(len(issue.events) for issue in issues),
            'filtered_events': 0
        }

        for issue in issues:
            # Check if issue should be included
            issue_in_range = True  # Default to True if no filters
            
            if self.start_date or self.end_date:
                issue_in_range = (
                    self.isWithinDateRange(issue.created_date) or 
                    self.isWithinDateRange(issue.updated_date)
                )
            
            if not issue_in_range:
                continue
                
            stats['filtered_issues'] += 1
            
            # Filter and count events
            for event in issue.events:
                if event.event_date:
                    if (not self.start_date and not self.end_date) or self.isWithinDateRange(event.event_date):
                        event_hours.append(event.event_date.hour)
                        stats['filtered_events'] += 1
            
            if issue.created_date:
                issue_hours.append(issue.created_date.hour)
            if issue.updated_date:
                issue_hours.append(issue.updated_date.hour)

        # Generate heatmap data
        issue_counts = self.countHours(issue_hours)
        event_counts = self.countHours(event_hours)

        # Create visualization
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        
        # Date range display
        date_text = []
        if self.start_date:
            date_text.append(f"Start: {self.start_date.strftime('%Y-%m-%d')}")
        if self.end_date:
            date_text.append(f"End: {self.end_date.strftime('%Y-%m-%d')}")
        
        if date_text:
            fig.text(0.5, 0.95, " | ".join(date_text), 
                    ha='center', 
                    va='center',
                    fontsize=14,
                    fontweight='bold')
        else:
            fig.text(0.5, 0.95, "No date filters applied", 
                    ha='center', 
                    va='center',
                    fontsize=14,
                    fontweight='bold')
        
        # Heatmap for Issues
        sns.heatmap(
            [issue_counts],
            annot=[[self.formatHeatmapNumber(n) for n in issue_counts]],
            fmt='',
            cmap="Blues",
            xticklabels=range(24),
            yticklabels=["Issues"],
            cbar_kws={'label': 'Count'},
            ax=ax1
        )
        ax1.set_title(f"Issue Activity ({self.formatHeatmapNumber(stats['filtered_issues'])} issues)", 
                     pad=12,
                     fontsize=12)
        ax1.set_xlabel("Hour of the Day (UTC)")
        
        # Heatmap for Events
        sns.heatmap(
            [event_counts],
            annot=[[self.formatHeatmapNumber(n) for n in event_counts]],
            fmt='',
            cmap="Reds",
            xticklabels=range(24),
            yticklabels=["Events"],
            cbar_kws={'label': 'Count'},
            ax=ax2
        )
        ax2.set_title(f"Event Activity ({self.formatHeatmapNumber(stats['filtered_events'])} events)", 
                     pad=12,
                     fontsize=12)
        ax2.set_xlabel("Hour of the Day (UTC)")
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)
        plt.show()

if __name__ == "__main__":
    TimestampActivityAnalysis().run()
    