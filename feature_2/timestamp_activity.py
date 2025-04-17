import json
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import config
from datetime import datetime
from typing import List, Dict

from data_loader import DataLoader
from model import Issue, Event


class TimestampActivityAnalysis:
    def __init__(self):
        pass

    def count_hours(self, hour_list):
        counts = defaultdict(int)
        for hour in hour_list:
            counts[hour] += 1
        return [counts[h] for h in range(24)]
    
    def format_number(self, num):
        """Convert large numbers to readable format (1.5k, 2.3M, etc.)"""
        if num >= 1_000_000:
            return f'{num/1_000_000:.1f}M'
        if num >= 1_000:
            return f'{num/1_000:.1f}k'
        return str(num)
        
    def run(self):
        issues: List[Issue] = DataLoader().get_issues()
        
        # Separate issue and event timestamps
        issue_hours = []
        event_hours = []

        for issue in issues:
            # 1. Extract issue timestamps (created & updated)
            if issue.created_date:
                issue_hours.append(issue.created_date.hour)
            if issue.updated_date:
                issue_hours.append(issue.updated_date.hour)
            
            # 2. Extract event timestamps
            for event in issue.events:
                if event.event_date:
                    event_hours.append(event.event_date.hour)
                
        issue_counts = self.count_hours(issue_hours)
        event_counts = self.count_hours(event_hours)
        
        # Format numbers for display
        formatted_issue_counts = [[self.format_number(num) for num in issue_counts]]
        formatted_event_counts = [[self.format_number(num) for num in event_counts]]
        
        # Plot side-by-side heatmaps
        plt.figure(figsize=(18, 6))
        
        # Heatmap for Issues
        plt.subplot(1, 2, 1)
        sns.heatmap(
            [issue_counts],  # Use original values for color mapping
            annot=formatted_issue_counts,  # Use formatted values for display
            fmt='',  # Empty fmt since we pre-formatted
            cmap="Blues",
            xticklabels=range(24),
            yticklabels=["Issues"],
            cbar_kws={'label': 'Count'}
        )
        plt.title("Issue Activity (Created/Updated)")
        plt.xlabel("Hour of the Day (UTC)")
        
        # Heatmap for Events
        plt.subplot(1, 2, 2)
        sns.heatmap(
            [event_counts],  # Use original values for color mapping
            annot=formatted_event_counts,  # Use formatted values for display
            fmt='',
            cmap="Reds",
            xticklabels=range(24),
            yticklabels=["Events"],
            cbar_kws={'label': 'Count'}
        )
        plt.title("Event Activity (Comments/Labels/Closures)")
        plt.xlabel("Hour of the Day (UTC)")
        
        plt.tight_layout()
        plt.show()

            
# Example usage
if __name__ == "__main__":
    analysis = TimestampActivityAnalysis()
    analysis.run()