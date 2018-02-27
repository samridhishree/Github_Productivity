'''
Creates a people-module membership dictionary.
Looks at the files committed by a person and then links it to the module number that the file belongs to.
This transitive relation is stored as a dictionary containing people-module membership per project.

Output - {user1:[module1,....,module_n]....}
'''

import os
import sys
import csv
import pandas as pd
import cPickle as pickle
from collections import defaultdict
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--people_file_pickle_dir', help='Directory with people-file pickles (output of: people_file_dict.py)')
parser.add_argument('--file_mod_pickle_dir', help='Directory with file-module pickles (output of: file_module_dict.py)')
parser.add_argument('--output_pickle_dir', help='Pickle file containing the people-module dictionary pickles per project')
args, unknown = parser.parse_known_args()

people_file_pickle_dir = args.people_file_pickle_dir
file_mod_pickle_dir = args.file_mod_pickle_dir
output_pickle_dir = args.output_pickle_dir

# Placeholder to properly unpickle the inputs
def dd():
	return defaultdict(int)

for fileName in os.listdir(people_file_pickle_dir):
	if fileName.endswith('.pickle'):
		project_name = fileName.split('_user_file.pickle')[0]
		file_mod_pickle = project_name + '_file_mod.pickle'
		file_mod_p_file = file_mod_pickle_dir + file_mod_pickle

		if os.path.isfile(file_mod_p_file):
			with open(os.path.join(people_file_pickle_dir, fileName), "rb") as f:
				user_file_dict = pickle.load(f)
				print "Processing for project: ", project_name
				file_mod_dict = pickle.load(open(file_mod_p_file, "rb"))
				file_mod_dict = dict((k.lower(), v) for k,v in file_mod_dict.iteritems())
				
				user_mod_dict = defaultdict(set)
				for user in user_file_dict:
					files_affected = user_file_dict[user]
					files_affected = list(map(lambda x: x.lower(), files_affected))
					for file in files_affected:
						if file in file_mod_dict:
							user_mod_dict[user].add(file_mod_dict[file])
					
				#Save the user-module dict
				user_module_pick = os.path.join(output_pickle_dir, (project_name + '_user_module.pickle'))
				with open(user_module_pick, 'wb') as u_pickle:
					pickle.dump(user_mod_dict, u_pickle)
