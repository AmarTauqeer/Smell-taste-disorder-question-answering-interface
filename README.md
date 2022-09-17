# Question understanding interface for Smell or Taste Disorder

A user interface is offered in which one can choose from a list of questions. Subsequently, a sub-graph (in the environment of the question) of a knowledg graph can be displayed, or a question graph can be generated for this question.

## Technical aspects:
* Programming language: Python
* UI Framework/Graph Framework: Dash-Plotly, Bootstrap components for plotly


## How to use
1. Install the requirements using the requirements.txt file
2. Start the app.py file in the root (tested with python 3.9)
3. Open the displayed url in your webbrowser (probably http://127.0.0.1:8050/ tested with chrome and firefox)
4. Select one of the questions using the select item in the middle of the screen
   1. Use the "Open knowledge graph" button to display the subset of the knowledge graph around this question
   2. Use the "Open question graph" button for generating a question graph
      1. Using the items above the question graph it is possible to edit the question graph
5. If you have any issues, have a look on the help menu using the "?" button
