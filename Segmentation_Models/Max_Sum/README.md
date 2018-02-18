# Maximal Sum Segments Segmentation

This folder contains an implementation of the timeline segmentation of project activities using the method from: _Lappas, Theodoros, et al. "On burstiness-aware search for document sequences."_

## Dependencies
1. __Pandas__ - https://pandas.pydata.org/

## Data
The input consists of the raw csv files containing the daily activity counts for different activities in a GitHub project. Since the sequence should be continuous run of days, a `NullState` is inserted in between 2 contiguous days to make a full continuous interval.

## Execution Steps
The execution is divided into following steps. Each step is noted with the corresponding script file. Please have a look at the file for the commandline arguments and usage:

1. __Computing Burst Scores for the Projects__ - The raw csv files with daily activity counts are read with the activities summed for each day. Burst score for each day in the timeline is then calculated.
> Script : __compute_burst_score.py__

2. __Find Maximal Sum Segemnts__ - Given the burst scores for each day, finds the intervals of days that maximize the overall burst score.
> Script: __maximal_bursts.py__ 

3. __Format the Burst__ - The maximal intervals found by the previous step, are mapped to actual timeline date objects for consistent burst representation across all three methods.
> Script : __interpret_bursts.py__
