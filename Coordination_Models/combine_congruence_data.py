'''
Combines the individual bursty congruence measures into a single csv file with project_name and project_owner information
'''

import os
import pdb
import sys
import csv
import pandas as pd
import cPickle as pickle
from collections import defaultdict
import argparse
csv.field_size_limit(sys.maxsize)

parser = argparse.ArgumentParser()
parser.add_argument('--congruence_dir', help='Directory containing the out csvs from burst_congruence.py',\
    default='Sample_Data/congruence/congruence_outputs/output_csv/')
parser.add_argument('--extraneous_events', help='Directory containing tables of extraneous events',
    default='Sample_Data/congruence/extraneous_events/')
parser.add_argument('--dont_extraneous', help='Skip processing of extraneous events',
    action="store_true")
parser.add_argument('--lines_of_code', help='include lines of code per commit',
    default="Sample_Data/congruence/loc.csv")
parser.add_argument('--output_file', help='Final regression table',\
    default='Sample_Data/congruence/congruence_outputs/regression_table.csv')
args = parser.parse_args()

congruence_dir = args.congruence_dir
extra_dir = args.extraneous_events
output_file = args.output_file
locfile = args.lines_of_code
do_extraneous = not args.dont_extraneous

title_row = ['burst_id', 'burst_start', 'burst_end', 'burst_duration_days', 'total_activity', 'num_commits',\
            'num_files (Change Size)', 'file_modules (#Teams)', 'total_num_issues', 'issues_opened', 'issues_closed',\
            'avg_res_time_hours', 'efficiency', 'issue_per_person (Team Load)', \
            'activity_per_person', 'committing_users', 'commenting_users', 'total_actors',\
            'component_experience', 'tenure', 'structural_congruence_fct', 'mr_congruence_fct', 'users_to_coordinate']
if do_extraneous: title_row.append('extraneous_events')
if len(locfile): 
    print "Reading lines of code information"
    title_row.extend(["insertions","deletions","loc_net","loc_changed"])
    loccsv = csv.DictReader(open(locfile))
    loccache = defaultdict(dict)
    for locrow in loccsv:
        loccache[locrow["project"]][int(locrow["burstid"])] =  \
            {"insertions":  int(locrow["insertions"]),
             "deletions": int(locrow["deletions"])}

w = open(output_file, 'wb')
writer = csv.writer(w, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
writer.writerow(['project'] + title_row)

#for project in projects:
print "Scanning projects"
for filename in os.listdir(congruence_dir):
    project = filename.split('_cm_mr_info.csv')[0]
    #congruence_file = os.path.join(congruence_dir, project.replace('~','_') + '_cm_mr_info.csv')
    congruence_file = os.path.join(congruence_dir, filename)
    if os.path.isfile(congruence_file) == False:
        continue
    print "Processing for project = ", project
    data = pd.read_csv(congruence_file)
    data.dropna(inplace=True)
        
    if do_extraneous:
        try:
            extraneous_events = pd.read_csv(os.path.join(extra_dir, project + "_extra.csv"))
        except Exception, e:
            print type(e), e, project 
            import pdb; pdb.set_trace()
    for idx,row in data.iterrows():
        if len(locfile):
            row["insertions"] = loccache[project][row["burst_id"]]["insertions"]
            row["deletions"] = loccache[project][row["burst_id"]]["deletions"]
            row["loc_net"] = row["insertions"]-row["deletions"]
            row["loc_changed"] = row["insertions"] + row["deletions"]
        if do_extraneous:
            row["extraneous_events"] = int(extraneous_events.loc[extraneous_events["burst_id"] == row["burst_id"]]["extraneous_events"])
            print "Extraneous events for ", project, "burst ", row["burst_id"], "are ", row["extraneous_events"]
        to_write = [project]
        to_write.extend(list(row[title_row]))
        writer.writerow(to_write)
w.close()


