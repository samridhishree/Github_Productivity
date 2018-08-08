'''
Interpret the trained HMM model. Loads the transiton probabilities and mean and the variances of the states estimated and stores it in a csv.
'''

import os
import sys  
import csv
import joblib
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--model_dir', help='The trained models directory', default='Sample_Data/HMM/results/GaussianHMMdiag/')
parser.add_argument('--output_dir', help='Interpreted csv output folder', default='Sample_Data/HMM/results/model_interpretations/')
args, unknown = parser.parse_known_args()


model_dir = args.model_dir
output_dir = args.output_dir

focus_vars = ['commit_messages', 'pull_request_merged',
           'issue_comment', 'commit_comments', 'issue_title', 'issue_closed',
           'pull_request_title', 'pull_request_commit_comment',
           'pull_request_commit']

try:
    os.makedirs(output_dir)
except:
    pass

    
for model_file in os.listdir(model_dir):

    # Load the model
    nstates = int(model_file[:2])
    print "Processing for nstates = ", nstates
    model = joblib.load(os.path.join(model_dir, model_file))
    output_file = os.path.join(output_dir, model_file + '_stats.csv')
    f = open(output_file, 'wb')
    writer = csv.writer(f)

    # Write the priors of the states
    writer.writerow([])
    writer.writerow(['Value']+range(nstates))
    writer.writerow(['Start Probs']+model.startprob_.tolist())

    #Write the state means. model.means_ shape = (n_states X n_features)
    writer.writerow([])
    writer.writerow(['Means']+range(nstates))
    for i in range(len(focus_vars)):
        row_means=[]
        for j in range(nstates):
            row_means.append(model.means_[j,i])
        writer.writerow([focus_vars[i]]+row_means)

    # Write the state variances. model.covars_ shape = (n_states X n_features)
    writer.writerow([])
    writer.writerow(['Variances']+range(nstates))
    for i in range(len(focus_vars)):
        row_vars=[]
        for j in range(nstates):
            row_vars.append(model.covars_[j,i, i])
        writer.writerow([focus_vars[i]]+row_vars)

    # Write the transition probabilities. model.transmat_ shape = (n_states X n_states)
    writer.writerow([])
    writer.writerow(['Transition Probabilities'])
    writer.writerow(['\t']+range(nstates))

    for i in range(nstates):
        row=[i]
        for j in range(nstates):
            row.append(model.transmat_[i,j])
        writer.writerow(row)

    f.close()



