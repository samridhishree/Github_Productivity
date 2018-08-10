'''
Computes number of tt segments per burst (Klein/HMM/Max)
'''

import os
import sys
import csv
import pandas as pd
import cPickle as pickle
from datetime import datetime, date
from dateutil import relativedelta
from collections import OrderedDict
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--ref_burst_pickle', help='Reference Bursts',
                    default='Sample_Data/HMM/results/daily_bursts.pickle')
parser.add_argument('--tt_burst_dir', help='TT Segments per project',
                    default = 'Sample_Data/People_TT/tt_per_project/')
#parser.add_argument('--project_active_days_pickle', help='Pickled list of active days of project (output of create_project_active_days.py)')
parser.add_argument('--output_file', help='csv file containing number of TT segments per reference burst',
                    default='Sample_Data/People_TT/tt_segments_per_burst.csv')
args, unknown = parser.parse_known_args()

ref_burst_pickle = args.ref_burst_pickle
tt_burst_dir = args.tt_burst_dir
#project_active_days_pickle = args.project_active_days_pickle
output_file = args.output_file

ref_bursts = pickle.load(open(ref_burst_pickle, 'rb'))
projects = ref_bursts.keys()
#active_days = pickle.load(open(project_active_days_pickle, 'rb'))

# Converts a string time to date
def ConvertToDate(str_time, str_format):
    if 'NullState' in str_time:
        return str_time
    else:
        return datetime.strptime(str_time, str_format).date()

# Converts a list of string times to datetime objects
# def ConvertToDateList(str_time_list, str_format):
#     formatted = []
#     for str_time in str_time_list:
#         # For Nullstate put it as is
#         if 'NullState' in str_time:
#             formatted.append(str_time)
#         else:
#             formatted.append(ConvertToDate(str_time, str_format))
#     return formatted

# converts burst start and end points to datetime objects 
def FormatBurstIntervals(bursts):
    formatted_bursts = []
    for burst in bursts:
        parts = burst.split('-')
        start = ConvertToDate(parts[0], '%Y/%m/%d')
        end = ConvertToDate(parts[1], '%Y/%m/%d')
        formatted_bursts.append((start, end))
    return formatted_bursts

# Compute the burst day membership for all the days in project activity list
def CreateBurstDayMembership(project_bursts, project_active_days):
    project_bursts = FormatBurstIntervals(project_bursts)
    project_bursts = sorted(project_bursts)
    burst_membership = OrderedDict()
    no_burst_idx = len(project_bursts) + 1 
    previous_marker = 0
    for b_id, burst in enumerate(project_bursts):
        start = burst[0]
        end = burst[1]
        start_idx = project_active_days.index(start)
        end_idx = project_active_days.index(end)
        # Mark everything before start_idx and the last marked burst idx to no_burst_idx
        for day in project_active_days[previous_marker : start_idx]:
            burst_membership[day] = no_burst_idx
        no_burst_idx += 1
        previous_marker = end_idx+1
        # Mark within burst days with b_id
        for day in project_active_days[start_idx : end_idx+1]:
            burst_membership[day] = b_id
    # Mark the tail end of days if any
    if previous_marker < len(project_active_days):
        for day in project_active_days[previous_marker : len(project_active_days)]:
            burst_membership[day] = no_burst_idx
    return burst_membership

# def FormatTTBursts(tt_bursts):
#     new_tt = OrderedDict()
#     for k,v in tt_bursts.items():
#         format_k = ConvertToDate(k, '%Y/%m/%d')
#         new_tt[format_k] = v
#     return new_tt

w = open(output_file, 'wb')
writer = csv.writer(w)
writer.writerow(['project', 'burst_id', 'burst', 'num_days', 'num_tt_segments'])

# Compute P_k for each project
for project in projects:
    tt_file = os.path.join(tt_burst_dir, project + '_tt_segments.pickle')
    if os.path.isfile(tt_file) == False:
        continue
    project_ref_bursts = ref_bursts[project]
    if len(project_ref_bursts) == 0:
        continue
    
    print "Processing for project: ", project
    #project_active_days = active_days[project]
    #project_active_days = ConvertToDateList(project_active_days, '%Y/%m/%d')
    hyp_burst = pickle.load(open(tt_file, 'rb'))
    #hyp_burst = FormatTTBursts(hyp_burst)
    #ref_burst = CreateBurstDayMembership(project_ref_bursts, project_active_days)

    # Compute segments per burst
    for b_id, burst in enumerate(project_ref_bursts):
        parts = burst.split('-')
        cur = ConvertToDate(parts[0], '%Y/%m/%d')
        end = ConvertToDate(parts[1], '%Y/%m/%d')
        num_days = (end - cur).days + 1
        segments = set()

        while cur <= end:
            segments.add(hyp_burst[cur])
            cur += relativedelta.relativedelta(days=1)
        num_segments = len(list(segments))

        writer.writerow([project, b_id, burst, num_days, num_segments])
w.close()
    









