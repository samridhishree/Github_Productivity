
# coding: utf-8

# In[41]:


import os
import sys
import csv
import pandas as pd
import cPickle as pickle
from datetime import datetime, date
from collections import OrderedDict, defaultdict
from dateutil import relativedelta
import argparse
csv.field_size_limit(sys.maxsize)


parser = argparse.ArgumentParser()
parser.add_argument('--ref_burst_pickle', help='Pickle file contianing the project bursts', 
                default='Sample_Data/HMM/results/daily_bursts.pickle')
parser.add_argument('--tt_burst_dir', help='Dictionary for pickled dictionary for TT membership per project', 
                default='Sample_Data/People_TT/tt_per_project/')
parser.add_argument('--output_file', help='csv file containing number of TT segments per reference burst',
                    default='Sample_Data/People_TT/sub_bursts_from_tt_segments.pickle')


# In[42]:


ref_burst_pickle = args.ref_burst_pickle
tt_burst_dir = args.tt_burst_dir
output_file = args.output_file


# In[43]:


# Converts a list of string times to datetime objects, taking care of nullstates in between
def CreateDaySeries(str_time_list):
    null_num = 0
    formatted = []
    for str_time in str_time_list:
        # For Nullstate put it as is
        if 'NullState' in str_time:
            formatted.append(str_time + str(null_num))
            null_num += 1
        else:
            str_time = str_time[0:4] + "-" + str_time[4:6] + "-" + str_time[6:]
            formatted.append(datetime.strptime(str_time, '%Y-%m-%d').date())
    return formatted

# Converts a string time to date
def ConvertToDate(str_time, str_format):
    if 'NullState' in str_time:
        return str_time
    else:
        return datetime.strptime(str_time, str_format).date()
    
# converts burst start and end points to datetime objects 
def FormatBurstIntervals(bursts):
    formatted_bursts = []
    for burst in bursts:
        parts = burst.split('-')
        start = ConvertToDate(parts[0], '%Y/%m/%d')
        end = ConvertToDate(parts[1], '%Y/%m/%d')
        formatted_bursts.append((start, end))
    return formatted_bursts


# In[44]:


ref_bursts = pickle.load(open(ref_burst_pickle, 'rb'))
projects = ref_bursts.keys()
final_dict = {}

def ConvertToStringTime(time_obj):
    str_time = str(time_obj.year) + "/" + str(time_obj.month) + "/" + str(time_obj.day)
    return str_time

for project in projects:
    tt_file = os.path.join(tt_burst_dir, project + '_tt_segments.pickle')
    if os.path.isfile(tt_file) == False:
        continue
    project_bursts = ref_bursts[project]
    formatted_bursts = FormatBurstIntervals(project_bursts)
    if len(project_bursts) == 0:
        continue
    print "Processing for project: ", project
    tt_burst = pickle.load(open(tt_file, 'rb'))
    new_bursts = []
    
    for start,end in formatted_bursts:
        cur_day = start
        segments = set()
        while cur_day <= end:
            segments.add(tt_burst[cur_day])
            cur_day += relativedelta.relativedelta(days=1)
        if len(segments) == 1:
            new_bursts.append(ConvertToStringTime(start) + '-' + ConvertToStringTime(end))
        else:
            #print "more than 1 segment"
            cur_start = start
            cur_end = start
            while cur_end <= end:
                #print cur_end
                cur_seg_idx = tt_burst[cur_start]
                while cur_end < end and cur_seg_idx == tt_burst[cur_start]:
                    cur_end += relativedelta.relativedelta(days=1)
                    cur_seg_idx = tt_burst[cur_end]
                
                if cur_end != end:
                    cur_end -= relativedelta.relativedelta(days=1)
                new_bursts.append(ConvertToStringTime(cur_start) + "-" + ConvertToStringTime(cur_end))
                cur_end += relativedelta.relativedelta(days=1)
                cur_start = cur_end
    final_dict[project] = new_bursts
f = open(output_file, 'wb')
pickle.dump(final_dict, f)
f.close()     
