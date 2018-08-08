'''
Implementation of Socio-Technical Congruence Measure introduced by Cataldo et.al. 
The original measure is calculated for 2 types of dependency - FCT (Files that Change Together) and CGRAPH (Call Graph - synctactic dependencies)
This implementation is only for the FCT dependencies.
The actual ccordination is also measured in two respects - CA_mod (people belonging to the same module) and 
														   CA_pr (people participating in the PR discussion thread)
Thus, there are 2 Congruence Measures calculated: CM_mod^FCT and CM_PR^FCT
'''
import os
import sys
import csv
import operator
import ast
import calendar
import numpy as np
import pandas as pd
import cPickle as pickle
from collections import defaultdict, OrderedDict
from itertools import groupby, combinations
from datetime import datetime
from dateutil import relativedelta
import argparse
import unicodedata

csv.field_size_limit(sys.maxsize)

parser = argparse.ArgumentParser()
parser.add_argument('--fct_adjacency_dir', help='Directory containing 2D adjacency matrix (output of: reformat_adjacency.py)',\
	default='Sample_Data/congruence/reformatted_co_commit_adj/')
parser.add_argument('--user_file_pickle_dir', help='Directory containing the user-file membership (output of: people_file_dict.py)',\
	default='Sample_Data/congruence/user_file_dict/')
parser.add_argument('--user_mod_fct', help='Directory containing user module membership (output of: people_module_dict.py)',\
	default='Sample_Data/congruence/user_module_dict/')
parser.add_argument('--bursty_commits_dir', help='Directory containing the per project per burst commits (output of: extract_burst_commits.py)',\
	default='Sample_Data/congruence/burst_commits/')
parser.add_argument('--bursty_issues_dir', help='Directory containing active issues per burst per project (output of: extract_burst_issues.py)',\
	default='Sample_Data/congruence/burst_issues/')
parser.add_argument('--project_bursts_pickle', help='Pickled list of bursts per project (output of: HMM/extract_daily_bursts.py)',\
	default='Sample_Data/HMM/results/daily_bursts.pickle')
parser.add_argument('--file_mod_pickle_dir', help='Directory containing the file module membership (output of: file_module_dict.py)',\
	default='Sample_Data/congruence/file_module_dict/')
parser.add_argument('--user_experience_pickle_dir', help='Directory containing component experience \
	per user for each project (output of: people_component_experience.py)',\
	default='Sample_Data/congruence/component_exp/')
parser.add_argument('--participation_csv', help='Input csv file containing the participation information for the users of the project',\
	default='Sample_Data/HMM/participation.csv')
parser.add_argument('--output_csv_dir', help='Output directory to hold project wise computed metrics for each burst',\
	default='Sample_Data/congruence/congruence_outputs/output_csv/')
parser.add_argument('--output_pickle_dir', help='Output directory to hold te computed metric as pickled dataframes',\
	default='Sample_Data/congruence/congruence_outputs/output_pickle/')
parser.add_argument('--output_csv_req_metrics', help='Output directory to hold the requirement matrices',\
	default='Sample_Data/congruence/congruence_outputs/output_requirements/')

args, unknown = parser.parse_known_args()

fct_adjacency_dir = args.fct_adjacency_dir
user_file_pickle_dir = args.user_file_pickle_dir	
user_mod_fct = args.user_mod_fct
bursty_commits_dir = args.bursty_commits_dir 
bursty_issues_dir = args.bursty_issues_dir
project_bursts_pickle = args.project_bursts_pickle
file_mod_pickle_dir = args.file_mod_pickle_dir
user_experience_pickle_dir = args.user_experience_pickle_dir
participation_csv = args.participation_csv
output_csv_dir = args.output_csv_dir
output_pickle_dir = args.output_pickle_dir
output_csv_req_metrics = args.output_csv_req_metrics


try:
    os.makedirs(output_csv_dir)
    os.makedirs(output_pickle_dir)
    os.makedirs(output_csv_req_metrics)
