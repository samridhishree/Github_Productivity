'''
Creates a dictionary of files committed by the people of the project
'''
import os
import sys
import csv
import pandas as pd
import cPickle as pickle
from collections import defaultdict

csv.field_size_limit(sys.maxsize)

commit_dep_path = sys.argv[1]
output_pickle_path = sys.argv[2]

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
			#files_affected = []
			for i in range(7, len(row)):
				#if(row[i].strip().endswith('.py')):
				if(len(row[i].strip()) > 0):
					user_file_dict[user_name][row[i].strip()] += 1
			#user_file_dict[user_name].extend(files_affected)

		#Save the module-file and user-file dictionaries
		#conv_dict = {}
		#print user_file_dict
		#print type(user_file_dict)
		user_file_pick = os.path.join(output_pickle_path, (project_name + '_user_file.pickle'))
		with open(user_file_pick, 'wb') as u_pickle:
			pickle.dump(user_file_dict, u_pickle)