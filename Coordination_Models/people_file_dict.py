'''
Creates a dictionary of the list files committed by the people of the project.
Also contains the number of times a person made committed a particular file.
Output - {username:[file1:count1, file2:count2, ...] ....}
'''
import os
import sys
import csv
import pandas as pd
import cPickle as pickle
from collections import defaultdict
import argparse

csv.field_size_limit(sys.maxsize)

parser = argparse.ArgumentParser()
parser.add_argument('--commit_dep_path', help='Directory containing processed commits per project (output of - preprocess_commits_for_graph)')
parser.add_argument('--output_pickle_path', help='Output directory to store pickle files per project to store user-file membership')
args, unknown = parser.parse_known_args()

commit_dep_path = args.commit_dep_path
output_pickle_path = args.output_pickle_path

def dd():
	return defaultdict(int)


for fileName in os.listdir(commit_dep_path):
	if fileName.endswith('.csv'):
		project_name = fileName.split('_commitDep.csv')[0]
		print "processing for project: ", project_name
		
		#Create a dictionary of files that each user touched
		f = open(os.path.join(commit_dep_path, fileName), 'rb')
		reader = csv.reader(f)
		next(reader, None)

		user_file_dict = defaultdict(dd)
		for row in reader:
			user_name = row[3].strip().lower()
			for i in range(7, len(row)):
				if(len(row[i].strip()) > 0):
					user_file_dict[user_name][row[i].strip()] += 1
			
		user_file_pick = os.path.join(output_pickle_path, (project_name + '_user_file.pickle'))
		with open(user_file_pick, 'wb') as u_pickle:
			pickle.dump(user_file_dict, u_pickle)


