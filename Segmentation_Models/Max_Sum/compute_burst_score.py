'''
Computes the burst score per interval for each project and pickles the dict = {project:[burst_scores]}.
The score are calculated as explained in the paper: Lappas, Theodoros, et al. "On Burstiness-Aware Search for Document Sequences"
'''

import os
import sys
import csv
import pandas as pd
import cPickle as pickle
from collections import defaultdict
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', help='Input directory containing project-wise daily activity counts')
parser.add_argument('--output_file', help='Output filename for the pickled dictionary {project:[score_list]}')
args, unknown = parser.parse_known_args()

input_dir = args.input_dir
output_file = args.output_file
final_dict = defaultdict(list)


for filename in os.listdir(input_dir):
    if '.csv' not in filename:
        continue

    print "Processing for file = ", filename
    project_name = filename.split('.csv')[0]
    activity_sum = []
    reader = csv.reader(open(os.path.join(input_dir, filename)))
    reader.next()
    for row in reader:
        acts = row[2:]
        acts = [int(x) if x != "nan" else 0 for x in acts]
        total_acts = sum(acts)
        activity_sum.append(total_acts)

    # Compute the burst scores for the project
    total_project_activity = float(sum(activity_sum))
    for act in activity_sum:
        score = (act/total_project_activity) - (1./float(len(activity_sum)))
        final_dict[project_name].append(score)

with open(output_file, 'wb') as p_pickle:
    pickle.dump(final_dict, p_pickle)
