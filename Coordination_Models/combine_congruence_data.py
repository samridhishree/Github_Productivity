'''
Combines the individual bursty congruence measures into a single csv file with project_name and project_owner information
'''

import os
import sys
import csv
import pandas as pd
import cPickle as pickle
import argpase
csv.field_size_limit(sys.maxsize)

parser = argparse.ArgumentParser()
parser.add_argument('--congruence_dir', help='Directory containing the out csvs from burst_congruence.py',\
    default='Sample_Data/congruence/congruence_outputs/output_csv/')
parser.add_argument('--output_file', help='Final regression table',\
    default='Sample_Data/congruence/congruence_outputs/regression_table.csv')
args, unknown = parser.parse_known_args()

congruence_dir = args.congruence_dir
output_file = args.output_file

title_row = ['burst_id', 'burst_start', 'burst_end', 'burst_duration_days', 'total_activity', \
            'num_files (Change Size)', 'file_modules (#Teams)', 'total_num_issues', 'issues_opened', 'issues_closed',\
            'avg_res_time_hours', 'efficiency', 'issue_per_person (Team Load)', \
            'activity_per_person', 'committing_users', 'commenting_users', 'total_actors',\
            'component_experience', 'tenure', 'structural_congruence_fct', 'mr_congruence_fct', 'users_to_coordinate']

w = open(output_file, 'wb')
writer = csv.writer(w, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
writer.writerow(['project'] + title_row)

#for project in projects:
for filename in os.listdir(congruence_dir):
    project = filename.split('_cm_mr_info.csv')[0]
    #congruence_file = os.path.join(congruence_dir, project.replace('~','_') + '_cm_mr_info.csv')
    congruence_file = os.path.join(congruence_dir, filename)
    if os.path.isfile(congruence_file) == False:
        continue
    print "Processing for project = ", project
    data = pd.read_csv(congruence_file)
    data.dropna(inplace=True)
    for idx,row in data.iterrows():
        to_write = [project]
        to_write.extend(list(row[title_row]))
        writer.writerow(to_write)
w.close()


