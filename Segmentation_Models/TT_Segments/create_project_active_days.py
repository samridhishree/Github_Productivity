'''
From the non-nullstate daily activity file create a list of active days of a project
Pickled dictionary has the format: {project:[list of active days]}
NullState dates are numbered in sequential order
'''

import os
import sys
import pandas as pd
import csv
import cPickle as pickle
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--daily_activity_dir', help='Directory containing daily activity counts per project',
              default="Sample_Data/HMM/daily_data/")
parser.add_argument('--output_file', help='Pickled dictionary of the format: {project:[list of active days]}',
              default="Sample_Data/alternate_bursts/tt/active_days.pickle")
args, unknown = parser.parse_known_args()

daily_activity_dir = args.daily_activity_dir
output_file = args.output_file
final_dict = {}

if not os.path.exists(os.path.dirname(output_file)):
    os.makedirs(os.path.dirname(output_file))

def FormatDates(dates_list):
    null_num = 0
    formatted = []
    for date in dates_list:
        if 'NullState' in date:
            formatted.append(date + str(null_num))
            null_num += 1
        else:
            formatted.append(date[0:4] + "/" + date[4:6] + "/" + date[6:8])
    return formatted

for filename in os.listdir(daily_activity_dir):
    daily_data_file = os.path.join(daily_activity_dir, filename)
    project = filename.split('.csv')[0]
    print "Processing for project = ", project
    daily_data = pd.read_csv(daily_data_file)
    dates = list(daily_data['period'])
    dates = list(map(lambda x: str(x), dates))
    dates = FormatDates(dates)
    final_dict[project] = dates
   
with open(output_file, 'wb') as p_pickle:
    pickle.dump(final_dict, p_pickle)
