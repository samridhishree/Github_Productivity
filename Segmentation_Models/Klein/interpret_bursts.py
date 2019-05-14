'''
Interpret the bursts assigned by the Kleinberg algorithm.
Assigns to each timestamp the highest automate state assigned and then find contiguous intervals for those.
'''
import os
import sys
import pandas as pd
from collections import defaultdict
import cPickle as pickle
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--klein_burst_dir', help='Directory with the csv files containing the computed automata state assignments',
             default="Sample_Data/alternate_bursts/klein/burst_output")
parser.add_argument('--offsets_dir', help='Directory containing computed offsets for each day to map them back to actual dates',
             default="Sample_Data/alternate_bursts/klein/computed_offsets/")
parser.add_argument('--output_file', help='Output pickle storing the directory {project:{level:[bursts]}}',
             default="Sample_Data/alternate_bursts/klein/level_bursts.pickle")
args, unknown = parser.parse_known_args()

klein_burst_dir = args.klein_burst_dir
offsets_dir = args.offsets_dir
output_file = args.output_file

final_dict = {}
for ix, filename in enumerate(os.listdir(klein_burst_dir)):
    if '.csv' not in filename:
        continue

    print "Processing for project ", ix, ":", filename
    project = filename.split('.csv')[0]

    # Enumerate the states' ranges
    level_range = {}
    data = pd.read_csv(os.path.join(klein_burst_dir, filename))
    for idx,row in data.iterrows():
        level_range[row['level']] = (row['start'], row['end'])

    # Get the list of offsets
    offset_data = pd.read_csv(os.path.join(offsets_dir, filename))
    offsets = list(offset_data['offset'])
    offset_date_dict = {}
    for idx,row in offset_data.iterrows():
        offset_date_dict[row['offset']] = row['date']



    # Get the state assignments
    levels = level_range.keys()
    levels = sorted(levels, reverse=True)
    assn = {}
    for level in levels:
        off_range = level_range[level]
        valid_offsets = [x for x in offsets if ((x >= off_range[0]) and (x <= off_range[1]))]
        for off in valid_offsets:
            if off not in assn:
                assn[off] = level


    # Find the bursts with their intensities (state assignments)
    bursts = defaultdict(list)
    offsets = sorted(offsets)
    label = assn[offsets[0]]
    cur_list = []
    for cur_offset in offsets:
        if label == assn[cur_offset]:
            cur_list.append(cur_offset)
        else:
            label = assn[cur_offset]
            if len(cur_list) > 0:
                bursts[label].append((min(cur_list), max(cur_list)))
            cur_list = []
            cur_list.append(cur_offset)

    # Corner case of only 1 level of burst
    if len(bursts) == 0 and len(cur_list) > 0:
        bursts[label].append((min(cur_list), max(cur_list)))

    # Match the offsets with the dates to find the actual bursts
    for level in bursts:
        burst_tuples = bursts[level]
        burst_tuples = [(offset_date_dict[start], offset_date_dict[end]) for (start,end) in burst_tuples]
        bursts[level] = burst_tuples

    final_dict[project] = bursts

with open(output_file, 'wb') as p_pickle:
    pickle.dump(final_dict, p_pickle)


    





