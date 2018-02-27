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


csv.field_size_limit(sys.maxsize)

parser = argparse.ArgumentParser()
parser.add_argument('--processed_commit_dir', help='Directory containing commit files processed for graphs')
parser.add_argument('--output_pickle_dir', help='Output pickle file containing pairwise file co-commit counts')
args, unknown = parser.parse_known_args()

processed_commit_dir = args.processed_commit_dir
output_pickle_dir = args.output_pickle_dir

for filename in os.listdir(processed_commit_dir):
	commit_file = os.path.join(processed_commit_dir, filename)
	project_name = filename.split('_commitDep.csv')[0]
	co_commit_pick = os.path.join(output_pickle_dir, (project_name + '_co_commit.pickle'))

	if os.path.isfile(commit_file) == True and os.path.isfile(co_commit_pick) == False:
		start = time.time()
		print "Processing for project: ", project_name
		f = open(commit_file, 'rb')
		reader = csv.reader(f)
		next(reader, None)
		co_commit_dict = defaultdict(int)
		singletons = set()
		all_files = set()
		all_pairs = set()
		affected_pairs = []

		#Get the list of files in each commit and edit their matrix entries
		for row in reader:
			files_affected = []
			for i in range(7, len(row)):
				file = row[i].strip().lower()
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
		#Save as csv
		# df = pd.DataFrame.from_dict(co_commit_dict, orient='index')
		# output_file = os.path.join(output_file_dir, (project_name + '_co_commit.csv'))
		# df.to_csv(output_file)



