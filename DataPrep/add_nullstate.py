'''
Copies the daily_data files (which give counts of activity for each day for a project)
and adds in a "NullState" date for in between days when nothing happened.
'''


import os
import sys
import csv
import glob
import calendar
from collections import defaultdict
from datetime import datetime
import pdb
import argparse

csv.field_size_limit(sys.maxsize)


parser = argparse.ArgumentParser()
#parser.add_argument('--aliases', help='list of csv files, each containing (provenance, alias1, alias2)',
#                default='DataPrep/aliases_prs.csv,DataPrep/aliases_pushes.csv')
parser.add_argument('--daily_data', help='daily activity counts per project',
                default='Sample_Data/HMM/daily_data/')
parser.add_argument('--daily_data_with_nullstate', help='daily activity counts per project with empty days added',
                default='Sample_Data/HMM/daily_data_with_nullstate2/')
args, unknown = parser.parse_known_args()

def mkdirp(d):
    try:
        os.makedirs(d)
    except:
        pass

mkdirp(args.daily_data_with_nullstate)

def difference(startdate, enddate):
    """Calculate time difference between two dates in YYYYMMDD format"""
    st = datetime.strptime(startdate, "%Y%m%d")
    en = datetime.strptime(enddate, "%Y%m%d")
    return (en-st).days
    

for ix, project in enumerate(sorted(os.listdir(args.daily_data))):
    print ix, project
    infile = csv.DictReader(open(os.path.join(args.daily_data,project)))
    columns = infile.fieldnames
    outfile = csv.writer(open(os.path.join(args.daily_data_with_nullstate,project),"w"))
    outfile.writerow(columns)
    lastperiod = ""
    for inrow in infile:
        if lastperiod != "":
            for period in range(difference(lastperiod, inrow["period"])-1):
                outfile.writerow([inrow["project"], "NullState"] + [0 for c in columns[2:]])
        outfile.writerow([inrow[c] for c in columns])
        lastperiod = inrow["period"]
