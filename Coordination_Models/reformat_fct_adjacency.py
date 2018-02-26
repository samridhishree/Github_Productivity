'''
Reformat fct adjacancy from {(file1.py, pile2.py):num....} to a 2D adjacency representation
'''
import os
import sys
import pandas as pd
import cPickle as pickle
from collections import defaultdict

fct_adjacency_dir = sys.argv[1]
#valid_projects_pickle = sys.argv[2]
output_pickle_dir = sys.argv[2]
#projects = pickle.load(open(valid_projects_pickle, 'rb'))

def dd():
	return defaultdict(int)

for fileName in os.listdir(fct_adjacency_dir):
#for project in projects:
	#fileName = project + '_co_commit.pickle'
	file_path = os.path.join(fct_adjacency_dir, fileName)
	adj_pick = os.path.join(output_pickle_dir, fileName)
	if os.path.isfile(file_path) == True and os.path.isfile(adj_pick) == False:
		#project_name = fileName.split('_co_commit.pickle')[0]
		print "Processing for file: ", fileName
		fct_adjacency = pickle.load(open(file_path, 'rb'))
		reformed_dict = defaultdict(dd)

		for file1, file2 in fct_adjacency:
			reformed_dict[file1][file2] = fct_adjacency[(file1,file2)]
			reformed_dict[file2][file1] = fct_adjacency[(file1,file2)]

		#Save as pickle
		adj_df = pd.DataFrame.from_dict(reformed_dict, orient='index')
		adj_df.fillna(0.0, inplace=True)
		adj_df.to_pickle(adj_pick)