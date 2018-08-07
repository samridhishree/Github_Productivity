'''
Computes pairwise P_k scores for the three burst segregation types
'''

import os
import sys
import csv
import pandas as pd
import cPickle as pickle
from datetime import datetime, date
import math
from collections import OrderedDict
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--ref_burst_pickle', help='Pickled dictionary for model 1 burst')
parser.add_argument('--hyp_burst_pickle', help='Pickled dictionary for model 2 burst')
parser.add_argument('--project_active_days_pickle', help='Pickled dictionary of the format: {project:[list of active days]}')
parser.add_argument('--output_file', help='Output csv file containing pairwise average pk values')
args, unknown = parser.parse_known_args()

ref_burst_pickle = args.ref_burst_pickle
hyp_burst_pickle = args.hyp_burst_pickle
project_active_days_pickle = args.project_active_days
output_file = args.output_file

ref_bursts = pickle.load(open(ref_burst_pickle, 'rb'))
hyp_bursts = pickle.load(open(hyp_burst_pickle, 'rb'))
active_days = pickle.load(open(project_active_days_pickle, 'rb'))
projects = ref_bursts.keys()

# converts burst start and end points to datetime objects 
def FormatBurstIntervals(bursts):
    formatted_bursts = []
    for burst in bursts:
        parts = burst.split('-')
        start = ConvertToDate(parts[0], '%Y/%m/%d')
        end = ConvertToDate(parts[1], '%Y/%m/%d')
        formatted_bursts.append((start, end))
    return formatted_bursts

# Converts a string time to date
def ConvertToDate(str_time, str_format):
    if 'NullState' in str_time:
        return str_time
    else:
        return datetime.strptime(str_time, str_format).date()

# Converts a list of string times to datetime objects
def ConvertToDateList(str_time_list, str_format):
    formatted = []
    for str_time in str_time_list:
        # For Nullstate put it as is
        if 'NullState' in str_time:
            formatted.append(str_time)
        else:
            formatted.append(ConvertToDate(str_time, str_format))
    return formatted

# Compute the burst day membership for all the days in project activity list
def CreateBurstDayMembership(project_bursts, project_active_days):
    project_bursts = sorted(project_bursts)
    project_bursts = FormatBurstIntervals(project_bursts)
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

def ComputePk(ref_burst, hyp_burst, project_active_days, avg_len):
    k = int(max(math.ceil(0.5 * avg_len), 1))
    n = len(project_active_days)
    # Compute pk
    okay = 0
    fa = 0  # False Alarm
    miss = 0
    i = 0
    end_mark = k
    # print "n = ", n
    # print "k = ", k
    # print "avg_len = ", avg_len
    while (i+end_mark) < n:
        d1 = project_active_days[i]
        d2 = project_active_days[i+end_mark]
        d_ref = ref_burst[d1] == ref_burst[d2]
        d_hyp = hyp_burst[d1] == hyp_burst[d2]   
        if d_ref == d_hyp:
            okay += 1
        elif d_ref == True:
            fa += 1
        else:
            miss += 1
        i += 1
        end_mark += 1
    den = float(miss + fa + okay)
    if den == 0.0:
        return nan
    pk = (miss + fa)/den
    return pk



w = open(output_file, 'wb')
writer = csv.writer(w)
writer.writerow(['project', 'p_k'])

# Compute P_k for each project
for project in projects:
    if project not in hyp_burst:
        continue
    print "Computing pk values for the project = ", project
    # Get the active days
    project_active_days = active_days[project]
    project_active_days = ConvertToDateList(project_active_days, '%Y/%m/%d')

    # Get the burst memberships
    hyp_burst = hyp_bursts[project]
    project_ref_bursts = ref_bursts[project]
    
    if len(project_ref_bursts) == 0 or len(hyp_burst) == 0:
        writer.writerow([project, 1.0, 1.0, 1.0])
        continue

    ref_burst = CreateBurstDayMembership(project_ref_bursts, project_active_days)
    hyp_burst = CreateBurstDayMembership(hyp_burst, project_active_days)

    # Direction 1 pk
    segments = list(set(ref_burst.values()))
    avg_len = len(ref_burst)/float(len(segments))
    print "Direction 1 pk, avg_len = ", avg_len
    pk1 = ComputePk(ref_burst, hyp_burst, project_active_days, avg_len)

    #Direction 2 pk
    segments = list(set(hyp_burst.values()))
    avg_len = len(hyp_burst)/float(len(segments))
    print "Direction 2 pk, avg_len = ", avg_len
    pk2 = ComputePk(ref_burst, hyp_burst, project_active_days, avg_len)

    #Average pk
    pk = (pk1+pk2)/2.0
    writer.writerow([project, pk])
w.close()
print "length of projects = ", len(projects)










