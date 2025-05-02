from data_loader import DataLoader
from typing import List
import matplotlib.pyplot as plt
from collections import Counter
from model import Issue
import config

class KeywordDemand():
    def __init__(self, keyword:str = None):
        """
        Constructor that initializes the keyword to search for
        """
        if keyword is None:
            keyword = config.get_parameter("keyword")
        self.keyword = (keyword or "").lower()

    def run(self):
        """
        This is method is to run the feature
        """
        if not self.keyword:
            print("Please input the keyword as --keyword")
            return

        # Getting the issues
        issues: List[Issue] = DataLoader().get_issues()
        self.matched = []

        for issue in issues:
            title = (issue.title or "").lower()
            body = (issue.text or "").lower()

            if self.keyword in title or self.keyword in body:
                self.matched.append(issue)

        self.analyze_and_plot(self.matched)

    def analyze_and_plot(self,matched:List):
        """
        Here, the labels, comments and the timelines in which the keywords appeared will be counted and plotted
        """

        if not matched:
            print(f"No issues found mentioning '{self.keyword}'")
            return

        label_counts = Counter()
        monthly_counts = Counter()
        total_comments = 0

        for issue in matched:
            # Count comments
            comment_count = len([e for e in issue.events if e.event_type == 'comment'])
            total_comments += comment_count

            # Count labels
            for label in issue.labels:
                label_counts[label] += 1

            # Count issues per month
            if issue.created_date:
                month = issue.created_date.strftime("%Y-%m")
                monthly_counts[month] += 1

        print(f" Found {len(matched)} issues mentioning '{self.keyword}'")
        print(f"Avg. comments per issue: {total_comments / len(matched):.2f}")

        # Plot label bar chart
        if label_counts:
            labels, counts = zip(*label_counts.most_common(5))
            plt.figure()
            plt.bar(labels, counts)
            plt.title(f"Top Labels for '{self.keyword}'")
            plt.ylabel("Count")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()

        # Plot keyword timeline
        if monthly_counts:
            months = sorted(monthly_counts)
            values = [monthly_counts[m] for m in months]
            plt.figure()
            plt.plot(months, values, marker='o')
            plt.title(f"Keyword Trend: '{self.keyword}'")
            plt.xlabel("Month")
            plt.ylabel("Mentions")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
