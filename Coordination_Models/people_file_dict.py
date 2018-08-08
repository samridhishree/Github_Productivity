'''
Creates a dictionary of files committed by the people of the project
'''
import os
import sys
import csv
import pandas as pd
import cPickle as pickle
from collections import defaultdict
import ast
import time
import unicodedata
import argparse

csv.field_size_limit(sys.maxsize)

parser = argparse.ArgumentParser()
parser.add_argument('--commit_dir', help='Directory containing commits per project',\
					default='Sample_Data/congruence/raw_commits/')
parser.add_argument('--output_pickle_path', help='Output directory to store pickle files per project to store user-file membership', \
					default='Sample_Data/congruence/user_file_dict/')
args, unknown = parser.parse_known_args()

commit_dir = args.commit_dir
output_pickle_path = args.output_pickle_path

try:
    os.makedirs(output_pickle_path)
except:
    pass

def dd():
	return defaultdict(int)

def ConvertToFilesList(list_str):
	#print list_str
	files = ast.literal_eval(list_str)
	files = files[0]
	files = unicodedata.normalize('NFKD', files).encode('ascii', 'ignore')
	if "[" not in files:
		return []
	files = ast.literal_eval(files)
	return files


for fileName in os.listdir(commit_dir):
	if fileName.endswith('.csv'):
		project_name = fileName.split('_commits.csv')[0]
		project_name = project_name.replace('repo_','',1)
		print "processing for project: ", project_name
		
		#Create a dictionary of files that each user touched
		data = pd.read_csv(os.path.join(commit_dir, fileName))
		user_file_dict = defaultdict(dd)
		for idx,row in data.iterrows():
			raw_files = row['paths']
			if pd.isnull(row['paths']):
				continue
			files = ConvertToFilesList(raw_files)
			user_name = str(row['actor']).strip().lower()
			for file in files:
				file = file.strip().lower()
				if(len(file) > 0):
					user_file_dict[user_name][file] += 1

		user_file_pick = os.path.join(output_pickle_path, (project_name + '_user_file.pickle'))
		with open(user_file_pick, 'wb') as u_pickle:
			pickle.dump(user_file_dict, u_pickle)



