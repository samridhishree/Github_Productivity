# Hidden Markov Model Segmentation

This contains an implementation of the timeline segmentation of project activities using a Hidden Markov Model.

## Dependencies
1. __hmmlearn__ - http://hmmlearn.readthedocs.io/en/latest/
2. __joblib__ - https://pypi.python.org/pypi/joblib
3. __NumPy__ - http://www.numpy.org/
4. __Pandas__ - https://pandas.pydata.org/
5. __hdf5__ - https://support.hdfgroup.org/HDF5/

## Data
The input consists of the raw csv files containing the daily activity counts for different activities in a GitHub project. Since the sequence should be continuous run of days, a `NullState` is inserted in between 2 contiguous days to make a full continuous interval.

## Execution Steps
The execution is divided into following steps. Each step is noted with the corresponding script file. Please have a look at the file for the commandline arguments and usage:

1. __Preparing the data for HMM__ - The raw csv files are read and converted into a numpy array of sequential project activity counts, stored in hdf5 format.
> Script : __prepare_data_for_hmm.py__

2. __Training HMM__ - Train the model using the data from above.
> Script: __train_hmm.py__ 
> 
> Script: __train_hmm_parallel.py__ (trains in parallel for different states using multiple processors for faster execution (one processor for each state))

3. __State Prediction__ - Use the trained model with the best likelihood on the validation set to predict the states for each timepoint for all projects.
> Script : __predict_hmm.py__

4. __Interpret Model__ - Interpret the model with the best likelihood to get the mean parameter values at each state in order to find the 'active' and the 'non-active' states.
>   Script : __interpret_hmm.py__

5. __Filter the Active States__ - Once the active states of the model are identified, this step filters the days of the project that are assigned any one of these active states.
> Script: __filter_active_states.py__

6. __Extract Activity Bursts__ - From the filtered, active days of the project a contiguous run of days (with a maximum gap of 3 days), are clubbed together to form a burst. 
> Script: __extract_daily_bursts.py__

