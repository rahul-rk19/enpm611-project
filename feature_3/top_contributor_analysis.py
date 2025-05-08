import json
from collections import defaultdict
import matplotlib.pyplot as plt
import sys
import os

# Add root to import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

class TopContributorAnalysis:
    def __init__(self):
        self.data_path = config.get_parameter("DATA_FILE")

    def load_data(self):
        with open(self.data_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def run(self):
        issues = self.load_data()
        if not issues:
            print("No issues found in dataset.")
            return {}

        contributions = defaultdict(int)

        countable_events = {"commented", "closed", "labeled", "reopened"}

        for issue in issues:
            creator = issue.get("creator")
            if creator:
                contributions[creator] += 1

            for event in issue.get("events", []):
                if isinstance(event, dict):
                    author = event.get("author")
                    event_type = event.get("event_type")
                    if event_type in countable_events and author:
                        contributions[author] += 1

        if not contributions:
            print("No contributor activity found.")
            return {}

        top_contributors = dict(sorted(contributions.items(), key=lambda x: x[1], reverse=True)[:10])

        plt.figure(figsize=(12, 6))
        plt.bar(top_contributors.keys(), top_contributors.values())
        plt.xticks(rotation=45, ha='right')
        plt.title("Top Contributors (Partial Event Types Only)")
        plt.xlabel("Username")
        plt.ylabel("Total Contributions")
        plt.tight_layout()
        plt.show()

        return top_contributors
