# Hidden Markov Model Segmentation

This contains an implementation of the timeline segmentation of project activities using a Hidden Markov Model.

## Dependencies
1. __hmmlearn__ - http://hmmlearn.readthedocs.io/en/latest/
2. __joblib__ - https://pypi.python.org/pypi/joblib
3. __NumPy__ - http://www.numpy.org/
4. __Pandas__ - https://pandas.pydata.org/
5. __hdf5__ - https://support.hdfgroup.org/HDF5/

## Data
The input the the raw csv files containing the daily activity counts for different activities in a GitHub project. Since the seqience should be continuous run of days, a `NullState` is inserted in between 2 contiguous days to make a full continuous interval.

## Execution Steps
The execution is divided into following steps:

1. Preparing the data for HMM
> The raw csv files are read and converted into a numpy array of sequential project activity counts.

> ```python prepare_data_for_hmm.py --input_dir <project wise row count csv location> --output_dir <directory to store the data in hdf5 format>```

