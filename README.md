# ENPM611 Project Application Template

This is the template for the ENPM611 class project. Use this template in conjunction with the provided data to implement an application that analyzes GitHub issues for the [poetry](https://github.com/python-poetry/poetry/issues) Open Source project and generates interesting insights.

This application template implements some of the basic functions:

- `data_loader.py`: Utility to load the issues from the provided data file and returns the issues in a runtime data structure (e.g., objects)
- `model.py`: Implements the data model into which the data file is loaded. The data can then be accessed by accessing the fields of objects.
- `config.py`: Supports configuring the application via the `config.json` file. You can add other configuration paramters to the `config.json` file.
- `run.py`: This is the module that will be invoked to run your application. Based on the `--feature` command line parameter, one of the three analyses you implemented will be run. You need to extend this module to call other analyses.

With the utility functions provided, you should focus on implementing creative analyses that generate intersting and insightful insights.

In addition to the utility functions, an example analysis has also been implemented in `example_analysis.py`. It illustrates how to use the provided utility functions and how to produce output.

## Setup

To get started, your team should create a fork of this repository. Then, every team member should clone your repository to their local computer. 


### Install dependencies

In the root directory of the application, create a virtual environment, activate that environment, and install the dependencies like so:

```
pip install -r requirements.txt
```

### Download and configure the data file

Download the data file (in `json` format) from the project assignment in Canvas and update the `config.json` with the path to the file. Note, you can also specify an environment variable by the same name as the config setting (`ENPM611_PROJECT_DATA_PATH`) to avoid committing your personal path to the repository.


### Run an analysis

With everything set up, you should be able to run the existing example analysis:

```
python run.py --feature 0
```

That will output basic information about the issues to the command line.


## VSCode run configuration

To make the application easier to debug, runtime configurations are provided to run each of the analyses you are implementing. When you click on the run button in the left-hand side toolbar, you can select to run one of the three analyses or run the file you are currently viewing. That makes debugging a little easier. This run configuration is specified in the `.vscode/launch.json` if you want to modify it.

The `.vscode/settings.json` also customizes the VSCode user interface sligthly to make navigation and debugging easier. But that is a matter of preference and can be turned off by removing the appropriate settings.

# Milestone 2

Modified requirements.txt file. Added Seaborn Library.

## Feature 1

This feature analyzes how frequently a specific keyword appears in GitHub issues. It searches the keyword in both issue titles and descriptions, then analyzes related labels, comment activity, and the monthly trend of mentions. The output includes a bar chart of the top 5 associated labels and a line chart showing keyword usage over time. Line chart will be shown after the bar chart is closed.

1. **To generate the barchart, run the following command**:
   
    ```sh
    python run.py --feature 1 --keyword <keyword>

## Feature 2

This feature visualizes when GitHub issues and events are most active throughout the day. It analyzes the hourly distribution of issue creation, updates, and related events, with optional filtering based on start and end dates from the configuration. The output consists of two side-by-side heatmaps: one for issue activity and one for event activity, both showing counts per hour in UTC. This helps reveal peak activity periods within the project’s lifecycle.

Note: The total issues displayed above the graph may not match the sum of the graph data, as both creation and update timestamps are considered.

1. **To generate the heatmaps, run the following command**:
   
    ```sh
    python run.py --feature 2
    
2. **You can also provide optional date filters**:

    ```sh
    python run.py --feature 2 --start-date 2024-05-20 --end-date 2024-05-25    

## Feature 3

Top Contributor Analysis identifies and visualizes the most active contributors in the GitHub issue dataset. It calculates a total activity score for each user based on event type. The system parses the JSON file to extract contributors from the creator field of issues and the author fields in comments and events. The top 10 contributors, ranked by their overall activity, are displayed in a bar chart with usernames on the x-axis and contribution counts on the y-axis.


1. **To generate the chart, run the following command**:
   
     ```sh
    python3 run.py --feature 3
