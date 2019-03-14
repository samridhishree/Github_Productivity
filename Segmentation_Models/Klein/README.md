# Kleinberg Segmentation

This folder contains an implementation of the timeline segmentation of project activities using the method from: _Kleinberg, Jon. "Bursty and hierarchical structure in streams." Data Mining and Knowledge Discovery 7.4 (2003)."_

## Dependencies
1. __R Package "Bursts"__- https://cran.rproject.org/web/packages/bursts/index.html
2. __Pandas__ - https://pandas.pydata.org/

## Data
The input consists of the raw csv files containing the daily activity counts for different activities in a GitHub project.

## Execution Steps
The execution is divided into following steps. Each step is noted with the corresponding script file. Please have a look at the file for the commandline arguments and usage:

1. __Compute the frequency of occurance of the project events__ - The raw csv files with daily activity counts are converted into their frequency of arrival from the beginning of the project (inverse of the offset of the days from the beginning of the project).
> Script : __create_offsets_from_activity.py__

2. __Segment the Timeline__ - The frequencies calculated above are modeled using an automaton.
> Script: Rscript __klein_bursts.R__ 

3. __Interpret the Burst__  - make project -> level -> [burst] pickle
> Script : __interpret_bursts.py__

4. __Format the Burst__ - From the automata state assignments predicted from the previous step, map it to daily bursts (continuous run of days with the same state)
> Script : __format_klein_bursts.py__
