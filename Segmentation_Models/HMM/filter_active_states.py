'''
Filters the active days of the project only
'''

import os
import sys
import csv
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--prediction_dir', help='Directory with predicted states in project timeline', default='Sample_Data/HMM/results/predictions/')
parser.add_argument('--filtered_dir', help='Output directory with filtered states', default='Sample_Data/HMM/results/filtered_states/')
args, unknown = parser.parse_known_args()

prediction_dir = args.prediction_dir
filtered_dir = args.filtered_dir
active_states = [1,2,4,5,6,7,8,9,10,15,16]

try:
    os.makedirs(filtered_dir)
except:
    pass

for filename in os.listdir(prediction_dir):
    if '.csv' not in filename:
        continue

    print "Processing for file = ", filename
    output_filename = filename.split('.csv')[0] + '_filtered.csv'
    writer = csv.writer(open(os.path.join(filtered_dir, output_filename), 'wb'))
    data = pd.read_csv(os.path.join(prediction_dir, filename))
    header = list(data.columns)
    writer.writerow(header)

    for index,row in data.iterrows():
        if int(row['State']) in active_states:
            writer.writerow(list(row))
