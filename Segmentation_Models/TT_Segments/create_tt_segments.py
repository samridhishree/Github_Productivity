'''
This script creates the TT Segments for the days of acitivity in a project.
The vectors compared are the vector representations of all the words that occur as comments, issue titles or commit messages on that day.
Output - per project pickle of {day: segment_id}.
'''

import os
import sys
import csv
import pandas as pd
import numpy as np
import cPickle as pickle
from collections import defaultdict
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--project_active_days_pickle', help='Pickled list of active days of project (output of create_project_active_days.py)',
         default="Sample_Data/alternate_bursts/tt/active_days.pickle")
parser.add_argument('--combined_activity_dir', help='Directory containing project combined commits and issues (cleaned)',
         default="Sample_Data/alternate_bursts/tt/stemmed/")
parser.add_argument('--output_dir', help='Directory to store the project-wise TT Segments',
         default="Sample_Data/alternate_bursts/tt/segments/")
args, unknown = parser.parse_known_args()

project_active_days_pickle = args.project_active_days_pickle
combined_activity_dir = args.combined_activity_dir
output_dir = args.output_dir
active_days = pickle.load(open(project_active_days_pickle, 'rb'))
k = 1

# Converts a list of string times to datetime objects
def ConvertToTime(str_time_list, str_format):
    null_num = 0
    formatted = []
    for str_time in str_time_list:
        # For Nullstate put it as is
        if 'NullState' in str_time:
            formatted.append(str_time + str(null_num))
            null_num += 1
        else:
            str_time = str_time.replace('/', '-')
            if '+' in str_time:
                str_time = str_time.split('+')[0]
            formatted.append(datetime.strptime(str_time, str_format).date())
    return formatted


#for project in projects:
for filename in os.listdir(combined_activity_dir):
    #combined_file = os.path.join(combined_activity_dir, project + '_issue_comment.csv')
    combined_file = os.path.join(combined_activity_dir, filename)
    project = filename.split('_issue_comment.csv')[0]
    output_file = os.path.join(output_dir, project + '_tt_segments.pickle')
    if os.path.isfile(output_file) == True:
        print "Already computed for project = ", project
        continue

    print "Computing segments for project: ", project
    # Build the vocabulary for this project
    vocab = defaultdict(lambda: len(vocab)) 
    data = pd.read_csv(combined_file)
    text_df = data['text']
    text_df.dropna(inplace=True)
    all_text = list(text_df)

    formatted_text = []     #List where texts are replaced by their word IDs
    for text in all_text:
        temp = [str(vocab[word]) for word in text.split()]
        id_text = ' '.join(temp)
        if id_text != ' ':
            formatted_text.append(id_text)
    formatted_df = pd.Series(formatted_text)
    data['formatted_text'] = formatted_df
    
    # Get the active days of the project
    days = active_days[project]
    days = ConvertToTime(days, '%Y-%m-%d')
    times = list(data['time'])
    data['formatted_time'] = pd.Series(ConvertToTime(times, '%Y-%m-%d %H:%M:%S')) 
    activity_dict = defaultdict(lambda: [0] * len(vocab))

    # For each acitivty day fetch the formatted texts and update the activity dict
    for day in days:
        if 'NullState' in str(day):
            activity_dict[day]
        else:
            sub_df = data.loc[data['formatted_time'] == day]
            sub_text_df = sub_df['formatted_text']
            sub_text_df.dropna(inplace=True)
            sub_texts = list(sub_text_df)
            if len(sub_texts) == 0:
                continue
            day_string = str(day.year) + '-' + str(day.month).zfill(2) + '-' + str(day.day).zfill(2)
            for text in sub_texts:
                word_ids = text.split()
                word_ids = [int(_id) for _id in word_ids]
                for _id in word_ids:
                    activity_dict[day][_id] += 1

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
    segments = {}
    idx = 0
    for b_idx in boundaries:
        for i in range(idx, b_idx):
            segments[days[i]] = b_idx
        idx = b_idx + 1

    # Assign the last tail of days
    if idx < len(days):
        seg_id = idx
        for i in range(idx, len(days)):
            segments[days[i]] = seg_id

    # Save as pickle
    print "Saving as pickle"
    with open(output_file, 'wb') as p_pickle:
        pickle.dump(segments, p_pickle)





















