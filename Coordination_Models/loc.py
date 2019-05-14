'''
'''
import os
import sys
import csv
import operator
import ast
import calendar
import numpy as np
import pandas as pd
import cPickle as pickle
from pymongo import MongoClient
from collections import defaultdict, OrderedDict
from itertools import groupby, combinations
from datetime import datetime, timedelta
from dateutil import relativedelta
import argparse
import unicodedata

# Read from mongo and the burst pickle into a dedicated file

csv.field_size_limit(sys.maxsize)

parser = argparse.ArgumentParser()
parser.add_argument('--db', help="Mongo database to read lines of code info from", default="pypi-v6")
parser.add_argument('--locfile', help="file to write lines of code into", default="Sample_Data/congruence/loc.csv")
parser.add_argument('--burst_pickle', help="File containing burst boundaries", default="Sample_Data/HMM/results/fixed_bursts.pickle")


args = parser.parse_args()
client = MongoClient("mongodb://127.0.0.1:27017")
issue_events = client[args.db]["issue_events"]

'''
Converts the burst intervals to actual datetime intervals
'''
def FormatBurstTimeInterval(bursts):
	formatted = []
	for i,burst in enumerate(bursts):
		parts= burst.split('-')
		low = parts[0]
		high = parts[1]
		low = low.replace('/', '-')
		high_str = high.replace('/', '-')
		low = datetime.strptime(low, '%Y-%m-%d')
		high = datetime.strptime(high_str, '%Y-%m-%d')
		formatted.append((low, high))
	return formatted

#db.project_events.find({project_name_lower:"kids.cache", project_owner_lower:"0k"},{rectype:1,_id:0,time:1,insertions:1,deletions:1})
#{ "deletions" : 2, "rectype" : "commit_messages", "insertions" : 3, "time" : ISODate("2015-04-27T04:40:32Z") }
#{ "deletions" : 20, "rectype" : "commit_messages", "insertions" : 241, "time" : ISODate("2015-04-24T09:24:48Z") }

locf = csv.writer(open(args.locfile,"w"))
locf.writerow(["project","burstid","daterange","insertions","deletions","merges","changed_files"])

print "Loading burst boundaries..."
burst_dict = pickle.load(open(args.burst_pickle, 'rb'))
projects = burst_dict.keys()


for p in projects:
    powner, pname = p.split("~")
    print p
    for burstid, intv in enumerate(FormatBurstTimeInterval(burst_dict[p])):
        (insertions, deletions, changed_files, merges) = (0,0,0,0)
        for commit in issue_events.find({"time": {"$gte": intv[0], "$lt": intv[1]+timedelta(days=1)}, 
                                           "rectype": "pull_request_merged",
                                           "project_name_lower": pname.lower(), "project_owner_lower": powner.lower()} ):
            try:
                insertions += commit["status"]["additions"]
                deletions += commit["status"]["deletions"]
                changed_files += commit["status"]["changed_files"]
                merges += 1
            except:
                pass
        locf.writerow([p,burstid,burst_dict[p][burstid],insertions,deletions,merges,changed_files])
         
