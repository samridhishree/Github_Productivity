'''
Creates file-module dictionaries per project.
Module - cluster/module class obtained after partioning the co-commit graph.
{file1.py: module_number, ...., file_n.py: module_number}
'''

import os
import sys
import csv
import cPickle as pickle
import pandas as pd
import argparse

csv.field_size_limit(sys.maxsize)

parser = argparse.ArgumentParser()
parser.add_argument('--code_metric_path', help='Directory containing graph metrics obtained by partioning the graph',\
					default='data/co_commit_graph_stats/')
parser.add_argument('--output_pickle_path', help='Output directory to store pickle files per project to store file-module membership',\
					default='data/file_module_dict/')
args, unknown = parser.parse_known_args()

code_metric_path = args.code_metric_path
output_pickle_path = args.output_pickle_path

try:
    os.makedirs(output_pickle_path)
except:
    pass

for fileName in os.listdir(code_metric_path):
	if fileName.endswith('.csv'):
		project_name = fileName.split('_code_graph_metrics.csv')[0]
		print "Processing for project: ", project_name
		code_metrics = pd.read_csv(os.path.join(code_metric_path, fileName))
		files = code_metrics['file_name']
		modules = code_metrics['modularity_class']

		#Create the file-module dictionary
		module_mem_from_graph = {}
		for file,module in zip(files, modules):
			module_mem_from_graph[file] = module

		#Save as pickle
		file_mod_pickle = os.path.join(output_pickle_path, (project_name + '_file_mod.pickle'))
		with open(file_mod_pickle, 'wb') as c_pickle:
			pickle.dump(module_mem_from_graph, c_pickle)