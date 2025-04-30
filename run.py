

"""
Starting point of the application. This module is invoked from
the command line to run the analyses.
"""

import argparse

import config
from example_analysis import ExampleAnalysis
from feature_3.top_contributor_analysis import TopContributorAnalysis

from feature_2.timestamp_activity import TimestampActivityAnalysis

from feature_1.keyword_demand import KeywordDemand


def parse_args():
    """
    Parses the command line arguments that were provided along
    with the python command. The --feature flag must be provided as
    that determines what analysis to run. Optionally, you can pass in
    a user and/or a label to run analysis focusing on specific issues.
    
    You can also add more command line arguments following the pattern
    below.
    """
    ap = argparse.ArgumentParser("run.py")
    
    # Required parameter specifying what analysis to run
    ap.add_argument('--feature', '-f', type=int, required=True,
                    help='Which of the three features to run')
    
    # Optional parameter for analyses focusing on a specific user (i.e., contributor)
    ap.add_argument('--user', '-u', type=str, required=False,
                    help='Optional parameter for analyses focusing on a specific user')
    
    # Optional parameter for analyses focusing on a specific label
    ap.add_argument('--label', '-l', type=str, required=False,
                    help='Optional parameter for analyses focusing on a specific label')
    ap.add_argument('--keyword',type=str, required=False,
                    help='Put the parameter you want facts about')
    
    ap.add_argument('--start-date', '-s', type=str, required=False,
                help='Start date for filtering (format: YYYY-MM-DD)')
    
    ap.add_argument('--end-date', '-e', type=str, required=False,
                help='End date for filtering (format: YYYY-MM-DD)')
    
    return ap.parse_args()



# Parse feature to call from command line arguments
args = parse_args()
# Add arguments to config so that they can be accessed in other parts of the application
config.overwrite_from_args(args)
    
# Run the feature specified in the --feature flag
if args.feature == 0:
    ExampleAnalysis().run()
elif args.feature == 1:
    if not args.keyword:
        print("Please enter a keyword argument")
    else:
        KeywordDemand(args.keyword).run()
elif args.feature == 2:
    TimestampActivityAnalysis().run()
elif args.feature == 3:
    TopContributorAnalysis().run()
else:
    print('Need to specify which feature to run with --feature flag.')
