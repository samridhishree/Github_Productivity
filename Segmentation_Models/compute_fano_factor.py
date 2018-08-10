'''
Computes the fano factor of daily acitivites = variance/mean
'''

import os
import sys
import csv
import pandas as pd
import cPickle as pickle
from collections import defaultdict
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', help='Folder containing daily stats for project with nullstates for dummy days', 
                default='Sample_Data/HMM/daily_data_with_nullstate/')
parser.add_argument('--output_file', help='Path for the output pickle containing fano factor per project', 
                default='Sample_Data/HMM/results/fano_factor_per_project.pickle')

args, unknown = parser.parse_known_args()
input_dir = args.input_dir
output_file = args.output_file
final_dict = defaultdict(int)


for filename in os.listdir(input_dir):
    if '.csv' not in filename:
        continue

    print "Processing for file = ", filename
    project_name = filename.strip('.csv')
    activity_sum = []
    reader = csv.reader(open(os.path.join(input_dir, filename)))
    reader.next()
    for row in reader:
        acts = row[2:]
        acts = [int(x) if x != "nan" else 0 for x in acts]
        total_acts = sum(acts)
        activity_sum.append(total_acts)

    # Compute the fano scores for the project
    score = np.var(activity_sum)/np.mean(activity_sum)
    final_dict[project_name] = score

with open(output_file, 'wb') as p_pickle:
    pickle.dump(final_dict, p_pickle)
