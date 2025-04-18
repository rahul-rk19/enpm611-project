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
        Constructor with date filtering for both issues and events
        """
        # Get date parameters from config
        self.start_date: Optional[datetime] = None
        self.end_date: Optional[datetime] = None
        
        if start_date_str := config.get_parameter('start_date'):
            self.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').replace(
                tzinfo=tz.UTC
            )
        if end_date_str := config.get_parameter('end_date'):
            # Set end date to end of day (23:59:59) in UTC
            self.end_date = datetime.combine(
                datetime.strptime(end_date_str, '%Y-%m-%d'),
                time.max
            ).replace(tzinfo=tz.UTC)

    def make_tz_aware(self, dt: datetime) -> datetime:
        """Ensure datetime is timezone-aware (UTC)"""
        if dt and not dt.tzinfo:
            return dt.replace(tzinfo=tz.UTC)
        return dt

    def is_within_date_range(self, dt: datetime) -> bool:
        """Check if datetime falls within filter range"""
        if not dt:
            return False
            
        dt = self.make_tz_aware(dt)
        
        # Only check start date if it exists
        if self.start_date and dt < self.start_date:
            return False
        # Only check end date if it exists
        if self.end_date and dt > self.end_date:
            return False
        return True

    def format_heatmap_number(self, num: int) -> str:
        """Format numbers with 1 decimal K/M (e.g. 41100 → 41.1K)"""
        if num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        if num >= 1_000:
            return f"{num/1_000:.1f}K"
        return str(num)

    def count_hours(self, hour_list: List[int]) -> List[int]:
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
            # Check if issue should be included (either created or updated in range)
            issue_in_range = True  # Default to True if no filters
            
            # Only apply filters if at least one date is specified
            if self.start_date or self.end_date:
                issue_in_range = (
                    self.is_within_date_range(issue.created_date) or 
                    self.is_within_date_range(issue.updated_date)
                )
            
            if not issue_in_range:
                continue
                
            stats['filtered_issues'] += 1
            
            # Filter and count events (only if date filters exist)
            for event in issue.events:
                if event.event_date:
                    if (not self.start_date and not self.end_date) or self.is_within_date_range(event.event_date):
                        event_hours.append(event.event_date.hour)
                        stats['filtered_events'] += 1
            
            # Include issue timestamps
            if issue.created_date:
                issue_hours.append(issue.created_date.hour)
            if issue.updated_date:
                issue_hours.append(issue.updated_date.hour)

        # Generate heatmap data
        issue_counts = self.count_hours(issue_hours)
        event_counts = self.count_hours(event_hours)

        # Create the visualization
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        
        # Create date range text
        date_text = []
        if self.start_date:
            date_text.append(f"Start: {self.start_date.strftime('%Y-%m-%d')}")
        if self.end_date:
            date_text.append(f"End: {self.end_date.strftime('%Y-%m-%d')}")
        
        # Add date range as text above heatmaps
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
            annot=[[self.format_heatmap_number(n) for n in issue_counts]],
            fmt='',
            cmap="Blues",
            xticklabels=range(24),
            yticklabels=["Issues"],
            cbar_kws={'label': 'Count'},
            ax=ax1
        )
        ax1.set_title(f"Issue Activity ({self.format_heatmap_number(stats['filtered_issues'])} issues)", 
                     pad=12,
                     fontsize=12)
        ax1.set_xlabel("Hour of the Day (UTC)")
        
        # Heatmap for Events
        sns.heatmap(
            [event_counts],
            annot=[[self.format_heatmap_number(n) for n in event_counts]],
            fmt='',
            cmap="Reds",
            xticklabels=range(24),
            yticklabels=["Events"],
            cbar_kws={'label': 'Count'},
            ax=ax2
        )
        ax2.set_title(f"Event Activity ({self.format_heatmap_number(stats['filtered_events'])} events)", 
                     pad=12,
                     fontsize=12)
        ax2.set_xlabel("Hour of the Day (UTC)")
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.85) 
        plt.show()

if __name__ == "__main__":
    TimestampActivityAnalysis().run()