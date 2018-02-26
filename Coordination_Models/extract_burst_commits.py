'''
Extracts the commits belonging to the bursty periods for projects.
Output - csv file per burst per project containing the commits that occured during a burst.
Bursts are indexed by their IDs (arranged chronologically)
'''

import os
import sys
import csv
import calendar
import cPickle as pickle
import pandas as pd
from collections import defaultdict
from datetime import datetime
import argparse


csv.field_size_limit(sys.maxsize)

parser = argparse.ArgumentParser()
parser.add_argument('--raw_commits_dir', help='Directory with project-wise commit files')
parser.add_argument('--output_dir', help='Directory containing commits per burst per project')
parser.add_argument('--burst_pickle', help='Pickle file containing the project burst information')
args, unknown = parser.parse_known_args()


raw_commits_dir = args.raw_commits_dir
output_dir = args.output_dir
project_burst_pickle = args.burst_pickle

burst_dict = pickle.load(open(project_burst_pickle, 'rb'))
projects = burst_dict.keys()

def ConvertToTime(time_df):
	times = list(time_df)
	formatted_time = []
	for t in times:
		ft = t.split('+')[0]
		t_obj = datetime.strptime(ft, '%Y-%m-%d %H:%M:%S')
		formatted_time.append(t_obj.date())
	formatted_series = pd.Series(formatted_time)
	return formatted_series

def ExtractAndStoreCommits(commit_file, bursts, project_name):
	commits = pd.read_csv(commit_file)
	commit_times = commits['time']
	formatted_time = ConvertToTime(commit_times)
	commits['formatted_time'] = formatted_time
	for i,burst in enumerate(bursts):
		parts= burst.split('-')
		low = parts[0]
		high = parts[1]
		low = low.replace('/', '-')
		high_str = high.replace('/', '-')
		low = datetime.strptime(low, '%Y-%m-%d')
		high = datetime.strptime(high_str, '%Y-%m-%d')
		sub_commit = commits.loc[commits['formatted_time'] >= low.date()]
		sub_commit = sub_commit.loc[sub_commit['formatted_time'] <= high.date()]
		sub_commit.to_csv(os.path.join(output_dir, project_name + '_burst_' + str(i) + '_commits.csv'))

# ExtractAndStoreCommits(os.path.join(commits_dir, 'repo_google_oauth2client_commits.csv'), google_bursts, 'google_oauth2client')
for project in projects:
	commit_file_project = project.replace('~', '_')
	commit_file_name = 'repo_' + commit_file_project + '_commits.csv'
	commit_file = os.path.join(raw_commits_dir, commit_file_name)
	if os.path.isfile(commit_file):
		print "Processing for project : ", project
		burst = burst_dict[project]
		ExtractAndStoreCommits(commit_file, burst, project)





