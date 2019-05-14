'''
Converts the data from project combined stats to the offset format required to run the Kleinberg burst detection.
Create a pickle of dictionary {project:[offsets]}
Each offset is a tuple (data, offset from beginning)
'''

import os
import sys
import pandas as pd
from datetime import datetime
from collections import defaultdict
import cPickle as pickle
import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', help='Input directory containing project-wise daily activity counts',
         default="Sample_Data/HMM/daily_data/")
parser.add_argument('--output_dir', help='Output directory for csv files containing computed offsets each day',
         default="Sample_Data/alternate_bursts/klein/computed_offsets")
args, unknown = parser.parse_known_args()

input_dir = args.input_dir
output_dir = args.output_dir

for filename in os.listdir(input_dir):
    if '.csv' not in filename:
        continue

    print "Processing for project = ", filename
    data = pd.read_csv(os.path.join(input_dir, filename))
    days = data['period']
    days = sorted(days)
    days = list(map(lambda x: str(x), days))
    dates = list(map(lambda x: x[0:4] + "-" + x[4:6] + "-" + x[6:], days))
    dates = list(map(lambda x: datetime.strptime(x, '%Y-%m-%d'), dates))
    if len(dates) == 0: continue
    start = dates[0]
    offsets = [(str(cur.year) + '-' + str(cur.month) + '-' + str(cur.day), (cur-start).days) for cur in dates]
    project = filename.split('.csv')[0]
    output_file = os.path.join(output_dir, filename)
    w = open(output_file, 'wb')
    writer = csv.writer(w)
    writer.writerow(['project', 'date', 'offset'])
    for date, off in offsets:
        writer.writerow([project, date, off])
    w.close()
