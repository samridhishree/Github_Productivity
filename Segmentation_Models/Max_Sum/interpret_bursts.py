'''
Convert the bursts score offsets computed by the maximal sum algorithm to actual date outputs

Input: burst_pickle, daily_data_pickle.
Output: Pickled dictionary containing interpretable bursts.
'''

import os
import sys
import csv
import cPickle as pickle
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--burst_pickle', help='The pickled file containing project maximal bursts',
           default="Sample_Data/alternate_bursts/max_sum/max_sum_segments.pickle")
parser.add_argument('--daily_data_dir', help='Directory with project daily counts',
           default="Sample_Data/HMM/daily_data/")
parser.add_argument('--output_file', help='Output filename for the reformatted bursts',
           default="Sample_Data/alternate_bursts/max_sum/reformatted_bursts.pickle")
args, unknown = parser.parse_known_args()

burst_pickle = args.burst_pickle
daily_data_dir = args.daily_data_dir
output_file = args.output_file
maximal_bursts = pickle.load(open(burst_pickle, 'rb'))
projects = maximal_bursts.keys()
final_dict = {}

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

for project in projects:
    data_file = os.path.join(daily_data_dir, project + '.csv')
    if os.path.isfile(data_file) == False:
        continue

    print "Processing for project: ", project
    project_data = pd.read_csv(data_file)
    periods = list(project_data['period'])
    days = list(map(lambda x: str(x), periods))
    dates = FormatDates(days)
    project_bursts_idx = maximal_bursts[project]
    bursts = [dates[start_idx] + '-' + dates[end_idx] for (start_idx, end_idx) in project_bursts_idx]
    final_dict[project] = bursts

with open(output_file, 'wb') as p_pickle:
    pickle.dump(final_dict, p_pickle)



