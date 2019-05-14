'''
Extracts the issues belonging to the bursty periods for projects.
Output -  csv file per burst per project containing the issues that were active during a burst.
Bursts are indexed by their IDs (arranged chronologically)
Also outputs an "extraneous_events" file counting how many events inside a burst were
not included (because the issue neither stopped nor started during the burst, or because
the issue was never eventually closed)
'''

import os
import sys
import csv
import glob
import calendar
import cPickle as pickle
import pandas as pd
from collections import defaultdict
from datetime import datetime, timedelta
import argparse


csv.field_size_limit(sys.maxsize)

parser = argparse.ArgumentParser()
parser.add_argument('--issue_dir', help='Directory with issue files', default='Sample_Data/congruence/raw_issues/')
parser.add_argument('--output_dir', help='Directory containing active issues per burst per project', default='Sample_Data/congruence/burst_issues/')
parser.add_argument('--dont_extraneous', help='Do not count up other events during the burst not associated with issues that start and end here', action="store_true")
parser.add_argument('--output_dir_extraneous', help='Place to put extra events that happend outside issues that start or end in the burst', default='Sample_Data/congruence/extraneous_events/')
parser.add_argument('--all_events', help='Include all events.  If option is not specified, just include events from those issues that opened or closed during the burst, and that eventually closed', action="store_true")
parser.add_argument('--burst_pickle', help='Pickle file containing the project burst information', default='Sample_Data/HMM/results/daily_bursts.pickle')
args = parser.parse_args()


issue_dir = args.issue_dir
output_dir = args.output_dir
output_dir_extraneous = args.output_dir_extraneous
project_burst_pickle = args.burst_pickle
do_extraneous = not args.dont_extraneous

print "Do_extraneous = ", do_extraneous

try:
    os.makedirs(output_dir)
except:
    pass
try:
    os.makedirs(output_dir_extraneous)
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
Extract issues that had any event occur during the bursty period
'''
def ExtractAndStoreIssuesAllEvents(bursts, project_name):
	pattern = issue_dir + '*' + project_name + '_issue*.csv'
	issue_files = glob.glob(pattern)

	formatted_bursts = FormatBurstTimeInterval(bursts)
	for file in issue_files:
		issues = pd.read_csv(file)#, names=colnames, header=None)

    		issue_times = issues['time']
    		formatted_time = ConvertToTime(issue_times)
    		issues['formatted_time'] = formatted_time
    		for i,burst in enumerate(bursts):
        		parts= burst.split('-')
        		low = parts[0]
        		high = parts[1]
        		low = low.replace('/', '-')
        		high_str = high.replace('/', '-')
        		low = datetime.strptime(low, '%Y-%m-%d')
        		high = datetime.strptime(high_str, '%Y-%m-%d') # This is NOT a bug; omit.  + timedelta(days=1)
        		sub_issues = issues.loc[issues['formatted_time'] >= low.date()]
        		sub_issues = sub_issues.loc[sub_issues['formatted_time'] <= high.date()]
        		sub_issues.to_csv(os.path.join(output_dir, project_name + '_burst_' + str(i) + '_issues.csv'), header = (i==0), mode = ("w" if i == 0 else "a"))

'''
Extract issues that were either opened or closed during the bursty period
'''
def ExtractAndStoreIssues(bursts, project_name):
	pattern = issue_dir + '*' + project_name + '_issue*.csv'
	issue_files = glob.glob(pattern)

	#Get the correct issues with appropriate start and end times
	valid_issues = defaultdict(list)
	formatted_bursts = FormatBurstTimeInterval(bursts)
              # burstid -> number of extraneous events (events during burst wrt issue that did not begin or end in burst, or that never ended
        if do_extraneous:
            extraneous_events = defaultdict(int)  
            extraneous_outf = csv.writer(open(os.path.join(output_dir_extraneous, project_name + "_extra.csv"),"w"))
            extraneous_outf.writerow("project,burst_id,extraneous_events".split(","))
	for file in issue_files:
		issue = pd.read_csv(file)#, names=colnames, header=None)
		issue.fillna('', inplace=True)
		start = issue.loc[issue['rectype'] == 'issue_title']
		close = issue.loc[issue['rectype'] == 'issue_closed']
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
                                elif do_extraneous == True:
        				sub_issues = issue.loc[issue['time'] >= low.date().isoformat()]
        				sub_issues = sub_issues.loc[sub_issues['time'] <= high.date().isoformat()]
					if len(sub_issues) > 0: 
						#print "Extraneous events: burst",i,"range",low.date().isoformat(),"-",high.date().isoformat(),"issues",set(sub_issues["issueid"]),"date1",sub_issues["time"].max(),set(sub_issues["rectype"])
                        			extraneous_events[i] += len(sub_issues)
		elif do_extraneous == True:
			for i,burst in enumerate(formatted_bursts):
				low = burst[0]
				high = burst[1]
        			sub_issues = issue.loc[issue['time'] >= low.date().isoformat()]
        			sub_issues = sub_issues.loc[sub_issues['time'] <= high.date().isoformat()]
				if len(sub_issues) > 0: 
					#print "Extraneous events: burst",i,"range",low.date().isoformat(),"-",high.date().isoformat(),"issues",set(sub_issues["issueid"]),"date1",sub_issues["time"].max(),set(sub_issues["rectype"])
                        		extraneous_events[i] += len(sub_issues)

	#Store the respective files
	for burst in valid_issues:
		burst_df = pd.concat(valid_issues[burst], axis=0)
		burst_df.to_csv(os.path.join(output_dir, project_name + "_" + burst + '_issues.csv'))
                burst_id = int(burst.split("_")[1])
                if do_extraneous:
                    extraneous_outf.writerow([project, burst_id, extraneous_events.get(burst_id,0)])

#Extract for the case study commits
# ExtractAndStoreIssues(bokeh_bursts, 'bokeh_bokeh')
# ExtractAndStoreIssues(django_bursts, 'django-extensions_django-extensions')
# ExtractAndStoreIssues(google_bursts, 'google_oauth2client')
for project in projects:
	print "Processing for project : ", project
	burst = burst_dict[project]
        print args
	if args.all_events:
		ExtractAndStoreIssuesAllEvents(burst, project)
	else:
		ExtractAndStoreIssues(burst, project)




			
