'''
Calculates the component experience of the people in a project per burst.
Component Experience - average number of times the people invovled in a burst have worked on the same files as the ones in the burst.
Output: {username:{burst_id:{filename1: count, filename2: count...}...}...}
'''
import os
import sys
import csv
import ast
import pandas as pd
import cPickle as pickle
from collections import defaultdict
from itertools import groupby, combinations
from datetime import datetime
from dateutil import relativedelta
import argparse

csv.field_size_limit(sys.maxsize)

parser = argparse.ArgumentParser()
parser.add_argument('--raw_commit_path', help='Directory containing commit files per project',\
					default='Sample_Data/congruence/raw_commits/')
parser.add_argument('--project_bursts_pickle', help='Pickled list of bursts per project',
					default='Sample_Data/HMM/results/daily_bursts.pickle')
parser.add_argument('--output_pickle_path', help='Output directory to store the pickled dictionary of component experience',\
					default='Sample_Data/congruence/component_exp/')
args = parser.parse_args()

raw_commit_path = args.raw_commit_path
project_bursts_pickle = args.project_bursts_pickle
output_pickle_path = args.output_pickle_path

try:
    os.makedirs(output_pickle_path)
except:
    pass

def dd():
	return defaultdict(int)

def outer_dd():
	return defaultdict(dd)

burst_dict = pickle.load(open(project_bursts_pickle, 'rb'))
projects = burst_dict.keys()

def FormatBurstTimeInterval(bursts):
	formatted = []
	for i,burst in enumerate(bursts):
		parts= burst.split('-')
		low = parts[0]
		high = parts[1]
		low = low.replace('/', '-')
		high_str = high.replace('/', '-')
		low = datetime.strptime(low, '%Y-%m-%d')
		high = datetime.strptime(high_str, '%Y-%m-%d')
		formatted.append((low, high))
	return formatted

def ConvertToTime(time_df):
	times = list(time_df)
	formatted_time = []
	for t in times:
		ft = t.split('+')[0]
		t_obj = datetime.strptime(ft, '%Y-%m-%d %H:%M:%S')
		formatted_time.append(t_obj)
	formatted_series = pd.Series(formatted_time)
	return formatted_series

for project in projects:
	commit_project = project.replace('~', '_')
	commit_file_name = project + '_commits.csv'
	commit_file = os.path.join(raw_commit_path, commit_file_name)
	if os.path.isfile(commit_file) == False:
		commit_file_name = "repo_" + commit_project + '_commits.csv'
		commit_file = os.path.join(raw_commit_path, commit_file_name)
		if os.path.isfile(commit_file) == False:
			continue

	print "Processing for project = ", project
	project_burst = burst_dict[project]
	formatted_burst = FormatBurstTimeInterval(project_burst)
	experience_dict = defaultdict(outer_dd)
	commits = pd.read_csv(open(commit_file, 'rU'))
	commit_times = commits['time']
	formatted_time = ConvertToTime(commit_times)
	commits['formatted_time'] = formatted_time
        commits.sort_values('formatted_time')
	
	for burst_id,burst in enumerate(formatted_burst):
		valid_commits = commits.loc[commits['formatted_time'] < burst[0]]
	        if burst_id > 0:
                    for user in experience_dict:
                        experience_dict[user][burst_id] = experience_dict[user][burst_id-1].copy()
		for index, row in valid_commits.iterrows():
			files = str(row['paths'])
			user = row['actor']
                        try:
                            file_list = eval(eval(files)[0])
			    for file in file_list:
				file = file.lower()
				if file.endswith('.py'):
					experience_dict[user][burst_id][file] += 1
                        except:
                            pass
		commits = commits.loc[commits['formatted_time'] >= burst[0]]

	user_exp_pick = os.path.join(output_pickle_path, (project + '_user_experience.pickle'))
	with open(user_exp_pick, 'wb') as u_pickle:
		pickle.dump(experience_dict, u_pickle)



