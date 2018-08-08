'''
Generates all pairs of files that are committed together and updates their counts.
Output - pair of files comitted together along with the number of times they are committed together
'''
import os
import sys
import csv
import glob
import ast
import pandas as pd
import cPickle as pickle
from collections import defaultdict
from itertools import combinations, product, chain
import time
import argparse
import unicodedata


csv.field_size_limit(sys.maxsize)

parser = argparse.ArgumentParser()
parser.add_argument('--commit_dir', help='Directory containing commit files processed for graphs',\
					default='Sample_Data/congruence/raw_commits/')
parser.add_argument('--output_pickle_dir', help='Output pickle file containing pairwise file co-commit counts',\
					default='Sample_Data/congruence/co_commit_adj_pickle/')
args, unknown = parser.parse_known_args()

commit_dir = args.commit_dir
output_pickle_dir = args.output_pickle_dir

try:
    os.makedirs(output_pickle_dir)
except:
    pass

def ConvertToFilesList(list_str):
	#print list_str
	files = ast.literal_eval(list_str)
	files = files[0]
	files = unicodedata.normalize('NFKD', files).encode('ascii', 'ignore')
	if "[" not in files:
		return []
	files = ast.literal_eval(files)
	return files


for filename in os.listdir(commit_dir):
	commit_file = os.path.join(commit_dir, filename)
	project_name = filename.split('_commits.csv')[0]
	co_commit_pick = os.path.join(output_pickle_dir, (project_name + '_co_commit.pickle'))

	if os.path.isfile(commit_file) == True:
		start = time.time()
		print "Processing for project: ", project_name
		data = pd.read_csv(os.path.join(commit_dir, filename))
		co_commit_dict = defaultdict(int)
		singletons = set()
		all_files = set()
		all_pairs = set()
		affected_pairs = []

		#Get the list of files in each commit and edit their matrix entries
		for idx,row in data.iterrows():
			files_affected = []
			raw_files = row['paths']
			if pd.isnull(row['paths']):
				continue
			files = ConvertToFilesList(raw_files)
			for file in files:
				file = file.strip().lower()
				if(file.endswith('.py')):
					all_files.add(file)
					files_affected.append(file)

			if len(files_affected)<=1:
				singletons.update(files_affected)
			else:
				#Generate all possible pairs of the files co-committed
				affected_pairs = list(combinations(files_affected,2))
				affected_pairs = list(map(lambda x: tuple(sorted(x)), affected_pairs))
				for pair in affected_pairs:
					all_pairs.add(pair)
					co_commit_dict[pair] += 1

		cache = set(chain.from_iterable(all_pairs))
		new_singletons = set()
		for file in singletons:
			if file not in cache:
				new_singletons.add(file)

		#Generate pairs with singletons for completeness
		for file in new_singletons:
			pair = (file, file)
			if pair not in co_commit_dict:
				co_commit_dict[pair] = 1

		end = time.time()
		print "Time taken = ", (end-start)

		#Save as pickle
		print "Saving as pickle for project :", project_name
		with open(co_commit_pick, 'wb') as c_pickle:
			pickle.dump(co_commit_dict, c_pickle)






