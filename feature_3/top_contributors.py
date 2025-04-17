import json
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
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
            return

        contributions = defaultdict(int)

        for issue in issues:
            # Count issue creators
            creator = issue.get("creator")
            if creator:
                contributions[creator] += 1

            # Count events
            for event in issue.get("events", []):
                author = event.get("author")
                if event.get("event_type") in {"commented", "closed"} and author:
                    contributions[author] += 1

        if not contributions:
            print("No contributor activity found.")
            return

        top_contributors = dict(sorted(contributions.items(), key=lambda x: x[1], reverse=True)[:10])

        plt.figure(figsize=(12, 6))
        plt.bar(top_contributors.keys(), top_contributors.values())
        plt.xticks(rotation=45, ha='right')
        plt.title("Top Contributors (Issues + Comments + Closures)")
        plt.xlabel("Username")
        plt.ylabel("Total Contributions")
        plt.tight_layout()
        plt.show()
