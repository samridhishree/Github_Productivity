# Text Tiling

This folder contains an implementation of the timeline segmentation using the TextTiling approach from: _Hearst, Marti A. "TextTiling: Segmenting text into multi-paragraph subtopic passages."_

## Dependencies
1. __NLTK__- http://www.nltk.org/
2. __Pandas__ - https://pandas.pydata.org/
3. __sklearn__ - http://scikit-learn.org/stable/

## Data
Following are the inputs needed:
1. __Project Daily Activity__ - In order to get all the active days of a project.
2. __Project Issues__ - All the issues and Pull Requests associated with the project (title, actor, conversations and action)
3. __Project Commits__ - Al the commits associated with the project (title, actor, comments, action, files).

## Execution Steps
The execution is divided into following steps. Each step is noted with the corresponding script file. Please have a look at the file for the commandline arguments and usage:

1. __Active Days Helper Pickle__ - Creates a list of active days of a project.
> Script : __create_project_active_days.py__

2. __Combine Issue and Commit Text__ - Combines the text (comments and titles) from the project issues and commits.
> Script: __combine_issue_comments.py__ 

3. __Predict TextTiled Segements__ - Creates TT segments by comparing the word vector representations of all the words that occur as comments, issue titles or commit messages of each consecutive day.
> Script : __create_tt_segments.py__
4. __Count Number of TT Segments per Burst__ - Count the number of TT segments contained in one burst of a non-lexical segmentation model (Klein/Max-Sum/HMM).
> Script : __num_tt_segments_per_burst.py__