except:
    pass

'''
Converts the burst intervals to actual datetime intervals
'''
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
Calculate the cm matrix
'''
def CalculateCM(ca_df, cr_df):
	rows, cols = np.where(cr_df != 0)
	rows = list(rows)
	cols = list(cols)
	pairs = zip(rows, cols)
	count = 0
	for r,c in pairs:
		if r != c:
			if ca_df.iloc[r,c] != 0.0:
				count += 1
	
	non_diagonal_pairs = [p for p in pairs if p[0] != p[1]]
	cr_cardinality = len(non_diagonal_pairs)
	if cr_cardinality == 0.0:
		cm = 0.0
	else:
		cm = (float)(count)/(float)(cr_cardinality)
	return cm

'''
Bookeeping function to unpickle user_file adjacency
'''
def dd():
	return defaultdict(int)

def outer_dd():
	return defaultdict(dd)

def fill_diagonal(df, val):
	for i in df.index:
		df.loc[i,i] = val
	return df

# There are 2 level lists. First literal eval gives the unicode that is converted to a string for the second literal eval
def ConvertToFilesList(list_str):
	files = ast.literal_eval(list_str)
	files = files[0]
	files = unicodedata.normalize('NFKD', files).encode('ascii', 'ignore')
	if "[" not in files:
		return []
	files = ast.literal_eval(files)
	return files

def ConvertStringToTime(str_time):
	str_time = str_time.split('+')[0]
	str_obj = datetime.strptime(str_time, '%Y-%m-%d %H:%M:%S')
	return str_obj

'''
Get the open and close times of an issue and convert them to datetime objects for better processing
'''
def GetIssueTimes(issue_df, burst_start, burst_end, for_art=False):
	starts = issue_df.loc[issue_df['action'] == 'start issue']
	closes = issue_df.loc[issue_df['action'] == 'closed issue']
	s_times = starts['time']
	c_times = closes['time']
	if((starts.empty == False) and (closes.empty == False)):
		start_times = []
		close_times = []
		for start in s_times:
			start_obj = ConvertStringToTime(str(start))
			start_times.append(start_obj)
		for close in c_times:
			close_obj = ConvertStringToTime(str(close))
			close_times.append(close_obj)

		if for_art == True:
			start_close_times = zip(start_times, close_times)
			start_times = []
			close_times = []
			for (start,close) in start_close_times:
				if close.date() > burst_end.date():
					continue
				elif start.date() < burst_start.date():
					start_times.append(burst_start)
					close_times.append(close)
				else:
					start_times.append(start)
					close_times.append(close)
		return start_times, close_times


'''
Get the number of issues opened in the burst period and the number of issues_closed
'''
def GetOpenCloseIssues(issue_df, burst_start, burst_end):
	opened = 0
	closed = 0
	starts = issue_df.loc[issue_df['action'] == 'start issue']
	closes = issue_df.loc[issue_df['action'] == 'closed issue']
	s_times = starts['time']
	c_times = closes['time']
	if((starts.empty == False) and (closes.empty == False)):
		start_times, close_times = GetIssueTimes(issue_df, burst_start, burst_end)
		for start in start_times:
			if start.date() >= burst_start.date():
				opened += 1
		for close in close_times:
			if close.date() <= burst_end.date():
				closed += 1
	return opened, closed

'''
Calculates the average issue resolution time for the issues active in the burst and closed before the burst ended.
Does not take into account the issues which failed to close before the burst ended.
For issues opened before the burst, takes the burst_start as the issue_start time.
'''
def CalculateAvgResolutionTime(issues, burst_start, burst_end):
	start_times, close_times = GetIssueTimes(issues, burst_start, burst_end, True)
	issue_times = []
	avg = 0.0
	for (start, close) in zip(start_times, close_times):
		resolve_time = close - start
		num_hours = resolve_time.total_seconds()/3600.0
		issue_times.append(num_hours)
	if len(issue_times) > 0:
		avg = sum(issue_times)/(float)(len(issue_times))
	return avg

'''
Returns the interval between the first issue opened in the burst and the last issue closed in the burst
'''
def CalculateBurstIssueInterval(issues, burst_start, burst_end):
	start_times, close_times = GetIssueTimes(issues, burst_start, burst_end, True)
	if len(start_times) > 0 and len(close_times)>0:
		start_times.sort()
		close_times.sort()
		start = start_times[0]
		end = close_times[len(close_times)-1]
		interval = end - start
		num_hours = interval.total_seconds()/3600.0
		return num_hours
	else:
		return 0

'''
Converts a string time datframe to formatted time dataframe
'''
def ConvertToFormattedTime(time_df):
	times = list(time_df)
	formatted_time = []
	for t in times:
		ft = t.split('+')[0]
		t_obj = datetime.strptime(ft, '%Y-%m-%d %H:%M:%S')
		formatted_time.append(t_obj)
	formatted_series = pd.Series(formatted_time)
	return formatted_series

'''
Get the issues active in the burst
'''
def GetIssueInBurst(issue_df, burst_start, burst_end):
	times = issue_df['time']
	times.dropna(inplace=True)
	issue_df['formatted_time'] = ConvertToFormattedTime(times)
	sub1 = issue_df.loc[issue_df['formatted_time'] >= burst_start]
	sub2 = sub1.loc[sub1['formatted_time'] <= burst_end]
	return sub2

'''
Returns only the comments that happened in the burst with valid rectypes (comment and title)
'''
def GetValidIssueCommentsForBurst(issue_df):
	df_comment = issue_df.loc[issue_df['rectype'].str.find('comment')>0]
	df_title = issue_df.loc[issue_df['rectype'].str.find('title')>0]
	df = pd.concat([df_comment, df_title])
	df.fillna('', inplace=True)
	df_non_repeat = df.drop_duplicates(subset=['text'], keep='first')
	return df_non_repeat

'''
Returns the average number of days in github for the users in the burst at the burst end
'''
def CalculateTenure(participation, users, burst_end):
	tenure = 0.0
	num_users = 0.0
	avg = 0.0
	for user in users:
		user_part = participation.loc[participation['actor'] == user]
		dates = list(user_part['first_participation_date'])
		if len(dates) == 0:
			continue
		part_date = str(dates[0])
		part_date = part_date.replace('T', ' ')
		part_date_obj = ConvertStringToTime(part_date)
		if burst_end >= part_date_obj:
			interval = burst_end - part_date_obj
			tenure += interval.days
			num_users += 1
	if num_users > 0:
		avg = tenure/(float)(num_users)
	return avg


'''
Read the PR info csv files for each project and compute measure for each PR in the project
'''
def CalculateAndStoreCongruence(project_name, bursts):
	prev = project_name
	project_name = project_name.replace("~", "_")	
	fct_adjacency_file = project_name + '_co_commit.pickle'
	user_file_pickle = project_name + '_user_file.pickle'
	user_mod_filename = prev + '_user_module.pickle'
	file_mod_filename = "repo_" + project_name + '_file_mod.pickle'
	exp_dict_filename = prev +'_user_experience.pickle'
	pickle_file = os.path.join(output_pickle_dir, project_name + '_cm_mr_info.pickle')

	print os.path.join(user_mod_fct, user_mod_filename)

	if (os.path.isfile(os.path.join(user_mod_fct, user_mod_filename)) == True) and \
	(os.path.isfile(os.path.join(fct_adjacency_dir, fct_adjacency_file)) == True):
		print "Calculating the measure for the project = ", project_name
		
		#Load all the data from the required files
		fct_adjacency = pickle.load(open(os.path.join(fct_adjacency_dir, fct_adjacency_file), 'rb'))
		user_file_dict = pickle.load(open(os.path.join(user_file_pickle_dir, user_file_pickle), 'rb'))
		user_mod_fct_dict = pickle.load(open(os.path.join(user_mod_fct, user_mod_filename), 'rb'))
		file_mod_fct_dict = pickle.load(open(os.path.join(file_mod_pickle_dir, file_mod_filename), 'rb'))
		exp_dict = pickle.load(open(os.path.join(user_experience_pickle_dir, exp_dict_filename), 'rb'))
		all_participation = pd.read_csv(participation_csv)
		all_participation['actor'] = all_participation['actor'].apply(lambda x: str(x).lower())
		all_participation['owner'] = all_participation['owner'].apply(lambda x: str(x).lower())
		all_participation['project'] = all_participation['project'].apply(lambda x: str(x).lower())

		final_info_dict = []
		
		for burst_id,burst in enumerate(bursts):
			commit_file_name = prev + "_burst_" + str(burst_id) + "_commits.csv"
			issue_file_name = prev + "_burst_" + str(burst_id) + "_issues.csv"
			commit_file = os.path.join(bursty_commits_dir, commit_file_name)
			issue_file = os.path.join(bursty_issues_dir, issue_file_name)
			file_modules_involved = set()
			user_modules_involved = set()
			
			if os.path.isfile(commit_file) == True and os.path.isfile(issue_file) == True:
				commits = pd.read_csv(open(commit_file,'rU'))#, encoding='utf-8')
				issues = pd.read_csv(open(issue_file,'rU'))#, encoding='utf-8')
				issues = issues[issues['time'] != 'time']
				issue_events_in_burst = GetIssueInBurst(issues, burst[0], burst[1])
				valid_issues = GetValidIssueCommentsForBurst(issue_events_in_burst)
				
				#Commits
				all_files = commits['paths']
				all_files.fillna('', inplace=True)
				files_modified = set()
				for files_commited in list(all_files):
					if str(files_commited) == '':
						continue
					files_commited = ConvertToFilesList(files_commited)
					#print "files_commited = ", files_commited
					for file in files_commited:
						if file.endswith('.py'):
							file = file.lower()
							files_modified.add(file)
							if file in file_mod_fct_dict:
								file_modules_involved.add(file_mod_fct_dict[file])


				commiting_users = set(commits['actor'])
				user_superset = set(user_file_dict.keys())
				commenting_users = set(issues['actor'])

				commenting_users = set(commenting_users)
				commiting_users = set(commiting_users)

				commenting_users = list(map(lambda x:str(x), commenting_users))
				commiting_users = list(map(lambda x: str(x), commiting_users))
				commenting_users = list(map(lambda x: x.lower(), commenting_users))
				commiting_users = list(map(lambda x: x.lower(), commiting_users))
				commenting_users = [user for user in commenting_users if user in user_superset]
				commiting_users = [user for user in commiting_users if user in user_superset]

				#Group the issues by their issue_ids
				grouped = issues.groupby('issueid', axis=0)
				issue_dict = {}
				for i,group in grouped:
					issue_dict[i] = set(group['actor'])
				
				all_users = set(commenting_users + commiting_users)
				all_users = set(map(lambda x: x.lower(), all_users))
				
				files_modified = list(files_modified)
				comp_experience = 0.0
				avg_comp_experience = 0.0
				if len(files_modified) > 0 and len(commiting_users) > 1: #and len(commiting_users) > 0:
					ta_dict = defaultdict(lambda: defaultdict(int))
					for user in commiting_users:
						if user in user_file_dict:
							for file in files_modified:
								ta_dict[user][file] = user_file_dict[user][file]
								if file in exp_dict[user][burst_id]:
									comp_experience += exp_dict[user][burst_id][file]
					avg_comp_experience = comp_experience/(float)(len(commiting_users) * len(files_modified))	

					ta_df = pd.DataFrame.from_dict(ta_dict, orient='index')
					ta_df.fillna(0.0, inplace=True)

					#Td_FCT - submatrix of the adjacency matrix
					try:
						td_fct_df = fct_adjacency.loc[files_modified, files_modified]
					except Exception as e:
						print "Exception at fct_adjaceny: ", e
						continue
					td_fct_df = fill_diagonal(td_fct_df, 0.0)
					td_fct_df.fillna(0.0, inplace=True)
					

					#CR_fct
					cr_fct_temp = ta_df.dot(td_fct_df)
					cr_fct = cr_fct_temp.dot(ta_df.transpose())

					#Sort the rows and columns for easier comparison
					cr_fct.sort_index(inplace = True)
					cr_fct = cr_fct.reindex_axis(sorted(cr_fct.columns), axis=1)
					cr_fct.fillna(0.0, inplace=True)
					
					'''
					Actual Coordination (Mod) - people belonging to the same module
					'''

					#Ca_mod - peopleXpeople for people belonging of the same module - FCT
					ca_fct_dict = defaultdict(lambda: defaultdict(int))
					for user in commiting_users:
						target_modules = set(user_mod_fct_dict[user])
						user_modules_involved.update(target_modules)
						for other_user in commiting_users:
							if other_user == user:
								continue
							user_modules = set(user_mod_fct_dict[other_user])
							if user_modules <= target_modules or target_modules <= user_modules:
								ca_fct_dict[user][other_user] = 1.0
							else:
								ca_fct_dict[user][other_user] = 0.0

					#Create a proper adjacency representation of the above dictionary
					ca_mod_fct_df = pd.DataFrame.from_dict(ca_fct_dict, orient='index')
					ca_mod_fct_df.fillna(0, inplace = True)
					ca_mod_fct_df = fill_diagonal(ca_mod_fct_df, 0.0)

					#Sort the rows and columns for easier comparison
					ca_mod_fct_df.sort_index(inplace = True)
					ca_mod_fct_df = ca_mod_fct_df.reindex_axis(sorted(ca_mod_fct_df.columns), axis=1)

					#Create a nested dictionary of all the people who commented on the same issue
					ca_mr_dict = defaultdict(lambda: defaultdict(int))
					for issue_id, users in issue_dict.items():
						user_pairs = list(combinations(list(users), 2))
						if len(user_pairs) > 0:
							for u1, u2 in user_pairs:
								u1 = str(u1).lower()
								u2 = str(u2).lower()
								ca_mr_dict[u1][u2] += 1
								ca_mr_dict[u2][u1] += 1
						elif len(users) > 0:
							for user in users:
								user = str(user).lower()
								ca_mr_dict[user][user] += 1

					'''
					Actual Coordination (MR) - people commenting on the issue threads (commenting users)
					'''
					#For users present in commit list but not in the issue, add zero rows for them
					common_users = set(commiting_users).intersection(set(commenting_users))
					remaining_users = set(commiting_users) - common_users
					
					#print ca_mr_dict
					for user in remaining_users:
						ca_mr_dict[user][user] = 1
					ca_mr_df = pd.DataFrame.from_dict(ca_mr_dict, orient='index')
					
					#Consider only the subset of committing users from the above adjacency matrix
					commiting_users = set(commiting_users)
					ca_mr_df = ca_mr_df.loc[commiting_users, commiting_users]
					ca_mr_df.fillna(0.0, inplace = True)
					ca_mr_df.sort_index(inplace=True)
					ca_mr_df = ca_mr_df.reindex_axis(sorted(ca_mr_df.columns), axis=1)


					
					# Congruence Measures Calculations - CM_mod^FCT and CM_PR^FCT
					cm_mod_fct = CalculateCM(ca_mod_fct_df, cr_fct)
					cm_mr_fct = CalculateCM(ca_mr_df, cr_fct)
					cr_file = project_name + "_burst_" + str(burst_id) + "_requirements.csv"
					ca_mod_file = project_name + "_burst_" + str(burst_id) + "_actual_mod.csv"
					ca_mr_file = project_name + "_burst_" + str(burst_id) + "_actual_mr.csv"
					cr_fct.to_csv(os.path.join(output_csv_req_metrics, cr_file))
					ca_mod_fct_df.to_csv(os.path.join(output_csv_req_metrics, ca_mod_file))
					ca_mr_df.to_csv(os.path.join(output_csv_req_metrics, ca_mr_file))
				else:
					cm_mod_fct = "NA"
					cm_mr_fct = "NA"


				#Calculate the values of the control variables
				time_delta = burst[1] - burst[0]
				burst_duration_days = abs(time_delta.days) + 1
				burst_issue_duration = CalculateBurstIssueInterval(issues, burst[0], burst[1])
				issue_comments = valid_issues['text']
				issue_comments = list(issue_comments.dropna())
				num_comments = len(issue_comments)
				num_commits = commits.shape[0]
				num_issues = len(issue_dict.keys())
				num_committers = len(set(commiting_users))
				num_commenters = len(set(commenting_users))
				num_all_users = len(all_users)
				issues_opened, issues_closed = GetOpenCloseIssues(issues, burst[0], burst[1])
				avg_issue_time = CalculateAvgResolutionTime(issues, burst[0], burst[1])

				if num_committers == 0:
					issue_per_person = "NA"
					efficiency = "NA"
				else:
					issue_per_person = num_issues/(float)(num_committers)
					efficiency = issues_closed/(float)(num_committers)

				if num_all_users == 0:
					activity_per_person = "NA"
				else:
					activity_per_person = (num_comments + num_commits)/(float)(num_all_users)

				# Calculate Tenure
				parts = project_name.split('_')
				project_owner = parts[0].lower()
				project = ' '.join(parts[1:]).lower()
				valid_participation = all_participation.loc[all_participation['owner'] == project_owner]
				valid_participation_1 = valid_participation.loc[valid_participation['project'] == project]
				if valid_participation_1.empty == False:
					avg_tenure = CalculateTenure(valid_participation_1, commiting_users, burst[1])
				else:
					avg_tenure = "NA"

				#Save as a new dictionary
				temp = OrderedDict()
				temp['burst_id'] = burst_id
				temp['burst_start'] = burst[0]
				temp['burst_end'] = burst[1]
				temp['burst_duration_days'] = burst_duration_days
				temp['total_activity'] = num_commits + num_comments
				temp['num_files (Change Size)'] = len(files_modified)
				temp['file_modules (#Teams)'] = len(file_modules_involved)
				temp['total_num_issues'] = num_issues
				temp['issues_opened'] = issues_opened
				temp['issues_closed'] = issues_closed
				temp['avg_res_time_hours'] = avg_issue_time
				temp['efficiency'] = efficiency
				temp['issue_per_person (Team Load)'] = issue_per_person
				temp['activity_per_person'] = activity_per_person
				temp['committing_users'] = num_committers
				temp['commenting_users'] = num_commenters
				temp['total_actors'] = num_all_users
				temp['component_experience'] = avg_comp_experience
				temp['tenure'] = avg_tenure
				temp['structural_congruence_fct'] = cm_mod_fct  
				temp['mr_congruence_fct'] = cm_mr_fct
				temp['users_to_coordinate'] = commiting_users
				final_info_dict.append(temp)

			#Save the final info for this project as a pickle file
			pickle_file = os.path.join(output_pickle_dir, project_name + '_cm_mr_info.pickle')
			with open(pickle_file, 'wb') as p_pickle:
				pickle.dump(final_info_dict, p_pickle)
			info_df = pd.DataFrame(final_info_dict)
			info_df.to_csv(os.path.join(output_csv_dir, project_name + '_cm_mr_info.csv'))

burst_dict = pickle.load(open(project_bursts_pickle, 'rb'))
projects = burst_dict.keys()
ignore_projects = ['python-diamond~Diamond', 'juanifioren~django-oidc-provider']

for project_name in projects:
	if project_name in ignore_projects:
		continue
	project_burst = burst_dict[project_name]
	formatted_burst = FormatBurstTimeInterval(project_burst)
	CalculateAndStoreCongruence(project_name, formatted_burst)







		