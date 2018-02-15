'''
Uses the trained model to predict the sates for the timeline of the projects.
Since the projects are shuffled during training, the feature matrices for each project is re-created and the prediction is made.
'''

import os
import sys
import csv
import h5py
import numpy as np
import pandas as pd
import joblib
import warnings
from collections import defaultdict
from hmmlearn import hmm
import argparse

# To remove the deprecation warnings
warnings.filterwarnings('ignore',category=DeprecationWarning)

parser = argparse.ArgumentParser()
parser.add_argument('--project_data_dir', help='Directory with the daily activity counts of each project')
parser.add_argument('--model_dir', help='Directory that stores the trained models on different #states')
parser.add_argument('--output_dir', default='Directory to store state predictions for each project')
parser.add_argument('--nstates', default='number of states HMM model to use')
args, unknown = parser.parse_known_args()

project_data_dir = args.project_data_dir
model_dir = args.model_dir
output_dir = args.output_dir
nstates = int(args.nstates)
focus_var = ['git_commits', 'gha_pr_merge', 'gha_pushes', \
            'gha_issue_comments' , 'gha_commit_comments', \
            'nml_pull_request_title', 'issues_opened', 'issues_closed']

# Load the model - model is saved in this format from train_hmm
model_filename = str(nstates) + 'states'
model = joblib.load(os.path.join(model_dir, model_filename))

# Create data matrix for each project data and make predictions for it
for filename in os.listdir(project_data_dir):
    if '.csv' not in filename:
        continue

    print "Processing for the project data file = ", filename
    data_collection = defaultdict(list)
    lengths = []
    data = pd.read_csv(os.path.join(project_data_dir, filename))
    lengths.append(data.shape[0])
    for var in focus_var:
        seq=list(data[var].values)
        data_collection[var].append(seq)

    data_seq=[]
    for var in focus_var:
        data_seq.append(np.concatenate(data_collection[var]))
    final_data_seq=np.column_stack(data_seq)
    predictions = model.predict(final_data_seq)

    data['State'] = pd.Series(predictions, index=data.index)
    output_file = filename.replace('.csv', '_with_state.csv')
    data.to_csv(os.path.join(output_dir, output_file))












