'''
Saves the people-module dictionary. Should be calculated for both FCT and CGRAPH
'''

import os
import sys
import csv
import pandas as pd
import cPickle as pickle
from collections import defaultdict

people_file_pickle_dir = sys.argv[1]
file_mod_pickle_dir = sys.argv[2]
output_pickle_dir = sys.argv[3]

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
				#print file_mod_dict.keys()

				user_mod_dict = defaultdict(set)
				for user in user_file_dict:
					files_affected = user_file_dict[user]
					files_affected = list(map(lambda x: x.lower(), files_affected))
					#print files_affected
					for file in files_affected:
						if file in file_mod_dict:
							#print "file: ", file
							user_mod_dict[user].add(file_mod_dict[file])
					#user_mod_dict[user] = [file_mod_dict[f] for f in files_affected if f in file_mod_dict]

				#Save the user-module dict
				user_module_pick = os.path.join(output_pickle_dir, (project_name + '_user_module.pickle'))
				with open(user_module_pick, 'wb') as u_pickle:
					pickle.dump(user_mod_dict, u_pickle)
