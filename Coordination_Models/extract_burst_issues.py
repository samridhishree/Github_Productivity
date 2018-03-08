'''
Extracts the issues belonging to the bursty periods for projects.
Output -  csv file per burst per project containing the issues that were active during a burst.
Bursts are indexed by their IDs (arranged chronologically)
'''

import os
import sys
import csv
import glob
import calendar
import cPickle as pickle
import pandas as pd
from collections import defaultdict
from datetime import datetime
import argparse


csv.field_size_limit(sys.maxsize)

parser = argparse.ArgumentParser()
parser.add_argument('--issue_dir', help='Directory with issue files', default='data/raw_issues/')
parser.add_argument('--output_dir', help='Directory containing active issues per burst per project', default='data/bursty_issues/')
parser.add_argument('--burst_pickle', help='Pickle file containing the project burst information', default='results/daily_bursts.pickle')
args, unknown = parser.parse_known_args()


issue_dir = args.issue_dir
output_dir = args.output_dir
project_burst_pickle = args.burst_pickle

try:
    os.makedirs(output_dir)
except:
    pass

burst_dict = pickle.load(open(project_burst_pickle, 'rb'))
projects = burst_dict.keys()
colnames = ["rectype", "issueid", "project_owner", "project_name", "actor", "time", "text", "action", "title"]

def ConvertToTime(time_df):
	times = list(time_df)
	formatted_time = []
	for t in times:
		ft = t.split('+')[0]
		t_obj = datetime.strptime(ft, '%Y-%m-%d %H:%M:%S')
		formatted_time.append(t_obj)
	formatted_series = pd.Series(formatted_time)
	return formatted_series

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

'''
Extract issues that were either opened or closed during the bursty period
'''
def ExtractAndStoreIssues(bursts, project_name):
	pattern = issue_dir + '*' + project_name + '_issue*.csv'
	issue_files = glob.glob(pattern)

	#Get the correct issues with appropriate start and end times
	valid_issues = defaultdict(list)
	formatted_bursts = FormatBurstTimeInterval(bursts)
	for file in issue_files:
		issue = pd.read_csv(file)#, names=colnames, header=None)
		issue.fillna('', inplace=True)
		start = issue.loc[issue['action'] == 'start issue']
		close = issue.loc[issue['action'] == 'closed issue']
		if((start.empty == False) and (close.empty == False)):
			start_time = start['time']
			start_time = str(start_time.values[0])
			start_time = start_time.split('+')[0]

			close_time = close['time']
			close_time = str(close_time.values[0])
			close_time = close_time.split('+')[0]

			start_obj = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
			close_obj = datetime.strptime(close_time, '%Y-%m-%d %H:%M:%S')

			for i,burst in enumerate(formatted_bursts):
				low = burst[0]
				high = burst[1]
				if (start_obj.date() >= low.date() and start_obj.date() <= high.date()) or \
				   (close_obj.date() >= low.date() and close_obj.date() <= high.date()):
				   key = "burst_" + str(i)
				   valid_issues[key].append(issue)

	#Store the respective files
	for burst in valid_issues:
		burst_df = pd.concat(valid_issues[burst], axis=0)
		burst_df.to_csv(os.path.join(output_dir, project_name + "_" + burst + '_issues.csv'))

#Extract for the case study commits
# ExtractAndStoreIssues(bokeh_bursts, 'bokeh_bokeh')
# ExtractAndStoreIssues(django_bursts, 'django-extensions_django-extensions')
# ExtractAndStoreIssues(google_bursts, 'google_oauth2client')
for project in projects:
	print "Processing for project : ", project
	burst = burst_dict[project]
	ExtractAndStoreIssues(burst, project)




			
