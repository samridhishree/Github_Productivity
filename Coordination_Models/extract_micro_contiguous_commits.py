'''
Extracts the commits belonging to the bursty periods for projects
'''

import os
import sys
import csv
import calendar
import cPickle as pickle
import pandas as pd
from collections import defaultdict
from datetime import datetime


csv.field_size_limit(sys.maxsize)

raw_commits_dir = sys.argv[1]
output_dir = sys.argv[2]
project_burst_pickle = sys.argv[3]
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
		#low = low + '-01'
		#high = high + '-30'
		low = datetime.strptime(low, '%Y-%m-%d')
		high = datetime.strptime(high_str, '%Y-%m-%d')
		#print "low = ", low
		#day_range = calendar.monthrange(high.year, high.month)
		#print "day_range : ", day_range
		#high = high_str + '-' + str(day_range[1])
		#print "high = ", high
		#high = datetime.strptime(high, '%Y-%m-%d')
		
		#print "high = ", high
		sub_commit = commits.loc[commits['formatted_time'] >= low.date()]
		sub_commit = sub_commit.loc[sub_commit['formatted_time'] <= high.date()]
		sub_commit.to_csv(os.path.join(output_dir, project_name + '_burst_' + str(i) + '_commits.csv'))

#Extract for the case study commits
# ExtractAndStoreCommits(os.path.join(commits_dir, 'repo_bokeh_bokeh_commits.csv'), bokeh_bursts, 'bokeh_bokeh')
# ExtractAndStoreCommits(os.path.join(commits_dir, 'repo_django-extensions_django-extensions_commits.csv'), django_bursts, 'django-extensions_django-extensions')
# ExtractAndStoreCommits(os.path.join(commits_dir, 'repo_google_oauth2client_commits.csv'), google_bursts, 'google_oauth2client')
for project in projects:
	commit_file_project = project.replace('~', '_')
	commit_file_name = 'repo_' + commit_file_project + '_commits.csv'
	#print commit_file_name
	commit_file = os.path.join(raw_commits_dir, commit_file_name)
	if os.path.isfile(commit_file):
		print "Processing for project : ", project
		burst = burst_dict[project]
		ExtractAndStoreCommits(commit_file, burst, project)





