'''
Reformat fct adjacancy from {(file1.py, pile2.py):num....} to a 2D adjacency representation. 
Required for congruence calculations
'''
import os
import sys
import pandas as pd
import cPickle as pickle
from collections import defaultdict
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input_adjacency_dir', help='Directory containing pickles list of file pair co-commit counts',\
					default='Sample_Data/congruence/co_commit_adj_pickle/')
parser.add_argument('--output_pickle_dir', help='Directory reformatted 2d adjacency matrix per project',\
					default='Sample_Data/congruence/co_commit_adj/')
args, unknown = parser.parse_known_args()

input_adjacency_dir = args.input_adjacency_dir
output_pickle_dir = args.output_pickle_dir

try:
    os.makedirs(output_pickle_dir)
except:
    pass

def dd():
	return defaultdict(int)

for fileName in os.listdir(input_adjacency_dir):
	file_path = os.path.join(input_adjacency_dir, fileName)
	adj_pick = os.path.join(output_pickle_dir, fileName)

	if os.path.isfile(file_path) == True and os.path.isfile(adj_pick) == False:
		print "Processing for file: ", fileName
		fct_adjacency = pickle.load(open(file_path, 'rb'))
		reformed_dict = defaultdict(dd)

		for file1, file2 in fct_adjacency:
			reformed_dict[file1][file2] = fct_adjacency[(file1,file2)]
			reformed_dict[file2][file1] = fct_adjacency[(file1,file2)]

		#Save as pickle
		adj_df = pd.DataFrame.from_dict(reformed_dict, orient='index')
		adj_df.fillna(0.0, inplace=True)
                try:
		    adj_df.to_pickle(adj_pick)
                except SystemError, se:
                    print "Cannot write pickle for " + fileName
