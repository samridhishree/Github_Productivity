
# coding: utf-8

# In[2]:


'''
Does text tiling of people active on particular days of the project
'''
import os
import sys
import csv
import pandas as pd
import numpy as np
import cPickle as pickle
from collections import defaultdict, OrderedDict
from datetime import datetime, date
from sklearn.metrics.pairwise import cosine_similarity
from pymongo import MongoClient
from dateutil import relativedelta
import argparse



parser = argparse.ArgumentParser()
parser.add_argument('--daily_activity_dir', help='Folder containing daily stats for projects', 
                default='Sample_Data/HMM/daily_data/')
parser.add_argument('--output_dir', help='Output dictionary for pickled dictionary for TT membership per project', 
                default='Sample_Data/People_TT/tt_per_project/')

args, unknown = parser.parse_known_args()
daily_activity_dir = args.daily_activity_dir
output_dir = args.output_dir

try:
    os.makedirs(output_dir)
except:
    pass


client = MongoClient("mongodb://127.0.0.1:27017")
project_events = client["pypi-v6"].project_events
issue_events = client["pypi-v6"].issue_events
k = 1

# Converts a list of string times to datetime objects
def ConvertToTime(str_time_list):
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

def ConvertToDate(str_time):
    str_time = str_time[0:4] + "-" + str_time[4:6] + "-" + str_time[6:]
    time_obj = datetime.strptime(str_time, '%Y-%m-%d').date()
    return time_obj

# Converts a list of string time to objects, removes NullState
def CreateDaySeries(str_time_list):
    str_time_list = sorted(str_time_list)
    cur = ConvertToDate(str(str_time_list[0]))
    end = ConvertToDate(str(str_time_list[-1]))
    day_list = []
    while cur <= end:
        day_list.append(cur)
        cur += relativedelta.relativedelta(days=1)
    return day_list


# In[ ]:


# Applies the text tiling algorithm from 
# Hearst MA (1994) Multi-paragraph segmentation of expository text. 
#  In: Pro-ceedings of the 32nd annual meeting on Association for 
#  Computational Lin-guistics, Association for Computational Linguistics, pp 9–16
# It uses people instead of words to find sequences of similar people working
for filename in os.listdir(daily_activity_dir):
    project = filename.split('.csv')[0].strip()
    print "Processing for project = ", project
    parts = project.split('~')
    project_owner = parts[0].lower()
    project_name = parts[1].lower()
    ievents = issue_events.find({"project_owner_lower": project_owner,
                                         "project_name_lower": project_name})
    pevents = project_events.find({"project_owner_lower": project_owner,
                                 "project_name_lower": project_name})

    daywise_activity = defaultdict(set)
    actor_vocab = defaultdict(lambda: len(actor_vocab))

    for irow in ievents:
        if irow["actor"] is None:
            actor = 'ghost~user'
        else:
            actor = irow["actor_lower"]
        daywise_activity[irow["time"].date()].add(actor_vocab[actor])

    for irow in pevents:
        if irow["actor"] is None:
            actor = 'ghost~user'
        else:
            actor = irow["actor_lower"]
        daywise_activity[irow["time"].date()].add(actor_vocab[actor])

    data = pd.read_csv(os.path.join(daily_activity_dir, filename))
    periods = list(data['period'])
    periods = list(map(lambda x: str(x), periods))
    if len(periods) == 0:
        continue
    days = CreateDaySeries(periods)
    activity_dict = defaultdict(lambda: np.zeros(len(actor_vocab)))

    for day in days:
        active_actors = list(daywise_activity[day])
        activity_dict[day][active_actors] = 1

    # Compute the similarity scores for sequence gap
    sim_scores = {}
    for i in range(1, len(days)-k):
        left_vectors = []
        for j in range(i-k, i):
            left_vectors.append(activity_dict[days[j]])
        left_aggregate = np.sum(np.array(left_vectors), axis=0)
        right_vectors = []
        for j in range(i, i+k):
            right_vectors.append(activity_dict[days[j]])
        right_aggregate = np.sum(np.array(right_vectors), axis=0)


        # If either is a NullState, assign the similarity to 0
        if np.sum(left_aggregate) == 0.0 or np.sum(right_aggregate) == 0.0:
            sim_scores[i] = 0.0
        else:
            sim_scores[i] = cosine_similarity([left_aggregate], [right_aggregate])[0][0]

    # Compute the depth score for each sequence gap index
    depth = {}
    for gap in sim_scores:
        left_peak = sim_scores[gap]
        right_peak = sim_scores[gap]

        # Compute the left diff
        for i in range(gap, 0, -1):
            if sim_scores[i] > left_peak:
                left_peak = sim_scores[i]
            else:
                break

        # Compute the right diff
        for i in range(gap+1, len(sim_scores.keys())):
            if sim_scores[i] > right_peak:
                right_peak = sim_scores[i]
            else:
                break

        left_diff = left_peak - sim_scores[gap]
        right_diff = right_peak - sim_scores[gap]
        depth[gap] = left_diff + right_diff

    # Compute the segment indexes (gap value indexes) from the thresholding depth scores
    depth_scores = np.array(depth.values())
    non_zero = [score for score in depth_scores if score > 0]
    boundaries = []
    if len(non_zero) == 0:
        print "No non zero depth scores. Putting all the days in one segment"
        boundaries.append(len(days))
    else:
        threshold = np.mean(non_zero) - np.std(non_zero)/2.0
        print "threshold = ", threshold
        for idx,score in depth.items():
            if score > threshold:
                boundaries.append(idx)

    # Compute the segment membership and pickle the resultant dictionary
    output_file = open(os.path.join(output_dir, project + '_tt_segments.pickle'), 'wb')
    segments = {}
    idx = 0
    for b_idx in boundaries:
        for i in range(idx, b_idx):
            segments[days[i]] = b_idx
        idx = b_idx

    # Assign the last tail of days
    if idx < len(days):
        seg_id = idx
        for i in range(idx, len(days)):
            segments[days[i]] = seg_id

    # Save as pickle
    print "Saving as pickle"
    pickle.dump(segments, output_file)

