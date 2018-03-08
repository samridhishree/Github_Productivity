'''
Converts the project-wise data (with NullState) to data matrix for HMM. Also creates the length matrix
Data Matrix = n_sequenceXnum_features
Length = lengths of the sequences
'''

import os
import sys
import h5py
import pandas as pd
import numpy as np
from collections import defaultdict
import argparse

# Day HMM activity traces
focus_var = ['git_commits', 'gha_pr_merge', 'gha_pushes', \
            'gha_issue_comments' , 'gha_commit_comments', \
            'nml_pull_request_title', 'issues_opened', 'issues_closed']

def CreateDataLengthMatrix(project_list, input_dir, is_train, compressed_file):
    data_collection = defaultdict(list)
    lengths = []

    # Collect the sequences for each of these focus variables across the projects.
    for project in project_list:
        if '.csv' not in project:
            continue
        print "Processing the data for project = ", project
        data = pd.read_csv(os.path.join(input_dir, project))
        lengths.append(data.shape[0])
        for var in focus_var:
            seq=list(data[var].values)
            data_collection[var].append(seq)

    # Concatenate each list of sequences for each of the focus var from the collection dictionary
    data_seq=[]
    for var in focus_var:
        data_seq.append(np.concatenate(data_collection[var]))

    # Stack the columns (each column - one focus var) of the train_seq list to create the data matrix - n_sequences X features
    final_data_seq=np.column_stack(data_seq)

    print "len(lengths) = ", len(lengths)
    print "Total Length = ", sum(lengths)
    print "final_data_seq.shape = ", final_data_seq.shape

    if is_train:
        train_group=compressed_file.create_group("train")
        train_set=train_group.create_dataset("traindata",data=final_data_seq)
        train_len=train_group.create_dataset("trainlengths",data=lengths)
    else:
        test_group=compressed_file.create_group("test")
        test_set=test_group.create_dataset("testdata",data=final_data_seq)
        test_len=test_group.create_dataset("testlengths",data=lengths)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', \
                        help='Directory containing daily activity counts (with nullstates inserted in non active days)',\
                        default='data/daily_data_nullstate/')
    parser.add_argument('--output_dir',\
                        help='Directory to store the data in hdf5 format', \
                        default='data/')
    args, unknown = parser.parse_known_args()

    projects = os.listdir(args.input_dir)
    np.random.shuffle(projects)

    # Get the training-testing split (80-20)
    train_last_index = int(len(projects) * 0.8)
    train_project_list = projects[:train_last_index]
    test_project_list = projects[train_last_index:]

    # Output compressed file
    f = h5py.File(os.path.join(args.output_dir, "hmm_data.hdf5"),"w")

    # Create training data
    print "Creating Training Data"
    CreateDataLengthMatrix(train_project_list, args.input_dir, True, f)

    #Create Test Data
    print "Creating Test Data"
    CreateDataLengthMatrix(test_project_list, args.input_dir, False, f)

    f.close()






