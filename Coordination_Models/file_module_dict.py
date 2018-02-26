'''
Creates file-module dictionaries per project.
{file1.py: module, ...., file_n.py: module}
'''

import os
import sys
import csv
import cPickle as pickle
import pandas as pd

csv.field_size_limit(sys.maxsize)

code_metric_path = sys.argv[1]
output_pickle_path = sys.argv[2]

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